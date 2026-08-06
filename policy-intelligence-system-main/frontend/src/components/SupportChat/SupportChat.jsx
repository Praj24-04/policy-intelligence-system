import { useState, useEffect, useRef } from "react";
import { MessageSquare, X, Send, Shield, RefreshCw } from "lucide-react";
import { fetchSupportMessages, sendSupportMessage } from "../../services/api";

const MAX_CHAR_LIMIT = 2000;

export default function SupportChat({ user }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [hasUnread, setHasUnread] = useState(false);
  const messagesEndRef = useRef(null);
  const lastOpenedTimeRef = useRef(Date.now());

  // Do not render if not logged in
  if (!user) return null;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadMessages = async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const data = await fetchSupportMessages();
      if (Array.isArray(data)) {
        setMessages(data);

        // Check if there are any admin replies received after last opened timestamp
        const newAdminReply = data.some(
          m => m.sender === "admin" && new Date(m.created_at).getTime() > lastOpenedTimeRef.current
        );
        if (newAdminReply && !isOpen) {
          setHasUnread(true);
        }
      }
    } catch (err) {
      if (!silent) {
        setError("Failed to load chat history. Please try again.");
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  // Initial load and periodic polling for new messages
  useEffect(() => {
    loadMessages();
    const interval = setInterval(() => {
      loadMessages(true);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isOpen) {
      setHasUnread(false);
      lastOpenedTimeRef.current = Date.now();
      scrollToBottom();
    }
  }, [isOpen, messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = inputMsg.strip ? inputMsg.strip() : inputMsg.trim();
    if (!trimmed || sending) return;

    if (trimmed.length > MAX_CHAR_LIMIT) {
      setError(`Message exceeds limit of ${MAX_CHAR_LIMIT} characters.`);
      return;
    }

    const tempId = `temp-${Date.now()}`;
    const optimisticMsg = {
      id: tempId,
      user_id: user.id,
      message: trimmed,
      sender: "client",
      status: "open",
      created_at: new Date().toISOString(),
      pending: true
    };

    // Optimistic UI update
    setMessages(prev => [...prev, optimisticMsg]);
    setInputMsg("");
    setSending(true);
    setError(null);
    scrollToBottom();

    try {
      const confirmedMsg = await sendSupportMessage(trimmed);
      setMessages(prev =>
        prev.map(m => (m.id === tempId ? { ...confirmedMsg, pending: false } : m))
      );
      scrollToBottom();
    } catch (err) {
      // Rollback on failure
      setMessages(prev => prev.filter(m => m.id !== tempId));
      setError(err.message || "Failed to send message. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ position: "fixed", bottom: "24px", right: "24px", zIndex: 9999 }}>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: "relative",
            width: "52px",
            height: "52px",
            borderRadius: "50%",
            background: "#09090B",
            border: "1.5px solid #5c9e2e",
            color: "#5c9e2e",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 4px 20px rgba(92, 158, 46, 0.35)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease"
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.06)"}
          onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
          title="Support Assistance"
        >
          <MessageSquare size={22} color="#5c9e2e" />
          {hasUnread && (
            <span style={{
              position: "absolute",
              top: "-2px",
              right: "-2px",
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              background: "#a3e635",
              border: "2px solid #09090B"
            }} />
          )}
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div style={{
          width: "360px",
          maxHeight: "520px",
          height: "80vh",
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: "12px",
          display: "flex",
          flexDirection: "column",
          boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
          overflow: "hidden"
        }}>
          {/* Header */}
          <div style={{
            padding: "12px 16px",
            background: "var(--bg-hover)",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div style={{
                width: "28px", height: "28px", borderRadius: "6px",
                background: "rgba(92, 158, 46, 0.15)",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <Shield size={16} color="#5c9e2e" />
              </div>
              <div>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-main)", fontFamily: "DM Sans" }}>
                  PolicyIQ Support
                </div>
                <div style={{ fontSize: "10px", color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                  Logged-in as {user.full_name || user.email}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "4px",
                borderRadius: "4px"
              }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Error Notice */}
          {error && (
            <div style={{
              padding: "8px 12px",
              background: "rgba(244, 63, 94, 0.1)",
              borderBottom: "1px solid rgba(244, 63, 94, 0.2)",
              color: "#f43f5e",
              fontSize: "11px",
              fontFamily: "DM Sans"
            }}>
              {error}
            </div>
          )}

          {/* Message Thread */}
          <div style={{
            flex: 1,
            padding: "14px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            background: "var(--bg-deep)"
          }}>
            {loading ? (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1, gap: 8, color: "var(--text-muted)", fontSize: 12 }}>
                <RefreshCw size={14} className="spin" /> Loading chat...
              </div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: "12px", marginTop: "40px", fontFamily: "DM Sans" }}>
                No messages yet. Send a query below to get help from our policy support team!
              </div>
            ) : (
              messages.map((m) => {
                const isClient = m.sender === "client";
                return (
                  <div
                    key={m.id}
                    style={{
                      alignSelf: isClient ? "flex-end" : "flex-start",
                      maxWidth: "82%",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: isClient ? "flex-end" : "flex-start"
                    }}
                  >
                    <span style={{ fontSize: "10px", color: "var(--text-dim)", marginBottom: "2px", fontFamily: "JetBrains Mono" }}>
                      {isClient ? "You" : "Support Team"} · {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <div style={{
                      padding: "8px 12px",
                      borderRadius: isClient ? "12px 12px 2px 12px" : "12px 12px 12px 2px",
                      background: isClient ? "#5c9e2e" : "var(--bg-card)",
                      color: isClient ? "#ffffff" : "var(--text-main)",
                      border: isClient ? "none" : "1px solid var(--border)",
                      fontSize: "12px",
                      lineHeight: "1.4",
                      fontFamily: "DM Sans",
                      wordBreak: "break-word",
                      opacity: m.pending ? 0.7 : 1
                    }}>
                      {/* 
                        SECURITY NOTICE: React's default text node rendering ensures plain text safety.
                        Message content is NEVER rendered as HTML or markdown (prevents stored XSS).
                      */}
                      {m.message}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form
            onSubmit={handleSend}
            style={{
              padding: "10px 12px",
              background: "var(--bg-card)",
              borderTop: "1px solid var(--border)",
              display: "flex",
              flexDirection: "column",
              gap: "6px"
            }}
          >
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <input
                type="text"
                placeholder="Ask support a question..."
                value={inputMsg}
                maxLength={MAX_CHAR_LIMIT}
                disabled={sending}
                onChange={(e) => setInputMsg(e.target.value)}
                style={{
                  flex: 1,
                  background: "var(--bg-hover)",
                  border: "1px solid var(--border)",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  fontSize: "12px",
                  color: "var(--text-main)",
                  fontFamily: "DM Sans",
                  outline: "none"
                }}
              />
              <button
                type="submit"
                disabled={sending || !inputMsg.trim()}
                style={{
                  background: "#5c9e2e",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  color: "#ffffff",
                  cursor: sending || !inputMsg.trim() ? "not-allowed" : "pointer",
                  opacity: sending || !inputMsg.trim() ? 0.5 : 1,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center"
                }}
              >
                <Send size={14} />
              </button>
            </div>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "10px",
              color: "var(--text-dim)",
              fontFamily: "JetBrains Mono"
            }}>
              <span>Max length: 2000 chars</span>
              <span>{inputMsg.length}/{MAX_CHAR_LIMIT}</span>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
