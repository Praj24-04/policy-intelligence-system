import { useEffect, useState } from "react";
import { fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries, fetchStatus } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, Cell
} from "recharts";

const COLORS = ["#22d3ee","#818cf8","#34d399","#f59e0b","#f43f5e","#a78bfa","#fb923c","#38bdf8"];

export default function Analytics() {
  const [sectors,   setSectors]   = useState([]);
  const [regions,   setRegions]   = useState([]);
  const [trends,    setTrends]    = useState([]);
  const [countries, setCountries] = useState([]);
  const [status,    setStatus]    = useState([]);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries(), fetchStatus()])
      .then(([sec, reg, tr, ctr, st]) => {
        setSectors(Object.entries(sec).map(([name, value]) => ({ name, value })));
        setRegions(Object.entries(reg).map(([name, value]) => ({ name, value })));
        setTrends(Object.entries(tr).map(([year, count]) => ({ year: String(year), count })));
        setCountries(Object.entries(ctr).sort((a,b) => b[1]-a[1]).slice(0,10).map(([name, value]) => ({ name, value })));
        setStatus(Object.entries(st).map(([name, value]) => ({ name, value })));
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingSpinner label="Generating analytics..." />;

  const ChartCard = ({ title, sub, children, delay = 1 }) => (
    <div className={`card fade-up fade-up-${delay}`} style={{ padding: "20px 24px" }}>
      <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 2 }}>{title}</div>
      <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>{sub}</div>
      {children}
    </div>
  );

  const TTStyle = { background: "#111827", border: "1px solid #1e2a3a", borderRadius: 8, fontSize: 12 };

  return (
    <div style={{ padding: "28px 32px" }}>
      <div className="fade-up" style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ width: 3, height: 22, background: "#f59e0b", borderRadius: 2 }} />
          <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
            Analytics & Insights
          </h1>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
          Aggregated view of global policy intelligence data
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Country bar */}
        <ChartCard title="Top Countries by Policy Mentions" sub="Extracted via spaCy NER from policy content" delay={1}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={countries} layout="vertical" barSize={10}>
              <XAxis type="number" tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={110} />
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
              <PolarGrid stroke="#1e2a3a" />
              <PolarAngleAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 10 }} />
              <Radar dataKey="value" stroke="var(--cyan)" fill="var(--cyan)" fillOpacity={0.15} strokeWidth={2} />
              <Tooltip contentStyle={TTStyle} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
        {/* Year trend */}
        <ChartCard title="Global Policy Adoption Timeline" sub="Year-wise policy enactment trend" delay={3}>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={trends} barSize={24}>
              <XAxis dataKey="year" tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} width={20} />
              <Tooltip contentStyle={TTStyle} />
              <Bar dataKey="count" radius={[4,4,0,0]}>
                {trends.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Status */}
        <ChartCard title="Policy Status" sub="Active vs Under Review" delay={4}>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 8 }}>
            {status.map((s, i) => (
              <div key={i} style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "12px 16px", borderRadius: 10,
                background: s.name === "Active" ? "rgba(16,185,129,0.08)" : "rgba(245,158,11,0.08)",
                border: `1px solid ${s.name === "Active" ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"}`,
              }}>
                <span style={{ fontSize: 13, color: s.name === "Active" ? "#10b981" : "#f59e0b" }}>{s.name}</span>
                <span style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 28, color: s.name === "Active" ? "#10b981" : "#f59e0b" }}>
                  {s.value}
                </span>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>
    </div>
  );
}