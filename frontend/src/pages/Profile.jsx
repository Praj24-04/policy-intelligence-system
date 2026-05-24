import { useEffect, useState } from "react";
import { fetchHistory } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { 
  User, Shield, Mail, Calendar, UploadCloud, 
  FileText, GitCompare, Sparkles, CheckCircle2 
} from "lucide-react";

export default function Profile({ user }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPriorities, setSelectedPriorities] = useState(["AI Governance", "Data Privacy"]);

  useEffect(() => {
    fetchHistory()
      .then(data => {
        if (data) {
          setHistory(data);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const togglePriority = (sector) => {
    if (selectedPriorities.includes(sector)) {
      setSelectedPriorities(selectedPriorities.filter(s => s !== sector));
    } else {
      setSelectedPriorities([...selectedPriorities, sector]);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    }) + " " + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) return <LoadingSpinner label="Retrieving account analytics..." />;

  const totalUploads = history?.uploads?.length || 0;
  const totalGenerates = history?.generates?.length || 0;
  const totalCompares = history?.compares?.length || 0;
  const totalContributions = totalUploads + totalGenerates + totalCompares;

  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "var(--bg-deep)",
      minHeight: "100vh"
    }}>
      <div style={{
        maxWidth: "1280px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>
        {/* Page Header */}
        <div className="fade-up" style={{ marginBottom: "28px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#5c9e2e" }} />
            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
              ACCOUNT / PROFILE
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
            Your workspaces <span className="half-highlight-custom">analytics.</span>
          </h1>
          <p style={{ fontFamily: "DM Sans", fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
            Lead regulatory analyst environment overview · spaCy NER pipeline status
          </p>
        </div>

        {/* Dashboard Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px", alignItems: "start" }}>
          
          {/* Left Column: User Profile Details */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Identity Card */}
            <div className="fade-up" style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "24px 28px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center"
            }}>
              <div style={{
                width: "72px",
                height: "72px",
                borderRadius: "16px",
                background: "rgba(92, 158, 46, 0.08)",
                border: "1px solid rgba(92, 158, 46, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "28px",
                fontWeight: 700,
                color: "#5c9e2e",
                fontFamily: "DM Sans",
                marginBottom: "16px"
              }}>
                {userInitial}
              </div>
              <h2 style={{
                fontFamily: "DM Sans",
                fontSize: "18px",
                fontWeight: 700,
                color: "var(--text-main)",
                marginBottom: "4px"
              }}>
                {user?.full_name || "Analyst User"}
              </h2>
              <div style={{
                fontFamily: "JetBrains Mono",
                fontSize: "10px",
                color: "#5c9e2e",
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                background: "rgba(92, 158, 46, 0.08)",
                border: "1px solid rgba(92, 158, 46, 0.15)",
                borderRadius: "4px",
                padding: "2px 8px",
                marginBottom: "20px"
              }}>
                {user?.role || "USER"}
              </div>

              <div style={{ width: "100%", height: "1px", background: "var(--border)", marginBottom: "20px" }} />

              <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: "14px", textAlign: "left" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Mail size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                  <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                    {user?.email || "N/A"}
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Shield size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                  <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                    JWT Authenticated Session
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Calendar size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                  <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                    Joined: {formatDate(user?.created_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* Recommender Preferences */}
            <div className="fade-up" style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "22px 26px"
            }}>
              <div style={{ 
                display: "inline-block", 
                background: "rgba(92, 158, 46, 0.08)", 
                border: "1px solid rgba(92, 158, 46, 0.15)", 
                borderRadius: "4px", 
                padding: "4px 10px", 
                marginBottom: "12px" 
              }}>
                <span style={{ fontFamily: "DM Sans", fontWeight: 600, fontSize: "13px", color: "#5c9e2e", letterSpacing: "0.02em" }}>
                  ML Priority Alignments
                </span>
              </div>
              <p style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)", marginBottom: "16px" }}>
                Select priority sectors to filter recommendations and cluster search weight.
              </p>
              
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {["AI Governance", "Data Privacy", "Cybersecurity", "Healthcare AI", "Financial Regulation", "ESG Policies", "IoT and Robotics"].map((sector) => {
                  const active = selectedPriorities.includes(sector);
                  return (
                    <button 
                      key={sector}
                      onClick={() => togglePriority(sector)}
                      style={{
                        background: active ? "rgba(92, 158, 46, 0.08)" : "var(--bg-hover)",
                        border: active ? "1px solid rgba(92, 158, 46, 0.3)" : "1px solid var(--border)",
                        borderRadius: "20px",
                        padding: "4px 12px",
                        fontSize: "12px",
                        fontFamily: "DM Sans",
                        color: active ? "#5c9e2e" : "var(--text-muted)",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        transition: "all 0.15s ease"
                      }}
                    >
                      {active && <CheckCircle2 size={12} color="#5c9e2e" />}
                      {sector}
                    </button>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Right Column: Key Stats & Activity Streams */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Multi-Metric Cards Row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
              {[
                { label: "PDFs Ingested", value: totalUploads, icon: UploadCloud, desc: "Processed via spaCy NER" },
                { label: "Templates Drafted", value: totalGenerates, icon: FileText, desc: "Created via Template Gen" },
                { label: "Comparisons Executed", value: totalCompares, icon: GitCompare, desc: "Standard pdf exports" }
              ].map((stat, idx) => {
                const StatIcon = stat.icon;
                return (
                  <div key={idx} className="fade-up" style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    padding: "16px 20px"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                        {stat.label}
                      </span>
                      <StatIcon size={14} color="#5c9e2e" />
                    </div>
                    <span style={{ fontSize: "32px", fontFamily: "DM Sans", fontWeight: 700, color: "var(--text-main)", display: "block", marginBottom: "4px" }}>
                      {stat.value}
                    </span>
                    <span style={{ fontSize: "11px", fontFamily: "DM Sans", color: "var(--text-dim)" }}>
                      {stat.desc}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Custom Interactive Tabs for History Lists */}
            <div className="fade-up" style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "24px 28px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <div>
                  <div style={{ 
                    display: "inline-block", 
                    background: "rgba(92, 158, 46, 0.08)", 
                    border: "1px solid rgba(92, 158, 46, 0.15)", 
                    borderRadius: "4px", 
                    padding: "4px 10px", 
                    marginBottom: "8px" 
                  }}>
                    <span style={{ fontFamily: "DM Sans", fontWeight: 600, fontSize: "13px", color: "#5c9e2e", letterSpacing: "0.02em" }}>
                      Platform Activity Logs
                    </span>
                  </div>
                  <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                    Detailed log of your regulatory analytical transactions
                  </div>
                </div>
                <span style={{ 
                  background: "var(--bg-hover)", 
                  border: "1px solid var(--border)", 
                  borderRadius: "4px", 
                  padding: "4px 10px", 
                  fontSize: "11px", 
                  color: "var(--text-muted)", 
                  fontFamily: "JetBrains Mono" 
                }}>
                  {totalContributions} TOTAL ACTIONS
                </span>
              </div>

              {/* Activity Lists Wrapper */}
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                
                {/* 1. PDF Uploads */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", borderBottom: "1px solid var(--border)", paddingBottom: "6px" }}>
                    <UploadCloud size={14} color="#5c9e2e" />
                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600, letterSpacing: "0.05em" }}>
                      INGESTED DOCUMENTS ({totalUploads})
                    </span>
                  </div>
                  
                  {totalUploads === 0 ? (
                    <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-dim)", padding: "10px 0" }}>
                      No documents ingested yet. Go to Discover &gt; Upload PDF to process a document.
                    </div>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {history.uploads.map((up) => (
                        <div key={up.id} style={{
                          background: "var(--bg-hover)",
                          border: "1px solid var(--border)",
                          borderRadius: "6px",
                          padding: "10px 14px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}>
                          <div>
                            <span style={{ fontSize: "13px", fontFamily: "DM Sans", fontWeight: 600, color: "var(--text-main)", display: "block" }}>
                              {up.title || up.filename}
                            </span>
                            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                              {up.filename} · {up.word_count || 0} words
                            </span>
                          </div>
                          <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                            {formatDate(up.created_at)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 2. Custom Templates */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", borderBottom: "1px solid var(--border)", paddingBottom: "6px" }}>
                    <FileText size={14} color="#5c9e2e" />
                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600, letterSpacing: "0.05em" }}>
                      DRAFTED TEMPLATES ({totalGenerates})
                    </span>
                  </div>

                  {totalGenerates === 0 ? (
                    <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-dim)", padding: "10px 0" }}>
                      No templates generated yet. Go to Discover &gt; Generate Policy to draft a framework.
                    </div>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {history.generates.map((gen) => (
                        <div key={gen.id} style={{
                          background: "var(--bg-hover)",
                          border: "1px solid var(--border)",
                          borderRadius: "6px",
                          padding: "10px 14px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}>
                          <div>
                            <span style={{ fontSize: "13px", fontFamily: "DM Sans", fontWeight: 600, color: "var(--text-main)", display: "block" }}>
                              {gen.sector} Framework
                            </span>
                            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                              Target Jurisdiction: {gen.country}
                            </span>
                          </div>
                          <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                            {formatDate(gen.created_at)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 3. Comparators */}
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", borderBottom: "1px solid var(--border)", paddingBottom: "6px" }}>
                    <GitCompare size={14} color="#5c9e2e" />
                    <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600, letterSpacing: "0.05em" }}>
                      GAP ANALYSIS COMPARISONS ({totalCompares})
                    </span>
                  </div>

                  {totalCompares === 0 ? (
                    <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-dim)", padding: "10px 0" }}>
                      No comparisons executed yet. Go to Prep &gt; Compare to align frameworks.
                    </div>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {history.compares.map((comp) => (
                        <div key={comp.id} style={{
                          background: "var(--bg-hover)",
                          border: "1px solid var(--border)",
                          borderRadius: "6px",
                          padding: "10px 14px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}>
                          <div>
                            <span style={{ fontSize: "13px", fontFamily: "DM Sans", fontWeight: 600, color: "var(--text-main)", display: "block" }}>
                              Bilateral Gap Comparison
                            </span>
                            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                              Policies: {comp.policy_id_1} ⇄ {comp.policy_id_2}
                            </span>
                          </div>
                          <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-dim)" }}>
                            {formatDate(comp.created_at)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
