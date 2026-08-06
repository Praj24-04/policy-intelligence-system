import { useState, useEffect } from "react";
import {
  Shield, Users, Activity, Server, Search, ChevronLeft, ChevronRight,
  Trash2, ShieldCheck, ShieldOff, Ban, UserCheck, Clock, Upload,
  GitCompare, FileText, LogIn, KeyRound, Globe2, AlertTriangle, Database,
  Cpu, BarChart3, RefreshCw, UserPlus, Plus, Play, ExternalLink, CheckCircle,
  MessageSquare, Send, MessageCircle
} from "lucide-react";
import {
  fetchAdminStats, fetchAdminUsers, fetchAdminSystem,
  fetchActivityLogs, updateUserRole, deleteUser, blockUser, createAdminUser,
  fetchTrustedSources, createTrustedSource, updateTrustedSourceStatus,
  deleteTrustedSource, testTrustedSource,
  fetchAdminSectors, createAdminSector, updateAdminSector, deleteAdminSector,
  fetchAdminSupportMessages, sendAdminReply, updateUserSupportStatus
} from "../services/api";


const ACTION_COLORS = {
  login: "#3b82f6", register: "#10b981", google_login: "#f59e0b",
  upload: "#0284c7", compare: "#ec4899", generate: "#06b6d4",
  password_change: "#f97316", role_change: "#10b981", user_delete: "#dc2626",
  user_block: "#b91c1c", user_unblock: "#16a34a", policy_delete: "#991b1b",
};
const ACTION_ICONS = {
  login: LogIn, register: UserCheck, google_login: Globe2,
  upload: Upload, compare: GitCompare, generate: FileText,
  password_change: KeyRound, role_change: ShieldCheck,
  user_delete: Trash2, user_block: Ban, user_unblock: UserCheck,
  policy_delete: Trash2,
};

function timeAgo(dateStr) {
  if (!dateStr) return "Never";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return days === 1 ? "Yesterday" : `${days}d ago`;
}

// ── Stat Card ──────────────────────────────────────────────────────────────
function AdminStat({ icon: Icon, label, value, accent = "var(--cyan)" }) {
  return (
    <div className="admin-stat-card">
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: `${accent}15`, display: "flex",
          alignItems: "center", justifyContent: "center"
        }}>
          <Icon size={16} color={accent} />
        </div>
        <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", letterSpacing: "0.05em", textTransform: "uppercase" }}>
          {label}
        </span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color: "var(--text-main)", fontFamily: "Inter" }}>
        {value ?? "—"}
      </div>
    </div>
  );
}

// ── Tab Button ─────────────────────────────────────────────────────────────
function TabBtn({ icon: Icon, label, active, onClick }) {
  return (
    <button onClick={onClick} className={`admin-tab-btn${active ? " active" : ""}`}>
      <Icon size={15} />
      <span>{label}</span>
    </button>
  );
}

// ── Overview Tab ───────────────────────────────────────────────────────────
function OverviewTab({ stats }) {
  if (!stats) return <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>Loading...</div>;
  return (
    <div className="fade-up">
      <div className="admin-stats-grid">
        <AdminStat icon={Users} label="Total Users" value={stats.total_users} />
        <AdminStat icon={ShieldCheck} label="Admins" value={stats.total_admins} accent="#10b981" />
        <AdminStat icon={Activity} label="Active 24h" value={stats.active_24h} accent="#059669" />
        <AdminStat icon={Clock} label="Active 7d" value={stats.active_7d} accent="#3b82f6" />
        <AdminStat icon={Database} label="Policies" value={stats.total_policies} accent="#f59e0b" />
        <AdminStat icon={Upload} label="Uploads" value={stats.total_uploads} accent="#0284c7" />
        <AdminStat icon={GitCompare} label="Compares" value={stats.total_compares} accent="#ec4899" />
        <AdminStat icon={FileText} label="Generates" value={stats.total_generates} accent="#06b6d4" />
      </div>

      {/* Mini Charts */}
      <div className="two-column-grid" style={{ marginTop: 20 }}>
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", marginBottom: 12, fontFamily: "JetBrains Mono" }}>
            USER GROWTH (14 DAYS)
          </div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 60 }}>
            {(stats.user_growth || []).map((d, i) => {
              const max = Math.max(...(stats.user_growth || []).map(x => x.count), 1);
              return (
                <div key={i} title={`${d.day}: ${d.count}`} style={{
                  flex: 1, background: "var(--cyan)", borderRadius: 2, opacity: 0.8,
                  height: `${Math.max(4, (d.count / max) * 100)}%`, transition: "height 0.3s",
                }} />
              );
            })}
            {(!stats.user_growth || stats.user_growth.length === 0) && (
              <span style={{ fontSize: 11, color: "var(--text-dim)" }}>No data yet</span>
            )}
          </div>
        </div>
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", marginBottom: 12, fontFamily: "JetBrains Mono" }}>
            ACTIVITY TREND (14 DAYS)
          </div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 60 }}>
            {(stats.activity_trend || []).map((d, i) => {
              const max = Math.max(...(stats.activity_trend || []).map(x => x.count), 1);
              return (
                <div key={i} title={`${d.day}: ${d.count}`} style={{
                  flex: 1, background: "#3b82f6", borderRadius: 2, opacity: 0.8,
                  height: `${Math.max(4, (d.count / max) * 100)}%`, transition: "height 0.3s",
                }} />
              );
            })}
            {(!stats.activity_trend || stats.activity_trend.length === 0) && (
              <span style={{ fontSize: 11, color: "var(--text-dim)" }}>No data yet</span>
            )}
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 20, marginTop: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", marginBottom: 4, fontFamily: "JetBrains Mono" }}>
          NEW USERS (LAST 7 DAYS)
        </div>
        <div style={{ fontSize: 24, fontWeight: 800, color: "var(--cyan)" }}>{stats.new_users_7d}</div>
        <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>
          {stats.total_feedback} feedback entries collected
        </div>
      </div>
    </div>
  );
}

// ── Users Tab ──────────────────────────────────────────────────────────────
function UsersTab() {
  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [page, setPage] = useState(1);
  const [actionLoading, setActionLoading] = useState(null);

  // Allocate Admin Form state
  const [showAddAdmin, setShowAddAdmin] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newName, setNewName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [addError, setAddError] = useState("");
  const [addSuccess, setAddSuccess] = useState("");

  const load = () => {
    fetchAdminUsers({ search, role: roleFilter, page, limit: 15 }).then(d => d && setData(d));
  };
  useEffect(load, [search, roleFilter, page]);

  const handleCreateAdminSubmit = async (e) => {
    e.preventDefault();
    setAddError("");
    setAddSuccess("");
    if (!newEmail || !newPassword) {
      setAddError("Email and Password are required");
      return;
    }
    if (newPassword.length < 6) {
      setAddError("Password must be at least 6 characters");
      return;
    }
    setSubmitting(true);
    try {
      const res = await createAdminUser({
        email: newEmail,
        password: newPassword,
        full_name: newName || "Admin User"
      });
      setAddSuccess(res.message);
      setNewEmail("");
      setNewPassword("");
      setNewName("");
      load();
      setTimeout(() => {
        setShowAddAdmin(false);
        setAddSuccess("");
      }, 2500);
    } catch (err) {
      setAddError(err.message || "Failed to create admin");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRoleChange = async (id, newRole) => {
    if (!window.confirm(`Change this user's role to "${newRole}"?`)) return;
    setActionLoading(id);
    try { await updateUserRole(id, newRole); load(); }
    catch (e) { alert(e.message); }
    finally { setActionLoading(null); }
  };

  const handleBlock = async (id) => {
    setActionLoading(id);
    try { await blockUser(id); load(); }
    catch (e) { alert(e.message); }
    finally { setActionLoading(null); }
  };

  const handleDelete = async (id, email) => {
    if (!window.confirm(`Permanently delete user ${email}? This cannot be undone.`)) return;
    setActionLoading(id);
    try { await deleteUser(id); load(); }
    catch (e) { alert(e.message); }
    finally { setActionLoading(null); }
  };

  const roleBadge = (role) => {
    const colors = { admin: "#059669", user: "#0284c7", blocked: "#ef4444" };
    const bgColors = { admin: "rgba(16, 185, 129, 0.15)", user: "rgba(2, 132, 199, 0.12)", blocked: "rgba(239, 68, 68, 0.12)" };
    return (
      <span className="admin-badge" style={{ background: bgColors[role] || "rgba(107, 114, 128, 0.12)", color: colors[role] || "#6b7280", border: `1px solid ${colors[role] || "#6b7280"}40` }}>
        {role}
      </span>
    );
  };

  return (
    <div className="fade-up">
      <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ flex: 1, minWidth: 200, display: "flex", alignItems: "center", gap: 8, background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 12px" }}>
          <Search size={14} color="var(--text-muted)" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by name or email..." style={{ background: "none", border: "none", outline: "none", color: "var(--text-main)", fontSize: 13, width: "100%" }} />
        </div>
        {["", "user", "admin", "blocked"].map(r => (
          <button key={r} onClick={() => { setRoleFilter(r); setPage(1); }}
            className={`admin-filter-pill${roleFilter === r ? " active" : ""}`}>
            {r || "All"}
          </button>
        ))}

        <button
          onClick={() => { setShowAddAdmin(!showAddAdmin); setAddError(""); setAddSuccess(""); }}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "8px 14px",
            borderRadius: 8,
            background: showAddAdmin ? "var(--bg-hover)" : "var(--text-main)",
            color: showAddAdmin ? "var(--text-main)" : "var(--bg-card)",
            border: showAddAdmin ? "1px solid var(--border)" : "none",
            fontSize: 12,
            fontFamily: "DM Sans",
            fontWeight: 600,
            cursor: "pointer",
            transition: "all 0.15s ease",
            whiteSpace: "nowrap"
          }}
        >
          <UserPlus size={14} />
          {showAddAdmin ? "Cancel" : "Allocate Admin"}
        </button>
      </div>

      {/* Allocate Admin Form */}
      {showAddAdmin && (
        <div className="card fade-up" style={{ padding: 20, marginBottom: 20, border: "1px solid var(--border-lit)" }}>
          <div className="flex-toolbar" style={{ justifyContent: "space-between", marginBottom: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <ShieldCheck size={18} color="#5c9e2e" />
              <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
                Allocate New Admin Account
              </span>
            </div>
            <span style={{ fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
              Grants full administrative oversight & control privileges
            </span>
          </div>

          {addError && (
            <div style={{ padding: "8px 12px", borderRadius: 6, background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", fontSize: 12, marginBottom: 12 }}>
              {addError}
            </div>
          )}
          {addSuccess && (
            <div style={{ padding: "8px 12px", borderRadius: 6, background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", color: "#10b981", fontSize: 12, marginBottom: 12 }}>
              {addSuccess}
            </div>
          )}

          <form onSubmit={handleCreateAdminSubmit} className="four-column-form-grid">
            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                EMAIL ADDRESS *
              </label>
              <input
                type="email"
                required
                value={newEmail}
                onChange={e => setNewEmail(e.target.value)}
                placeholder="newadmin@policyiq.com"
                style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                FULL NAME
              </label>
              <input
                type="text"
                value={newName}
                onChange={e => setNewName(e.target.value)}
                placeholder="e.g. Alex Rivera"
                style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                SET PASSWORD *
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="Min 6 characters"
                style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: "9px 20px",
                borderRadius: 6,
                background: "#5c9e2e",
                color: "#ffffff",
                border: "none",
                fontSize: 13,
                fontFamily: "DM Sans",
                fontWeight: 700,
                cursor: submitting ? "not-allowed" : "pointer",
                whiteSpace: "nowrap"
              }}
            >
              {submitting ? "Allocating..." : "Create Admin"}
            </button>
          </form>
        </div>
      )}

      <div className="card" style={{ overflow: "hidden" }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>User</th><th>Email</th><th>Role</th><th>Joined</th><th>Last Active</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.users?.map(u => (
              <tr key={u.id}>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 28, height: 28, borderRadius: 6, background: "#5c6bc0", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 12 }}>
                      {u.full_name?.charAt(0)?.toUpperCase() || "?"}
                    </div>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{u.full_name}</span>
                  </div>
                </td>
                <td style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>{u.email}</td>
                <td>{roleBadge(u.role)}</td>
                <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                <td style={{ fontSize: 12, color: "var(--text-muted)" }}>{timeAgo(u.last_active)}</td>
                <td>
                  <div style={{ display: "flex", gap: 4 }}>
                    {u.role === "user" && (
                      <button className="admin-action-btn" title="Promote to Admin" disabled={actionLoading === u.id}
                        onClick={() => handleRoleChange(u.id, "admin")}><ShieldCheck size={13} /></button>
                    )}
                    {u.role === "admin" && (
                      <button className="admin-action-btn" title="Demote to User" disabled={actionLoading === u.id}
                        onClick={() => handleRoleChange(u.id, "user")}><ShieldOff size={13} /></button>
                    )}
                    <button className="admin-action-btn" title={u.role === "blocked" ? "Unblock" : "Block"} disabled={actionLoading === u.id}
                      onClick={() => handleBlock(u.id)} style={{ color: u.role === "blocked" ? "#16a34a" : "#f59e0b" }}>
                      <Ban size={13} />
                    </button>
                    <button className="admin-action-btn danger" title="Delete User" disabled={actionLoading === u.id}
                      onClick={() => handleDelete(u.id, u.email)}><Trash2 size={13} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {(!data?.users || data.users.length === 0) && (
              <tr><td colSpan={6} style={{ textAlign: "center", padding: 32, color: "var(--text-dim)" }}>No users found</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.pages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, marginTop: 16 }}>
          <button className="admin-action-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}><ChevronLeft size={16} /></button>
          <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
            Page {page} of {data.pages} · {data.total} users
          </span>
          <button className="admin-action-btn" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}><ChevronRight size={16} /></button>
        </div>
      )}
    </div>
  );
}

// ── Activity Tab ───────────────────────────────────────────────────────────
function ActivityTab() {
  const [data, setData] = useState(null);
  const [actionFilter, setActionFilter] = useState("");
  const [emailFilter, setEmailFilter] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetchActivityLogs({ action: actionFilter, user_email: emailFilter, page, limit: 25 }).then(d => d && setData(d));
  }, [actionFilter, emailFilter, page]);

  return (
    <div className="fade-up">
      <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 180, display: "flex", alignItems: "center", gap: 8, background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 12px" }}>
          <Search size={14} color="var(--text-muted)" />
          <input value={emailFilter} onChange={e => { setEmailFilter(e.target.value); setPage(1); }}
            placeholder="Filter by email..." style={{ background: "none", border: "none", outline: "none", color: "var(--text-main)", fontSize: 13, width: "100%" }} />
        </div>
        <select value={actionFilter} onChange={e => { setActionFilter(e.target.value); setPage(1); }}
          className="select-custom" style={{ minWidth: 140 }}>
          <option value="">All Actions</option>
          {(data?.action_types || []).map(a => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {data?.logs?.map((log, i) => {
          const Icon = ACTION_ICONS[log.action] || Activity;
          const color = ACTION_COLORS[log.action] || "#6b7280";
          return (
            <div key={log.id} className="admin-activity-item" style={{ animationDelay: `${i * 0.03}s` }}>
              <div style={{ width: 30, height: 30, borderRadius: 8, background: `${color}15`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon size={14} color={color} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <span style={{ fontWeight: 600, fontSize: 13, color: "var(--text-main)" }}>{log.user_email}</span>
                  <span className="admin-badge" style={{ background: `${color}15`, color, border: `1px solid ${color}30`, fontSize: 10 }}>
                    {log.action}
                  </span>
                </div>
                {log.detail && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{log.detail}</div>}
              </div>
              <div style={{ textAlign: "right", flexShrink: 0 }}>
                <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono" }}>{timeAgo(log.created_at)}</div>
                {log.ip_address && <div style={{ fontSize: 10, color: "var(--text-dim)" }}>{log.ip_address}</div>}
              </div>
            </div>
          );
        })}
        {(!data?.logs || data.logs.length === 0) && (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text-dim)" }}>No activity logs yet</div>
        )}
      </div>

      {data && data.pages > 1 && (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, marginTop: 16 }}>
          <button className="admin-action-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}><ChevronLeft size={16} /></button>
          <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>Page {page} of {data.pages}</span>
          <button className="admin-action-btn" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}><ChevronRight size={16} /></button>
        </div>
      )}
    </div>
  );
}

// ── System Tab ─────────────────────────────────────────────────────────────
function SystemTab() {
  const [sys, setSys] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = () => {
    setLoading(true);
    fetchAdminSystem().then(d => { if (d) setSys(d); setLoading(false); });
  };
  useEffect(load, []);

  const statusDot = (ok) => (
    <div style={{ width: 8, height: 8, borderRadius: "50%", background: ok ? "#10b981" : "#ef4444", boxShadow: `0 0 8px ${ok ? "#10b981" : "#ef4444"}` }} />
  );

  return (
    <div className="fade-up">
      <div className="flex-toolbar" style={{ justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#5c9e2e" }} />
          <span style={{ fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            SYSTEM HEALTH & RUNTIME METRICS
          </span>
        </div>
        <button 
          onClick={load} 
          disabled={loading}
          style={{ 
            display: "inline-flex", 
            alignItems: "center", 
            gap: 6, 
            padding: "8px 16px", 
            borderRadius: 6,
            background: "var(--text-main)",
            color: "var(--bg-card)",
            border: "none",
            fontSize: 12,
            fontFamily: "DM Sans",
            fontWeight: 600,
            cursor: loading ? "not-allowed" : "pointer",
            transition: "all 0.15s ease",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)"
          }}
        >
          <RefreshCw size={13} className={loading ? "spin-icon" : ""} /> 
          {loading ? "Refreshing..." : "Refresh Diagnostics"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 20 }}>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            {statusDot(sys?.database === "connected")}
            <span style={{ fontSize: 12, fontWeight: 700, fontFamily: "JetBrains Mono", color: "var(--text-main)" }}>DATABASE</span>
          </div>
          <div style={{ fontSize: 13, color: sys?.database === "connected" ? "#10b981" : "#ef4444" }}>
            {sys?.database || "Checking..."}
          </div>
        </div>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            {statusDot(sys?.ml_status?.fitted)}
            <span style={{ fontSize: 12, fontWeight: 700, fontFamily: "JetBrains Mono", color: "var(--text-main)" }}>ML ENGINE</span>
          </div>
          <div style={{ fontSize: 13, color: sys?.ml_status?.fitted ? "#10b981" : "#f59e0b" }}>
            {sys?.ml_status?.fitted ? "Fitted & Active" : "Not fitted"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 2 }}>
            {sys?.ml_status?.countries || 0} country embeddings
          </div>
        </div>
      </div>

      <div className="two-column-grid">
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", marginBottom: 12, fontFamily: "JetBrains Mono" }}>
            POLICIES BY SECTOR
          </div>
          {sys?.policy_by_sector?.map((s, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontSize: 13, color: "var(--text-main)" }}>{s.sector}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: "var(--cyan)", fontFamily: "JetBrains Mono" }}>{s.count}</span>
            </div>
          ))}
          {(!sys?.policy_by_sector || sys.policy_by_sector.length === 0) && (
            <div style={{ fontSize: 12, color: "var(--text-dim)" }}>No data</div>
          )}
        </div>
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-main)", marginBottom: 12, fontFamily: "JetBrains Mono" }}>
            POLICIES BY REGION
          </div>
          {sys?.policy_by_region?.map((r, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontSize: 13, color: "var(--text-main)" }}>{r.region}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: "#3b82f6", fontFamily: "JetBrains Mono" }}>{r.count}</span>
            </div>
          ))}
          {(!sys?.policy_by_region || sys.policy_by_region.length === 0) && (
            <div style={{ fontSize: 12, color: "var(--text-dim)" }}>No data</div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Sectors Registry & Classification Tab ────────────────────────────────────
function SectorsTab() {
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingSector, setEditingSector] = useState(null);

  // Form states
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [color, setColor] = useState("#64748b");
  const [keywords, setKeywords] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const loadSectors = () => {
    setLoading(true);
    fetchAdminSectors()
      .then(data => {
        if (data) setSectors(data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadSectors();
  }, []);

  const handleCreateSector = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    if (!name.trim()) {
      setErrorMsg("Sector name is required");
      return;
    }
    setSubmitting(true);
    try {
      const res = await createAdminSector({
        name: name.trim(),
        description,
        color,
        keywords
      });
      setSuccessMsg(res.message);
      setName("");
      setDescription("");
      setColor("#64748b");
      setKeywords("");
      loadSectors();
      setTimeout(() => {
        setShowAddModal(false);
        setSuccessMsg("");
      }, 2000);
    } catch (err) {
      setErrorMsg(err.message || "Failed to create sector");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateSectorSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setSubmitting(true);
    try {
      const res = await updateAdminSector(editingSector.id, {
        name: editingSector.name.trim(),
        description: editingSector.description,
        color: editingSector.color,
        keywords: editingSector.keywords,
        status: editingSector.status
      });
      setSuccessMsg(res.message);
      loadSectors();
      setTimeout(() => {
        setEditingSector(null);
        setSuccessMsg("");
      }, 2000);
    } catch (err) {
      setErrorMsg(err.message || "Failed to update sector");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteSector = async (id, sectorName) => {
    if (!window.confirm(`Delete custom sector "${sectorName}"? Policies currently matching this sector will fall back to default classification.`)) return;
    try {
      await deleteAdminSector(id);
      loadSectors();
    } catch (err) {
      alert("Failed to delete sector: " + err.message);
    }
  };

  return (
    <div className="fade-up">
      <div className="card" style={{ padding: "18px 24px", marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Database size={18} color="#5c9e2e" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
              Sectors Registry & Classification Rules
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 12, color: "var(--text-muted)", fontFamily: "DM Sans" }}>
            Add custom policy domains and define keywords for automated policy ingestion classification.
          </p>
        </div>

        <button
          onClick={() => { setShowAddModal(!showAddModal); setEditingSector(null); setErrorMsg(""); setSuccessMsg(""); }}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "9px 16px",
            borderRadius: 8,
            background: showAddModal ? "var(--bg-hover)" : "#5c9e2e",
            color: showAddModal ? "var(--text-main)" : "#ffffff",
            border: showAddModal ? "1px solid var(--border)" : "none",
            fontSize: 13,
            fontFamily: "DM Sans",
            fontWeight: 700,
            cursor: "pointer",
            transition: "all 0.15s ease"
          }}
        >
          {showAddModal ? <RefreshCw size={14} /> : <Plus size={14} />}
          {showAddModal ? "Cancel" : "Add Custom Sector"}
        </button>
      </div>

      {showAddModal && (
        <div className="card fade-up" style={{ padding: 22, marginBottom: 20, border: "1px solid var(--border-lit)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Plus size={16} color="var(--cyan)" />
            <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
              Register Custom Policy Sector
            </span>
          </div>

          {errorMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", fontSize: 12, marginBottom: 14 }}>
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", color: "#10b981", fontSize: 12, marginBottom: 14 }}>
              {successMsg}
            </div>
          )}

          <form onSubmit={handleCreateSector} className="two-column-grid">
            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                SECTOR NAME *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. Supply Chain Security"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                COLOR THEME (HEX)
              </label>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  type="color"
                  value={color}
                  onChange={e => setColor(e.target.value)}
                  style={{ width: 40, height: 38, padding: 0, border: "1px solid var(--border)", borderRadius: 6, cursor: "pointer", background: "none" }}
                />
                <input
                  type="text"
                  value={color}
                  onChange={e => setColor(e.target.value)}
                  placeholder="#64748b"
                  style={{ flex: 1, padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
                />
              </div>
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                CLASSIFICATION KEYWORDS (COMMA SEPARATED)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={e => setKeywords(e.target.value)}
                placeholder="e.g. supply chain, logistics, vendor, procurement, third party"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                DESCRIPTION / SCOPE
              </label>
              <input
                type="text"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="e.g. Policies managing cybersecurity and integrity of components, software, and vendor feeds"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <button
                type="submit"
                disabled={submitting}
                style={{
                  padding: "10px 24px",
                  borderRadius: 6,
                  background: "#5c9e2e",
                  color: "#ffffff",
                  border: "none",
                  fontSize: 13,
                  fontFamily: "DM Sans",
                  fontWeight: 700,
                  cursor: submitting ? "not-allowed" : "pointer"
                }}
              >
                {submitting ? "Registering..." : "Register Custom Sector"}
              </button>
            </div>
          </form>
        </div>
      )}

      {editingSector && (
        <div className="card fade-up" style={{ padding: 22, marginBottom: 20, border: "1px solid var(--cyan)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <KeyRound size={16} color="var(--cyan)" />
            <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
              Edit Custom Sector: {editingSector.name}
            </span>
          </div>

          {errorMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", fontSize: 12, marginBottom: 14 }}>
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", color: "#10b981", fontSize: 12, marginBottom: 14 }}>
              {successMsg}
            </div>
          )}

          <form onSubmit={handleUpdateSectorSubmit} className="two-column-grid">
            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                SECTOR NAME *
              </label>
              <input
                type="text"
                required
                value={editingSector.name}
                onChange={e => setEditingSector({ ...editingSector, name: e.target.value })}
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                COLOR THEME (HEX)
              </label>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  type="color"
                  value={editingSector.color || "#64748b"}
                  onChange={e => setEditingSector({ ...editingSector, color: e.target.value })}
                  style={{ width: 40, height: 38, padding: 0, border: "1px solid var(--border)", borderRadius: 6, cursor: "pointer", background: "none" }}
                />
                <input
                  type="text"
                  value={editingSector.color || ""}
                  onChange={e => setEditingSector({ ...editingSector, color: e.target.value })}
                  style={{ flex: 1, padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                STATUS
              </label>
              <select
                value={editingSector.status}
                onChange={e => setEditingSector({ ...editingSector, status: e.target.value })}
                className="select-custom"
                style={{ width: "100%", height: 38 }}
              >
                <option value="Active">Active</option>
                <option value="Disabled">Disabled</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                CLASSIFICATION KEYWORDS
              </label>
              <input
                type="text"
                value={editingSector.keywords || ""}
                onChange={e => setEditingSector({ ...editingSector, keywords: e.target.value })}
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div style={{ gridColumn: "1 / -1" }}>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                DESCRIPTION / SCOPE
              </label>
              <input
                type="text"
                value={editingSector.description || ""}
                onChange={e => setEditingSector({ ...editingSector, description: e.target.value })}
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 8 }}>
              <button
                type="button"
                onClick={() => setEditingSector(null)}
                style={{
                  padding: "10px 18px",
                  borderRadius: 6,
                  background: "var(--bg-hover)",
                  color: "var(--text-main)",
                  border: "1px solid var(--border)",
                  fontSize: 13,
                  fontFamily: "DM Sans",
                  cursor: "pointer"
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                style={{
                  padding: "10px 24px",
                  borderRadius: 6,
                  background: "#5c9e2e",
                  color: "#ffffff",
                  border: "none",
                  fontSize: 13,
                  fontFamily: "DM Sans",
                  fontWeight: 700,
                  cursor: submitting ? "not-allowed" : "pointer"
                }}
              >
                {submitting ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Sectors Registry Table */}
      <div className="card" style={{ overflow: "hidden" }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Sector Details</th>
              <th>Type</th>
              <th>Keywords</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sectors.map((s, idx) => (
              <tr key={s.id || `sys-${idx}`}>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{
                      width: 14, height: 14, borderRadius: "50%",
                      background: s.color || "var(--cyan)",
                      backgroundColor: s.color || "var(--cyan)",
                      border: "1px solid var(--border)"
                    }} />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 13, color: "var(--text-main)" }}>{s.name}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{s.description}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <span className="admin-badge" style={{
                    background: s.is_builtin ? "rgba(2, 132, 199, 0.12)" : "rgba(163, 230, 53, 0.12)",
                    color: s.is_builtin ? "#0284c7" : "#5c9e2e",
                    border: `1px solid ${s.is_builtin ? "#0284c7" : "#5c9e2e"}40`
                  }}>
                    {s.is_builtin ? "System Default" : "Custom Registry"}
                  </span>
                </td>
                <td>
                  <div style={{ display: "flex", gap: 4, flexWrap: "wrap", maxWidth: 300 }}>
                    {s.keywords ? s.keywords.split(",").map((kw, i) => (
                      <span key={i} style={{ fontSize: 10, fontFamily: "JetBrains Mono", padding: "1px 5px", background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 4, color: "var(--text-muted)" }}>
                        {kw.trim()}
                      </span>
                    )) : (
                      <span style={{ fontSize: 11, color: "var(--text-dim)", fontStyle: "italic" }}>
                        {s.is_builtin ? "System hardcoded matching rules" : "No classification keywords set"}
                      </span>
                    )}
                  </div>
                </td>
                <td>
                  <span className="admin-badge" style={{
                    background: s.status === "Active" ? "rgba(16, 185, 129, 0.12)" : "rgba(107, 114, 128, 0.12)",
                    color: s.status === "Active" ? "#10b981" : "#6b7280",
                    border: `1px solid ${s.status === "Active" ? "#10b981" : "#6b7280"}40`
                  }}>
                    {s.status}
                  </span>
                </td>
                <td>
                  {!s.is_builtin ? (
                    <div style={{ display: "flex", gap: 6 }}>
                      <button
                        className="admin-action-btn"
                        title="Edit Custom Sector"
                        onClick={() => { setEditingSector(s); setShowAddModal(false); setErrorMsg(""); setSuccessMsg(""); }}
                        style={{ color: "#0284c7" }}
                      >
                        Edit
                      </button>
                      <button
                        className="admin-action-btn danger"
                        title="Delete Custom Sector"
                        onClick={() => handleDeleteSector(s.id, s.name)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ) : (
                    <span style={{ fontSize: 11, color: "var(--text-dim)", fontStyle: "italic" }}>Immutable default</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Trusted Domain Sources & Scaling Tab ─────────────────────────────────────
function SourcesTab() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [allSectors, setAllSectors] = useState([]);

  // Form state
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [sourceType, setSourceType] = useState("web_scraper");
  const [country, setCountry] = useState("Global");
  const [sector, setSector] = useState("All");
  const [description, setDescription] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Test Crawl State
  const [testingId, setTestingId] = useState(null);
  const [testResult, setTestResult] = useState(null);

  const loadSources = () => {
    setLoading(true);
    fetchTrustedSources()
      .then(d => {
        if (d && d.sources) setSources(d.sources);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  const loadSectorsList = () => {
    fetchAdminSectors()
      .then(d => {
        if (d) {
          const activeSectors = d.filter(s => s.status === "Active").map(s => s.name);
          setAllSectors([...new Set(activeSectors)].sort());
        }
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    loadSources();
    loadSectorsList();
  }, []);

  const handleCreateSource = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    if (!name || !url) {
      setErrorMsg("Source Name and URL Link are required");
      return;
    }
    setSubmitting(true);
    try {
      const res = await createTrustedSource({
        name,
        url,
        source_type: sourceType,
        country,
        sector,
        description
      });
      setSuccessMsg(res.message);
      setName("");
      setUrl("");
      setDescription("");
      loadSources();
      setTimeout(() => {
        setShowAddModal(false);
        setSuccessMsg("");
      }, 2000);
    } catch (err) {
      setErrorMsg(err.message || "Failed to add source link");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleStatus = async (id, currentStatus) => {
    const nextStatus = currentStatus === "Active" ? "Disabled" : "Active";
    try {
      await updateTrustedSourceStatus(id, nextStatus);
      loadSources();
    } catch (err) {
      alert("Failed to update status: " + err.message);
    }
  };

  const handleDeleteSource = async (id, sourceName) => {
    if (!window.confirm(`Remove trusted source link "${sourceName}"?`)) return;
    try {
      await deleteTrustedSource(id);
      loadSources();
    } catch (err) {
      alert("Failed to delete source: " + err.message);
    }
  };

  const handleTestCrawl = async (id) => {
    setTestingId(id);
    setTestResult(null);
    try {
      const res = await testTrustedSource(id);
      setTestResult({ sourceId: id, ...res });
    } catch (err) {
      alert("Crawl test failed: " + err.message);
    } finally {
      setTestingId(null);
    }
  };

  const sourceTypeBadge = (type) => {
    const badges = {
      sparql: { bg: "rgba(147, 51, 234, 0.15)", color: "#a855f7", label: "SPARQL API" },
      json_api: { bg: "rgba(2, 132, 199, 0.15)", color: "#0284c7", label: "JSON API" },
      rss_feed: { bg: "rgba(245, 158, 11, 0.15)", color: "#f59e0b", label: "RSS Feed" },
      web_scraper: { bg: "rgba(16, 185, 129, 0.15)", color: "#10b981", label: "Web Scraper" },
    };
    const b = badges[type] || badges.web_scraper;
    return (
      <span className="admin-badge" style={{ background: b.bg, color: b.color, border: `1px solid ${b.color}40`, fontFamily: "JetBrains Mono" }}>
        {b.label}
      </span>
    );
  };

  return (
    <div className="fade-up">
      {/* Header bar */}
      <div className="card" style={{ padding: "18px 24px", marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Globe2 size={18} color="#5c9e2e" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
              Trusted Domain Links & Ingestion Pipeline Scaling
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: 12, color: "var(--text-muted)", fontFamily: "DM Sans" }}>
            Add official government sites, RSS feeds, or API endpoints to scale PolicyIQ's automated ingestion engine.
          </p>
        </div>

        <div className="flex-toolbar" style={{ gap: 10 }}>
          <button
            onClick={() => { setShowAddModal(!showAddModal); setErrorMsg(""); setSuccessMsg(""); }}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "9px 16px",
              borderRadius: 8,
              background: showAddModal ? "var(--bg-hover)" : "#5c9e2e",
              color: showAddModal ? "var(--text-main)" : "#ffffff",
              border: showAddModal ? "1px solid var(--border)" : "none",
              fontSize: 13,
              fontFamily: "DM Sans",
              fontWeight: 700,
              cursor: "pointer",
              transition: "all 0.15s ease"
            }}
          >
            {showAddModal ? <RefreshCw size={14} /> : <Plus size={14} />}
            {showAddModal ? "Cancel" : "Add Trusted Domain Link"}
          </button>
        </div>
      </div>

      {/* Add Trusted Source Form Modal/Card */}
      {showAddModal && (
        <div className="card fade-up" style={{ padding: 22, marginBottom: 20, border: "1px solid var(--border-lit)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Globe2 size={16} color="var(--cyan)" />
            <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "DM Sans", color: "var(--text-main)" }}>
              Provision New Policy Ingestion Link
            </span>
          </div>

          {errorMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", fontSize: 12, marginBottom: 14 }}>
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div style={{ padding: "10px 14px", borderRadius: 8, background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)", color: "#10b981", fontSize: 12, marginBottom: 14 }}>
              {successMsg}
            </div>
          )}

          <form onSubmit={handleCreateSource} className="two-column-grid">
            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                SOURCE NAME *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. NIST Cybersecurity Portal"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                TARGET URL LINK *
              </label>
              <input
                type="url"
                required
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://www.nist.gov/cyberframework/feed"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                SOURCE INGESTION TYPE
              </label>
              <select
                value={sourceType}
                onChange={e => setSourceType(e.target.value)}
                className="select-custom"
                style={{ width: "100%", height: 38 }}
              >
                <option value="web_scraper">Web Page Scraper (HTML)</option>
                <option value="rss_feed">RSS / Atom Feed (XML)</option>
                <option value="json_api">JSON REST API</option>
                <option value="sparql">SPARQL RDF Query</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                JURISDICTION / COUNTRY
              </label>
              <input
                type="text"
                value={country}
                onChange={e => setCountry(e.target.value)}
                placeholder="e.g. United States / Global"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                PRIMARY SECTOR FOCUS
              </label>
              <select
                value={sector}
                onChange={e => setSector(e.target.value)}
                className="select-custom"
                style={{ width: "100%", height: 38 }}
              >
                <option value="All">All Sectors</option>
                {allSectors.map((s, idx) => (
                  <option key={idx} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 11, fontFamily: "JetBrains Mono", color: "var(--text-muted)", marginBottom: 4 }}>
                DESCRIPTION / NOTES
              </label>
              <input
                type="text"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="e.g. Official US standards & guidelines RSS feed"
                style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: "1px solid var(--border)", background: "var(--bg-hover)", color: "var(--text-main)", fontSize: 13, outline: "none" }}
              />
            </div>

            <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <button
                type="submit"
                disabled={submitting}
                style={{
                  padding: "10px 24px",
                  borderRadius: 6,
                  background: "#5c9e2e",
                  color: "#ffffff",
                  border: "none",
                  fontSize: 13,
                  fontFamily: "DM Sans",
                  fontWeight: 700,
                  cursor: submitting ? "not-allowed" : "pointer"
                }}
              >
                {submitting ? "Provisioning Source..." : "Add & Provision Source Link"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Test Result Preview Modal / Panel */}
      {testResult && (
        <div className="card fade-up" style={{ padding: 20, marginBottom: 20, border: "1px solid var(--cyan)", background: "rgba(6, 182, 212, 0.04)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <CheckCircle size={16} color="var(--cyan)" />
              <span style={{ fontSize: 13, fontWeight: 700, color: "var(--text-main)", fontFamily: "DM Sans" }}>
                Test Crawl Preview: {testResult.message}
              </span>
            </div>
            <button className="admin-action-btn" onClick={() => setTestResult(null)}>✕</button>
          </div>
          <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "0 0 12px 0" }}>
            Extracted <strong>{testResult.extracted_count}</strong> policy documents during live site inspection:
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 220, overflowY: "auto" }}>
            {testResult.sample_policies?.map((p, idx) => (
              <div key={idx} style={{ padding: 10, borderRadius: 6, background: "var(--bg-hover)", border: "1px solid var(--border)", fontSize: 12 }}>
                <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: 2 }}>{p.title}</div>
                <div style={{ display: "flex", gap: 12, fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                  <span>Sector: {p.sector}</span>
                  <span>Country: {p.country}</span>
                  <a href={p.source_url} target="_blank" rel="noreferrer" style={{ color: "var(--cyan)", display: "flex", alignItems: "center", gap: 2 }}>
                    Link <ExternalLink size={10} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sources List Table */}
      <div className="card" style={{ overflow: "hidden" }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Domain Source</th>
              <th>Type</th>
              <th>Jurisdiction & Sector</th>
              <th>Fetched Policies</th>
              <th>Last Crawled</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sources.map(s => (
              <tr key={s.id}>
                <td>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "var(--text-main)" }}>{s.name}</div>
                    <a href={s.url} target="_blank" rel="noreferrer" style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", display: "inline-flex", alignItems: "center", gap: 4, textDecoration: "none" }}>
                      {s.url.length > 45 ? s.url.substring(0, 45) + "..." : s.url}
                      <ExternalLink size={10} />
                    </a>
                  </div>
                </td>
                <td>{sourceTypeBadge(s.source_type)}</td>
                <td>
                  <div style={{ fontSize: 12 }}>
                    <span style={{ fontWeight: 600, color: "var(--text-main)" }}>{s.country}</span>
                    <span style={{ color: "var(--text-muted)", marginLeft: 6 }}>({s.sector})</span>
                  </div>
                </td>
                <td>
                  <span style={{ fontFamily: "JetBrains Mono", fontSize: 13, fontWeight: 700, color: "#5c9e2e" }}>
                    {s.policies_fetched || 0}
                  </span>
                </td>
                <td style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  {s.last_crawled_at ? timeAgo(s.last_crawled_at) : "Never"}
                </td>
                <td>
                  <span className="admin-badge" style={{
                    background: s.status === "Active" ? "rgba(16, 185, 129, 0.12)" : "rgba(107, 114, 128, 0.12)",
                    color: s.status === "Active" ? "#10b981" : "#6b7280",
                    border: `1px solid ${s.status === "Active" ? "#10b981" : "#6b7280"}40`
                  }}>
                    {s.status}
                  </span>
                </td>
                <td>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button
                      className="admin-action-btn"
                      title="Test Crawl Site Link"
                      disabled={testingId === s.id}
                      onClick={() => handleTestCrawl(s.id)}
                      style={{ color: "#0284c7" }}
                    >
                      {testingId === s.id ? <RefreshCw size={13} className="spin" /> : <Play size={13} />}
                    </button>

                    <button
                      className="admin-action-btn"
                      title={s.status === "Active" ? "Disable Source" : "Enable Source"}
                      onClick={() => handleToggleStatus(s.id, s.status)}
                      style={{ color: s.status === "Active" ? "#f59e0b" : "#16a34a" }}
                    >
                      <Ban size={13} />
                    </button>

                    <button
                      className="admin-action-btn danger"
                      title="Delete Source Link"
                      onClick={() => handleDeleteSource(s.id, s.name)}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {(!sources || sources.length === 0) && !loading && (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: 32, color: "var(--text-dim)" }}>
                  No domain sources configured yet. Click "Add Trusted Domain Link" above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Support Queries Tab ───────────────────────────────────────────────────
function SupportTab() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAdminSupportMessages();
      if (Array.isArray(data)) {
        setMessages(data);
      }
    } catch (err) {
      setError("Failed to fetch support queries.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const conversationsMap = {};
  messages.forEach((msg) => {
    const uid = msg.user_id;
    if (!conversationsMap[uid]) {
      conversationsMap[uid] = {
        user_id: uid,
        user_name: msg.user_name || "Unknown User",
        user_email: msg.user_email || "no-email",
        status: msg.status || "open",
        latest_message: msg.message,
        latest_date: msg.created_at,
        messages: []
      };
    }
    conversationsMap[uid].messages.push(msg);
    conversationsMap[uid].latest_message = msg.message;
    conversationsMap[uid].latest_date = msg.created_at;
    if (msg.status === "open") {
      conversationsMap[uid].status = "open";
    }
  });

  const conversationList = Object.values(conversationsMap).filter((c) => {
    if (filterStatus === "open") return c.status === "open";
    if (filterStatus === "resolved") return c.status === "resolved";
    return true;
  });

  useEffect(() => {
    if (conversationList.length > 0 && (!selectedUserId || !conversationsMap[selectedUserId])) {
      setSelectedUserId(conversationList[0].user_id);
    }
  }, [messages, filterStatus]);

  const activeConv = selectedUserId ? conversationsMap[selectedUserId] : null;

  const handleSendReply = async (e) => {
    e.preventDefault();
    if (!selectedUserId || !replyText.trim() || sending) return;

    setSending(true);
    try {
      await sendAdminReply(selectedUserId, replyText.trim());
      setReplyText("");
      await loadData();
    } catch (err) {
      alert(err.message || "Failed to send reply");
    } finally {
      setSending(false);
    }
  };

  const handleToggleStatus = async () => {
    if (!selectedUserId || !activeConv) return;
    const newStatus = activeConv.status === "open" ? "resolved" : "open";
    try {
      await updateUserSupportStatus(selectedUserId, newStatus);
      await loadData();
    } catch (err) {
      alert("Failed to update status");
    }
  };

  if (loading) {
    return <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)", fontFamily: "DM Sans" }}>Loading support conversations...</div>;
  }

  return (
    <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div style={{ display: "flex", gap: 8 }}>
          {["all", "open", "resolved"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              style={{
                background: filterStatus === st ? "#5c9e2e" : "var(--bg-card)",
                color: filterStatus === st ? "#ffffff" : "var(--text-muted)",
                border: "1px solid var(--border)",
                borderRadius: 6,
                padding: "6px 14px",
                fontSize: 12,
                fontFamily: "DM Sans",
                cursor: "pointer",
                textTransform: "capitalize",
                fontWeight: filterStatus === st ? 600 : 400
              }}
            >
              {st} ({Object.values(conversationsMap).filter(c => st === "all" ? true : c.status === st).length})
            </button>
          ))}
        </div>
        <button
          onClick={loadData}
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: 6,
            padding: "6px 12px",
            color: "var(--text-main)",
            fontSize: 12,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 6
          }}
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {error && (
        <div style={{ padding: 12, background: "rgba(244, 63, 94, 0.1)", border: "1px solid rgba(244, 63, 94, 0.2)", borderRadius: 6, color: "#f43f5e", fontSize: 12 }}>
          {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 16, minHeight: 480 }}>
        <div style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column"
        }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", background: "var(--bg-hover)", fontSize: 12, fontWeight: 700, fontFamily: "JetBrains Mono" }}>
            CLIENT THREADS ({conversationList.length})
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            {conversationList.length === 0 ? (
              <div style={{ padding: 24, textAlign: "center", color: "var(--text-muted)", fontSize: 12 }}>
                No support queries matching filter.
              </div>
            ) : (
              conversationList.map((conv) => {
                const isSelected = selectedUserId === conv.user_id;
                return (
                  <div
                    key={conv.user_id}
                    onClick={() => setSelectedUserId(conv.user_id)}
                    style={{
                      padding: "12px 14px",
                      borderBottom: "1px solid var(--border)",
                      background: isSelected ? "var(--bg-hover)" : "transparent",
                      cursor: "pointer",
                      display: "flex",
                      flexDirection: "column",
                      gap: 4
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-main)", fontFamily: "DM Sans" }}>
                        {conv.user_name}
                      </span>
                      <span style={{
                        fontSize: 10,
                        fontFamily: "JetBrains Mono",
                        padding: "2px 6px",
                        borderRadius: 4,
                        background: conv.status === "open" ? "rgba(92, 158, 46, 0.15)" : "var(--bg-hover)",
                        color: conv.status === "open" ? "#5c9e2e" : "var(--text-dim)"
                      }}>
                        {conv.status.toUpperCase()}
                      </span>
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {conv.user_email}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-dim)", fontFamily: "DM Sans", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginTop: 2 }}>
                      {conv.latest_message}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden"
        }}>
          {activeConv ? (
            <>
              <div style={{
                padding: "14px 18px",
                borderBottom: "1px solid var(--border)",
                background: "var(--bg-hover)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-main)", fontFamily: "DM Sans" }}>
                    {activeConv.user_name}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                    {activeConv.user_email} · User ID: {activeConv.user_id}
                  </div>
                </div>
                <button
                  onClick={handleToggleStatus}
                  style={{
                    background: activeConv.status === "open" ? "rgba(92, 158, 46, 0.1)" : "var(--bg-hover)",
                    border: "1px solid " + (activeConv.status === "open" ? "rgba(92, 158, 46, 0.3)" : "var(--border)"),
                    color: activeConv.status === "open" ? "#5c9e2e" : "var(--text-muted)",
                    borderRadius: 6,
                    padding: "6px 12px",
                    fontSize: 11,
                    fontFamily: "JetBrains Mono",
                    cursor: "pointer"
                  }}
                >
                  Status: {activeConv.status.toUpperCase()} (Click to toggle)
                </button>
              </div>

              <div style={{
                flex: 1,
                padding: 16,
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: 12,
                background: "var(--bg-deep)"
              }}>
                {activeConv.messages.map((m) => {
                  const isAdmin = m.sender === "admin";
                  return (
                    <div
                      key={m.id}
                      style={{
                        alignSelf: isAdmin ? "flex-end" : "flex-start",
                        maxWidth: "80%",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: isAdmin ? "flex-end" : "flex-start"
                      }}
                    >
                      <span style={{ fontSize: 10, color: "var(--text-dim)", marginBottom: 2, fontFamily: "JetBrains Mono" }}>
                        {isAdmin ? "Admin (You)" : activeConv.user_name} · {new Date(m.created_at).toLocaleString()}
                      </span>
                      <div style={{
                        padding: "10px 14px",
                        borderRadius: isAdmin ? "10px 10px 2px 10px" : "10px 10px 10px 2px",
                        background: isAdmin ? "#5c9e2e" : "var(--bg-card)",
                        color: isAdmin ? "#ffffff" : "var(--text-main)",
                        border: isAdmin ? "none" : "1px solid var(--border)",
                        fontSize: 13,
                        lineHeight: 1.5,
                        fontFamily: "DM Sans",
                        wordBreak: "break-word"
                      }}>
                        {m.message}
                      </div>
                    </div>
                  );
                })}
              </div>

              <form
                onSubmit={handleSendReply}
                style={{
                  padding: 12,
                  borderTop: "1px solid var(--border)",
                  background: "var(--bg-card)",
                  display: "flex",
                  gap: 10
                }}
              >
                <input
                  type="text"
                  placeholder="Type an admin reply..."
                  value={replyText}
                  maxLength={2000}
                  onChange={(e) => setReplyText(e.target.value)}
                  disabled={sending}
                  style={{
                    flex: 1,
                    background: "var(--bg-hover)",
                    border: "1px solid var(--border)",
                    borderRadius: 6,
                    padding: "8px 12px",
                    fontSize: 13,
                    color: "var(--text-main)",
                    fontFamily: "DM Sans",
                    outline: "none"
                  }}
                />
                <button
                  type="submit"
                  disabled={sending || !replyText.trim()}
                  style={{
                    background: "#5c9e2e",
                    color: "#ffffff",
                    border: "none",
                    borderRadius: 6,
                    padding: "8px 16px",
                    fontSize: 12,
                    fontWeight: 600,
                    fontFamily: "DM Sans",
                    cursor: sending || !replyText.trim() ? "not-allowed" : "pointer",
                    opacity: sending || !replyText.trim() ? 0.5 : 1,
                    display: "flex",
                    alignItems: "center",
                    gap: 6
                  }}
                >
                  <Send size={14} /> {sending ? "Sending..." : "Reply"}
                </button>
              </form>
            </>
          ) : (
            <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)", fontSize: 13, fontFamily: "DM Sans" }}>
              Select a client conversation on the left to view messages and reply.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main Admin Dashboard ───────────────────────────────────────────────────
export default function AdminDashboard() {
  const [tab, setTab] = useState("overview");
  const [stats, setStats] = useState(null);

  useEffect(() => { fetchAdminStats().then(d => d && setStats(d)); }, []);

  const tabs = [
    { id: "overview", icon: BarChart3, label: "Overview" },
    { id: "users", icon: Users, label: "Users" },
    { id: "support", icon: MessageSquare, label: "Support Queries" },
    { id: "sectors", icon: Database, label: "Sectors Registry" },
    { id: "sources", icon: Globe2, label: "Trusted Sources" },
    { id: "activity", icon: Activity, label: "Activity Log" },
    { id: "system", icon: Server, label: "System" },
  ];

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="fade-up" style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
          <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#5c9e2e" }} />
          <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
            ADMIN / CONTROL PANEL
          </span>
        </div>
        <h1 style={{ 
          fontFamily: "'DM Sans', sans-serif", 
          fontSize: "52px", 
          fontWeight: 700, 
          color: "var(--text-main)",
          margin: "0 0 16px 0",
          letterSpacing: "-1.5px",
          lineHeight: "1.1"
        }}>
          System oversight <span className="half-highlight-custom">console.</span>
        </h1>
        <p style={{ fontFamily: "DM Sans", fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
          Role-based user administration · Audit logging · Dynamic crawler scaling & trusted sources
        </p>
      </div>

      {/* Tabs */}
      <div className="admin-tab-bar">
        {tabs.map(t => (
          <TabBtn key={t.id} icon={t.icon} label={t.label} active={tab === t.id} onClick={() => setTab(t.id)} />
        ))}
      </div>

      {/* Content */}
      <div style={{ marginTop: 20 }}>
        {tab === "overview" && <OverviewTab stats={stats} />}
        {tab === "users" && <UsersTab />}
        {tab === "support" && <SupportTab />}
        {tab === "sectors" && <SectorsTab />}
        {tab === "sources" && <SourcesTab />}
        {tab === "activity" && <ActivityTab />}
        {tab === "system" && <SystemTab />}
      </div>
    </div>
  );
}

