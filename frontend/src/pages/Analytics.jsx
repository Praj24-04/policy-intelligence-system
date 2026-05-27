import { useEffect, useState } from "react";
import { fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries, fetchStatus } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PieChart, Pie, Cell,
  AreaChart, Area, CartesianGrid,
} from "recharts";
import {
  TrendingUp, Globe, BarChart2, Activity,
  ThumbsUp, MessageSquare, Star, Award
} from "lucide-react";

// ── Design Tokens matching Dashboard ─────────────────────────────────────────
const ACCENT       = "#5c9e2e";
const ACCENT_LIGHT = "#a3e635";

const SECTOR_COLORS = {
  "Data Privacy":         "#5c9e2e",
  "Cybersecurity":        "#2563eb",
  "AI Governance":        "#d97706",
  "Financial Regulation": "#6b7280",
  "Healthcare AI":        "#7c3aed",
  "IoT and Robotics":     "#0891b2",
  "ESG Policies":         "#a3e635",
  "POSH Policies":        "#374151",
};

const CHART_COLORS = [
  "#5c9e2e","#a3e635","#2563eb","#7c3aed",
  "#d97706","#0891b2","#6b7280","#374151","#ef4444","#f472b6"
];

const TTStyle = {
  background: "var(--bg-card)",
  border: "1px solid var(--border)",
  borderRadius: "6px",
  fontSize: "12px",
  fontFamily: "DM Sans",
  color: "var(--text-main)",
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

// ── Reusable Card matching Dashboard card style ───────────────────────────────
const ChartCard = ({ title, sub, badge, children, delay = 1, span1 }) => (
  <div
    className={`fade-up fade-up-${delay}`}
    style={{
      background: "var(--bg-card)",
      border: "1px solid var(--border)",
      borderRadius: "8px",
      padding: "22px 28px",
      gridColumn: span1 ? "span 1" : undefined,
    }}
  >
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
      <div>
        <div style={{
          display: "inline-block",
          background: "rgba(92,158,46,0.08)",
          border: "1px solid rgba(92,158,46,0.15)",
          borderRadius: "4px",
          padding: "4px 10px",
          marginBottom: "6px",
        }}>
          <span style={{ fontFamily: "DM Sans", fontWeight: 600, fontSize: "13px", color: ACCENT }}>
            {title}
          </span>
        </div>
        <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>{sub}</div>
      </div>
      {badge && (
        <span style={{
          background: "var(--bg-hover)",
          border: "1px solid var(--border)",
          borderRadius: "4px",
          padding: "3px 8px",
          fontSize: "10px",
          color: "var(--text-muted)",
          fontFamily: "JetBrains Mono",
          flexShrink: 0,
        }}>
          {badge}
        </span>
      )}
    </div>
    {children}
  </div>
);

// ── Stat mini-card (same style as Dashboard stat cards) ──────────────────────
const StatCard = ({ label, value, sub, Icon, delay }) => (
  <div
    className={`fade-up fade-up-${delay}`}
    style={{
      background: "var(--bg-card)",
      border: "1px solid var(--border)",
      borderRadius: "8px",
      padding: "18px 22px",
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
    }}
  >
    <div>
      <span style={{
        fontSize: "11px", fontFamily: "JetBrains Mono",
        color: "var(--text-muted)", letterSpacing: "0.08em",
        textTransform: "uppercase", marginBottom: "10px", display: "block",
      }}>
        {label}
      </span>
      <span style={{
        fontSize: "36px", fontFamily: "DM Sans", fontWeight: 700,
        color: "var(--text-main)", lineHeight: 1,
        marginBottom: "6px", display: "block",
      }}>
        {value ?? "—"}
      </span>
      <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>{sub}</div>
    </div>
    {Icon && <Icon size={16} color={ACCENT} style={{ marginTop: 2, flexShrink: 0 }} />}
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
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
        setCountries(
          Object.entries(ctr || {})
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([name, value]) => ({
              name: name.replace("European Union","EU").replace("United States","USA").replace("United Kingdom","UK"),
              value,
            }))
        );
        setStatus(Object.entries(st || {}).map(([name, value]) => ({ name, value })));
        setLoading(false);
      });

    fetch("http://localhost:8000/api/feedback/summary")
      .then(r => r.json())
      .then(setFeedbackStats)
      .catch(() => {});
  }, []);

  if (loading) return <LoadingSpinner label="Generating analytics..." />;

  const totalPolicies = status.reduce((s, i) => s + i.value, 0);
  const recentTrend   = trends.slice(-3).reduce((s, t) => s + t.count, 0);
  const topSector     = sectors.sort((a, b) => b.value - a.value)[0];
  const topCountry    = countries[0];

  return (
    <div style={{ flex: 1, overflowY: "auto", background: "var(--bg-deep)", minHeight: "100vh" }}>
      <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "32px 40px", width: "100%" }}>

        {/* ── PAGE HEADER ───────────────────────────────────────────────── */}
        <div className="fade-up" style={{ marginBottom: "28px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: ACCENT }} />
            <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
              PREP / INSIGHTS
            </span>
          </div>
          <h1 style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "52px", fontWeight: 700,
            color: "var(--text-main)",
            margin: "0 0 12px 0",
            letterSpacing: "-1.5px", lineHeight: "1.1",
          }}>
            Discover global <span className="half-highlight-custom">trends.</span>
          </h1>
          <p style={{ fontFamily: "DM Sans", fontSize: "14px", color: "var(--text-muted)", margin: 0 }}>
            Aggregated intelligence across {totalPolicies} policies · {sectors.length} sectors · {countries.length} top jurisdictions
          </p>
        </div>

        {/* ── SUMMARY STAT CARDS (same 4-card row as Dashboard) ─────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "16px", marginBottom: "24px" }}>
          <StatCard label="Total Policies"    value={totalPolicies}       sub="Across all statuses"      Icon={BarChart2}  delay={1} />
          <StatCard label="Recent (3yr)"      value={recentTrend}         sub="New policies 2022–2024"   Icon={TrendingUp} delay={2} />
          <StatCard label="Top Sector"        value={topSector?.value}    sub={topSector?.name}          Icon={Activity}   delay={3} />
          <StatCard label="Top Jurisdiction"  value={topCountry?.value}   sub={topCountry?.name}         Icon={Globe}      delay={4} />
        </div>

        {/* ── ROW 1: Top Countries + Sector Donut ───────────────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "20px", marginBottom: "20px" }}>

          {/* Top Countries — horizontal bars with rank numbers */}
          <ChartCard
            title="Top Jurisdictions by Policy Mentions"
            sub="Extracted via spaCy NER from policy content"
            badge="NER Extraction"
            delay={1}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "9px" }}>
              {countries.slice(0, 8).map((c, i) => {
                const max = countries[0]?.value || 1;
                const pct = (c.value / max) * 100;
                return (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{
                      width: "18px", flexShrink: 0,
                      fontSize: "10px", fontFamily: "JetBrains Mono",
                      color: "var(--text-dim)", textAlign: "right",
                    }}>
                      #{i + 1}
                    </span>
                    <div style={{
                      width: "82px", flexShrink: 0,
                      fontSize: "13px", fontFamily: "DM Sans",
                      fontWeight: 500, color: "var(--text-main)",
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                    }}>
                      {c.name}
                    </div>
                    <div style={{
                      flex: 1, height: "5px",
                      background: "var(--bg-hover)",
                      borderRadius: "3px", overflow: "hidden",
                    }}>
                      <div style={{
                        width: `${pct}%`, height: "100%",
                        background: `linear-gradient(90deg, ${ACCENT}, ${ACCENT_LIGHT})`,
                        borderRadius: "3px",
                        transition: "width 0.7s ease",
                      }} />
                    </div>
                    <span style={{
                      width: "32px", textAlign: "right", flexShrink: 0,
                      fontSize: "12px", fontFamily: "JetBrains Mono",
                      color: "var(--text-muted)", fontWeight: 600,
                    }}>
                      {c.value}
                    </span>
                  </div>
                );
              })}
            </div>
          </ChartCard>

          {/* Sector donut + legend */}
          <ChartCard
            title="Sector Distribution"
            sub="Policy breakdown by domain"
            badge={`${sectors.length} sectors`}
            delay={2}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "0px" }}>
              <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                  <Pie
                    data={sectors} dataKey="value" nameKey="name"
                    innerRadius={42} outerRadius={68} paddingAngle={2}
                  >
                    {sectors.map((s, i) => (
                      <Cell key={i} fill={SECTOR_COLORS[s.name] || CHART_COLORS[i % CHART_COLORS.length]} strokeWidth={0} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TTStyle} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px 12px", marginTop: "4px" }}>
                {sectors.map((s, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <div style={{
                      width: "7px", height: "7px", borderRadius: "50%", flexShrink: 0,
                      background: SECTOR_COLORS[s.name] || CHART_COLORS[i % CHART_COLORS.length],
                    }} />
                    <span style={{ fontSize: "11px", fontFamily: "DM Sans", color: "var(--text-muted)", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {s.name}
                    </span>
                    <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600 }}>
                      {s.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </ChartCard>
        </div>

        {/* ── ROW 2: Adoption Timeline (full width) ─────────────────────── */}
        <div style={{ marginBottom: "20px" }}>
          <ChartCard
            title="Global Policy Adoption Timeline"
            sub="Year-wise policy enactment trend — shows accelerating regulatory activity post-2018"
            badge="Adoption trend"
            delay={3}
          >
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={ACCENT} stopOpacity={0.10} />
                    <stop offset="95%" stopColor={ACCENT} stopOpacity={0}    />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" strokeWidth={0.5} />
                <XAxis dataKey="year" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} width={24} />
                <Tooltip contentStyle={TTStyle} />
                <Area
                  type="monotone" dataKey="count"
                  stroke={ACCENT} strokeWidth={2}
                  fillOpacity={1} fill="url(#trendGrad)"
                  dot={{ fill: ACCENT, r: 3, strokeWidth: 0 }}
                  activeDot={{ r: 5, fill: ACCENT_LIGHT }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ── ROW 3: Regional Radar + Policy Status ─────────────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>

          {/* Regional Radar — cleaner */}
          <ChartCard
            title="Regional Policy Distribution"
            sub="Geographic spread across global regions"
            badge="Radar view"
            delay={4}
          >
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart data={regions} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis
                  dataKey="name"
                  tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Sans" }}
                />
                <Radar
                  dataKey="value"
                  stroke={ACCENT} fill={ACCENT} fillOpacity={0.12}
                  strokeWidth={2}
                />
                <Tooltip contentStyle={TTStyle} />
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Policy Status — cleaner cards */}
          <ChartCard
            title="Policy Status Breakdown"
            sub="Active vs Under Review vs other states"
            delay={5}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {status.map((s, i) => {
                const isActive   = s.name === "Active";
                const isReview   = s.name === "Under Review";
                const color      = isActive ? ACCENT : isReview ? "#d97706" : "#6b7280";
                const bgColor    = isActive ? "rgba(92,158,46,0.06)" : isReview ? "rgba(217,119,6,0.06)" : "var(--bg-hover)";
                const borderClr  = isActive ? "rgba(92,158,46,0.2)" : isReview ? "rgba(217,119,6,0.18)" : "var(--border)";
                const total      = status.reduce((a, x) => a + x.value, 0);
                const pct        = total ? Math.round((s.value / total) * 100) : 0;
                return (
                  <div key={i} style={{
                    padding: "14px 18px",
                    borderRadius: "8px",
                    background: bgColor,
                    border: `1px solid ${borderClr}`,
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <span style={{ fontSize: "13px", fontFamily: "DM Sans", fontWeight: 600, color }}>
                        {s.name}
                      </span>
                      <span style={{ fontSize: "24px", fontFamily: "DM Sans", fontWeight: 700, color }}>
                        {s.value}
                      </span>
                    </div>
                    {/* Mini progress bar */}
                    <div style={{ height: "3px", background: "var(--bg-hover)", borderRadius: "2px", overflow: "hidden" }}>
                      <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: "2px" }} />
                    </div>
                    <div style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-dim)", marginTop: "5px" }}>
                      {pct}% of total
                    </div>
                  </div>
                );
              })}
            </div>
          </ChartCard>
        </div>

        {/* ── ROW 4: Feedback Intelligence (conditional) ────────────────── */}
        {feedbackStats && (
          <div className="fade-up" style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            marginBottom: "20px",
          }}>
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
              <div>
                <div style={{
                  display: "inline-block",
                  background: "rgba(92,158,46,0.08)",
                  border: "1px solid rgba(92,158,46,0.15)",
                  borderRadius: "4px", padding: "4px 10px", marginBottom: "6px",
                }}>
                  <span style={{ fontFamily: "DM Sans", fontWeight: 600, fontSize: "13px", color: ACCENT }}>
                    Recommendation Feedback Intelligence
                  </span>
                </div>
                <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                  User validation of ML recommendations
                </div>
              </div>
            </div>

            {/* Feedback Stat Row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "14px", marginBottom: "20px" }}>
              {[
                { label: "Total Feedback", value: feedbackStats.total_feedback, color: "#2563eb",  Icon: MessageSquare },
                { label: "Marked Helpful", value: feedbackStats.positive,        color: ACCENT,     Icon: ThumbsUp      },
                { label: "Accuracy Rate",  value: `${feedbackStats.accuracy_rate}%`, color: "#d97706", Icon: Star      },
              ].map((s, i) => (
                <div key={i} style={{
                  background: "var(--bg-hover)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "16px 18px",
                  display: "flex", alignItems: "center", gap: "14px",
                }}>
                  <div style={{
                    width: "36px", height: "36px", borderRadius: "8px",
                    background: `${s.color}14`, border: `1px solid ${s.color}30`,
                    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                  }}>
                    <s.Icon size={16} color={s.color} />
                  </div>
                  <div>
                    <div style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>
                      {s.label}
                    </div>
                    <div style={{ fontSize: "22px", fontFamily: "DM Sans", fontWeight: 700, color: s.color }}>
                      {s.value}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty state */}
            {feedbackStats.total_feedback === 0 && (
              <div style={{
                textAlign: "center", padding: "24px",
                color: "var(--text-dim)", fontSize: "13px",
                fontFamily: "JetBrains Mono",
                background: "var(--bg-hover)", borderRadius: "8px",
                border: "1px solid var(--border)",
              }}>
                No feedback yet — use the Recommender and rate suggestions
              </div>
            )}

            {/* Top validated recommendations */}
            {feedbackStats.top_helpful?.length > 0 && (
              <div>
                <div style={{
                  fontSize: "10px", fontFamily: "JetBrains Mono",
                  color: "var(--text-muted)", letterSpacing: "0.08em",
                  fontWeight: 600, marginBottom: "10px", textTransform: "uppercase",
                  display: "flex", alignItems: "center", gap: "6px",
                }}>
                  <Award size={11} color={ACCENT} />
                  Top Validated Recommendations
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {feedbackStats.top_helpful.map((f, i) => (
                    <div key={i} style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      padding: "10px 14px", borderRadius: "8px",
                      background: "rgba(92,158,46,0.04)",
                      border: "1px solid rgba(92,158,46,0.10)",
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span style={{
                          width: "20px", height: "20px", borderRadius: "6px",
                          background: "rgba(92,158,46,0.12)", border: "1px solid rgba(92,158,46,0.2)",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: "9px", fontFamily: "JetBrains Mono", fontWeight: 700, color: ACCENT,
                        }}>
                          #{i + 1}
                        </span>
                        <span style={{ fontSize: "13px", fontFamily: "DM Sans", color: "var(--text-main)", fontWeight: 600 }}>
                          {f.country}
                        </span>
                        <span style={{ fontSize: "10px", color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>
                          {f.policy_id}
                        </span>
                      </div>
                      <span style={{ fontSize: "12px", fontFamily: "DM Sans", color: ACCENT, fontWeight: 600 }}>
                        👍 {f.votes} vote{f.votes > 1 ? "s" : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}