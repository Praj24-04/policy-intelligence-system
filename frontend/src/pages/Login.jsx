import { useState } from "react";
import { Globe2, Lock, User, Eye, EyeOff } from "lucide-react";

export default function Login({ onLogin }) {
  const [username,  setUsername]  = useState("");
  const [password,  setPassword]  = useState("");
  const [showPass,  setShowPass]  = useState(false);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const form = new FormData();
    form.append("username", username);
    form.append("password", password);

    try {
      const res = await fetch("http://localhost:8000/api/auth/token", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");

      // Store token
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify({
        username: data.username,
        role: data.role,
        full_name: data.full_name
      }));

      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "var(--bg-deep)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}>
      <div style={{ width: 400 }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 14,
            background: "linear-gradient(135deg, var(--cyan-dim), #0e7490)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 16px",
          }}>
            <Globe2 size={28} color="#fff" />
          </div>
          <h1 style={{
            fontFamily: "Syne", fontSize: 26, fontWeight: 800,
            color: "var(--text-main)", marginBottom: 6
          }}>
            PolicyIQ
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: 13 }}>
            Global Policy Intelligence System
          </p>
        </div>

        {/* Card */}
        <div className="card" style={{ padding: "32px 36px" }}>
          <div style={{
            fontFamily: "Syne", fontSize: 17, fontWeight: 700,
            color: "var(--text-main)", marginBottom: 6
          }}>
            Sign In
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: 12, marginBottom: 24 }}>
            Enter your credentials to access the platform
          </p>

          <form onSubmit={handleLogin}>
            {/* Username */}
            <div style={{ marginBottom: 16 }}>
              <label style={{
                fontSize: 11, color: "var(--text-muted)",
                fontFamily: "JetBrains Mono", letterSpacing: "0.08em",
                display: "block", marginBottom: 6
              }}>
                USERNAME
              </label>
              <div style={{
                display: "flex", alignItems: "center", gap: 10,
                background: "var(--bg-hover)", border: "1px solid var(--border)",
                borderRadius: 8, padding: "10px 14px",
              }}>
                <User size={14} color="var(--text-muted)" />
                <input
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="admin or analyst"
                  required
                  style={{
                    background: "none", border: "none", outline: "none",
                    color: "var(--text-main)", fontSize: 13, width: "100%"
                  }}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ marginBottom: 24 }}>
              <label style={{
                fontSize: 11, color: "var(--text-muted)",
                fontFamily: "JetBrains Mono", letterSpacing: "0.08em",
                display: "block", marginBottom: 6
              }}>
                PASSWORD
              </label>
              <div style={{
                display: "flex", alignItems: "center", gap: 10,
                background: "var(--bg-hover)", border: "1px solid var(--border)",
                borderRadius: 8, padding: "10px 14px",
              }}>
                <Lock size={14} color="var(--text-muted)" />
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  style={{
                    background: "none", border: "none", outline: "none",
                    color: "var(--text-main)", fontSize: 13, width: "100%"
                  }}
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}>
                  {showPass
                    ? <EyeOff size={14} color="var(--text-muted)" />
                    : <Eye size={14} color="var(--text-muted)" />
                  }
                </button>
              </div>
            </div>

            {error && (
              <div style={{
                padding: "10px 14px", borderRadius: 8, marginBottom: 16,
                background: "rgba(244,63,94,0.08)",
                border: "1px solid rgba(244,63,94,0.2)",
                color: "#f43f5e", fontSize: 12
              }}>
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} style={{
              width: "100%", padding: "12px",
              background: loading ? "var(--bg-hover)" : "linear-gradient(135deg, var(--cyan-dim), #0e7490)",
              border: "none", borderRadius: 8,
              color: loading ? "var(--text-muted)" : "#fff",
              fontFamily: "Syne", fontWeight: 700, fontSize: 14,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
            }}>
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Demo credentials */}
          <div style={{
            marginTop: 24, padding: "12px 14px", borderRadius: 8,
            background: "rgba(34,211,238,0.04)",
            border: "1px solid rgba(34,211,238,0.12)",
          }}>
            <div style={{
              fontSize: 10, color: "var(--cyan)",
              fontFamily: "JetBrains Mono", marginBottom: 8
            }}>
              DEMO CREDENTIALS
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.8 }}>
              <span style={{ color: "var(--text-main)" }}>Admin:</span> admin / policy2024<br />
              <span style={{ color: "var(--text-main)" }}>Analyst:</span> analyst / analyst2024
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}