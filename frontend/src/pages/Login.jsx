import { useState } from "react";
import { Globe2, Lock, User, Eye, EyeOff, Mail, ArrowLeft, CheckCircle } from "lucide-react";
import { loginUser, registerUser, forgotPassword } from "../services/api";

// ── Reusable input wrapper ─────────────────────────────────────────────────
function InputField({ icon: Icon, type = "text", value, onChange, placeholder, required, rightSlot }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      background: "var(--bg-hover)", border: "1px solid var(--border)",
      borderRadius: 8, padding: "10px 14px",
    }}>
      <Icon size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
      <input
        type={type} value={value} onChange={onChange}
        placeholder={placeholder} required={required}
        style={{
          background: "none", border: "none", outline: "none",
          color: "var(--text-main)", fontSize: 13, width: "100%"
        }}
      />
      {rightSlot}
    </div>
  );
}

// ── Error / Success banners ────────────────────────────────────────────────
function ErrorBanner({ msg }) {
  if (!msg) return null;
  return (
    <div style={{
      padding: "10px 14px", borderRadius: 8, marginBottom: 16,
      background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.2)",
      color: "#f43f5e", fontSize: 12
    }}>{msg}</div>
  );
}

function SuccessBanner({ msg }) {
  if (!msg) return null;
  return (
    <div style={{
      padding: "10px 14px", borderRadius: 8, marginBottom: 16,
      background: "rgba(163,230,53,0.08)", border: "1px solid rgba(163,230,53,0.25)",
      color: "#4d7c0f", fontSize: 12, display: "flex", alignItems: "center", gap: 8
    }}>
      <CheckCircle size={14} /> {msg}
    </div>
  );
}

// ── Submit button ──────────────────────────────────────────────────────────
function SubmitBtn({ loading, label }) {
  return (
    <button type="submit" disabled={loading} style={{
      width: "100%", padding: "12px",
      background: loading ? "var(--bg-hover)" : "var(--cyan)",
      border: "none", borderRadius: 8,
      color: loading ? "var(--text-muted)" : "#000",
      fontFamily: "Inter", fontWeight: 700, fontSize: 14,
      cursor: loading ? "not-allowed" : "pointer",
      transition: "all 0.2s",
    }}>
      {loading ? "Please wait..." : label}
    </button>
  );
}

// ── Label ──────────────────────────────────────────────────────────────────
function Label({ text }) {
  return (
    <label style={{
      fontSize: 11, color: "var(--text-muted)",
      fontFamily: "JetBrains Mono", letterSpacing: "0.08em",
      display: "block", marginBottom: 6
    }}>{text}</label>
  );
}

// ── Login Form ─────────────────────────────────────────────────────────────
function LoginForm({ onLogin, onForgot, onSwitch }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      const data = await loginUser(email, password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ marginBottom: 16 }}>
        <Label text="EMAIL ADDRESS" />
        <InputField icon={Mail} type="email" value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com" required />
      </div>
      <div style={{ marginBottom: 8 }}>
        <Label text="PASSWORD" />
        <InputField icon={Lock} type={showPass ? "text" : "password"}
          value={password} onChange={e => setPassword(e.target.value)}
          placeholder="••••••••" required
          rightSlot={
            <button type="button" onClick={() => setShowPass(!showPass)}
              style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}>
              {showPass ? <EyeOff size={14} color="var(--text-muted)" />
                        : <Eye size={14} color="var(--text-muted)" />}
            </button>
          }
        />
      </div>
      <div style={{ textAlign: "right", marginBottom: 24 }}>
        <button type="button" onClick={onForgot} style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--text-muted)", fontSize: 12, padding: 0
        }}>Forgot password?</button>
      </div>
      <ErrorBanner msg={error} />
      <SubmitBtn loading={loading} label="Sign In →" />
      <p style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 12, marginTop: 20 }}>
        Don't have an account?{" "}
        <button type="button" onClick={onSwitch} style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--cyan)", fontWeight: 700, fontSize: 12, padding: 0
        }}>Create one</button>
      </p>
    </form>
  );
}

// ── Register Form ──────────────────────────────────────────────────────────
function RegisterForm({ onLogin, onSwitch }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail]     = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (password.length < 6) { setError("Password must be at least 6 characters."); return; }
    setLoading(true);
    try {
      const data = await registerUser(email, fullName, password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ marginBottom: 16 }}>
        <Label text="FULL NAME" />
        <InputField icon={User} value={fullName}
          onChange={e => setFullName(e.target.value)}
          placeholder="Jane Smith" required />
      </div>
      <div style={{ marginBottom: 16 }}>
        <Label text="EMAIL ADDRESS" />
        <InputField icon={Mail} type="email" value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com" required />
      </div>
      <div style={{ marginBottom: 24 }}>
        <Label text="PASSWORD" />
        <InputField icon={Lock} type={showPass ? "text" : "password"}
          value={password} onChange={e => setPassword(e.target.value)}
          placeholder="Min. 6 characters" required
          rightSlot={
            <button type="button" onClick={() => setShowPass(!showPass)}
              style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}>
              {showPass ? <EyeOff size={14} color="var(--text-muted)" />
                        : <Eye size={14} color="var(--text-muted)" />}
            </button>
          }
        />
      </div>
      <ErrorBanner msg={error} />
      <SubmitBtn loading={loading} label="Create Account →" />
      <p style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 12, marginTop: 20 }}>
        Already have an account?{" "}
        <button type="button" onClick={onSwitch} style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--cyan)", fontWeight: 700, fontSize: 12, padding: 0
        }}>Sign in</button>
      </p>
    </form>
  );
}

// ── Forgot Password Form ───────────────────────────────────────────────────
function ForgotForm({ onBack }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [sent, setSent]       = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError(null);
    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (sent) return (
    <div style={{ textAlign: "center", padding: "16px 0" }}>
      <div style={{
        width: 56, height: 56, borderRadius: "50%",
        background: "rgba(163,230,53,0.15)",
        display: "flex", alignItems: "center", justifyContent: "center",
        margin: "0 auto 16px"
      }}>
        <CheckCircle size={28} color="#65a30d" />
      </div>
      <p style={{ color: "var(--text-main)", fontWeight: 700, fontSize: 15, marginBottom: 8 }}>
        Check your email
      </p>
      <p style={{ color: "var(--text-muted)", fontSize: 13, lineHeight: 1.6, marginBottom: 24 }}>
        If <strong>{email}</strong> is registered, we've sent a password reset link. Check your inbox.
      </p>
      <button type="button" onClick={onBack} style={{
        background: "none", border: "none", cursor: "pointer",
        color: "var(--cyan)", fontWeight: 700, fontSize: 13,
        display: "flex", alignItems: "center", gap: 6, margin: "0 auto"
      }}>
        <ArrowLeft size={14} /> Back to login
      </button>
    </div>
  );

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ color: "var(--text-muted)", fontSize: 13, lineHeight: 1.6, marginBottom: 24 }}>
        Enter your email address and we'll send you a link to reset your password.
      </p>
      <div style={{ marginBottom: 24 }}>
        <Label text="EMAIL ADDRESS" />
        <InputField icon={Mail} type="email" value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com" required />
      </div>
      <ErrorBanner msg={error} />
      <SubmitBtn loading={loading} label="Send Reset Link →" />
      <div style={{ textAlign: "center", marginTop: 16 }}>
        <button type="button" onClick={onBack} style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--text-muted)", fontSize: 12,
          display: "inline-flex", alignItems: "center", gap: 4
        }}>
          <ArrowLeft size={12} /> Back to login
        </button>
      </div>
    </form>
  );
}

// ── Main Export ────────────────────────────────────────────────────────────
export default function Login({ onLogin }) {
  const [view, setView] = useState("login"); // "login" | "register" | "forgot"

  const titles = {
    login:    { heading: "Welcome back",      sub: "Sign in to your PolicyIQ account" },
    register: { heading: "Create an account", sub: "Start tracking global regulations today" },
    forgot:   { heading: "Forgot password",   sub: "We'll send you a reset link" },
  };
  const { heading, sub } = titles[view];

  return (
    <div style={{
      minHeight: "100vh", background: "var(--bg-deep)",
      display: "flex", alignItems: "center", justifyContent: "center",
      backgroundImage: "radial-gradient(rgba(163,230,53,0.04) 1px, transparent 1px)",
      backgroundSize: "24px 24px",
    }}>
      <div style={{ width: 420 }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            width: 52, height: 52, borderRadius: 14,
            background: "var(--cyan)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 14px",
          }}>
            <Globe2 size={26} color="#000" />
          </div>
          <div style={{ fontWeight: 800, fontSize: 22, color: "var(--text-main)", letterSpacing: "-0.5px" }}>
            PolicyIQ
          </div>
          <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 4 }}>
            Global Policy Intelligence System
          </div>
        </div>

        {/* Card */}
        <div className="card" style={{ padding: "32px 36px" }}>
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontWeight: 700, fontSize: 18, color: "var(--text-main)", marginBottom: 6 }}>
              {heading}
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: 12 }}>{sub}</p>
          </div>

          {view === "login"    && <LoginForm    onLogin={onLogin} onForgot={() => setView("forgot")} onSwitch={() => setView("register")} />}
          {view === "register" && <RegisterForm onLogin={onLogin} onSwitch={() => setView("login")} />}
          {view === "forgot"   && <ForgotForm   onBack={() => setView("login")} />}
        </div>

        <p style={{ textAlign: "center", color: "var(--text-dim)", fontSize: 11, marginTop: 20 }}>
          © 2026 PolicyIQ Inc. · Your data is encrypted and secure.
        </p>
      </div>
    </div>
  );
}