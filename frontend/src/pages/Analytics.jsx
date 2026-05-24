import { useEffect, useState } from "react";
import { fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries, fetchStatus } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, Cell
} from "recharts";

// Premium color system matching the forest green/grey theme
const COLORS = ["#5c9e2e", "#7ca85a", "#9cb288", "#2563eb", "#5b84d4", "#8c9fb2"];

export default function Analytics() {
  const [sectors,       setSectors]       = useState([]);
  const [regions,       setRegions]       = useState([]);
  const [trends,        setTrends]        = useState([]);
  const [countries,     setCountries]     = useState([]);
  const [status,        setStatus]        = useState([]);
  const [loading,       setLoading]       = useState(true);
  const [feedbackStats, setFeedbackStats] = useState(null);

  useEffect(() => {
    Promise.all([fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries(), fetchStatus()])
      .then(([sec, reg, tr, ctr, st]) => {
        setSectors(Object.entries(sec || {}).map(([name, value]) => ({ name, value })));
        setRegions(Object.entries(reg || {}).map(([name, value]) => ({ name, value })));
        setTrends(Object.entries(tr || {}).map(([year, count]) => ({ year: String(year), count })));
        setCountries(Object.entries(ctr || {}).sort((a,b) => b[1]-a[1]).slice(0,10).map(([name, value]) => ({ name, value })));
        setStatus(Object.entries(st || {}).map(([name, value]) => ({ name, value })));
        setLoading(false);
      });

    // Fetch feedback summary
    fetch("http://localhost:8000/api/feedback/summary")
      .then(r => r.json())
      .then(setFeedbackStats)
      .catch(() => {});
  }, []);

  if (loading) return <LoadingSpinner label="Generating analytics..." />;

  // Styled unified Card Component matching Compare visual system with scaled up fonts
  const ChartCard = ({ title, sub, children, delay = 1 }) => (
    <div 
      className={`card fade-up fade-up-${delay}`} 
      style={{ 
        padding: "22px 28px",
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
        marginBottom: "0px" // Managed by grid/row layout
      }}
    >
      <h3 style={{ 
        fontFamily: "DM Sans", 
        fontWeight: 600, 
        fontSize: "15px", // Scaled up from 14px
        color: "var(--text-main)", 
        margin: "0 0 4px 0" 
      }}>
        {title}
      </h3>
      <p style={{ 
        fontFamily: "DM Sans", 
        fontSize: "13px", // Scaled up from 12px
        color: "var(--text-muted)", 
        margin: "0 0 20px 0" 
      }}>
        {sub}
      </p>
      {children}
    </div>
  );

  // Minimalist, high-legibility tooltip style
  const TTStyle = { 
    background: "var(--bg-card)", 
    border: "1px solid var(--border)", 
    borderRadius: "6px", 
    fontSize: "12px", 
    fontFamily: "DM Sans",
    color: "var(--text-main)",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)"
  };

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
        
        {/* Page Header (Exactly aligned with Compare and Database titles) */}
        <div className="fade-up" style={{ marginBottom: "28px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--cyan)", backgroundColor: "var(--cyan)" }}></span>
            <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)", letterSpacing: "0.05em" }}>
              PREP / INSIGHTS
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
            Discover global <span className="half-highlight-custom">trends.</span>
          </h1>
          <p style={{ fontFamily: "DM Sans", fontSize: "14px", color: "var(--text-muted)", margin: 0 }}>
            Aggregated view of global policy intelligence data
          </p>
        </div>

        {/* Grid Spacing Variable: 20px, Card Spacings: 28px */}

        {/* Charts Row 1 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "28px" }}>
          
          {/* Country bar */}
          <ChartCard title="Top Countries by Policy Mentions" sub="Extracted via spaCy NER from policy content" delay={1}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={countries} layout="vertical" barSize={10}>
                <XAxis type="number" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Sans" }} axisLine={false} tickLine={false} width={110} />
                <Tooltip contentStyle={TTStyle} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {countries.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Region radar */}
          <ChartCard title="Regional Policy Distribution" sub="Geographic spread across global regions" delay={2}>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={regions}>
                {/* Soft, clean grid lines in grey for light theme integration */}
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Sans" }} />
                <Radar dataKey="value" stroke="#5c9e2e" fill="#5c9e2e" fillOpacity={0.12} strokeWidth={2} />
                <Tooltip contentStyle={TTStyle} />
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Charts Row 2 */}
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "20px", marginBottom: "28px" }}>
          
          {/* Year trend */}
          <ChartCard title="Global Policy Adoption Timeline" sub="Year-wise policy enactment trend" delay={3}>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={trends} barSize={24}>
                <XAxis dataKey="year" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} width={25} />
                <Tooltip contentStyle={TTStyle} />
                <Bar dataKey="count" radius={[4,4,0,0]}>
                  {trends.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Status */}
          <ChartCard title="Policy Status" sub="Active vs Under Review" delay={4}>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {status.map((s, i) => {
                const isActive = s.name === "Active";
                return (
                  <div key={i} style={{
                    display: "flex", 
                    justifyContent: "space-between", 
                    alignItems: "center",
                    padding: "14px 20px", 
                    borderRadius: "8px",
                    background: isActive ? "#f0f7e8" : "rgba(245,158,11,0.05)",
                    border: `1px solid ${isActive ? "rgba(92,158,46,0.2)" : "rgba(245,158,11,0.15)"}`,
                  }}>
                    <span style={{ 
                      fontSize: "14px", // Scaled up from 13px
                      fontFamily: "DM Sans",
                      fontWeight: 600,
                      color: isActive ? "#3d6b1e" : "#d97706" 
                    }}>
                      {s.name}
                    </span>
                    <span style={{
                      fontFamily: "DM Sans", 
                      fontWeight: 700, 
                      fontSize: "28px",
                      color: isActive ? "#5c9e2e" : "#d97706"
                    }}>
                      {s.value}
                    </span>
                  </div>
                );
              })}
            </div>
          </ChartCard>
        </div>

        {/* Feedback Stats */}
        {feedbackStats && (
          <div 
            className="card fade-up" 
            style={{ 
              padding: "22px 28px", 
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
              marginTop: "0" 
            }}
          >
            <h3 style={{
              fontFamily: "DM Sans", 
              fontWeight: 600,
              fontSize: "15px", // Scaled up from 14px
              color: "var(--text-main)", 
              margin: "0 0 4px 0"
            }}>
              Recommendation Feedback
            </h3>
            <p style={{ 
              fontFamily: "DM Sans",
              fontSize: "13px", // Scaled up from 12px
              color: "var(--text-muted)", 
              margin: "0 0 20px 0" 
            }}>
              User validation of ML recommendations
            </p>

            {/* Feedback Summary Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "20px" }}>
              {[
                { label: "Total Feedback", value: feedbackStats.total_feedback, color: "#2563eb" },
                { label: "Marked Helpful", value: feedbackStats.positive, color: "#5c9e2e" },
                { label: "Accuracy Rate", value: `${feedbackStats.accuracy_rate}%`, color: "#d97706" },
              ].map((s, i) => (
                <div key={i} style={{
                  background: "var(--bg-hover)",
                  backgroundColor: "var(--bg-hover)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px", 
                  padding: "16px", 
                  textAlign: "center"
                }}>
                  <div style={{
                    fontSize: "11px", 
                    color: "var(--text-muted)",
                    fontWeight: 600,
                    letterSpacing: "0.06em",
                    fontFamily: "JetBrains Mono", 
                    marginBottom: "6px",
                    textTransform: "uppercase"
                  }}>
                    {s.label}
                  </div>
                  <div style={{
                    fontFamily: "DM Sans", 
                    fontWeight: 700,
                    fontSize: "24px", 
                    color: s.color
                  }}>
                    {s.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {feedbackStats.total_feedback === 0 && (
              <div style={{
                textAlign: "center", 
                padding: "20px",
                color: "var(--text-dim)", 
                fontSize: "13px",
                fontFamily: "JetBrains Mono"
              }}>
                No feedback yet — use the Recommender and rate recommendations
              </div>
            )}

            {/* Top Validated Recommendations */}
            {feedbackStats.top_helpful?.length > 0 && (
              <div>
                <div style={{
                  fontSize: "11px", 
                  color: "var(--text-muted)",
                  fontFamily: "JetBrains Mono", 
                  letterSpacing: "0.05em",
                  marginBottom: "10px",
                  fontWeight: 600
                }}>
                  TOP VALIDATED RECOMMENDATIONS
                </div>
                {feedbackStats.top_helpful.map((f, i) => (
                  <div key={i} style={{
                    display: "flex", 
                    justifyContent: "space-between",
                    alignItems: "center", 
                    padding: "10px 14px",
                    borderRadius: "8px", 
                    marginBottom: "8px",
                    background: "rgba(92,158,46,0.04)",
                    border: "1px solid rgba(92,158,46,0.1)"
                  }}>
                    <div>
                      <span style={{ fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-main)", fontWeight: 600 }}>
                        {f.country}
                      </span>
                      <span style={{
                        fontSize: "11px", 
                        color: "var(--text-muted)",
                        fontFamily: "JetBrains Mono", 
                        marginLeft: "8px"
                      }}>
                        {f.policy_id}
                      </span>
                    </div>
                    <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "#5c9e2e", fontWeight: 600 }}>
                      👍 {f.votes} vote{f.votes > 1 ? "s" : ""}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}