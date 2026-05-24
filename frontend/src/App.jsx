import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import DashboardNavbar from "./components/DashboardNavbar";
import Dashboard from "./pages/Dashboard";
import Policies from "./pages/Policies";
import PolicyDetail from "./pages/PolicyDetail";
import Compare from "./pages/Compare";
import Analytics from "./pages/Analytics";
import Recommend from "./pages/Recommend";
import UploadPolicy from "./pages/UploadPolicy";
import Login from "./pages/Login";
import GeneratePolicy from "./pages/GeneratePolicy";
import Home from "./pages/Home";
import Profile from "./pages/Profile";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (stored && token) {
      setUser(JSON.parse(stored));
    }
  }, []);

  const handleLogin = (userObj) => {
    // userObj is the `user` field from TokenResponse: { id, email, full_name, role }
    setUser(userObj);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  if (!user) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    );
  }

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-deep)" }}>
        <Sidebar user={user} onLogout={handleLogout} />
        <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh" }}>
          <DashboardNavbar user={user} />
          <main style={{ flex: 1, overflowY: "auto" }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/policies" element={<Policies />} />
              <Route path="/policies/:id" element={<PolicyDetail />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/recommend" element={<Recommend />} />
              <Route path="/upload" element={<UploadPolicy />} />
              <Route path="/generate" element={<GeneratePolicy />} />
              <Route path="/profile" element={<Profile user={user} />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}