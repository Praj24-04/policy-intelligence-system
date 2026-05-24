import { useEffect, useState } from "react";
import { fetchPolicies, fetchSectors, fetchRegions } from "../services/api";
import PolicyCard from "../components/PolicyCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { Search, Filter, X, Globe2, ExternalLink, MapPin } from "lucide-react";

export default function Policies() {
  const [policies, setPolicies] = useState([]);
  const [sectors,  setSectors]  = useState([]);
  const [regions,  setRegions]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [search,   setSearch]   = useState("");
  const [sector,   setSector]   = useState("");
  const [region,   setRegion]   = useState("");

  const load = () => {
    setLoading(true);
    fetchPolicies({ search, sector, region }).then(d => {
      setPolicies(d || []);
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchSectors().then(setSectors);
    fetchRegions().then(setRegions);
  }, []);

  useEffect(() => { load(); }, [search, sector, region]);

  const clearFilters = () => { setSearch(""); setSector(""); setRegion(""); };
  const hasFilters = search || sector || region;

  return (
    <div style={{
      flex: 1,
      overflowY: "auto",
      background: "var(--bg-deep)",
      minHeight: "100vh"
    }}>
      <div style={{
        maxWidth: "1100px",
        margin: "0 auto",
        padding: "32px 40px",
        width: "100%"
      }}>
        
        {/* ── Page Header Section ── */}
        <div className="fade-up" style={{ marginBottom: 24 }}>
          
          {/* Breadcrumb line above title */}
          <div style={{ 
            fontSize: "10px", 
            color: "var(--text-dim)", 
            fontFamily: "'JetBrains Mono', monospace", 
            textTransform: "uppercase", 
            letterSpacing: "1.5px", 
            marginBottom: 14,
            display: "flex",
            alignItems: "center",
            gap: 6
          }}>
            <span style={{ 
              width: 6, 
              height: 6, 
              background: "#5c9e2e", 
              display: "inline-block",
              borderRadius: "1px"
            }} />
            BROWSE / DATABASE
          </div>

          {/* Title Stack */}
          <h1 style={{ 
            fontFamily: "'DM Sans', sans-serif", 
            fontSize: "52px", 
            fontWeight: 700, 
            color: "var(--text-main)",
            margin: "0 0 16px 0",
            letterSpacing: "-1.5px",
            lineHeight: "1.1"
          }}>
            Search the <span className="half-highlight-custom">database.</span>
          </h1>

          {/* Subtitle & Stats Row */}
          <div style={{ 
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "flex-end", 
            flexWrap: "wrap",
            gap: 20,
            marginTop: 8
          }}>
            <p style={{ 
              fontFamily: "'DM Sans', sans-serif", 
              color: "var(--text-muted)", 
              fontSize: "14px", 
              margin: 0,
              maxWidth: "600px",
              lineHeight: 1.5
            }}>
              Open frameworks from partner jurisdictions plus curated global policies, updated daily.
            </p>

            {/* Metrics Stack */}
            <div style={{ 
              display: "flex", 
              gap: 16, 
              fontFamily: "'JetBrains Mono', monospace", 
              fontSize: "11px", 
              color: "var(--text-muted)",
              fontWeight: 500,
              alignItems: "center"
            }}>
              <span>ACTIVE <strong style={{ color: "var(--text-main)", marginLeft: 4 }}>{policies.filter(p => p.year >= 2023).length || 240}</strong></span>
              <span style={{ color: "var(--border)" }}>|</span>
              <span>UNDER REVIEW <strong style={{ color: "var(--text-main)", marginLeft: 4 }}>{policies.filter(p => p.year < 2023).length || 502}</strong></span>
              <span style={{ color: "var(--border)" }}>|</span>
              <span>INDEXED <strong style={{ color: "var(--bg-base)", background: "var(--text-main)", padding: "2px 6px", borderRadius: "3px", marginLeft: 4, fontWeight: 700 }}>{policies.length}</strong></span>
            </div>
          </div>

        </div>

        {/* ── Top Promo Card ── */}
        <div 
          className="fade-up"
          style={{
            padding: "16px 20px",
            borderRadius: "8px",
            border: "1px solid var(--border)",
            background: "var(--bg-card)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            cursor: "pointer",
            marginBottom: "24px",
            boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
            transition: "all 0.15s ease"
          }}
          onClick={() => setSector("AI Governance")}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            {/* Icon box */}
            <div style={{
              width: "40px",
              height: "40px",
              borderRadius: "6px",
              background: "var(--bg-hover)",
              border: "1px solid var(--border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--text-muted)"
            }}>
              <Globe2 size={18} />
            </div>
            {/* Text info */}
            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: "14px", fontWeight: 600, color: "var(--text-main)" }}>
                Top 100 Policy Frameworks in AI Governance 2026
              </div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "10px", color: "var(--text-dim)", letterSpacing: "0.06em" }}>
                GOVERNMENT / STANDARDS / ISO / REGULATION
              </div>
            </div>
          </div>
          <ExternalLink size={14} color="var(--text-dim)" />
        </div>

        {/* ── Search & Location Dual Inputs ── */}
        <div style={{
          display: "flex",
          gap: "12px",
          marginBottom: "16px",
          width: "100%"
        }}>
          {/* Main Search Input */}
          <div style={{ position: "relative", flex: 3, minWidth: "200px" }}>
            <Search 
              size={16} 
              color="var(--text-dim)" 
              style={{ 
                position: "absolute", 
                left: 16, 
                top: "50%", 
                transform: "translateY(-50%)",
                pointerEvents: "none"
              }} 
            />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by title, sector, or keyword..."
              className="search-input-custom"
              style={{
                width: "100%",
                height: 48,
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "0 16px 0 44px",
                outline: "none",
                fontSize: "14px",
                fontFamily: "'DM Sans', sans-serif",
                background: "var(--bg-card)",
                color: "var(--text-main)",
                boxShadow: "0 1px 2px rgba(0,0,0,0.02)"
              }}
            />
          </div>

          {/* Location Dropdown */}
          <div style={{ position: "relative", flex: 1, minWidth: "150px" }}>
            <span style={{ 
              position: "absolute", 
              left: 16, 
              top: "50%", 
              transform: "translateY(-50%)",
              pointerEvents: "none",
              color: "#9ca3af",
              display: "flex",
              alignItems: "center",
              zIndex: 1
            }}>
              <MapPin size={16} />
            </span>
            <select
              value={region}
              onChange={e => setRegion(e.target.value)}
              className="select-custom"
              style={{
                width: "100%",
                height: 48,
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "0 32px 0 40px",
                outline: "none",
                fontSize: "14px",
                fontFamily: "'DM Sans', sans-serif",
                background: "var(--bg-card)",
                color: "var(--text-main)",
                boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                cursor: "pointer",
                appearance: "none",
                WebkitAppearance: "none"
              }}
            >
              <option value="">Location (All)</option>
              {regions.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
            <span style={{
              position: "absolute",
              right: 16,
              top: "50%",
              transform: "translateY(-50%)",
              pointerEvents: "none",
              color: "#9ca3af",
              display: "flex",
              alignItems: "center"
            }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m6 9 6 6 6-6"/>
              </svg>
            </span>
          </div>
        </div>

        {/* ── Pill Tags Filter Row ── */}
        <div style={{
          display: "flex",
          justifyContent: "flex-start",
          alignItems: "center",
          gap: "16px",
          flexWrap: "wrap",
          marginBottom: "24px",
          borderBottom: "1px solid #f0f0f0",
          paddingBottom: "24px"
        }}>
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "10px",
            color: "#9ca3af",
            letterSpacing: "0.08em",
            marginRight: "4px"
          }}>
            FILTER /
          </span>
          
          {/* Sector Pills */}
          <button 
            onClick={() => setSector("")}
            style={{
              padding: "5px 14px",
              borderRadius: "20px",
              fontSize: "12px",
              fontFamily: "'DM Sans', sans-serif",
              cursor: "pointer",
              transition: "all 0.15s ease",
              background: sector === "" ? "var(--text-main)" : "var(--bg-card)",
              color: sector === "" ? "var(--bg-base)" : "var(--text-muted)",
              border: sector === "" ? "1px solid var(--text-main)" : "1px solid var(--border)",
              fontWeight: sector === "" ? 500 : 400
            }}
          >
            All Sectors
          </button>

          {["AI Governance", "Cybersecurity", "Data Privacy", "Healthcare AI", "Financial Regulation", "ESG Policies", "POSH Policies", "IoT and Robotics"].map(s => {
            const isSelected = sector === s;
            return (
              <button 
                key={s}
                onClick={() => setSector(s)}
                style={{
                  padding: "5px 14px",
                  borderRadius: "20px",
                  fontSize: "12px",
                  fontFamily: "'DM Sans', sans-serif",
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  background: isSelected ? "var(--text-main)" : "var(--bg-card)",
                  color: isSelected ? "var(--bg-base)" : "var(--text-muted)",
                  border: isSelected ? "1px solid var(--text-main)" : "1px solid var(--border)",
                  fontWeight: isSelected ? 500 : 400
                }}
              >
                {s}
              </button>
            );
          })}

          {hasFilters && (
            <button 
              onClick={clearFilters} 
              style={{
                display: "flex", 
                alignItems: "center", 
                gap: 5,
                background: "rgba(244,63,94,0.06)", 
                border: "1px solid rgba(244,63,94,0.12)",
                color: "#f43f5e", 
                borderRadius: "20px", 
                padding: "5px 14px",
                fontSize: "12px", 
                cursor: "pointer", 
                fontFamily: "'DM Sans', sans-serif",
                fontWeight: 500,
                transition: "all 0.15s ease"
              }}
            >
              <X size={12} /> Clear
            </button>
          )}
        </div>

        {/* ── Subtitle Divider Line ── */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          marginBottom: "20px",
          marginTop: "16px"
        }}>
          <div>
            <div style={{ 
              fontSize: "10px", 
              color: "var(--text-dim)", 
              fontFamily: "'JetBrains Mono', monospace", 
              textTransform: "uppercase", 
              letterSpacing: "1px", 
              marginBottom: 6,
              display: "flex",
              alignItems: "center",
              gap: 6
            }}>
              <span style={{ 
                width: 6, 
                height: 6, 
                background: "#5c9e2e", 
                display: "inline-block",
                borderRadius: "1px"
              }} />
              POLICY DATA / EMBEDDINGS
            </div>
            <h2 style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "18px",
              fontWeight: 600,
              color: "var(--text-main)",
              margin: 0,
              letterSpacing: "-0.5px"
            }}>
              Global policy intelligence database
            </h2>
          </div>

          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "10px",
            color: "var(--text-dim)",
            letterSpacing: "0.1em",
            fontWeight: 500
          }}>
            REFRESHED EVERY 24H
          </div>
        </div>

        {/* ── Responsive Card Grid ── */}
        {loading ? <LoadingSpinner label="Fetching policies..." /> : (
          <div>
            {policies.length === 0 ? (
              <div style={{ 
                textAlign: "center", 
                color: "var(--text-muted)", 
                padding: "60px 0",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px"
              }}>
                No policies match your filters.
              </div>
            ) : (
              <div className="policies-grid-custom">
                {policies.map((p, i) => (
                  <PolicyCard key={p.id} policy={p} delay={(i % 6) + 1} />
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}