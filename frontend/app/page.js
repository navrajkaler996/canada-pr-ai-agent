"use client";
import { useState, useRef, useEffect } from "react";

const RED = "#CC0000";
const RED_DARK = "#990000";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm your Canadian PR assistant. I'll help you calculate your Express Entry CRS score and estimate your chances of getting an ITA. Let's start — do you have a spouse or common-law partner? (yes / no)",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

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
      setMessages([...newMessages, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Is the backend running?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: "920px",
        margin: "0 auto",
        padding: "0 16px",
        boxSizing: "border-box",
        fontFamily: "Georgia",
      }}>
      {/* Header */}
      <div
        style={{
          padding: "20px 0 16px",

          flexShrink: 0,
          display: "flex",
          alignItems: "center",

          gap: "10px",
        }}>
        <div>
          <p
            style={{
              margin: 0,
              fontSize: "18px",
              fontWeight: 500,
              color: "var(--color-text-primary)",
            }}>
            CanPR.ai
          </p>
          {/* <p
            style={{
              margin: "2px 0 0",
              fontSize: "14px",
              color: "var(--color-text-secondary)",
            }}>
            Honest take on your Canadian Permanent Residency chance.
          </p> */}
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px 0",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              alignItems: "flex-start",
              gap: "10px",
            }}>
            <div
              style={{
                maxWidth: "80%",
                padding: "10px 14px",
                borderRadius:
                  msg.role === "user"
                    ? "18px 18px 4px 18px"
                    : "4px 18px 18px 18px",
                background:
                  msg.role === "user"
                    ? "#363535"
                    : "var(--color-background-secondary)",

                color:
                  msg.role === "user" ? "#ffffff" : "var(--color-text-primary)",
                fontSize: "16px",
                lineHeight: "1.6",
              }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "13px",
              }}></div>
            <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  style={{
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",

                    animation: "pulse 1.2s ease-in-out infinite",
                    animationDelay: `${i * 0.2}s`,
                  }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: "12px 0 24px",

          flexShrink: 0,
        }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: "#363535",
            // border: `1px solid #ddd`,
            borderRadius: "30px",
            padding: "8px 8px 8px 16px",
          }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Reply..."
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              fontSize: "15px",
              color: "var(--color-text-primary)",
              padding: 0,
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "var(--border-radius-md)",
              border: "none",
              background:
                input.trim() && !loading ? "transparent" : "transparent",
              color:
                input.trim() && !loading
                  ? "#ffffff"
                  : "var(--color-text-secondary)",
              cursor: input.trim() && !loading ? "pointer" : "default",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              transition: "background 0.15s",
            }}>
            ↑
          </button>
        </div>
      </div>

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1); }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${RED}66; border-radius: 4px; }
        input::placeholder { color: var(--color-text-secondary); }
      `}</style>
    </div>
  );
}
