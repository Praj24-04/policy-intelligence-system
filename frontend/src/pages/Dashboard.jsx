import { useEffect, useState } from "react";
import { fetchOverview, fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries } from "../services/api";
import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from "recharts";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

const SECTOR_COLORS  = { 
  "AI Governance": "#a3e635", 
  "Cybersecurity": "#84cc16", 
  "Data Privacy": "#65a30d",
  "Financial Regulation": "#4d7c0f",
  "Healthcare AI": "#3f6212",
  "ESG Policies": "#bef264",
  "POSH Policies": "#d9f99d",
  "IoT and Robotics": "#166534"
};
const REGION_COLORS  = ["#a3e635","#84cc16","#65a30d","#4d7c0f","#3f6212","#bef264","#d9f99d"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const displayLabel = label || payload[0].name;
  return (
    <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 14px", boxShadow: "0 4px 12px rgba(0,0,0,0.08)" }}>
      {displayLabel && <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 2 }}>{displayLabel}</div>}
      <div style={{ fontSize: 15, fontFamily: "Syne", fontWeight: 700, color: "var(--cyan)" }}>
        {payload[0].value}
      </div>
    </div>
  );
};

const getCountryData = (geoName, allCountriesObj) => {
  if (!allCountriesObj) return 0;
  if (allCountriesObj[geoName]) return allCountriesObj[geoName];
  if (geoName === "United States of America" && allCountriesObj["United States"]) return allCountriesObj["United States"];
  if (geoName === "United Kingdom" && allCountriesObj["UK"]) return allCountriesObj["UK"];
  if (geoName === "South Korea" && allCountriesObj["South Korea"]) return allCountriesObj["South Korea"];
  return 0;
};

export default function Dashboard() {
  const [overview,     setOverview]     = useState(null);
  const [sectors,      setSectors]      = useState([]);
  const [regions,      setRegions]      = useState([]);
  const [trends,       setTrends]       = useState([]);
  const [countries,    setCountries]    = useState([]);
  const [allCountries, setAllCountries] = useState({});
  const [loading,      setLoading]      = useState(true);
  const [fetchStatus,  setFetchStatus]  = useState(null);
  const [fetching,     setFetching]     = useState(false);
  const [hoveredRegion, setHoveredRegion] = useState(null);

  useEffect(() => {
    Promise.all([
      fetchOverview(), fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries()
    ]).then(([ov, sec, reg, tr, ctr]) => {
      setOverview(ov);
      setSectors(Object.entries(sec || {}).map(([name, value]) => ({ name, value })));
      setRegions(Object.entries(reg || {}).map(([name, value]) => ({ name, value })));
      setTrends(Object.entries(tr || {}).map(([year, count]) => ({ year: String(year), count })));
      setAllCountries(ctr || {});
      setCountries(Object.entries(ctr || {}).sort((a,b) => b[1]-a[1]).slice(0,8)
        .map(([name, value]) => ({ name: name.replace("European Union","EU").replace("United States","USA").replace("United Kingdom","UK"), value })));
      setLoading(false);
    });

    // Fetch live pipeline status
    fetch("http://localhost:8000/api/fetch/status")
      .then(r => r.json())
      .then(setFetchStatus)
      .catch(() => {});
  }, []);

  const triggerFetch = async () => {
    setFetching(true);
    try {
      await fetch("http://localhost:8000/api/fetch/trigger", { method: "POST" });
      setTimeout(() => {
        fetch("http://localhost:8000/api/fetch/status")
          .then(r => r.json())
          .then(d => { setFetchStatus(d); setFetching(false); });
      }, 5000);
    } catch {
      setFetching(false);
    }
  };

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
         Global policy landscape · {overview ? overview.total_sectors : "8"} sectors · Live data pipeline · ML-powered recommendations
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 24 }}>
        <StatCard label="Total Policies"    value={overview?.total_policies}  sub="Across all sectors"    accent="green" delay={1} />
        <StatCard label="Countries Covered" value={overview?.total_countries} sub="Unique jurisdictions"  accent="green" delay={2} />
        <StatCard label="Sectors Tracked"   value={overview?.total_sectors}   sub="AI · Cyber · Privacy"  accent="green" delay={3} />
        <StatCard label="Regions Mapped"    value={overview?.total_regions}   sub="Global coverage"       accent="green" delay={4} />
      </div>

      {/* Hybrid Intelligence Pipeline Banner */}
      <div className="card fade-up" style={{
        padding: "18px 22px", marginBottom: 16,
        borderColor: "rgba(34,211,238,0.2)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12, marginBottom: 14 }}>
          <div>
            <div style={{
              fontSize: 11, color: "var(--cyan)",
              fontFamily: "JetBrains Mono", marginBottom: 4,
              letterSpacing: "0.5px"
            }}>
              HYBRID INTELLIGENCE PIPELINE
            </div>
            <div style={{ fontSize: 13, color: "var(--text-main)", marginBottom: 2 }}>
              15 Curated Foundational Laws + {fetchStatus?.live_fetched || 0} Live API Policies · Auto-refreshes every 24h
            </div>
          </div>
          <button onClick={triggerFetch} disabled={fetching} style={{
            padding: "8px 18px", borderRadius: 8,
            background: fetching ? "var(--bg-hover)" : "rgba(34,211,238,0.1)",
            border: `1px solid ${fetching ? "var(--border)" : "rgba(34,211,238,0.3)"}`,
            color: fetching ? "var(--text-muted)" : "var(--cyan)",
            fontSize: 12, cursor: fetching ? "not-allowed" : "pointer",
            fontFamily: "JetBrains Mono", transition: "all 0.2s",
            flexShrink: 0,
          }}>
            {fetching ? "⟳ Fetching..." : "⟳ Fetch Live APIs"}
          </button>
        </div>

        {/* Per-source breakdown pills — all live */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {/* Foundational Standards */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 14px", borderRadius: 6,
            background: "var(--bg-hover)", border: "1px solid var(--border)",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#6b7280" }} />
            <span style={{ fontSize: 10, color: "#4b5563", fontFamily: "JetBrains Mono" }}>CURATED</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Foundational Core Standards</span>
            <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600, fontFamily: "JetBrains Mono" }}>
              15
            </span>
          </div>

          {/* EUR-Lex */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 14px", borderRadius: 6,
            background: "rgba(183, 255, 0, 0.06)", border: "1px solid rgba(183, 255, 0, 0.15)",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", animation: "pulse 2s infinite" }} />
            <span style={{ fontSize: 10, color: "#4d7c0f", fontFamily: "JetBrains Mono" }}>LIVE</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>EUR-Lex SPARQL</span>
            <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600, fontFamily: "JetBrains Mono" }}>
              {fetchStatus?.sources?.eurlex?.count || 0}
            </span>
          </div>

          {/* CISA KEV */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 14px", borderRadius: 6,
            background: "rgba(183, 255, 0, 0.06)", border: "1px solid rgba(183, 255, 0, 0.15)",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", animation: "pulse 2s infinite" }} />
            <span style={{ fontSize: 10, color: "#4d7c0f", fontFamily: "JetBrains Mono" }}>LIVE</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>CISA KEV</span>
            <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600, fontFamily: "JetBrains Mono" }}>
              {fetchStatus?.sources?.cisa?.count || 0}
            </span>
          </div>

          {/* Federal Register */}
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 14px", borderRadius: 6,
            background: "rgba(183, 255, 0, 0.06)", border: "1px solid rgba(183, 255, 0, 0.15)",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", animation: "pulse 2s infinite" }} />
            <span style={{ fontSize: 10, color: "#4d7c0f", fontFamily: "JetBrains Mono" }}>LIVE</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>US Federal Register</span>
            <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600, fontFamily: "JetBrains Mono" }}>
              {fetchStatus?.sources?.fedreg?.count || 0}
            </span>
          </div>
        </div>

        {/* Last fetch timestamp */}
        {fetchStatus?.last_fetch && (
          <div style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "JetBrains Mono", marginTop: 10 }}>
            Last fetch: {new Date(fetchStatus.last_fetch).toLocaleString()}
          </div>
        )}
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
                <Tooltip content={<CustomTooltip />} />
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

        {/* World Map */}
        <div className="card fade-up fade-up-3" style={{ padding: "20px 24px", position: "relative" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 }}>
            <div>
              <div style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 14, color: "var(--text-main)", marginBottom: 4 }}>
                Global Policy Map
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Policies mapped by jurisdiction</div>
            </div>
            
            <div style={{ display: "flex", gap: 8 }}>
              {allCountries["International"] > 0 && (
                <div style={{ background: "rgba(183, 255, 0, 0.1)", border: "1px solid rgba(183, 255, 0, 0.2)", padding: "4px 10px", borderRadius: 6 }}>
                  <span style={{ fontSize: 10, color: "#4d7c0f", fontFamily: "JetBrains Mono", marginRight: 6 }}>INTL</span>
                  <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600 }}>{allCountries["International"]}</span>
                </div>
              )}
              {allCountries["European Union"] > 0 && (
                <div style={{ background: "rgba(183, 255, 0, 0.1)", border: "1px solid rgba(183, 255, 0, 0.2)", padding: "4px 10px", borderRadius: 6 }}>
                  <span style={{ fontSize: 10, color: "#4d7c0f", fontFamily: "JetBrains Mono", marginRight: 6 }}>EU</span>
                  <span style={{ fontSize: 12, color: "var(--text-main)", fontWeight: 600 }}>{allCountries["European Union"]}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Map Container */}
          <div style={{ width: "100%", height: 260, marginTop: 16, position: "relative" }}>
            <ComposableMap projection="geoMercator" projectionConfig={{ scale: 145, center: [0, 30] }} width={800} height={400} style={{ width: "100%", height: "100%" }}>
              <Geographies geography="https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json">
                {({ geographies }) => {
                  const maxPolicies = Math.max(...Object.values(allCountries), 1);
                  const colorScale = scaleLinear().domain([1, maxPolicies]).range(["#d9f99d", "#4d7c0f"]);
                  
                  return geographies.map((geo) => {
                    const countryName = geo.properties.name;
                    const policyCount = getCountryData(countryName, allCountries);
                    
                    return (
                      <Geography
                        key={geo.rsmKey}
                        geography={geo}
                        fill={policyCount > 0 ? colorScale(policyCount) : "#64748b"}
                        stroke="#f8fafc"
                        strokeWidth={0.5}
                        style={{
                          default: { outline: "none" },
                          hover: { fill: policyCount > 0 ? "#65a30d" : "#e5e7eb", outline: "none", cursor: "pointer" },
                          pressed: { outline: "none" },
                        }}
                        onMouseEnter={() => {
                          setHoveredRegion({ name: countryName, count: policyCount });
                        }}
                        onMouseLeave={() => setHoveredRegion(null)}
                      />
                    );
                  });
                }}
              </Geographies>
            </ComposableMap>

            {/* Hover Tooltip Overlay */}
            {hoveredRegion && (
              <div style={{
                position: "absolute", bottom: 0, left: 0,
                background: "rgba(15, 23, 42, 0.85)", border: "1px solid rgba(34,211,238,0.3)",
                padding: "8px 12px", borderRadius: 8, pointerEvents: "none",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                backdropFilter: "blur(4px)", zIndex: 10
              }}>
                <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 2 }}>{hoveredRegion.name}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: hoveredRegion.count > 0 ? "var(--cyan)" : "#475569" }} />
                  <span style={{ fontSize: 13, fontFamily: "JetBrains Mono", color: hoveredRegion.count > 0 ? "#e2e8f0" : "#64748b", fontWeight: 600 }}>
                    {hoveredRegion.count} policies
                  </span>
                </div>
              </div>
            )}
          </div>
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