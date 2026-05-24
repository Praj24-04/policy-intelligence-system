import { useEffect, useState } from "react";
import { fetchOverview, fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { FileText, Globe, Layers, Map, RotateCw } from "lucide-react";
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid
} from "recharts";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";

const SECTOR_COLORS = {
  "Data Privacy":         "#5c9e2e",  // accent green
  "Cybersecurity":        "#2563eb",  // blue
  "AI Governance":        "#d97706",  // amber
  "Financial Regulation": "#6b7280",  // slate
  "Healthcare AI":        "#7c3aed",  // purple
  "IoT and Robotics":     "#0891b2",  // cyan
  "ESG Policies":         "#d1d5db",  // light gray
  "POSH Policies":        "#374151"   // dark gray
};

const globalTooltipStyle = {
  contentStyle: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    fontSize: '12px',
    fontFamily: 'DM Sans',
    color: 'var(--text-main)',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
  },
  labelStyle: {
    fontSize: '11px',
    fontFamily: 'JetBrains Mono',
    color: 'var(--text-muted)'
  },
  cursor: { stroke: 'var(--border)', strokeWidth: 1 }
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
  const [trends,       setTrends]       = useState([]);
  const [countries,    setCountries]    = useState([]);
  const [allCountries, setAllCountries] = useState({});
  const [loading,      setLoading]      = useState(true);
  const [fetchStatus,  setFetchStatus]  = useState(null);
  const [fetching,     setFetching]     = useState(false);
  const [hoveredRegion, setHoveredRegion] = useState(null);
  const [fetchHover,   setFetchHover]   = useState(false);

  useEffect(() => {
    Promise.all([
      fetchOverview(), fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries()
    ]).then(([ov, sec, reg, tr, ctr]) => {
      setOverview(ov);
      setSectors(Object.entries(sec || {}).map(([name, value]) => ({ name, value })));
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
              WORK / OVERVIEW
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
            Global policy <span className="half-highlight-custom">landscape.</span>
          </h1>
          <p style={{ fontFamily: "DM Sans", fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
            {overview ? overview.total_sectors : "8"} sectors · Live data pipeline · ML-powered recommendations
          </p>
        </div>

        {/* Stat Cards Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
          {[
            { label: "Total Policies", value: overview?.total_policies, sub: "Across all sectors", Icon: FileText, delay: 1 },
            { label: "Countries Covered", value: overview?.total_countries, sub: "Unique jurisdictions", Icon: Globe, delay: 2 },
            { label: "Sectors Tracked", value: overview?.total_sectors, sub: "AI · Cyber · Privacy", Icon: Layers, delay: 3 },
            { label: "Regions Mapped", value: overview?.total_regions, sub: "Global coverage", Icon: Map, delay: 4 }
          ].map((card, idx) => {
            const IconComponent = card.Icon;
            return (
              <div 
                key={idx} 
                className={`fade-up fade-up-${card.delay}`}
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "18px 22px",
                  boxShadow: "none",
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between"
                }}
              >
                <div>
                  <span style={{
                    fontSize: "11px",
                    fontFamily: "JetBrains Mono",
                    color: "var(--text-muted)",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    marginBottom: "10px",
                    display: "block"
                  }}>
                    {card.label}
                  </span>
                  <span style={{
                    fontSize: "36px",
                    fontFamily: "DM Sans",
                    fontWeight: 700,
                    color: "var(--text-main)",
                    lineHeight: 1,
                    marginBottom: "6px",
                    display: "block"
                  }}>
                    {card.value ?? "—"}
                  </span>
                  <div style={{
                    fontSize: "12px",
                    fontFamily: "DM Sans",
                    color: "var(--text-muted)"
                  }}>
                    {card.sub}
                  </div>
                </div>
                <IconComponent size={16} color="#5c9e2e" style={{ marginTop: "2px", flexShrink: 0 }} />
              </div>
            );
          })}
        </div>

        {/* Hybrid Intelligence Pipeline Banner */}
        <div className="card fade-up" style={{
          background: "var(--bg-hover)",
          border: "1px solid var(--border)",
          borderRadius: "8px",
          padding: "10px 16px",
          marginBottom: "24px",
          display: "flex",
          alignItems: "center",
          gap: "16px",
          flexWrap: "nowrap",
          overflowX: "auto",
          minHeight: "44px"
        }}>
          {/* LEFT — Label block */}
          <div style={{
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}>
            <span style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "#5c9e2e",
              flexShrink: 0
            }} />
            <span style={{
              fontSize: "9px",
              fontFamily: "JetBrains Mono",
              color: "#5c9e2e",
              letterSpacing: "0.14em",
              fontWeight: 600,
              whiteSpace: "nowrap"
            }}>
              HYBRID INTELLIGENCE PIPELINE
            </span>
          </div>
          
          {/* THIN DIVIDER after label */}
          <div style={{
            width: "1px",
            height: "16px",
            background: "var(--border)",
            flexShrink: 0
          }} />

          {/* CENTER — Single line description */}
          <div style={{
            flexShrink: 0,
            fontSize: "11px",
            fontFamily: "DM Sans",
            color: "var(--text-muted)",
            whiteSpace: "nowrap"
          }}>
            15 curated · {fetchStatus?.live_fetched || 0} live · refreshes every 24h
          </div>

          {/* THIN DIVIDER */}
          <div style={{
            width: "1px",
            height: "16px",
            background: "var(--border)",
            flexShrink: 0
          }} />

          {/* SOURCE PILLS row */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            flexShrink: 0
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "20px",
              padding: "3px 10px",
              whiteSpace: "nowrap"
            }}>
              <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "var(--text-dim)" }} />
              <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                Curated · 15
              </span>
            </div>

            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "20px",
              padding: "3px 10px",
              whiteSpace: "nowrap"
            }}>
              <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#5c9e2e" }} />
              <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                EUR-Lex · {fetchStatus?.sources?.eurlex?.count || 0}
              </span>
            </div>

            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "20px",
              padding: "3px 10px",
              whiteSpace: "nowrap"
            }}>
              <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#5c9e2e" }} />
              <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                CISA KEV · {fetchStatus?.sources?.cisa?.count || 0}
              </span>
            </div>

            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              borderRadius: "20px",
              padding: "3px 10px",
              whiteSpace: "nowrap"
            }}>
              <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: "#5c9e2e" }} />
              <span style={{ fontSize: "10px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                US Fed Register · {fetchStatus?.sources?.fedreg?.count || 0}
              </span>
            </div>
          </div>

          {/* RIGHT — Timestamp + Button */}
          <div style={{
            marginLeft: "auto",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            flexShrink: 0
          }}>
            {fetchStatus?.last_fetch && (
              <span style={{
                fontSize: "10px",
                fontFamily: "JetBrains Mono",
                color: "var(--text-dim)",
                whiteSpace: "nowrap"
              }}>
                Last fetch: {new Date(fetchStatus.last_fetch).toLocaleDateString()} {new Date(fetchStatus.last_fetch).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}

            <button 
              onClick={triggerFetch} 
              disabled={fetching} 
              onMouseEnter={() => setFetchHover(true)}
              onMouseLeave={() => setFetchHover(false)}
              style={{
                background: fetchHover ? "var(--border-lit)" : "var(--text-main)",
                color: "var(--bg-card)",
                border: "none",
                borderRadius: "6px",
                padding: "6px 12px",
                fontSize: "11px",
                fontFamily: "DM Sans",
                fontWeight: 600,
                cursor: fetching ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "5px",
                whiteSpace: "nowrap",
                flexShrink: 0,
                transition: "all 0.15s ease"
              }}
            >
              <RotateCw size={11} color="var(--bg-card)" className={fetching ? "spin-icon" : ""} />
              {fetching ? "FETCHING..." : "FETCH LIVE"}
            </button>
          </div>
        </div>

        {/* Charts Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "0px" }}>
          
          {/* Sector Distribution */}
          <div className="fade-up fade-up-2" style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            boxShadow: "none",
            marginBottom: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
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
                    Sector Distribution
                  </span>
                </div>
                <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                  Policy breakdown by domain
                </div>
              </div>
              <div style={{ display: "flex", gap: "6px" }}>
                <span style={{ 
                  background: "var(--bg-hover)", 
                  border: "1px solid var(--border)", 
                  borderRadius: "4px", 
                  padding: "3px 8px", 
                  fontSize: "10px", 
                  color: "var(--text-muted)", 
                  fontFamily: "JetBrains Mono" 
                }}>
                  {sectors.length} sectors
                </span>
                <span style={{ 
                  background: "var(--bg-hover)", 
                  border: "1px solid var(--border)", 
                  borderRadius: "4px", 
                  padding: "3px 8px", 
                  fontSize: "10px", 
                  color: "var(--text-muted)", 
                  fontFamily: "JetBrains Mono" 
                }}>
                  {overview?.total_policies || 0} total
                </span>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <ResponsiveContainer width="50%" height={220}>
                <PieChart>
                  <Pie data={sectors} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85}>
                    {sectors.map((s, i) => (
                      <Cell key={i} fill={SECTOR_COLORS[s.name] || "#64748b"} strokeWidth={0} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={globalTooltipStyle.contentStyle} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ flex: 1 }}>
                {sectors.map((s, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
                    <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: SECTOR_COLORS[s.name] || "#64748b", flexShrink: 0 }} />
                    <div style={{ flex: 1, fontSize: "14px", fontFamily: "DM Sans", color: "var(--text-main)" }}>{s.name}</div>
                    <div style={{ fontFamily: "JetBrains Mono", fontSize: "14px", color: "var(--text-main)", fontWeight: 600 }}>{s.value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Global Policy Map */}
          <div className="fade-up fade-up-3" style={{ 
            position: "relative",
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            boxShadow: "none",
            marginBottom: "20px",
            display: "flex",
            flexDirection: "column"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
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
                    Global Policy Map
                  </span>
                </div>
                <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                  Policies mapped by jurisdiction
                </div>
              </div>
              <div style={{ display: "flex", gap: "6px" }}>
                {allCountries["International"] > 0 && (
                  <span style={{ 
                    background: "var(--bg-hover)", 
                    border: "1px solid var(--border)", 
                    borderRadius: "4px", 
                    padding: "3px 8px", 
                    fontSize: "10px", 
                    color: "var(--text-muted)", 
                    fontFamily: "JetBrains Mono" 
                  }}>
                    INTL · {allCountries["International"]}
                  </span>
                )}
                {allCountries["European Union"] > 0 && (
                  <span style={{ 
                    background: "var(--bg-hover)", 
                    border: "1px solid var(--border)", 
                    borderRadius: "4px", 
                    padding: "3px 8px", 
                    fontSize: "10px", 
                    color: "var(--text-muted)", 
                    fontFamily: "JetBrains Mono" 
                  }}>
                    EU · {allCountries["European Union"]}
                  </span>
                )}
              </div>
            </div>
            
            <div style={{ width: "100%", height: "280px", position: "relative", marginTop: "10px" }}>
              <ComposableMap projection="geoMercator" projectionConfig={{ scale: 145, center: [0, 30] }} width={800} height={380} style={{ width: "100%", height: "100%" }}>
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
                          fill={policyCount > 0 ? colorScale(policyCount) : "var(--bg-hover)"}
                          stroke="var(--bg-card)"
                          strokeWidth={0.5}
                          style={{
                             default: { outline: "none" },
                             hover: { fill: policyCount > 0 ? "#65a30d" : "var(--border-lit)", outline: "none", cursor: "pointer" },
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

              {hoveredRegion && (
                <div style={{
                  position: "absolute", bottom: -10, left: 0,
                  background: "var(--bg-card)", border: "1px solid var(--border)",
                  padding: "8px 12px", borderRadius: 8, pointerEvents: "none",
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
                  zIndex: 10
                }}>
                  <div style={{ fontSize: 11, fontFamily: "DM Sans", color: "var(--text-muted)", marginBottom: 2 }}>{hoveredRegion.name}</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: hoveredRegion.count > 0 ? "#5c9e2e" : "var(--text-dim)" }} />
                    <span style={{ fontSize: 12, fontFamily: "JetBrains Mono", color: "var(--text-main)", fontWeight: 600 }}>
                      {hoveredRegion.count} policies
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Policy Adoption Timeline */}
          <div className="fade-up fade-up-4" style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            boxShadow: "none",
            marginBottom: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
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
                    Policy Adoption Timeline
                  </span>
                </div>
                <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                  Policies enacted by year
                </div>
              </div>
              <div style={{ display: "flex", gap: "6px" }}>
                <span style={{ 
                  background: "var(--bg-hover)", 
                  border: "1px solid var(--border)", 
                  borderRadius: "4px", 
                  padding: "3px 8px", 
                  fontSize: "10px", 
                  color: "var(--text-muted)", 
                  fontFamily: "JetBrains Mono" 
                }}>
                  Adoption trend
                </span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#5c9e2e" stopOpacity={0.06}/>
                    <stop offset="95%" stopColor="#5c9e2e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" strokeWidth={0.5} />
                <XAxis dataKey="year" tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} width={20} />
                <Tooltip contentStyle={globalTooltipStyle.contentStyle} labelStyle={globalTooltipStyle.labelStyle} cursor={globalTooltipStyle.cursor} />
                <Area 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#5c9e2e" 
                  strokeWidth={2} 
                  fillOpacity={1} 
                  fill="url(#areaGradient)" 
                  dot={{ fill: "#5c9e2e", r: 3 }} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Top Jurisdictions by NER */}
          <div className="fade-up fade-up-5" style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            boxShadow: "none",
            marginBottom: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
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
                    Top Jurisdictions by NER
                  </span>
                </div>
                <div style={{ fontSize: "12px", fontFamily: "DM Sans", color: "var(--text-muted)" }}>
                  Countries extracted via spaCy NLP
                </div>
              </div>
              <div style={{ display: "flex", gap: "6px" }}>
                <span style={{ 
                  background: "var(--bg-hover)", 
                  border: "1px solid var(--border)", 
                  borderRadius: "4px", 
                  padding: "3px 8px", 
                  fontSize: "10px", 
                  color: "var(--text-muted)", 
                  fontFamily: "JetBrains Mono" 
                }}>
                  NER Extraction
                </span>
              </div>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "0px" }}>
              {countries.map((c, i) => {
                const max = countries[0]?.value || 1;
                const pct = (c.value / max) * 100;
                return (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
                    <div style={{ 
                      fontSize: "14px", 
                      fontFamily: "DM Sans", 
                      fontWeight: 500, 
                      color: "var(--text-main)", 
                      width: "90px", 
                      flexShrink: 0 
                    }}>
                      {c.name}
                    </div>
                    <div style={{ 
                      flex: 1, 
                      height: "4px", 
                      background: "var(--bg-hover)", 
                      borderRadius: "2px", 
                      position: "relative",
                      overflow: "hidden"
                    }}>
                      <div style={{ 
                        width: `${pct}%`, 
                        height: "100%", 
                        background: "#5c9e2e", 
                        borderRadius: "2px", 
                        transition: "width 0.6s ease" 
                      }} />
                    </div>
                    <div style={{ 
                      fontSize: "14px", 
                      fontFamily: "JetBrains Mono", 
                      color: "var(--text-muted)", 
                      width: "36px", 
                      textAlign: "right" 
                    }}>
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