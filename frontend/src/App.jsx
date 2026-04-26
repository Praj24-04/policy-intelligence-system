import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard    from "./pages/Dashboard";
import Policies     from "./pages/Policies";
import PolicyDetail from "./pages/PolicyDetail";
import Compare      from "./pages/Compare";
import Analytics    from "./pages/Analytics";
import Recommend    from "./pages/Recommend";
import UploadPolicy from "./pages/UploadPolicy";
import Login        from "./pages/Login";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    const token  = localStorage.getItem("token");
    if (stored && token) {
      setUser(JSON.parse(stored));
    }
  }, []);

  const handleLogin = (data) => {
    setUser({ username: data.username, role: data.role, full_name: data.full_name });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  if (!user) return <Login onLogin={handleLogin} />;

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-deep)" }}>
        <Sidebar user={user} onLogout={handleLogout} />
        <main style={{ flex: 1, overflowY: "auto", minHeight: "100vh" }}>
          <Routes>
            <Route path="/"               element={<Dashboard />}    />
            <Route path="/policies"       element={<Policies />}     />
            <Route path="/policies/:id"   element={<PolicyDetail />} />
            <Route path="/compare"        element={<Compare />}      />
            <Route path="/analytics"      element={<Analytics />}    />
            <Route path="/recommend"      element={<Recommend />}    />
            <Route path="/upload"         element={<UploadPolicy />} />
            <Route path="*"               element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}