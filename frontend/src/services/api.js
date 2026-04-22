const BASE = "http://localhost:8000/api";

const get = (url) => fetch(`${BASE}${url}`).then(r => r.json());

export const fetchPolicies  = (params = {}) => {
  const q = new URLSearchParams(Object.fromEntries(
    Object.entries(params).filter(([,v]) => v)
  )).toString();
  return get(`/policies/${q ? "?" + q : ""}`);
};

export const fetchPolicy    = (id)        => get(`/policies/${id}`);
export const fetchSectors   = ()          => get("/policies/sectors");
export const fetchRegions   = ()          => get("/policies/regions");
export const fetchOverview  = ()          => get("/analytics/overview");
export const fetchCountries = ()          => get("/analytics/countries");
export const fetchSectorDist= ()          => get("/analytics/sectors");
export const fetchRegionDist= ()          => get("/analytics/regions");
export const fetchTrends    = ()          => get("/analytics/trends");
export const fetchStatus    = ()          => get("/analytics/status");
export const comparePolicies= (id1, id2) => get(`/compare/?id1=${id1}&id2=${id2}`);