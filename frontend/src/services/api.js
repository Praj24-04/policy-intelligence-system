const BASE = "http://localhost:8000/api";

const getToken = () => localStorage.getItem("token");

const get = (url) =>
  fetch(`${BASE}${url}`, {
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
    console.error(`API Error [${url}]:`, err);
    return null;
  });

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
export const comparePolicies   = (id1, id2) => get(`/compare/?id1=${id1}&id2=${id2}`);
export const fetchRecommendations = (policyId, topN = 5) =>
  get(`/recommend/${policyId}?top_n=${topN}`);
export const fetchClusters = () => get(`/recommend/clusters/summary`);

export const submitFeedback = (policyId, country, helpful) =>
  fetch(`http://localhost:8000/api/feedback/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ policy_id: policyId, country, helpful })
  }).then(r => r.json());

export const fetchFeedbackSummary = () =>
  get("/feedback/summary");