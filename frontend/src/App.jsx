import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard    from "./pages/Dashboard";
import Policies     from "./pages/Policies";
import PolicyDetail from "./pages/PolicyDetail";
import Compare      from "./pages/Compare";
import Analytics    from "./pages/Analytics";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-deep)" }}>
        <Sidebar />
        <main style={{ flex: 1, overflowY: "auto", minHeight: "100vh" }}>
          <Routes>
            <Route path="/"               element={<Dashboard />}    />
            <Route path="/policies"       element={<Policies />}     />
            <Route path="/policies/:id"   element={<PolicyDetail />} />
            <Route path="/compare"        element={<Compare />}      />
            <Route path="/analytics"      element={<Analytics />}    />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}