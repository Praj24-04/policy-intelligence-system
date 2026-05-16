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
            background: "var(--cyan)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 16px",
          }}>
            <Globe2 size={28} color="#000" />
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

          <button type="button" style={{
            width: "100%", padding: "10px",
            background: "var(--bg-base)", border: "1px solid var(--border)",
            borderRadius: 8, color: "var(--text-main)",
            fontFamily: "Syne", fontWeight: 600, fontSize: 13,
            cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            marginBottom: 20
          }}>
            <svg viewBox="0 0 24 24" width="16" height="16" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Sign in with Google
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }}></div>
            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>OR EMAIL</div>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }}></div>
          </div>

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
              background: loading ? "var(--bg-hover)" : "var(--cyan)",
              border: "none", borderRadius: 8,
              color: loading ? "var(--text-muted)" : "#000",
              fontFamily: "Syne", fontWeight: 700, fontSize: 14,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s",
            }}>
              {loading ? "Signing in..." : "Sign In with Email"}
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