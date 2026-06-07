"use client";

import React, { useState, useRef, useEffect } from "react";
import ChatMessage from "./components/ChatMessage";
import {
  getQuestion,
  getFirstQuestionId,
  getScoreMessage,
  convertScoresToCLB,
  isFlowComplete,
  CLB_CONVERSION,
} from "./data/questions.js";

const RED = "#CC0000";

// Build a message object from a question
function messageFromQuestion(question, profile) {
  const base = { role: "assistant", questionId: question.id };

  if (question.type === "options") {
    return { ...base, content: question.message, options: question.options };
  }

  if (question.type === "score_input") {
    const testKey =
      question.id === "first_language_scores"
        ? "first_language_test"
        : question.id === "spouse_language_scores"
          ? "spouse_language_test"
          : question.id === "second_language_scores"
            ? "second_language_test"
            : null;
    const test = testKey ? profile[testKey] : null;
    const hint = test ? CLB_CONVERSION[test]?.hint : "score";

    return {
      ...base,
      content: getScoreMessage(question.id, profile),
      scoreInput: { abilities: question.abilities, hint },
    };
  }

  // type: "text"
  return { ...base, content: question.message, options: null };
}

export default function Home() {
  const firstId = getFirstQuestionId();
  const firstQuestion = getQuestion(firstId);

  const WELCOME = {
    role: "assistant",
    content:
      "Hi! I'm **PRCompass** — your Canadian Express Entry guide.\n\nI can calculate your CRS score, analyze recent draws, and tell you exactly where you stand. What would you like to do?",
    showQuickReplies: true,
    options: [
      { label: "Calculate my CRS", value: "calculate_crs" },
      { label: "Latest draws", value: "latest_draws" },
      { label: "Am I competitive?", value: "competitive" },
      { label: "Just chat", value: "chat" },
    ],
  };

  const [messages, setMessages] = useState([WELCOME]);
  const [profile, setProfile] = useState({});
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [inCRSFlow, setInCRSFlow] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  // Move to next question
  const advanceQuestion = (updatedProfile, currentId) => {
    const current = getQuestion(currentId);
    if (!current) return;

    const nextId = current.next(updatedProfile);

    if (nextId === null) {
      finishCRSFlow(updatedProfile);
      return;
    }

    const nextQuestion = getQuestion(nextId);
    if (!nextQuestion) return;

    setCurrentQuestionId(nextId);
    setMessages((prev) => [
      ...prev,
      messageFromQuestion(nextQuestion, updatedProfile),
    ]);
  };

  // Handle option button tap
  const handleOptionSelect = (opt) => {
    if (!inCRSFlow) {
      if (opt.value === "calculate_crs") {
        startCRSFlow();
      } else {
        sendToAI(opt.label);
      }
      return;
    }

    const userMsg = { role: "user", content: opt.label };
    const updatedProfile = { ...profile, [currentQuestionId]: opt.value };
    setProfile(updatedProfile);
    setMessages((prev) => [...prev, userMsg]);
    advanceQuestion(updatedProfile, currentQuestionId);
  };

  // Handle score input submission
  const handleScoreSubmit = (scores) => {
    const question = getQuestion(currentQuestionId);
    const testKey =
      currentQuestionId === "first_language_scores"
        ? "first_language_test"
        : currentQuestionId === "spouse_language_scores"
          ? "spouse_language_test"
          : currentQuestionId === "second_language_scores"
            ? "second_language_test"
            : null;
    const test = testKey ? profile[testKey] : null;

    const clb = convertScoresToCLB(test, scores);

    const summary = question.abilities
      .map((a) => `${a}: ${scores[a]}${clb ? ` (CLB ${clb[a]})` : ""}`)
      .join(" · ");

    const userMsg = { role: "user", content: summary };
    const updatedProfile = {
      ...profile,
      [currentQuestionId]: scores,
      [`${currentQuestionId}_clb`]: clb,
    };

    setProfile(updatedProfile);
    setMessages((prev) => [...prev, userMsg]);
    advanceQuestion(updatedProfile, currentQuestionId);
  };

  // Start CRS flow
  const startCRSFlow = () => {
    setInCRSFlow(true);
    setCurrentQuestionId(firstId);
    const firstMsg = messageFromQuestion(firstQuestion, {});
    setMessages((prev) => [...prev, firstMsg]);
  };

  // Finish CRS flow — send profile to AI
  const finishCRSFlow = async (finalProfile) => {
    setInCRSFlow(false);
    setCurrentQuestionId(null);

    const completionMsg = { role: "user", content: "That's all my info!" };
    setMessages((prev) => [...prev, completionMsg]);
    setLoading(true);

    // Map frontend profile → crs_calculator.py format
    const hasSpouse = finalProfile.marital_status === "married_accompanying";
    const firstCLB = finalProfile.first_language_scores_clb ?? {};
    const secondCLB = finalProfile.second_language_scores_clb ?? null;
    const spouseCLB = finalProfile.spouse_language_scores_clb ?? {};

    const calcProfile = {
      has_spouse: hasSpouse,
      age: parseInt(finalProfile.age),
      education: finalProfile.education,
      clb_speaking: firstCLB.speaking ?? 0,
      clb_listening: firstCLB.listening ?? 0,
      clb_reading: firstCLB.reading ?? 0,
      clb_writing: firstCLB.writing ?? 0,
      canadian_work_years: finalProfile.canadian_experience ?? 0,
      foreign_work_years: finalProfile.foreign_experience ?? 0,
      first_language: ["CELPIP", "IELTS"].includes(
        finalProfile.first_language_test,
      )
        ? "english"
        : "french",
      has_canadian_sibling: finalProfile.sibling_in_canada === true,
      french_clb_scores: secondCLB
        ? [
            secondCLB.speaking,
            secondCLB.listening,
            secondCLB.reading,
            secondCLB.writing,
          ]
        : [],
      canadian_education_years:
        finalProfile.canadian_education === "three_plus_years"
          ? 3
          : finalProfile.canadian_education === "one_two_years"
            ? 1
            : 0,
      has_provincial_nomination: finalProfile.provincial_nomination === true,
      ...(hasSpouse && {
        spouse_education: finalProfile.spouse_education,
        spouse_clb_speaking: spouseCLB.speaking ?? 0,
        spouse_clb_listening: spouseCLB.listening ?? 0,
        spouse_clb_reading: spouseCLB.reading ?? 0,
        spouse_clb_writing: spouseCLB.writing ?? 0,
        spouse_canadian_work_years:
          finalProfile.spouse_canadian_experience ?? 0,
      }),
    };

    try {
      // Call real calculator
      const calcRes = await fetch("http://localhost:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(calcProfile),
      });
      const calcData = await calcRes.json();

      // Send real result to AI to explain
      const systemMsg = {
        role: "user",
        content: `The user just completed their CRS profile. Here is their REAL calculated CRS score from the official formula:\n\n${JSON.stringify(calcData, null, 2)}\n\nPresent this score clearly with a breakdown, then compare to recent draws and give actionable advice.`,
      };

      await streamFromAI([...messages, completionMsg, systemMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, couldn't reach the calculator. Is the backend running?",
        },
      ]);
      setLoading(false);
    }
  };

  // Send free text to AI
  const sendToAI = async (text) => {
    if (!text.trim() || loading) return;
    const userMsg = { role: "user", content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    await streamFromAI(newMessages);
  };

  // Stream response from backend
  const streamFromAI = async (newMessages) => {
    setLoading(true);
    setStreamingText("");

    try {
      const res = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: newMessages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split("\n")) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            try {
              const parsed = JSON.parse(data);
              if (parsed.token) {
                full += parsed.token;
                setStreamingText(full);
              }
            } catch {}
          }
        }
      }

      setMessages((prev) => [...prev, { role: "assistant", content: full }]);
      setStreamingText("");
    } catch {
      try {
        const res = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: newMessages.map((m) => ({
              role: m.role,
              content: m.content,
            })),
          }),
        });
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, something went wrong. Is the backend running?",
          },
        ]);
      }
    } finally {
      setLoading(false);
      setStreamingText("");
      inputRef.current?.focus();
    }
  };

  const currentQuestion = getQuestion(currentQuestionId);
  const isTextQuestion = currentQuestion?.type === "text";

  const handleTextAnswer = (value) => {
    const question = getQuestion(currentQuestionId);
    const error = question.validate?.(value);
    if (error) return;
    const updatedProfile = { ...profile, [currentQuestionId]: value };
    setProfile(updatedProfile);
    setMessages((prev) => [...prev, { role: "user", content: value }]);
    advanceQuestion(updatedProfile, currentQuestionId);
  };

  const handleSend = () => {
    if (!input.trim() || loading) return;
    if (inCRSFlow && isTextQuestion) {
      handleTextAnswer(input.trim());
      setInput("");
      return;
    }
    sendToAI(input);
    setInput("");
  };
  // Render
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        background: "var(--color-background)",
      }}>
      {/* Sidebar */}
      <aside
        style={{
          width: "140px",
          flexShrink: 0,
          borderRight: "1px solid rgba(255,255,255,0.07)",
          display: "flex",
          flexDirection: "column",
          padding: "24px 0",
          overflowY: "auto",
          background: "var(--color-background-secondary)",
        }}>
        <div
          style={{
            padding: "0 20px 24px",
            borderBottom: "1px solid rgba(255,255,255,0.07)",
          }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: RED,
              }}
            />
            <span
              style={{
                fontSize: "15px",
                fontWeight: 600,
                color: "var(--color-text-primary)",
                letterSpacing: "-0.3px",
              }}>
              PRCompass
            </span>
          </div>
          <p
            style={{
              margin: "6px 0 0",
              fontSize: "11px",
              color: "var(--color-text-secondary)",
              lineHeight: "1.5",
            }}>
            Canada Express Entry Intelligence
          </p>
        </div>
      </aside>

      {/* Chat area */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
        }}>
        {/* Header */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: "1px solid rgba(255,255,255,0.07)",
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}>
          <div>
            <p
              style={{
                margin: 0,
                fontSize: "15px",
                fontWeight: 500,
                color: "var(--color-text-primary)",
              }}>
              PRCompass
            </p>
            <p
              style={{
                margin: "2px 0 0",
                fontSize: "12px",
                color: "var(--color-text-secondary)",
              }}>
              Powered by live IRCC draw data
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <div
              style={{
                width: "7px",
                height: "7px",
                borderRadius: "50%",
                background: "#22c55e",
              }}
            />
            <span
              style={{
                fontSize: "12px",
                color: "var(--color-text-secondary)",
              }}>
              Online
            </span>
          </div>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "28px 24px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            maxWidth: "760px",
            width: "100%",
            margin: "0 auto",
            boxSizing: "border-box",
          }}>
          {messages.map((msg, i) => (
            <ChatMessage
              key={i}
              msg={msg}
              isLatest={i === messages.length - 1}
              isStreaming={false}
              onOptionSelect={handleOptionSelect}
              onScoreSubmit={handleScoreSubmit}
            />
          ))}

          {/* Streaming bubble */}
          {streamingText && (
            <ChatMessage
              msg={{ role: "assistant", content: streamingText }}
              isLatest={true}
              isStreaming={true}
              onOptionSelect={() => {}}
              onScoreSubmit={() => {}}
            />
          )}

          {/* Loading dots */}
          {loading && !streamingText && (
            <div style={{ display: "flex", gap: "5px", padding: "14px 0" }}>
              {[0, 1, 2].map((j) => (
                <div
                  key={j}
                  style={{
                    width: "7px",
                    height: "7px",
                    borderRadius: "50%",
                    background: RED,
                    animation: "bounce 1.2s ease-in-out infinite",
                    animationDelay: `${j * 0.18}s`,
                  }}
                />
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input — hidden during CRS flow */}

        <div
          style={{
            padding: "12px 24px 24px",
            flexShrink: 0,
            maxWidth: "760px",
            width: "100%",
            margin: "0 auto",
            boxSizing: "border-box",
          }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "#363535",
              borderRadius: "30px",
              padding: "8px 8px 8px 18px",
              border: "1px solid rgba(255,255,255,0.08)",
              opacity: inCRSFlow ? 0.4 : 1,
              transition: "opacity 0.2s",
            }}>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !e.shiftKey && handleSend()
              }
              placeholder={
                inCRSFlow && !isTextQuestion
                  ? "Use the buttons above to answer..."
                  : "Ask about your CRS score, draws, or PR strategy..."
              }
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                outline: "none",
                fontSize: "15px",
                color: "var(--color-text-primary)",
                padding: 0,
                opacity: inCRSFlow && !isTextQuestion ? 0.4 : 1,
                cursor: inCRSFlow && !isTextQuestion ? "not-allowed" : "text",
              }}
              disabled={inCRSFlow && !isTextQuestion}
            />
            <button
              onClick={handleSend}
              disabled={
                !input.trim() || loading || (inCRSFlow && !isTextQuestion)
              }
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "50%",
                border: "none",
                background:
                  input.trim() && !loading ? RED : "rgba(255,255,255,0.1)",
                color: "#fff",
                cursor: input.trim() && !loading ? "pointer" : "default",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "16px",
                transition: "background 0.15s",
                flexShrink: 0,
              }}>
              ↑
            </button>
          </div>
          <p
            style={{
              textAlign: "center",
              fontSize: "11px",
              color: "var(--color-text-secondary)",
              margin: "8px 0 0",
            }}>
            Always verify with official IRCC sources
          </p>
        </div>
      </div>

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${RED}55; border-radius: 4px; }
        input::placeholder { color: var(--color-text-secondary); opacity: 0.6; }
      `}</style>
    </div>
  );
}
