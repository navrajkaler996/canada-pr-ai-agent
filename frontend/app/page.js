"use client";
import { useState, useRef, useEffect } from "react";

const RED = "#CC0000";

// ── Tiny markdown renderer ──────────────────────────────────────────────────
function Markdown({ text }) {
  const lines = text.split("\n");
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Blank line
    if (!line.trim()) {
      i++;
      continue;
    }

    // Heading
    if (line.startsWith("### ")) {
      elements.push(
        <h3
          key={i}
          style={{
            fontsize: "16px",
            fontWeight: 600,
            margin: "12px 0 4px",
            color: "var(--color-text-primary)",
          }}>
          {line.slice(4)}
        </h3>,
      );
      i++;
      continue;
    }
    if (line.startsWith("## ")) {
      elements.push(
        <h2
          key={i}
          style={{
            fontSize: "16px",
            fontWeight: 700,
            margin: "14px 0 4px",
            color: "var(--color-text-primary)",
          }}>
          {line.slice(3)}
        </h2>,
      );
      i++;
      continue;
    }

    // Bullet list
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const items = [];
      while (
        i < lines.length &&
        (lines[i].startsWith("- ") || lines[i].startsWith("* "))
      ) {
        items.push(
          <li key={i} style={{ marginBottom: "3px" }}>
            {renderInline(lines[i].slice(2))}
          </li>,
        );
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} style={{ paddingLeft: "18px", margin: "6px 0" }}>
          {items}
        </ul>,
      );
      continue;
    }

    // Numbered list
    if (/^\d+\. /.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(
          <li key={i} style={{ marginBottom: "3px" }}>
            {renderInline(lines[i].replace(/^\d+\. /, ""))}
          </li>,
        );
        i++;
      }
      elements.push(
        <ol key={`ol-${i}`} style={{ paddingLeft: "18px", margin: "6px 0" }}>
          {items}
        </ol>,
      );
      continue;
    }

    // Normal paragraph
    elements.push(
      <p key={i} style={{ margin: "4px 0", lineHeight: "1.65" }}>
        {renderInline(line)}
      </p>,
    );
    i++;
  }

  return <div style={{ fontsize: "16px" }}>{elements}</div>;
}

function renderInline(text) {
  // Bold + italic + code inline
  const parts = [];
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let last = 0,
    m;
  while ((m = regex.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[0].startsWith("**"))
      parts.push(<strong key={m.index}>{m[2]}</strong>);
    else if (m[0].startsWith("*")) parts.push(<em key={m.index}>{m[3]}</em>);
    else
      parts.push(
        <code
          key={m.index}
          style={{
            background: "rgba(255,255,255,0.1)",
            borderRadius: "3px",
            padding: "1px 5px",
            fontSize: "13px",
            fontFamily: "monospace",
          }}>
          {m[4]}
        </code>,
      );
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

// ── Dummy sidebar data ──────────────────────────────────────────────────────
const DUMMY_DRAWS = [
  { date: "May 28, 2026", type: "French Language", crs: 409, itas: 4500 },
  { date: "May 21, 2026", type: "General", crs: 524, itas: 3500 },
  { date: "May 14, 2026", type: "CEC", crs: 491, itas: 3200 },
  { date: "May 7, 2026", type: "PNP", crs: 741, itas: 1200 },
  { date: "Apr 30, 2026", type: "General", crs: 519, itas: 4000 },
];

const TIPS = [
  "CLB 10 in all abilities adds up to 50 CRS points vs CLB 9.",
  "A provincial nomination adds 600 points — near-guaranteed ITA.",
  "Canadian work experience is worth more than foreign experience.",
  "French proficiency opens a lower-cutoff draw category.",
  "A job offer from a Canadian employer can add 50–200 points.",
];

// ── Main component ──────────────────────────────────────────────────────────
export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm **CanPR.ai**, your Canadian PR assistant. I can help you:\n- Calculate your **CRS score**\n- Estimate your **ITA chances**\n- Explain recent **Express Entry draws**\n\nLet's start — do you have a spouse or common-law partner?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: "user", content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
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
        const lines = chunk.split("\n");
        for (const line of lines) {
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
    } catch (err) {
      // Fallback to non-streaming
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

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        background: "var(--color-background)",
      }}>
      {/* ── Sidebar ── */}
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
        {/* Logo */}
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
                fontSize: "16px",
                fontWeight: 600,
                color: "var(--color-text-primary)",
                letterSpacing: "-0.3px",
              }}>
              CanPR.ai
            </span>
          </div>
          <p
            style={{
              margin: "6px 0 0",
              fontSize: "12px",
              color: "var(--color-text-secondary)",
              lineHeight: "1.5",
            }}>
            Canada Express Entry Intelligence
          </p>
        </div>

        {/* Recent Draws */}
        {/* <div style={{ padding: "20px 20px 0" }}>
          <p
            style={{
              fontSize: "11px",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "var(--color-text-secondary)",
              marginBottom: "12px",
            }}>
            Recent Draws
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {DUMMY_DRAWS.map((d, i) => (
              <div
                key={i}
                style={{
                  padding: "10px 12px",
                  borderRadius: "10px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.06)",
                }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "4px",
                  }}>
                  <span
                    style={{
                      fontSize: "12px",
                      fontWeight: 600,
                      color: "var(--color-text-primary)",
                    }}>
                    {d.type}
                  </span>
                  <span
                    style={{ fontSize: "13px", fontWeight: 700, color: RED }}>
                    {d.crs}
                  </span>
                </div>
                <div
                  style={{ display: "flex", justifyContent: "space-between" }}>
                  <span
                    style={{
                      fontSize: "11px",
                      color: "var(--color-text-secondary)",
                    }}>
                    {d.date}
                  </span>
                  <span
                    style={{
                      fontSize: "11px",
                      color: "var(--color-text-secondary)",
                    }}>
                    {d.itas.toLocaleString()} ITAs
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div> */}

        {/* Tips */}
        {/* <div style={{ padding: "20px 20px 0", marginTop: "8px" }}>
          <p
            style={{
              fontSize: "11px",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "var(--color-text-secondary)",
              marginBottom: "12px",
            }}>
            Quick Tips
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {TIPS.map((tip, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  gap: "8px",
                  alignItems: "flex-start",
                }}>
                <div
                  style={{
                    width: "4px",
                    height: "4px",
                    borderRadius: "50%",
                    background: RED,
                    marginTop: "7px",
                    flexShrink: 0,
                  }}
                />
                <p
                  style={{
                    fontSize: "12px",
                    color: "var(--color-text-secondary)",
                    lineHeight: "1.5",
                    margin: 0,
                  }}>
                  {tip}
                </p>
              </div>
            ))}
          </div>
        </div> */}
      </aside>

      {/* ── Chat area ── */}
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
                fontsize: "16px",
                fontWeight: 500,
                color: "var(--color-text-primary)",
              }}>
              CanPR.ai
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
            padding: "28px 2px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            maxWidth: "760px",
            width: "100%",
            margin: "0 auto",
            boxSizing: "border-box",
          }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              }}>
              <div
                style={{
                  maxWidth: "100%",
                  padding: "11px 15px",
                  borderRadius:
                    msg.role === "user"
                      ? "18px 18px 4px 18px"
                      : "4px 18px 18px 18px",
                  background:
                    msg.role === "user"
                      ? "#363535"
                      : "var(--color-background-secondary)",
                  color:
                    msg.role === "user"
                      ? "#ffffff"
                      : "var(--color-text-primary)",
                  fontsize: "16px",
                  lineHeight: "1.65",
                }}>
                {msg.role === "assistant" ? (
                  <Markdown text={msg.content} />
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {/* Streaming bubble */}
          {streamingText && (
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <div
                style={{
                  maxWidth: "100%",
                  padding: "11px 15px",
                  borderRadius: "4px 18px 18px 18px",
                  background: "var(--color-background-secondary)",
                  color: "var(--color-text-primary)",
                  // border: "1px solid rgba(255,255,255,0.06)",
                }}>
                <Markdown text={streamingText} />
                <span
                  style={{
                    display: "inline-block",
                    width: "2px",
                    height: "14px",
                    background: RED,
                    marginLeft: "2px",
                    verticalAlign: "middle",
                    animation: "blink 1s step-end infinite",
                  }}
                />
              </div>
            </div>
          )}

          {/* Loading dots */}
          {loading && !streamingText && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{ display: "flex", gap: "5px", padding: "14px 18px" }}>
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
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
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
            }}>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !e.shiftKey && sendMessage()
              }
              placeholder="Ask about your CRS score, draws, or PR strategy..."
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                outline: "none",
                fontsize: "16px",
                color: "var(--color-text-primary)",
                padding: 0,
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "50%",
                border: "none",
                background:
                  input.trim() && !loading ? RED : "rgba(255,255,255,0.1)",
                color: "#ffffff",
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
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1); }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${RED}55; border-radius: 4px; }
        input::placeholder { color: var(--color-text-secondary); opacity: 0.6; }
      `}</style>
    </div>
  );
}
