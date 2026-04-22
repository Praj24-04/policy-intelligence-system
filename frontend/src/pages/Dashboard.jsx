import { useEffect, useState } from "react";
import { fetchOverview, fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries } from "../services/api";
import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from "recharts";

const SECTOR_COLORS  = { "AI Governance": "#818cf8", "Cybersecurity": "#22d3ee", "Data Privacy": "#34d399" };
const REGION_COLORS  = ["#22d3ee","#818cf8","#34d399","#f59e0b","#f43f5e","#a78bfa","#fb923c"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#111827", border: "1px solid #1e2a3a", borderRadius: 8, padding: "8px 14px" }}>
      <div style={{ fontSize: 12, color: "#64748b", marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 15, fontFamily: "Syne", fontWeight: 700, color: "#22d3ee" }}>
        {payload[0].value}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [overview, setOverview]   = useState(null);
  const [sectors,  setSectors]    = useState([]);
  const [regions,  setRegions]    = useState([]);
  const [trends,   setTrends]     = useState([]);
  const [countries,setCountries]  = useState([]);
  const [loading,  setLoading]    = useState(true);

  useEffect(() => {
    Promise.all([
      fetchOverview(), fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries()
    ]).then(([ov, sec, reg, tr, ctr]) => {
      setOverview(ov);
      setSectors(Object.entries(sec).map(([name, value]) => ({ name, value })));
      setRegions(Object.entries(reg).map(([name, value]) => ({ name, value })));
      setTrends(Object.entries(tr).map(([year, count]) => ({ year: String(year), count })));
      setCountries(Object.entries(ctr).sort((a,b) => b[1]-a[1]).slice(0,8)
        .map(([name, value]) => ({ name: name.replace("European Union","EU").replace("United States","USA").replace("United Kingdom","UK"), value })));
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner label="Loading intelligence data..." />;

  return (
    <div style={{ padding: "28px 32px" }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ width: 3, height: 22, background: "var(--cyan)", borderRadius: 2 }} />
          <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
            Intelligence Dashboard
          </h1>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
          Global policy landscape · 3 sectors · Real-time NLP analysis
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 24 }}>
        <StatCard label="Total Policies"    value={overview?.total_policies}  sub="Across all sectors"    accent="cyan"   delay={1} />
        <StatCard label="Countries Covered" value={overview?.total_countries} sub="Unique jurisdictions"  accent="indigo" delay={2} />
        <StatCard label="Sectors Tracked"   value={overview?.total_sectors}   sub="AI · Cyber · Privacy"  accent="green"  delay={3} />
        <StatCard label="Regions Mapped"    value={overview?.total_regions}   sub="Global coverage"       accent="amber"  delay={4} />
      </div>

      {/* Charts Row 1 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Sector Pie */}
        <div className="card fade-up fade-up-2" style={{ padding: "20px 24px" }}>
          <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 4 }}>
            Sector Distribution
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Policy breakdown by domain</div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <ResponsiveContainer width="50%" height={160}>
              <PieChart>
                <Pie data={sectors} dataKey="value" nameKey="name" innerRadius={45} outerRadius={70}>
                  {sectors.map((s, i) => (
                    <Cell key={i} fill={SECTOR_COLORS[s.name] || "#64748b"} strokeWidth={0} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e2a3a", borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1 }}>
              {sectors.map((s, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: SECTOR_COLORS[s.name] || "#64748b", flexShrink: 0 }} />
                  <div style={{ flex: 1, fontSize: 12, color: "var(--text-muted)" }}>{s.name}</div>
                  <div style={{ fontFamily: "JetBrains Mono", fontSize: 13, color: "var(--text-main)", fontWeight: 500 }}>{s.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Region Bar */}
        <div className="card fade-up fade-up-3" style={{ padding: "20px 24px" }}>
          <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 4 }}>
            Regional Coverage
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Policies per geographic region</div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={regions} barSize={18}>
              <XAxis dataKey="name" tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} width={20} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {regions.map((_, i) => <Cell key={i} fill={REGION_COLORS[i % REGION_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Year Trend */}
        <div className="card fade-up fade-up-4" style={{ padding: "20px 24px" }}>
          <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 4 }}>
            Policy Adoption Timeline
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Policies enacted by year</div>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={trends}>
              <CartesianGrid stroke="#1e2a3a" strokeDasharray="3 3" />
              <XAxis dataKey="year" tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} width={20} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="count" stroke="var(--cyan)" strokeWidth={2} dot={{ fill: "var(--cyan)", r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Countries */}
        <div className="card fade-up fade-up-5" style={{ padding: "20px 24px" }}>
          <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 4 }}>
            Top Jurisdictions by NER
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}>Countries extracted via spaCy NLP</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {countries.map((c, i) => {
              const max = countries[0]?.value || 1;
              const pct = (c.value / max) * 100;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 60, fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", flexShrink: 0 }}>
                    {c.name}
                  </div>
                  <div style={{ flex: 1, height: 4, background: "var(--border)", borderRadius: 2 }}>
                    <div style={{ width: `${pct}%`, height: "100%", background: "var(--cyan)", borderRadius: 2, transition: "width 0.6s ease" }} />
                  </div>
                  <div style={{ width: 20, fontSize: 11, color: "var(--text-main)", fontFamily: "JetBrains Mono", textAlign: "right" }}>
                    {c.value}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}