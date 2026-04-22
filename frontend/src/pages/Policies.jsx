import { useEffect, useState } from "react";
import { fetchPolicies, fetchSectors, fetchRegions } from "../services/api";
import PolicyCard from "../components/PolicyCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { Search, Filter, X } from "lucide-react";

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
      setPolicies(d);
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

  const selectStyle = {
    background: "var(--bg-card)", border: "1px solid var(--border)",
    color: "var(--text-muted)", borderRadius: 8, padding: "8px 12px",
    fontSize: 13, cursor: "pointer", outline: "none",
  };

  return (
    <div style={{ padding: "28px 32px" }}>
      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div style={{ width: 3, height: 22, background: "#818cf8", borderRadius: 2 }} />
          <h1 style={{ fontFamily: "Syne", fontSize: 22, fontWeight: 800, color: "var(--text-main)" }}>
            Policy Library
          </h1>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, paddingLeft: 13 }}>
          {policies.length} policies · AI Governance · Cybersecurity · Data Privacy
        </p>
      </div>

      {/* Filter Bar */}
      <div className="card fade-up fade-up-1" style={{ padding: "14px 18px", marginBottom: 20, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1, minWidth: 200,
          background: "var(--bg-hover)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 12px" }}>
          <Search size={14} color="var(--text-muted)" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search policies, countries, keywords..."
            style={{ background: "none", border: "none", outline: "none", color: "var(--text-main)", fontSize: 13, width: "100%" }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Filter size={13} color="var(--text-muted)" />
        </div>

        <select value={sector} onChange={e => setSector(e.target.value)} style={selectStyle}>
          <option value="">All Sectors</option>
          {sectors.map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        <select value={region} onChange={e => setRegion(e.target.value)} style={selectStyle}>
          <option value="">All Regions</option>
          {regions.map(r => <option key={r} value={r}>{r}</option>)}
        </select>

        {hasFilters && (
          <button onClick={clearFilters} style={{
            display: "flex", alignItems: "center", gap: 5,
            background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.2)",
            color: "#f43f5e", borderRadius: 8, padding: "8px 12px",
            fontSize: 12, cursor: "pointer",
          }}>
            <X size={12} /> Clear
          </button>
        )}
      </div>

      {/* Grid */}
      {loading ? <LoadingSpinner label="Fetching policies..." /> : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 14 }}>
          {policies.length === 0
            ? <div style={{ gridColumn: "1/-1", textAlign: "center", color: "var(--text-muted)", padding: 48 }}>
                No policies match your filters.
              </div>
            : policies.map((p, i) => <PolicyCard key={p.id} policy={p} delay={(i % 5) + 1} />)
          }
        </div>
      )}
    </div>
  );
}