const getApiBase = () => {
  const override = typeof window !== 'undefined' && window.localStorage && window.localStorage.getItem("API_URL_OVERRIDE");
  if (override) {
    return override;
  }

  const envUrl = (import.meta.env && import.meta.env.VITE_API_URL) || 
                 (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL);
  if (envUrl) {
    if (window.location.protocol === 'https:' && envUrl.startsWith('http://') && envUrl.includes(window.location.hostname)) {
      return envUrl.replace('http://', 'https://');
    }
    return envUrl;
  }
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return "http://localhost:8000/api";
  }
  return "/api";
};

export const BASE = getApiBase();


export const getToken = () => {
  return localStorage.getItem("token");
};

let cache = {};
const CACHE_TTL = 60000; // 60 seconds

export const clearApiCache = () => {
  cache = {};
};

const get = (url) => {
  const now = Date.now();
  const cached = cache[url];
  if (cached && (now - cached.timestamp < CACHE_TTL)) {
    return cached.promise;
  }

  const fetchPromise = fetch(`${BASE}${url}`, {
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
    delete cache[url];
    return null;
  });

  cache[url] = {
    promise: fetchPromise,
    timestamp: now
  };

  return fetchPromise;
};

// ── Auth ───────────────────────────────────────────────────────────────────
const postJson = async (url, body) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  try {
    const res = await fetch(`${BASE}${url}`, {
      method: "POST",
      headers,
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
export const changePassword = (old_password, new_password) => postJson("/auth/change-password", { old_password, new_password });
export const updateProfile  = (full_name) => postJson("/auth/update-profile", { full_name });
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

// ── Admin APIs ────────────────────────────────────────────────────────────
export const fetchAdminStats   = () => get("/admin/stats");
export const fetchAdminSystem  = () => get("/admin/system");

export const fetchAdminUsers = (params = {}) => {
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v !== undefined));
  const q = new URLSearchParams(clean).toString();
  return get(`/admin/users${q ? "?" + q : ""}`);
};

export const fetchAdminUser    = (id) => get(`/admin/users/${id}`);

export const updateUserRole = (id, role) => postJson(`/admin/users/${id}/role`, { role });

export const blockUser = (id) =>
  fetch(`${BASE}/admin/users/${id}/block`, {
    method: "PUT",
    headers: { "Authorization": `Bearer ${getToken()}`, "Content-Type": "application/json" },
  }).then(r => r.json());

export const deleteUser = (id) =>
  fetch(`${BASE}/admin/users/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${getToken()}` },
  }).then(r => r.json());

export const fetchActivityLogs = (params = {}) => {
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v !== undefined));
  const q = new URLSearchParams(clean).toString();
  return get(`/admin/activity${q ? "?" + q : ""}`);
};

export const adminDeletePolicy = (id) =>
  fetch(`${BASE}/admin/policies/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${getToken()}` },
  }).then(r => r.json());

export const createAdminUser = (data) =>
  fetch(`${BASE}/admin/create-admin`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to create admin");
    return res;
  });

export const fetchTrustedSources = () => get("/admin/trusted-sources");

export const createTrustedSource = (data) =>
  fetch(`${BASE}/admin/trusted-sources`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to add source");
    return res;
  });

export const updateTrustedSourceStatus = (id, status) =>
  fetch(`${BASE}/admin/trusted-sources/${id}/status`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  }).then(r => r.json());

export const deleteTrustedSource = (id) =>
  fetch(`${BASE}/admin/trusted-sources/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${getToken()}` },
  }).then(r => r.json());

export const testTrustedSource = (id) =>
  fetch(`${BASE}/admin/trusted-sources/${id}/test`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${getToken()}` },
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Test crawl failed");
    return res;
  });

export const fetchAdminSectors = () => get("/admin/sectors");

export const createAdminSector = (data) =>
  fetch(`${BASE}/admin/sectors`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to create sector");
    return res;
  });

export const updateAdminSector = (id, data) =>
  fetch(`${BASE}/admin/sectors/${id}`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to update sector");
    return res;
  });

export const deleteAdminSector = (id) =>
  fetch(`${BASE}/admin/sectors/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${getToken()}` },
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to delete sector");
    return res;
  });

// ── Support Chat APIs ──────────────────────────────────────────────────────
export const sendSupportMessage = (message) => postJson("/support/messages", { message });
export const fetchSupportMessages = () => get("/support/messages");
export const fetchAdminSupportMessages = () => get("/support/admin/messages");
export const sendAdminReply = (userId, message) => postJson("/support/admin/reply", { user_id: userId, message });

export const updateSupportStatus = (messageId, status) =>
  fetch(`${BASE}/support/admin/messages/${messageId}/status`, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to update status");
    return res;
  });

export const updateUserSupportStatus = (userId, status) =>
  fetch(`${BASE}/support/admin/user/${userId}/status`, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  }).then(async r => {
    const res = await r.json();
    if (!r.ok) throw new Error(res.detail || "Failed to update status");
    return res;
  });