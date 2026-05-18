import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Scale, Lightbulb, FilePlus, Upload } from "lucide-react";
import TopNavbar from "../components/TopNavbar";
import { fetchPolicies } from "../services/api";
import PolicyCard from "../components/PolicyCard";

const PolicyTestimonialCard = ({ policy }) => (
  <div style={{ 
    background: "var(--bg-deep)", 
    border: "1px solid var(--border)", 
    borderRadius: 12, 
    padding: 24, 
    boxShadow: "0 4px 20px -2px rgba(0,0,0,0.05)",
    display: "flex",
    flexDirection: "column",
    gap: 16,
    textAlign: "left"
  }}>
    {policy.tags && policy.tags.length > 0 && (
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {policy.tags.slice(0, 3).map((tag, i) => (
          <span key={i} style={{ 
            background: "rgba(163, 230, 53, 0.15)", 
            color: "#4d7c0f", 
            padding: "4px 10px", 
            borderRadius: 6, 
            fontSize: 11, 
            fontWeight: 700,
            fontFamily: "Inter, sans-serif",
            letterSpacing: "0.02em",
            textTransform: "uppercase"
          }}>
            {tag}
          </span>
        ))}
      </div>
    )}
    <div style={{ color: "var(--text-muted)", fontSize: 14, lineHeight: 1.6, minHeight: 60, fontFamily: "Inter, sans-serif" }}>
      {policy.title || "Standard operational guidelines and data protection rules updated for compliance."}
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 8 }}>
      <div style={{ 
        width: 40, height: 40, borderRadius: "50%", 
        background: "var(--bg-hover)", 
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 16, fontWeight: 800, color: "var(--text-main)",
        border: "1px solid var(--border)",
        fontFamily: "Inter, sans-serif"
      }}>
        {(policy.country || "G")[0].toUpperCase()}
      </div>
      <div>
        <div style={{ color: "var(--text-main)", fontWeight: 700, fontSize: 14, fontFamily: "Inter, sans-serif" }}>
          {policy.country || "Global"}
        </div>
        <div style={{ color: "var(--text-dim)", fontSize: 12, fontFamily: "Inter, sans-serif" }}>
          {policy.sector || "General"} • {policy.status || "Active"}
        </div>
      </div>
    </div>
  </div>
);

export default function Home() {
  const nav = useNavigate();
  const [policies, setPolicies] = useState([]);

  useEffect(() => {
    fetchPolicies({}).then(data => {
      setPolicies(data || []);
    });
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
  };

  // Duplicate policies a few times to ensure the marquee content is long enough to loop seamlessly
  const marqueePoliciesH = [...policies, ...policies, ...policies, ...policies].slice(0, 20);
  
  // For vertical marquees, we split into 3 columns
  const pCount = policies.length || 1;
  const colSize = Math.ceil(pCount / 3);
  const col1 = [...policies.slice(0, colSize), ...policies.slice(0, colSize), ...policies.slice(0, colSize)];
  const col2 = [...policies.slice(colSize, colSize * 2), ...policies.slice(colSize, colSize * 2), ...policies.slice(colSize, colSize * 2)];
  const col3 = [...policies.slice(colSize * 2), ...policies.slice(colSize * 2), ...policies.slice(colSize * 2)];

  return (
    <div className="bg-texture" style={{ minHeight: "100vh", display: "flex", flexDirection: "column", overflowX: "hidden" }}>
      <TopNavbar />
      
      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
        
        {/* HERO SECTION */}
        <section id="hero" style={{ minHeight: "75vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", padding: "60px 20px 40px", width: "100%" }}>
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            style={{ textAlign: "center", maxWidth: 800, marginBottom: 48 }}
          >
            <motion.h1 variants={itemVariants} style={{
              fontSize: "clamp(3.5rem, 7vw, 6rem)", 
              fontWeight: 800, 
              lineHeight: 1.1,
              color: "var(--text-main)",
              letterSpacing: "-0.04em",
              marginBottom: 24,
            }}>
              Master global <br />
              <span className="half-highlight" style={{ display: "inline-block", color: "var(--text-main)" }}>
                <div className="flip-container">
                  <div className="flip-list">
                    <span>compliance.</span>
                    <span>regulations.</span>
                    <span>audits.</span>
                    <span>compliance.</span>
                  </div>
                </div>
              </span>
            </motion.h1>
            
            <motion.p variants={itemVariants} style={{
              fontSize: "1.1rem",
              color: "var(--text-muted)",
              maxWidth: 600,
              margin: "0 auto 32px",
              lineHeight: 1.6
            }}>
              PolicyIQ scores your compliance, tracks global regulations, runs gap analyses, 
              and alerts your legal team to upcoming regulatory changes in real-time.
            </motion.p>

            <motion.div variants={itemVariants} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16 }}>
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => nav("/login")}
                style={{
                  background: "var(--cyan)",
                  color: "#000",
                  border: "none",
                  padding: "14px 28px",
                  borderRadius: 8,
                  fontSize: 16,
                  fontWeight: 700,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  boxShadow: "0 4px 14px rgba(163, 230, 53, 0.3)"
                }}
              >
                Start free trial &rarr;
              </motion.button>
              
              <motion.button 
                whileHover={{ backgroundColor: "var(--bg-hover)" }}
                whileTap={{ scale: 0.95 }}
                style={{
                  background: "transparent",
                  color: "var(--text-main)",
                  border: "1px solid var(--border)",
                  padding: "14px 28px",
                  borderRadius: 8,
                  fontSize: 16,
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 8
                }}
              >
                View demo
              </motion.button>
            </motion.div>
          </motion.div>
        </section>

        {/* LIVE POLICIES HORIZONTAL MARQUEE */}
        <section style={{ 
          width: "100%", 
          padding: "40px 0", 
          borderTop: "1px solid var(--border)", 
          borderBottom: "1px solid var(--border)", 
          background: "var(--bg-base)", 
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          alignItems: "center"
        }}>
          <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "JetBrains Mono", letterSpacing: "0.1em", marginBottom: 24, fontWeight: 700, textTransform: "uppercase" }}>
            LIVE &bull; RECENT POLICIES
          </div>
          <div style={{ width: "100%", overflow: "hidden", display: "flex", position: "relative" }}>
            <div className="animate-marquee-h" style={{ gap: 24, paddingLeft: 12, paddingRight: 12 }}>
              {marqueePoliciesH.map((item, i) => (
                <div key={i} style={{ 
                  display: "inline-flex", alignItems: "center", gap: 12, 
                  background: "var(--bg-base)", border: "1px solid var(--border)", 
                  padding: "6px 16px 6px 6px", borderRadius: 8, fontSize: 14,
                  whiteSpace: "nowrap", cursor: "default",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                  fontFamily: "Inter, sans-serif"
                }}>
                  <span style={{ 
                    display: "flex", alignItems: "center", justifyContent: "center",
                    background: "rgba(163, 230, 53, 0.15)", color: "#65a30d", 
                    width: 24, height: 24, borderRadius: 6, fontSize: 12, fontWeight: 800
                  }}>
                    {(item.region || "G")[0].toUpperCase()}
                  </span>
                  <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{item.region || "Global"}</span>
                  <span style={{ color: "var(--text-muted)" }}>{item.category || "Regulation"}</span>
                  <span style={{ color: "var(--text-dim)" }}>&rarr;</span>
                  <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{item.status || "Active"}</span>
                </div>
              ))}
              {/* Duplicate for seamless infinite scroll if very few policies */}
              {marqueePoliciesH.length < 5 && marqueePoliciesH.map((item, i) => (
                <div key={"dup-"+i} style={{ 
                  display: "inline-flex", alignItems: "center", gap: 12, 
                  background: "var(--bg-base)", border: "1px solid var(--border)", 
                  padding: "6px 16px 6px 6px", borderRadius: 8, fontSize: 14,
                  whiteSpace: "nowrap", cursor: "default",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
                  fontFamily: "Inter, sans-serif"
                }}>
                  <span style={{ 
                    display: "flex", alignItems: "center", justifyContent: "center",
                    background: "rgba(163, 230, 53, 0.15)", color: "#65a30d", 
                    width: 24, height: 24, borderRadius: 6, fontSize: 12, fontWeight: 800
                  }}>
                    {(item.region || "G")[0].toUpperCase()}
                  </span>
                  <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{item.region || "Global"}</span>
                  <span style={{ color: "var(--text-muted)" }}>{item.category || "Regulation"}</span>
                  <span style={{ color: "var(--text-dim)" }}>&rarr;</span>
                  <span style={{ color: "var(--text-main)", fontWeight: 600 }}>{item.status || "Active"}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FEATURES SECTION */}
        <section id="features" style={{ padding: "100px 20px", width: "100%", maxWidth: 1200 }}>
          <div style={{ textAlign: "left", marginBottom: 64, maxWidth: 800 }}>
            <div style={{ color: "var(--text-dim)", fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "JetBrains Mono" }}>
              <span style={{ color: "var(--cyan)", marginRight: 8 }}>■</span> HOW IT WORKS
            </div>
            <h2 style={{ fontSize: "clamp(2.5rem, 5vw, 4rem)", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.04em", lineHeight: 1.1 }}>
              Four steps. <span style={{ color: "var(--text-dim)" }}>No fluff.</span>
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "1.1rem", marginTop: 24, maxWidth: 600, lineHeight: 1.6 }}>
              From a blank document to a fully tracked compliance policy in a single sitting, without switching tabs ten times.
            </p>
          </div>
          
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", 
            background: "var(--border)",
            gap: 1,
            borderRadius: 16,
            border: "1px solid var(--border)",
            overflow: "hidden"
          }}>
            {[
              { 
                step: "01", time: "instant", 
                title: "Upload", 
                desc: "Securely upload and manage all your corporate documents.", 
                icon: <Upload size={20} color="#fff" /> 
              },
              { 
                step: "02", time: "ai-scored", 
                title: "Compare", 
                desc: "Instantly score your policies against industry standards.", 
                icon: <Scale size={20} color="#fff" /> 
              },
              { 
                step: "03", time: "smart", 
                title: "Recommend", 
                desc: "Get AI-driven recommendations to fill compliance gaps.", 
                icon: <Lightbulb size={20} color="#fff" /> 
              },
              { 
                step: "04", time: "automated", 
                title: "Generate", 
                desc: "Automatically draft new policies based on your requirements.", 
                icon: <FilePlus size={20} color="#fff" /> 
              },
            ].map((f, i) => (
              <div key={i} style={{ background: "var(--bg-deep)", padding: "40px 32px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32, fontFamily: "JetBrains Mono", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  <span style={{ color: "var(--text-dim)", fontWeight: 600 }}>STEP / {f.step}</span>
                  <span style={{ color: "var(--cyan)", fontWeight: 800 }}>{f.time}</span>
                </div>
                <div style={{ 
                  width: 48, height: 48, borderRadius: 12, 
                  background: "#1C1917", 
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 24,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
                }}>
                  {f.icon}
                </div>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 12, color: "var(--text-main)", letterSpacing: "-0.02em" }}>{f.title}</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* SHIPPED OFFERS (POLICIES) VERTICAL MARQUEES */}
        <section id="shipped" style={{ 
          padding: "100px 20px", 
          width: "100%", 
          background: "var(--bg-card)", 
          borderTop: "1px solid var(--border)", 
          borderBottom: "1px solid var(--border)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          overflow: "hidden"
        }}>
          <div style={{ textAlign: "left", marginBottom: 64, maxWidth: 1200, width: "100%", zIndex: 2 }}>
            <div style={{ color: "var(--text-dim)", fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 16 }}>
              <span style={{ color: "var(--cyan)", marginRight: 8 }}>■</span> LIVE POLICIES
            </div>
            <h2 style={{ fontSize: "clamp(2.5rem, 5vw, 4rem)", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.04em", lineHeight: 1.1 }}>
              Real regulations. <span style={{ color: "var(--text-dim)" }}>Real-time updates.</span>
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "1.25rem", marginTop: 24, maxWidth: 600, lineHeight: 1.6 }}>
              Unedited live policy feeds directly from top authorities and governing bodies globally this year.
            </p>
          </div>

          {/* Gradient overlay wrapper */}
          <div style={{ position: "relative", width: "100%", maxWidth: 1200 }}>
            {/* Top fade */}
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0,
              height: 160,
              background: "linear-gradient(to bottom, var(--bg-card) 0%, transparent 100%)",
              zIndex: 10,
              pointerEvents: "none"
            }} />
            {/* Bottom fade */}
            <div style={{
              position: "absolute", bottom: 0, left: 0, right: 0,
              height: 160,
              background: "linear-gradient(to top, var(--bg-card) 0%, transparent 100%)",
              zIndex: 10,
              pointerEvents: "none"
            }} />

          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", 
            gap: 24, 
            height: 600, 
            width: "100%",
            overflow: "hidden",
            position: "relative",
          }}>
            {/* Column 1 - Up */}
            <div className="animate-marquee-v-up" style={{ gap: 24, padding: "20px 0" }}>
              {col1.map((p, i) => (
                <div key={`c1-${i}`} style={{ pointerEvents: "none" }}>
                  <PolicyTestimonialCard policy={p} />
                </div>
              ))}
            </div>
            
            {/* Column 2 - Down */}
            <div className="animate-marquee-v-down" style={{ gap: 24, padding: "20px 0" }}>
              {col2.map((p, i) => (
                <div key={`c2-${i}`} style={{ pointerEvents: "none" }}>
                  <PolicyTestimonialCard policy={p} />
                </div>
              ))}
            </div>

            {/* Column 3 - Up */}
            <div className="animate-marquee-v-up" style={{ gap: 24, padding: "20px 0" }}>
              {col3.map((p, i) => (
                <div key={`c3-${i}`} style={{ pointerEvents: "none" }}>
                  <PolicyTestimonialCard policy={p} />
                </div>
              ))}
            </div>
            </div>
          </div> {/* end gradient overlay wrapper */}
        </section>

        {/* PRICING */}
        <section id="pricing" style={{ padding: "100px 20px", width: "100%", maxWidth: 1200, textAlign: "center" }}>
          <h2 style={{ fontSize: "2.5rem", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.03em", marginBottom: 48 }}>
            Simple, transparent pricing.
          </h2>
          <div style={{ display: "flex", justifyContent: "center", gap: 24, flexWrap: "wrap" }}>
            <div className="card" style={{ padding: 48, width: 320, textAlign: "left" }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)" }}>Free</h3>
              <div style={{ fontSize: "3rem", fontWeight: 800, color: "var(--text-main)", margin: "16px 0" }}>$0</div>
              <p style={{ color: "var(--text-muted)", marginBottom: 32 }}>Basic tracking for small teams.</p>
              <button style={{ width: "100%", padding: "12px", borderRadius: 8, border: "1px solid var(--border)", background: "transparent", color: "var(--text-main)", fontWeight: 600, cursor: "pointer" }}>Get Started</button>
            </div>
            <div className="card" style={{ padding: 48, width: 320, textAlign: "left", borderColor: "var(--cyan)", position: "relative" }}>
              <div style={{ position: "absolute", top: -12, left: "50%", transform: "translateX(-50%)", background: "var(--cyan)", color: "#000", padding: "4px 12px", borderRadius: 100, fontSize: 12, fontWeight: 700 }}>MOST POPULAR</div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-main)" }}>Pro</h3>
              <div style={{ fontSize: "3rem", fontWeight: 800, color: "var(--text-main)", margin: "16px 0" }}>$249<span style={{ fontSize: "1rem", color: "var(--text-muted)" }}>/mo</span></div>
              <p style={{ color: "var(--text-muted)", marginBottom: 32 }}>Full access to AI extraction and alerts.</p>
              <button style={{ width: "100%", padding: "12px", borderRadius: 8, border: "none", background: "var(--cyan)", color: "#000", fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 14px rgba(163, 230, 53, 0.3)" }}>Upgrade to Pro</button>
            </div>
          </div>
        </section>

      </main>

      {/* FOOTER */}
      <footer style={{ background: "var(--bg-base)", borderTop: "1px solid var(--border)", padding: "48px 20px", textAlign: "center" }}>
        <div style={{ fontWeight: 800, fontSize: 20, color: "var(--text-main)", letterSpacing: "-0.5px", marginBottom: 16 }}>
          PolicyIQ
        </div>
        <div style={{ color: "var(--text-muted)", fontSize: 14, marginBottom: 24 }}>
          © 2026 PolicyIQ Inc. All rights reserved.
        </div>
        <div style={{ display: "flex", justifyContent: "center", gap: 24 }}>
          <a href="#" style={{ color: "var(--text-muted)", textDecoration: "none" }}>Twitter</a>
          <a href="#" style={{ color: "var(--text-muted)", textDecoration: "none" }}>GitHub</a>
          <a href="#" style={{ color: "var(--text-muted)", textDecoration: "none" }}>LinkedIn</a>
        </div>
      </footer>
    </div>
  );
}
