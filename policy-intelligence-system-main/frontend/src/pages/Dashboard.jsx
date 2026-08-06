import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { fetchOverview, fetchSectorDist, fetchRegionDist, fetchTrends, fetchCountries, fetchPolicies, BASE } from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";
import { FileText, Globe, Layers, Map, RotateCw, X, Search } from "lucide-react";
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid
} from "recharts";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";
import { scaleLinear } from "d3-scale";
import { geoPath } from "d3-geo";

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

const COUNTRY_ALIASES = {
  "us": "United States of America",
  "usa": "United States of America",
  "united states": "United States of America",
  "uk": "United Kingdom",
  "gbr": "United Kingdom",
  "gb": "United Kingdom",
  "ind": "India",
  "in": "India",
  "deu": "Germany",
  "de": "Germany",
  "fra": "France",
  "fr": "France",
  "can": "Canada",
  "ca": "Canada",
  "aus": "Australia",
  "au": "Australia",
  "jpn": "Japan",
  "jp": "Japan",
  "kor": "South Korea",
  "kr": "South Korea",
  "chn": "China",
  "cn": "China",
  "bra": "Brazil",
  "br": "Brazil",
  "sg": "Singapore",
  "sgp": "Singapore"
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [overview,     setOverview]     = useState(null);
  const [sectors,      setSectors]      = useState([]);
  const [trends,       setTrends]       = useState([]);
  const [countries,    setCountries]    = useState([]);
  const [allCountries, setAllCountries] = useState({});
  const [loading,      setLoading]      = useState(true);
  const [fetchStatus,  setFetchStatus]  = useState(null);
  const [fetching,     setFetching]     = useState(false);
  const [progress,     setProgress]     = useState({ status: "idle" });
  const [hoveredRegion, setHoveredRegion] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [fetchHover,   setFetchHover]   = useState(false);

  // Map drill-down states
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countryPolicies, setCountryPolicies] = useState([]);
  const [loadingPolicies, setLoadingPolicies] = useState(false);

  // Map search & zoom states
  const [mapSearch, setMapSearch] = useState("");
  const [mapPosition, setMapPosition] = useState({ center: [0, 30], zoom: 1 });
  const [focusedCountryName, setFocusedCountryName] = useState(null);
  const [showMapSuggestions, setShowMapSuggestions] = useState(false);
  const geographiesListRef = useRef([]);

  // Close sidebar on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setSelectedCountry(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleRegionClick = (geoName) => {
    let targetCountry = geoName;
    if (geoName === "United States of America") targetCountry = "United States";
    if (geoName === "United Kingdom") targetCountry = "UK";
    if (geoName === "South Korea") targetCountry = "South Korea";

    const policyCount = getCountryData(geoName, allCountries);
    if (policyCount <= 0) return;

    setSelectedCountry(targetCountry);
    setLoadingPolicies(true);

    fetchPolicies({ country: targetCountry })
      .then(data => {
        setCountryPolicies(data || []);
        setLoadingPolicies(false);
      })
      .catch(err => {
        console.error("Error fetching country policies:", err);
        setCountryPolicies([]);
        setLoadingPolicies(false);
      });
  };

  const handleSelectMapCountry = (geoItem) => {
    const cName = geoItem.properties?.name;
    if (!cName) return;
    setMapSearch(cName);
    setShowMapSuggestions(false);
    setFocusedCountryName(cName);

    try {
      const centroid = geoPath().centroid(geoItem);
      if (centroid && !isNaN(centroid[0]) && !isNaN(centroid[1])) {
        setMapPosition({ center: centroid, zoom: 3.5 });
      }
    } catch (err) {
      console.error("Centroid calculation error:", err);
    }

    handleRegionClick(cName);
  };

  const handleResetMap = () => {
    setMapSearch("");
    setShowMapSuggestions(false);
    setFocusedCountryName(null);
    setMapPosition({ center: [0, 30], zoom: 1 });
  };

  const searchClean = mapSearch.trim().toLowerCase();
  const aliasMatch = COUNTRY_ALIASES[searchClean];

  const mapMatchingCountries = (geographiesListRef.current || []).filter(geo => {
    if (!searchClean) return false;
    const name = (geo.properties?.name || "").toLowerCase();
    const id = String(geo.id || "").toLowerCase();
    if (name.includes(searchClean) || id.includes(searchClean)) return true;
    if (aliasMatch && name.includes(aliasMatch.toLowerCase())) return true;
    return false;
  }).slice(0, 8);


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

    // Fetch initial live pipeline status
    fetch(`${BASE}/fetch/status`)
      .then(r => r.json())
      .then(setFetchStatus)
      .catch(() => {});

    // Initial check on mount
    fetch(`${BASE}/fetch/progress`)
      .then(r => r.json())
      .then(data => {
        setProgress(data);
        if (data.status !== "idle") {
          setFetching(true);
        }
      })
      .catch(() => {});
  }, []);

  // Poll progress status every 3 seconds only while active
  useEffect(() => {
    if (!fetching) return;

    const check = () => {
      fetch(`${BASE}/fetch/progress`)
        .then(r => r.json())
        .then(data => {
          setProgress(data);
          if (data.status === "idle") {
            setFetching(false);
          }
        })
        .catch(() => {});
    };

    const interval = setInterval(check, 3000);
    return () => clearInterval(interval);
  }, [fetching]);

  // Refresh status and stats when fetching completes
  useEffect(() => {
    if (progress.status === "idle" && !loading) {
      Promise.all([
        fetchOverview(), fetchSectorDist(), fetchRegionDist(), fetchTrends(), fetchCountries()
      ]).then(([ov, sec, reg, tr, ctr]) => {
        setOverview(ov);
        setSectors(Object.entries(sec || {}).map(([name, value]) => ({ name, value })));
        setTrends(Object.entries(tr || {}).map(([year, count]) => ({ year: String(year), count })));
        setAllCountries(ctr || {});
        setCountries(Object.entries(ctr || {}).sort((a,b) => b[1]-a[1]).slice(0,8)
          .map(([name, value]) => ({ name: name.replace("European Union","EU").replace("United States","USA").replace("United Kingdom","UK"), value })));
      });

      fetch(`${BASE}/fetch/status`)
        .then(r => r.json())
        .then(setFetchStatus)
        .catch(() => {});
    }
  }, [progress.status]);

  const triggerFetch = async () => {
    setFetching(true);
    try {
      await fetch(`${BASE}/fetch/trigger`, { method: "POST" });
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
      <div className="page-container">
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
        <div className="stat-cards-grid-custom">
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

          {/* CENTER — Progress or description */}
          {progress.status !== "idle" ? (
            <div style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "11px",
              fontFamily: "JetBrains Mono",
              color: "#5c9e2e",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis"
            }}>
              <span className="pulse-dot" style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#5c9e2e",
                display: "inline-block",
                boxShadow: "0 0 8px #5c9e2e",
                flexShrink: 0
              }} />
              <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>
                <strong>{progress.task_name ? progress.task_name.toUpperCase() : "PROCESSING"}</strong>
                {progress.total_policies > 0 ? ` (${progress.processed_policies}/${progress.total_policies})` : ""}
                {progress.current_policy_title ? ` : ${progress.current_policy_title}` : ""}
              </span>
            </div>
          ) : (
            <>
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
            </>
          )}

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
        <div className="responsive-equal-two-col-grid" style={{ marginTop: "0px" }}>
          
          {/* Sector Distribution */}
          <div className="fade-up fade-up-2" style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            padding: "22px 28px",
            boxShadow: "none",
            marginBottom: "20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
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
            <div className="sector-dist-layout-custom">
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
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

              {/* Map Search Bar & Reset Controls */}
              <div style={{ position: "relative", width: "100%", maxWidth: "340px", zIndex: 30 }}>
                <form 
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (mapMatchingCountries.length > 0) {
                      handleSelectMapCountry(mapMatchingCountries[0]);
                    }
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    background: "var(--bg-hover)",
                    border: "1px solid var(--border-lit)",
                    borderRadius: "6px",
                    padding: "6px 12px",
                    gap: "8px",
                    transition: "border-color 0.2s ease"
                  }}
                >
                  <Search size={14} color="#5c9e2e" style={{ flexShrink: 0 }} />
                  <input
                    type="text"
                    placeholder="Search country or ISO code (e.g. India, USA, DEU)..."
                    value={mapSearch}
                    onChange={(e) => {
                      setMapSearch(e.target.value);
                      setShowMapSuggestions(true);
                    }}
                    onFocus={() => setShowMapSuggestions(true)}
                    style={{
                      background: "transparent",
                      border: "none",
                      outline: "none",
                      color: "var(--text-main)",
                      fontSize: "12px",
                      fontFamily: "DM Sans",
                      width: "100%"
                    }}
                  />
                  {mapSearch && (
                    <button
                      type="button"
                      onClick={handleResetMap}
                      style={{
                        background: "transparent",
                        border: "none",
                        cursor: "pointer",
                        color: "var(--text-muted)",
                        display: "flex",
                        alignItems: "center",
                        padding: 2
                      }}
                      title="Clear search and reset map view"
                    >
                      <X size={14} />
                    </button>
                  )}
                </form>

                {/* Autocomplete Suggestion Dropdown */}
                {showMapSuggestions && mapSearch.trim().length > 0 && (
                  <div style={{
                    position: "absolute",
                    top: "100%",
                    left: 0,
                    right: 0,
                    marginTop: "4px",
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: "6px",
                    maxHeight: "220px",
                    overflowY: "auto",
                    boxShadow: "0 6px 20px rgba(0,0,0,0.3)",
                    zIndex: 50
                  }}>
                    {mapMatchingCountries.length > 0 ? (
                      mapMatchingCountries.map((geoItem) => {
                        const cName = geoItem.properties?.name;
                        const count = getCountryData(cName, allCountries);
                        return (
                          <div
                            key={geoItem.rsmKey || cName}
                            onClick={() => handleSelectMapCountry(geoItem)}
                            style={{
                              padding: "8px 12px",
                              fontSize: "12px",
                              fontFamily: "DM Sans",
                              color: "var(--text-main)",
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              cursor: "pointer",
                              borderBottom: "1px solid var(--border)",
                              background: focusedCountryName === cName ? "var(--bg-hover)" : "transparent"
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = "var(--bg-hover)"}
                            onMouseLeave={(e) => e.currentTarget.style.background = focusedCountryName === cName ? "var(--bg-hover)" : "transparent"}
                          >
                            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                              <Globe size={12} color="#5c9e2e" />
                              <span style={{ fontWeight: 500 }}>{cName}</span>
                              {geoItem.id && (
                                <span style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "JetBrains Mono" }}>
                                  ({geoItem.id})
                                </span>
                              )}
                            </div>
                            <span style={{
                              fontSize: "10px",
                              fontFamily: "JetBrains Mono",
                              color: count > 0 ? "#5c9e2e" : "var(--text-dim)",
                              background: count > 0 ? "rgba(92, 158, 46, 0.1)" : "var(--bg-hover)",
                              padding: "2px 6px",
                              borderRadius: "4px"
                            }}>
                              {count} policies
                            </span>
                          </div>
                        );
                      })
                    ) : (
                      <div style={{
                        padding: "12px",
                        fontSize: "12px",
                        color: "var(--text-muted)",
                        fontFamily: "DM Sans",
                        textAlign: "center"
                      }}>
                        No matching countries found
                      </div>
                    )}
                  </div>
                )}
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
              <ComposableMap projection="geoMercator" projectionConfig={{ scale: 145 }} width={800} height={380} style={{ width: "100%", height: "100%" }}>
                <ZoomableGroup center={mapPosition.center} zoom={mapPosition.zoom} onMoveEnd={(pos) => setMapPosition(pos)}>
                  <Geographies geography="https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json">
                    {({ geographies }) => {
                      geographiesListRef.current = geographies;
                      const maxPolicies = Math.max(...Object.values(allCountries), 1);
                      const colorScale = scaleLinear().domain([1, maxPolicies]).range(["#d9f99d", "#4d7c0f"]);
                      
                      return geographies.map((geo) => {
                        const countryName = geo.properties.name;
                        const policyCount = getCountryData(countryName, allCountries);
                        const isFocused = focusedCountryName && (
                          countryName.toLowerCase() === focusedCountryName.toLowerCase() ||
                          (focusedCountryName === "United States" && countryName === "United States of America") ||
                          (focusedCountryName === "United States of America" && countryName === "United States") ||
                          (focusedCountryName === "UK" && countryName === "United Kingdom") ||
                          (focusedCountryName === "United Kingdom" && countryName === "UK")
                        );

                        return (
                          <Geography
                            key={geo.rsmKey}
                            geography={geo}
                            fill={isFocused ? "#a3e635" : (policyCount > 0 ? colorScale(policyCount) : "var(--bg-hover)")}
                            stroke={isFocused ? "#5c9e2e" : "var(--bg-card)"}
                            strokeWidth={isFocused ? 1.5 : 0.5}
                            style={{
                               default: { outline: "none" },
                               hover: { fill: policyCount > 0 ? "#65a30d" : "var(--border-lit)", outline: "none", cursor: policyCount > 0 ? "pointer" : "default" },
                               pressed: { outline: "none" },
                            }}
                            onMouseEnter={() => {
                              setHoveredRegion({ name: countryName, count: policyCount });
                            }}
                            onMouseMove={(e) => {
                              const rect = e.currentTarget.ownerSVGElement?.getBoundingClientRect?.() || { left: 0, top: 0 };
                              setTooltipPos({
                                x: e.clientX - rect.left,
                                y: e.clientY - rect.top
                              });
                            }}
                            onMouseLeave={() => setHoveredRegion(null)}
                            onClick={() => handleSelectMapCountry(geo)}
                          />
                        );
                      });
                    }}
                  </Geographies>
                </ZoomableGroup>
              </ComposableMap>


              {hoveredRegion && (
                <div style={{
                  position: "absolute",
                  left: tooltipPos.x + 12,
                  top: tooltipPos.y + 12,
                  background: "var(--bg-card)", border: "1px solid var(--border)",
                  padding: "8px 12px", borderRadius: 8, pointerEvents: "none",
                  boxShadow: "0 4px 14px rgba(0, 0, 0, 0.12)",
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
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

      {/* Sidebar Panel Backdrop Blur */}
      {selectedCountry && (
        <div 
          onClick={() => setSelectedCountry(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(8px)",
            WebkitBackdropFilter: "blur(8px)",
            zIndex: 100,
            animation: "fadeIn 0.25s ease-out"
          }}
        />
      )}

      {/* Sidebar Panel Overlay */}
      {selectedCountry && (
        <div className="dashboard-sidebar-panel" style={{
          background: "var(--bg-card)",
          borderLeft: "1px solid var(--border)",
          boxShadow: "-8px 0 32px rgba(0, 0, 0, 0.2)",
          padding: "32px",
          display: "flex",
          flexDirection: "column",
          animation: "slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
          textAlign: "left"
        }}>
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#5c9e2e" }} />
                <span style={{ fontSize: "11px", fontFamily: "JetBrains Mono", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  JURISDICTION DRILL-DOWN
                </span>
              </div>
              <h2 style={{ fontFamily: "DM Sans", fontSize: "24px", fontWeight: 700, color: "var(--text-main)", margin: 0 }}>
                {selectedCountry}
              </h2>
            </div>
            <button 
              onClick={() => setSelectedCountry(null)}
              style={{
                background: "none",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "8px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "all 0.2s"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "var(--bg-hover)";
                e.currentTarget.style.color = "var(--text-main)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "none";
                e.currentTarget.style.color = "var(--text-muted)";
              }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Subtitle */}
          <div style={{ 
            fontSize: "13px", 
            fontFamily: "DM Sans", 
            color: "var(--text-muted)", 
            marginBottom: "24px",
            borderBottom: "1px solid var(--border)",
            paddingBottom: "12px"
          }}>
            Showing {countryPolicies.length} {countryPolicies.length === 1 ? 'policy' : 'policies'} from the database
          </div>

          {/* Content */}
          <div style={{ flex: 1, overflowY: "auto", paddingRight: "4px" }}>
            {loadingPolicies ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "200px" }}>
                <RotateCw className="spin-icon" size={24} color="#5c9e2e" style={{ marginBottom: "12px" }} />
                <span style={{ fontSize: "12px", fontFamily: "JetBrains Mono", color: "var(--text-muted)" }}>
                  Fetching policies...
                </span>
              </div>
            ) : countryPolicies.length === 0 ? (
              <div style={{ padding: "32px 16px", textAlign: "center", color: "var(--text-muted)", fontFamily: "DM Sans" }}>
                No active policies found for this region.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {countryPolicies.map((policy) => (
                  <div 
                    key={policy.id}
                    onClick={() => {
                      setSelectedCountry(null);
                      navigate(`/policies/${policy.id}`);
                    }}
                    style={{
                      background: "var(--bg-hover)",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      padding: "16px",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      textAlign: "left"
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = "var(--text-main)";
                      e.currentTarget.style.transform = "translateY(-1.5px)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = "var(--border)";
                      e.currentTarget.style.transform = "none";
                    }}
                  >
                    <div style={{ 
                      fontSize: "10px", 
                      fontFamily: "JetBrains Mono", 
                      color: "#5c9e2e", 
                      fontWeight: 600, 
                      letterSpacing: "0.05em",
                      marginBottom: "6px",
                      display: "flex",
                      justifyContent: "space-between"
                    }}>
                      <span>{policy.sector.toUpperCase()}</span>
                      {policy.year && <span>{policy.year}</span>}
                    </div>
                    <h3 style={{ 
                      fontFamily: "DM Sans", 
                      fontSize: "14px", 
                      fontWeight: 600, 
                      color: "var(--text-main)",
                      margin: "0 0 8px 0",
                      lineHeight: "1.3"
                    }}>
                      {policy.title}
                    </h3>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "11px", fontFamily: "DM Sans" }}>
                      <span style={{ 
                        background: "rgba(92, 158, 46, 0.08)", 
                        color: "#5c9e2e", 
                        padding: "2px 8px", 
                        borderRadius: "12px",
                        fontWeight: 600
                      }}>
                        {policy.status || "Active"}
                      </span>
                      <span style={{ color: "var(--text-muted)" }}>View details &rarr;</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}