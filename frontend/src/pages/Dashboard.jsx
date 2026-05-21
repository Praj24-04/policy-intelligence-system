import { useEffect, useState } from "react";
import { fetchOverview, fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries } from "../services/api";
import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid, AreaChart, Area
} from "recharts";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

const SECTOR_COLORS  = { 
  "AI Governance": "#A3E635", 
  "Cybersecurity": "#78716C", 
  "Data Privacy": "#0C0A09",
  "Financial Regulation": "#E7E5E4",
  "Healthcare AI": "#BEF264",
  "ESG Policies": "#D6D3D1",
  "POSH Policies": "#A8A29E",
  "IoT and Robotics": "#57534E"
};
const REGION_COLORS  = ["#A3E635", "#78716C", "#0C0A09", "#E7E5E4", "#BEF264", "#D6D3D1"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const displayLabel = label || payload[0].name;
  return (
    <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 14px", boxShadow: "0 4px 12px rgba(0,0,0,0.08)" }}>
      {displayLabel && <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 2 }}>{displayLabel}</div>}
      <div style={{ fontSize: 15, fontFamily: "Inter", fontWeight: 700, color: "var(--cyan)" }}>
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
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "#ffffff",
      minHeight: "100vh"
    }}>
      <div style={{
        maxWidth: "1280px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>
        {/* Header */}
      <div className="fade-up" style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 12 }}>
          <span style={{ color: "var(--cyan)", marginRight: 8 }}>■</span> WORK / OVERVIEW
        </div>
        <h1 style={{ fontFamily: "Inter", fontSize: 44, fontWeight: 800, color: "var(--text-main)", letterSpacing: "-1px", marginBottom: 16 }}>
          Global policy <span className="half-highlight">landscape.</span>
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
         {overview ? overview.total_sectors : "8"} sectors · Live data pipeline · ML-powered recommendations
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
      <div className="card fade-up pipeline-banner-themed" style={{
        padding: "20px 24px", marginBottom: 24,
        borderColor: "rgba(163, 230, 53, 0.12)",
        background: "rgba(163, 230, 53, 0.02)",
        borderRadius: "12px",
        borderTop: "1.5px solid var(--cyan)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16, marginBottom: 14 }}>
          <div>
            <div style={{
              fontSize: "10px", color: "var(--stat-label)",
              fontFamily: "'JetBrains Mono', monospace", marginBottom: 4,
              letterSpacing: "0.08em", fontWeight: 600
            }}>
              HYBRID INTELLIGENCE PIPELINE
            </div>
            <div style={{ fontSize: 13, color: "var(--text-main)", fontWeight: 500 }}>
              15 Curated Foundational Laws + {fetchStatus?.live_fetched || 0} Live API Policies · Auto-refreshes every 24h
            </div>
          </div>
          
          {/* Issue 7: High-contrast CTA Fetch Button */}
          <button 
            onClick={triggerFetch} 
            disabled={fetching} 
            className="btn-fetch-themed"
            style={{
              padding: "8px 18px", 
              borderRadius: "4px",
              background: "var(--cyan)",
              border: "none",
              color: "#0f1a00",
              fontSize: "12px", 
              cursor: fetching ? "not-allowed" : "pointer",
              fontFamily: "'JetBrains Mono', monospace", 
              fontWeight: 600,
              letterSpacing: "0.04em",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              boxShadow: "0 2px 8px rgba(163, 230, 53, 0.2)",
              transition: "all 0.2s"
            }}
          >
            <span className={fetching ? "spin-icon" : ""} style={{ display: "inline-block" }}>
              ↻
            </span>
            {fetching ? "FETCHING..." : "FETCH LIVE"}
          </button>
        </div>

        {/* Issue 2: Pill-shaped live indicators */}
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center", marginTop: "12px" }}>
          {/* Curated core standards */}
          <div className="pipeline-pill-themed curated">
            <span className="dot static-dot" />
            <span className="label">Curated · 15</span>
          </div>

          {/* EUR-Lex */}
          <div className="pipeline-pill-themed live">
            <span className="dot pulsing-dot" />
            <span className="label">EUR-Lex · {fetchStatus?.sources?.eurlex?.count || 0}</span>
          </div>

          {/* CISA KEV */}
          <div className="pipeline-pill-themed live">
            <span className="dot pulsing-dot" />
            <span className="label">CISA KEV · {fetchStatus?.sources?.cisa?.count || 0}</span>
          </div>

          {/* Federal Register */}
          <div className="pipeline-pill-themed live">
            <span className="dot pulsing-dot" />
            <span className="label">US Fed Register · {fetchStatus?.sources?.fedreg?.count || 0}</span>
          </div>

          {/* Separation line & Fetch Timestamp */}
          {fetchStatus?.last_fetch && (
            <div style={{ 
              marginLeft: "auto",
              fontSize: "10px", 
              color: "var(--stat-sub)", 
              fontFamily: "'JetBrains Mono', monospace" 
            }}>
              Last fetch: {new Date(fetchStatus.last_fetch).toLocaleDateString()} {new Date(fetchStatus.last_fetch).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </div>

      {/* Charts Row 1 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
        {/* Sector Distribution */}
        <div className="fade-up fade-up-2 chart-card-themed">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 15, color: "var(--stat-label)", letterSpacing: "-0.3px" }}>
                Sector Distribution
              </div>
              <div style={{ fontSize: 11, color: "var(--stat-sub)", marginTop: 2, fontWeight: 500 }}>
                Policy breakdown by domain
              </div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <span style={{ background: "rgba(163, 230, 53, 0.1)", border: "1px solid rgba(163, 230, 53, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                {sectors.length} sectors
              </span>
              <span style={{ background: "rgba(125, 211, 252, 0.1)", border: "1px solid rgba(125, 211, 252, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "#38bdf8", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                {overview?.total_policies || 0} total
              </span>
            </div>
          </div>
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

        {/* Global Policy Map */}
        <div className="fade-up fade-up-3 chart-card-themed" style={{ position: "relative" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 15, color: "var(--stat-label)", letterSpacing: "-0.3px" }}>
                Global Policy Map
              </div>
              <div style={{ fontSize: 11, color: "var(--stat-sub)", marginTop: 2, fontWeight: 500 }}>
                Policies mapped by jurisdiction
              </div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              {allCountries["International"] > 0 && (
                <span style={{ background: "rgba(163, 230, 53, 0.1)", border: "1px solid rgba(163, 230, 53, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                  INTL · {allCountries["International"]}
                </span>
              )}
              {allCountries["European Union"] > 0 && (
                <span style={{ background: "rgba(163, 230, 53, 0.1)", border: "1px solid rgba(163, 230, 53, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                  EU · {allCountries["European Union"]}
                </span>
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
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        {/* Year Trend with subtle Area gradient */}
        <div className="fade-up fade-up-4 chart-card-themed">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 15, color: "var(--stat-label)", letterSpacing: "-0.3px" }}>
                Policy Adoption Timeline
              </div>
              <div style={{ fontSize: 11, color: "var(--stat-sub)", marginTop: 2, fontWeight: 500 }}>
                Policies enacted by year
              </div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <span style={{ background: "rgba(163, 230, 53, 0.1)", border: "1px solid rgba(163, 230, 53, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                Adoption trend
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={150}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--cyan)" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="var(--cyan)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(163, 230, 53, 0.08)" strokeDasharray="3 3" strokeWidth={0.5} />
              <XAxis dataKey="year" tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#475569", fontSize: 10 }} axisLine={false} tickLine={false} width={20} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="count" stroke="var(--cyan)" strokeWidth={2} fillOpacity={1} fill="url(#areaGradient)" dot={{ fill: "var(--cyan)", r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Top Countries with premium rounded bars */}
        <div className="fade-up fade-up-5 chart-card-themed">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 15, color: "var(--stat-label)", letterSpacing: "-0.3px" }}>
                Top Jurisdictions by NER
              </div>
              <div style={{ fontSize: 11, color: "var(--stat-sub)", marginTop: 2, fontWeight: 500 }}>
                Countries extracted via spaCy NLP
              </div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <span style={{ background: "rgba(163, 230, 53, 0.1)", border: "1px solid rgba(163, 230, 53, 0.2)", borderRadius: "4px", padding: "2px 6px", fontSize: "10px", color: "var(--stat-label)", fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                NER Extraction
              </span>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {countries.map((c, i) => {
              const max = countries[0]?.value || 1;
              const pct = (c.value / max) * 100;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 60, fontSize: 11, color: "var(--text-muted)", fontFamily: "JetBrains Mono", flexShrink: 0 }}>
                    {c.name}
                  </div>
                  <div style={{ flex: 1, height: 10, background: "var(--border)", borderRadius: 10, overflow: "hidden" }}>
                    <div style={{ 
                      width: `${pct}%`, 
                      height: "100%", 
                      background: "linear-gradient(90deg, var(--cyan) 0%, #7db800 100%)", 
                      borderRadius: 10, 
                      transition: "width 0.6s ease" 
                    }} />
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
    </div>
  );
}