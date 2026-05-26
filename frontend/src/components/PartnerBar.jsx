import { useTheme } from "../context/ThemeContext";

// SanatanLabs first (tall square logo), then the two horizontal logos
const PARTNERS = [
  { src: "/logos/sanatanlabs.png", alt: "Sanatan Labs", logoH: 42, maxW: 120 },
  { src: "/logos/passionit.png",   alt: "PASSION IT",  logoH: 20, maxW: 100 },
  { src: "/logos/pcombinator.png", alt: "PCombinator", logoH: 20, maxW: 100 },
];

/**
 * PartnerLogos — no pill boxes, no backgrounds.
 * Uses CSS mix-blend-mode to knock out the image's own white/dark
 * background so logos appear to float directly on the navbar.
 */
export default function PartnerLogos() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
      {/* Divider from PolicyIQ wordmark */}
      <div style={{
        width: 1, height: 22,
        background: "var(--border)",
        margin: "0 16px",
        opacity: 0.5,
        flexShrink: 0,
      }} />

      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {PARTNERS.map((p, i) => (
          <div key={p.alt} style={{ display: "flex", alignItems: "center", gap: 16 }}>

            <img
              src={p.src}
              alt={p.alt}
              title={p.alt}
              style={{
                height: p.logoH,
                width: "auto",
                maxWidth: p.maxW,
                objectFit: "contain",
                display: "block",
                // ── The magic: removes white bg in light mode, dark bg in dark mode
                mixBlendMode: isDark ? "screen" : "multiply",
                // Slight opacity boost in dark mode so colours pop
                opacity: isDark ? 0.9 : 0.85,
              }}
            />

            {/* Thin separator between logos */}
            {i < PARTNERS.length - 1 && (
              <div style={{
                width: 1, height: 14,
                background: "var(--border)",
                opacity: 0.35,
                flexShrink: 0,
              }} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
