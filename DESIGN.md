---
name: Policy Intelligence System
colors:
  dark:
    bg-deep: "#07090f"
    bg-base: "#0d111d"
    bg-card: "#111827"
    bg-hover: "#161d2e"
    border: "#1e2a3a"
    border-lit: "#2a3a52"
    cyan: "#22d3ee"
    cyan-dim: "#0891b2"
    amber: "#f59e0b"
    green: "#10b981"
    red: "#f43f5e"
    text-main: "#e2e8f0"
    text-muted: "#64748b"
    text-dim: "#334155"
  light:
    bg-deep: "#f0f4f8"
    bg-base: "#ffffff"
    bg-card: "#ffffff"
    bg-hover: "#f1f5f9"
    border: "#e2e8f0"
    border-lit: "#cbd5e1"
    cyan: "#0891b2"
    cyan-dim: "#0e7490"
    amber: "#d97706"
    green: "#059669"
    red: "#e11d48"
    text-main: "#0f172a"
    text-muted: "#475569"
    text-dim: "#94a3b8"
  semantics:
    ai:
      text: "#a5b4fc"
      bg: "rgba(99,102,241,0.15)"
      border: "rgba(99,102,241,0.3)"
    cyber:
      text: "#67e8f9"
      bg: "rgba(34,211,238,0.1)"
      border: "rgba(34,211,238,0.25)"
    priv:
      text: "#6ee7b7"
      bg: "rgba(16,185,129,0.1)"
      border: "rgba(16,185,129,0.25)"
    health:
      text: "#fcd34d"
      bg: "rgba(245,158,11,0.1)"
      border: "rgba(245,158,11,0.25)"
    fin:
      text: "#fda4af"
      bg: "rgba(244,63,94,0.1)"
      border: "rgba(244,63,94,0.25)"
    posh:
      text: "#c4b5fd"
      bg: "rgba(167,139,250,0.1)"
      border: "rgba(167,139,250,0.25)"
    esg:
      text: "#6ee7b7"
      bg: "rgba(52,211,153,0.1)"
      border: "rgba(52,211,153,0.25)"
    iot:
      text: "#7dd3fc"
      bg: "rgba(56,189,248,0.1)"
      border: "rgba(56,189,248,0.25)"
typography:
  body:
    fontFamily: DM Sans, sans-serif
    fontSize: 14px
    lineHeight: 1.6
  heading:
    fontFamily: Syne, sans-serif
  mono:
    fontFamily: JetBrains Mono, monospace
shadows:
  glow-cyan: 0 0 20px rgba(34, 211, 238, 0.15)
  glow-amber: 0 0 20px rgba(245, 158, 11, 0.15)
  text-glow: 0 0 20px rgba(34, 211, 238, 0.4)
rounded:
  card: 12px
  scrollbar: 4px
motion:
  fade-up:
    animation: fadeUp 0.4s ease both
    keyframes: "transform: translateY(16px) -> 0; opacity: 0 -> 1"
---

## Brand & Style
The design system of the Policy Intelligence System evokes a highly advanced, technical, and analytical environment. Operating primarily in a native Dark Mode, it feels like a modern command center or data dashboard designed for intelligence analysts, cyber-security professionals, or policy experts who need to parse vast amounts of complex data efficiently.

The aesthetic leans into a "Cyber-Analytical" motif. It relies heavily on deep, near-black backgrounds juxtaposed with striking, neon-adjacent accents (cyan, amber, green, and red). This contrast not only draws the eye to critical data points but also establishes a serious, high-tech tone. The UI is sharp, structured, and deliberate.

## Colors
The color palette is built for long-term focus and high legibility in low-light environments, with a structured light mode counterpart for versatility.

- **Backgrounds:** Deep, immersive tones like `#07090f` (deepest space) and `#0d111d` (base workspace) create a sense of infinite depth. Cards and elevated surfaces use `#111827` to stand out subtly against the deeper backdrops.
- **Accents:** High-vibrancy "lit" colors, notably Cyan (`#22d3ee`) and Amber (`#f59e0b`), act as the primary signaling colors. Cyan is used for active states, data highlights, and glowing elements, conveying a sense of processing and intelligence. Amber is used to draw attention to warnings or critical insights.
- **Semantic Pills:** A wide array of semantic colors (AI, Cyber, Privacy, Health, Finance) are utilized through low-opacity backgrounds paired with highly saturated borders and text. This creates a "glowing badge" effect that categorizes information without overwhelming the primary data.
- **Text:** Crisp, cool grays (`#e2e8f0` for main text) ensure excellent readability without the harshness of pure white against dark backgrounds.

## Typography
The typographic hierarchy reflects the system's dual nature: analytical rigor and modern presentation.

- **Headings:** **Syne** is utilized for headings. Its slightly widened, contemporary letterforms give the interface a forward-looking, bold identity.
- **Body Text:** **DM Sans** provides excellent legibility for dense data and long-form text, maintaining a clean, geometric neutrality at the standard `14px` base size.
- **Data & Code:** **JetBrains Mono** is employed for raw data, metrics, or technical readouts, reinforcing the developer/analyst aesthetic and ensuring numbers align perfectly in tables and charts.

## Layout & Spacing
The layout relies on a card-based architecture to compartmentalize information streams.
- **Cards:** Elements are housed in defined containers (`border: 1px solid var(--border)`) to maintain order. 
- **Scrollbars:** Custom, slim scrollbars (4px) with subtle rounded thumbs ensure that navigation tools don't distract from the core data.

## Elevation & Depth
Depth is created through subtle border variations and targeted luminescence rather than heavy drop shadows.

- **Hover States:** Cards become slightly lighter (`--bg-hover`) and their borders illuminate (`--border-lit`) upon interaction, providing crisp, immediate feedback.
- **Glows:** Instead of traditional shadows, the system uses "glows" (`box-shadow: 0 0 20px rgba(...)`) to lift active or critical elements off the screen. Cyan and Amber glows simulate LEDs or backlit screens, adding to the command-center feel.

## Shapes
The UI balances structure with approachability.
- **Cards and Containers:** A consistent `12px` border radius softens the hard, technical edge of the interface just enough to feel modern and polished, avoiding a rigid, brutalist look.
- **Pills:** Semantic tags and badges use tight, controlled padding and thin borders to encapsulate their vivid colors.

## Motion
Motion in the system is purposeful and understated, designed to guide rather than distract.
- **Entrance:** A smooth `fade-up` animation (`0.4s ease`) staggers the entrance of new data streams or cards. This cascading effect (using staggered delays) makes the interface feel responsive and alive as it "boots up" or loads new intelligence.
- **Transitions:** Quick `0.2s` and `0.3s` transitions on background and border colors ensure the UI reacts instantly to user input, maintaining a snappy, high-performance feel.
