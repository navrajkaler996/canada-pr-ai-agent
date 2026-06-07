import React, { useState } from "react";

// ChatMessage.js
// Renders a single chat message (user or assistant) with markdown support.

const RED = "#CC0000";

// Inline markdown renderer
function renderInline(text) {
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

// Block markdown renderer
function Markdown({ text }) {
  const lines = text.split("\n");
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i++;
      continue;
    }

    if (line.startsWith("### ")) {
      elements.push(
        <h3
          key={i}
          style={{
            fontSize: "15px",
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

    elements.push(
      <p key={i} style={{ margin: "4px 0", lineHeight: "1.65" }}>
        {renderInline(line)}
      </p>,
    );
    i++;
  }

  return <div style={{ fontSize: "15px" }}>{elements}</div>;
}

// Quick reply buttons
function QuickReplies({ options, onSelect }) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "8px",
        marginTop: "12px",
      }}>
      {options.map((opt) => (
        <button
          key={opt.value ?? opt.label}
          onClick={() => onSelect(opt)}
          style={{
            padding: "8px 14px",
            borderRadius: "20px",
            border: `1px solid ${RED}88`,
            background: "transparent",
            color: "var(--color-text-primary)",
            fontSize: "13px",
            cursor: "pointer",
            transition: "background 0.15s, border-color 0.15s",
            whiteSpace: "nowrap",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = `${RED}22`;
            e.currentTarget.style.borderColor = RED;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.borderColor = `${RED}88`;
          }}>
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// Score input fields (one per ability)
function ScoreInput({ abilities, hint, onSubmit }) {
  const [scores, setScores] = React.useState(
    Object.fromEntries(abilities.map((a) => [a, ""])),
  );
  const [error, setError] = React.useState(null);

  const handleSubmit = () => {
    for (const ability of abilities) {
      if (!scores[ability].trim()) {
        setError(`Please enter your ${ability} score.`);
        return;
      }
    }
    setError(null);
    onSubmit(scores);
  };

  return (
    <div
      style={{
        marginTop: "12px",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}>
      {abilities.map((ability) => (
        <div
          key={ability}
          style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              fontSize: "13px",
              color: "var(--color-text-secondary)",
              width: "72px",
              textTransform: "capitalize",
            }}>
            {ability}
          </span>
          <input
            type="text"
            value={scores[ability]}
            onChange={(e) =>
              setScores((prev) => ({ ...prev, [ability]: e.target.value }))
            }
            placeholder={hint ?? "score"}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            style={{
              width: "90px",
              padding: "6px 10px",
              borderRadius: "8px",
              border: `1px solid rgba(255,255,255,0.15)`,
              background: "rgba(255,255,255,0.05)",
              color: "var(--color-text-primary)",
              fontSize: "14px",
              outline: "none",
            }}
          />
        </div>
      ))}
      {error && (
        <p style={{ fontSize: "12px", color: RED, margin: "2px 0 0" }}>
          {error}
        </p>
      )}
      <button
        onClick={handleSubmit}
        style={{
          marginTop: "4px",
          alignSelf: "flex-start",
          padding: "8px 18px",
          borderRadius: "20px",
          border: "none",
          background: RED,
          color: "#fff",
          fontSize: "13px",
          cursor: "pointer",
        }}>
        Submit scores →
      </button>
    </div>
  );
}

// ChatMessage component
// Props:
//   msg          — { role, content, options, scoreInput, showQuickReplies }
//   isStreaming  — bool, shows blinking cursor
//   onOptionSelect(opt)      — called when quick reply button tapped
//   onScoreSubmit(scores)    — called when score input submitted
//   isLatest     — only the latest assistant message shows interactive elements

export default function ChatMessage({
  msg,
  isStreaming,
  onOptionSelect,
  onScoreSubmit,
  isLatest,
}) {
  const isUser = msg.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
      }}>
      <div style={{ maxWidth: "85%" }}>
        {/* Bubble */}
        <div
          style={{
            padding: "11px 15px",
            borderRadius: isUser ? "18px 18px 4px 18px" : "4px 18px 18px 18px",
            background: isUser
              ? "#363535"
              : "var(--color-background-secondary)",
            color: isUser ? "#ffffff" : "var(--color-text-primary)",
            fontSize: "15px",
            lineHeight: "1.65",
          }}>
          {isUser ? msg.content : <Markdown text={msg.content} />}

          {/* Streaming cursor */}
          {isStreaming && (
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
          )}
        </div>

        {/* Quick reply options — only on latest assistant message */}
        {!isUser && isLatest && msg.options && msg.options.length > 0 && (
          <QuickReplies options={msg.options} onSelect={onOptionSelect} />
        )}

        {/* Score input — only on latest assistant message */}
        {!isUser && isLatest && msg.scoreInput && (
          <ScoreInput
            abilities={msg.scoreInput.abilities}
            hint={msg.scoreInput.hint}
            onSubmit={onScoreSubmit}
          />
        )}
      </div>
    </div>
  );
}
