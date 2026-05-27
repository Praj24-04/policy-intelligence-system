const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

export const getToken = () => {
  return localStorage.getItem("token");
};

const get = (url) => {
  return fetch(`${BASE}${url}`, {
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    }
  })
  .then(r => {
    if (r.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.reload();
    }
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .catch(err => {
    return null;
  });
};

// ── Auth ───────────────────────────────────────────────────────────────────
const postJson = async (url, body) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout
  try {
    const res = await fetch(`${BASE}${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
  } catch (err) {
    if (err.name === "AbortError") throw new Error("Request timed out. Please try again.");
    throw err;
  } finally {
    clearTimeout(timeout);
  }
};

export const loginUser    = (email, password) => postJson("/auth/login", { email, password });
export const registerUser = (email, full_name, password) => postJson("/auth/register", { email, full_name, password });
export const forgotPassword = (email) => postJson("/auth/forgot-password", { email });
export const loginWithGoogle = (credential) => postJson("/auth/google", { credential });
export const resetPassword  = (token, new_password) => postJson("/auth/reset-password", { token, new_password });
export const fetchHistory   = () => get("/auth/history");

// Rest of api.js stays exactly the same
export const fetchPolicies  = (params = {}) => {
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v));
  const q = new URLSearchParams(clean).toString();
  return get(`/policies${q ? "?" + q : ""}`);
};

export const fetchPolicy       = (id) => get(`/policies/${id}`);
export const fetchSectors      = ()   => get(`/policies/sectors`);
export const fetchRegions      = ()   => get(`/policies/regions`);
export const fetchOverview     = ()   => get("/analytics/overview");
export const fetchCountries    = ()   => get("/analytics/countries");
export const fetchSectorDist   = ()   => get("/analytics/sectors");
export const fetchRegionDist   = ()   => get("/analytics/regions");
export const fetchTrends       = ()   => get("/analytics/trends");
export const fetchStatus       = ()   => get("/analytics/status");
export const comparePolicies   = (id1, id2) => get(`/compare/v2?id1=${id1}&id2=${id2}`);
export const fetchRecommendations = (policyId, topN = 5, weights = null) => {
  let url = `/recommend/v2/${policyId}?top_n=${topN}`;
  if (weights) {
    const { sector_gap, regulatory_maturity, semantic_need, regional_pressure, economic_tier } = weights;
    if (sector_gap !== undefined && sector_gap !== null) url += `&w_sector=${sector_gap}`;
    if (regulatory_maturity !== undefined && regulatory_maturity !== null) url += `&w_maturity=${regulatory_maturity}`;
    if (semantic_need !== undefined && semantic_need !== null) url += `&w_semantic=${semantic_need}`;
    if (regional_pressure !== undefined && regional_pressure !== null) url += `&w_regional=${regional_pressure}`;
    if (economic_tier !== undefined && economic_tier !== null) url += `&w_economic=${economic_tier}`;
  }
  return get(url);
};
export const fetchMLStatus = () => get("/ml/status");
export const fetchClusters = () => get(`/recommend/clusters/summary`);

export const submitFeedback = (policyId, country, helpful) =>
  fetch(`${BASE}/feedback/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy_id: policyId, country, helpful })
  }).then(r => r.json());

export const fetchFeedbackSummary = () =>
  get("/feedback/summary");

export const generatePolicyTemplate = (country, sector) =>
  fetch(`${BASE}/generate/policy`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ country, sector })
  }).then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });