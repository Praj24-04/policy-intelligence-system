import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Scale, Lightbulb, FilePlus, Upload, Globe2 } from "lucide-react";
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

const FAQItem = ({ question, answer }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div style={{ borderBottom: "1px solid var(--border)", padding: "24px 0" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%", display: "flex", justifyContent: "space-between", alignItems: "center",
          background: "transparent", border: "none", cursor: "pointer",
          color: "var(--text-main)", fontSize: "1.1rem", fontWeight: 600, textAlign: "left",
          padding: 0
        }}
      >
        <span>{question}</span>
        <span style={{ fontSize: "1.5rem", color: "var(--text-muted)", transition: "transform 0.2s", transform: isOpen ? "rotate(45deg)" : "rotate(0deg)" }}>+</span>
      </button>
      <motion.div
        initial={false}
        animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0, marginTop: isOpen ? 16 : 0 }}
        style={{ overflow: "hidden", color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6 }}
      >
        {answer}
      </motion.div>
    </div>
  );
};

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
                className="btn-gleam"
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
                Start free &rarr;
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
                <div key={"dup-" + i} style={{
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
                step: "01", tag: "UPLOAD",
                title: "Centralize your docs.",
                desc: "Securely upload and manage all your corporate documents in one compliance workspace.",
                bullets: ["Drag and drop interface", "Secure cloud storage", "Version control"],
                link: "Start free →",
                icon: <Upload size={20} color="#65a30d" />
              },
              {
                step: "02", tag: "COMPARE",
                title: "Score compliance.",
                desc: "Instantly score your policies against industry standards without wasting weeks of manual review.",
                bullets: ["GDPR & ISO readiness", "Automated gap detection", "Risk level scoring"],
                link: "View standards →",
                icon: <Scale size={20} color="#65a30d" />
              },
              {
                step: "03", tag: "RECOMMEND",
                title: "Fill the gaps.",
                desc: "Get AI-driven recommendations to fill compliance gaps accurately based on your jurisdiction.",
                bullets: ["Context-aware suggestions", "Peer benchmarking", "Actionable insights"],
                link: "See examples →",
                icon: <Lightbulb size={20} color="#65a30d" />
              },
              {
                step: "04", tag: "GENERATE",
                title: "Draft instantly.",
                desc: "Automatically draft new policies based on your requirements. Review, approve, and deploy.",
                bullets: ["One-click document drafting", "Legal-grade templates", "Export to PDF/Word"],
                link: "Draft now →",
                icon: <FilePlus size={20} color="#65a30d" />
              },
            ].map((f, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -5, borderColor: "var(--cyan)", boxShadow: "0 10px 30px -10px rgba(0,0,0,0.1)" }}
                style={{
                  background: "var(--bg-deep)",
                  padding: "40px 32px",
                  borderRadius: 12,
                  border: "1px solid var(--border)",
                  display: "flex",
                  flexDirection: "column",
                  transition: "all 0.2s"
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24, fontFamily: "JetBrains Mono", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-dim)", fontWeight: 600 }}>
                  <span style={{ color: "var(--cyan)" }}>■</span> {f.step} / {f.tag}
                </div>
                <div style={{
                  width: 48, height: 48, borderRadius: 12,
                  background: "rgba(163, 230, 53, 0.15)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 24,
                }}>
                  {f.icon}
                </div>
                <h3 style={{ fontSize: "1.4rem", fontWeight: 800, marginBottom: 12, color: "var(--text-main)", letterSpacing: "-0.03em" }}>{f.title}</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: 24 }}>{f.desc}</p>

                <ul style={{ listStyle: "none", padding: 0, margin: 0, flexGrow: 1, marginBottom: 32 }}>
                  {f.bullets.map((b, idx) => (
                    <li key={idx} style={{ color: "var(--text-muted)", fontSize: "0.9rem", display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 12 }}>
                      <span style={{ color: "var(--cyan)", fontSize: "1.2rem", lineHeight: 1 }}>•</span> {b}
                    </li>
                  ))}
                </ul>

                <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--text-main)", display: "inline-flex", alignItems: "center", gap: 4, cursor: "pointer" }}>
                  <span style={{ borderBottom: "1px solid var(--text-main)", paddingBottom: 2 }}>{f.link.replace('→', '')}</span> &rarr;
                </div>
              </motion.div>
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

        {/* FAQ SECTION */}
        <section id="faq" style={{ padding: "100px 20px", width: "100%", maxWidth: 1200, display: "flex", gap: "60px", alignItems: "flex-start", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 300px", position: "sticky", top: 100 }}>
            <div style={{ color: "var(--text-dim)", fontSize: 12, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "JetBrains Mono" }}>
              <span style={{ color: "var(--cyan)", marginRight: 8 }}>■</span> FAQ
            </div>
            <h2 style={{ fontSize: "clamp(2.5rem, 5vw, 4rem)", fontWeight: 800, color: "var(--text-main)", letterSpacing: "-0.04em", lineHeight: 1.1, marginBottom: 24 }}>
              Questions, <br />
              <span style={{ display: "inline-block", color: "var(--text-dim)" }}>answered.</span>
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "1.1rem", lineHeight: 1.6 }}>
              Anything not here, email <br />
              <a href="mailto:support@policyiq.com" style={{ color: "var(--cyan)", textDecoration: "none", borderBottom: "1px dashed var(--cyan)", paddingBottom: 2 }}>support@policyiq.com</a>.
            </p>
          </div>
          <div style={{ flex: "2 1 600px", borderTop: "1px solid var(--border)" }}>
            <FAQItem
              question="What is PolicyIQ?"
              answer="PolicyIQ is an AI-powered policy intelligence platform. It tracks global regulations from sources like EUR-Lex, CISA, and OECD, providing automated gap analysis and compliance recommendations."
            />
            <FAQItem
              question="Is the regulatory data updated in real-time?"
              answer="Yes, our live ingestion pipeline updates daily from official regulatory sources to ensure you always have the latest policies and frameworks."
            />
            <FAQItem
              question="How does the AI gap analysis work?"
              answer="You upload your corporate documents, and our custom NLP models compare them against selected industry standards (like GDPR or the EU AI Act). It identifies missing clauses, outdated references, and suggests draft text to fill the gaps."
            />
            <FAQItem
              question="Can I compare different policies across jurisdictions?"
              answer="Absolutely. Our built-in comparison tool allows you to select policies from different regions and highlights similarities and differences, helping you build unified global compliance strategies."
            />
            <FAQItem
              question="Who is PolicyIQ built for?"
              answer="It is designed for policy analysts, compliance officers, legal teams, and researchers who need a streamlined, automated way to track and implement complex regulatory changes."
            />
          </div>
        </section>

      </main>

      {/* FOOTER */}
      <footer className="footer-dark" style={{ borderTop: "1px solid var(--border)", padding: "80px 48px", width: "100%" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", flexWrap: "wrap", gap: 48, marginBottom: 80 }}>
          {/* Newsletter Column */}
          <div style={{ flex: "2 1 300px", maxWidth: 450 }}>
            <div style={{ color: "#A3E635", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 16, fontFamily: "JetBrains Mono" }}>
              <span style={{ color: "#A3E635", marginRight: 8 }}>■</span> NEWSLETTER
            </div>
            <h3 style={{ fontSize: "2rem", fontWeight: 800, color: "#FFFFFF", letterSpacing: "-0.03em", lineHeight: 1.1, marginBottom: 16 }}>
              One email. <span style={{ color: "#A8A29E" }}>Monday<br />mornings.</span>
            </h3>
            <p style={{ color: "#A8A29E", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: 24 }}>
              New regulations, platform updates, compliance tactics. No spam, unsubscribe in one click.
            </p>
            <div style={{ display: "flex", gap: 12 }}>
              <input type="email" placeholder="your@email.com" style={{ flex: 1, padding: "12px 16px", borderRadius: 8, border: "1px solid #292524", background: "#1C1917", color: "#FFF", fontSize: 14, outline: "none" }} />
              <button style={{ background: "#A3E635", color: "#000", border: "none", padding: "0 24px", borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
                Subscribe
              </button>
            </div>
          </div>

          {/* Platform Links */}
          <div style={{ flex: "1 1 120px" }}>
            <div style={{ color: "#57534E", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 24, fontFamily: "JetBrains Mono" }}>PLATFORM</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16, fontSize: 14 }}>
              <a href="#" style={{ textDecoration: "none" }}>Policies</a>
              <a href="#" style={{ textDecoration: "none" }}>Global Tracker</a>
              <a href="#" style={{ textDecoration: "none" }}>AI Analysis</a>
              <a href="#" style={{ textDecoration: "none" }}>API Docs</a>
              <a href="#" style={{ textDecoration: "none" }}>Integrations</a>
              <a href="#" style={{ textDecoration: "none" }}>Open source</a>
            </div>
          </div>

          {/* For Compliance Links */}
          <div style={{ flex: "1 1 120px" }}>
            <div style={{ color: "#57534E", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 24, fontFamily: "JetBrains Mono" }}>FOR COMPLIANCE</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16, fontSize: 14 }}>
              <a href="#" style={{ textDecoration: "none" }}>Overview</a>
              <a href="#" style={{ textDecoration: "none" }}>Enterprise</a>
              <a href="#" style={{ textDecoration: "none" }}>Dashboard</a>
            </div>
          </div>

          {/* Account Links */}
          <div style={{ flex: "1 1 120px" }}>
            <div style={{ color: "#57534E", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700, marginBottom: 24, fontFamily: "JetBrains Mono" }}>ACCOUNT</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16, fontSize: 14 }}>
              <a href="#" style={{ textDecoration: "none" }}>Start free</a>
              <a href="#" style={{ textDecoration: "none" }}>Sign In</a>
              <a href="#" style={{ textDecoration: "none" }}>Blog</a>
              <a href="#" style={{ textDecoration: "none" }}>Contact</a>
            </div>
          </div>
        </div>

        {/* Footer Bottom */}
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #292524", paddingTop: 32, gap: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 24, height: 24, borderRadius: 6, background: "#A3E635", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Globe2 size={12} color="#000" />
            </div>
            <div style={{ fontWeight: 800, fontSize: 16, color: "#FFFFFF", letterSpacing: "-0.5px" }}>PolicyIQ</div>
          </div>

          <div style={{ color: "#57534E", fontSize: 12, fontFamily: "JetBrains Mono" }}>
            © 2026 PolicyIQ. built globally.
          </div>

          <div style={{ display: "flex", gap: 24, fontSize: 12, fontWeight: 600 }}>
            <a href="#" style={{ textDecoration: "none" }}>Terms</a>
            <a href="#" style={{ textDecoration: "none" }}>Privacy</a>
            <a href="#" style={{ textDecoration: "none" }}>Refunds</a>
            <a href="#" style={{ textDecoration: "none" }}>Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
