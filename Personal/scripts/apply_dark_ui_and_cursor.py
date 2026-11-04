import os
import re

CONTENT_FILE = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41/.system_generated/steps/572/content.md"
PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(CONTENT_FILE, "r", encoding="utf-8") as f:
    raw_content = f.read()

# 1. Strip markdown frontmatter if present
doctype_idx = raw_content.find("<!DOCTYPE html>")
if doctype_idx != -1:
    html = raw_content[doctype_idx:]
else:
    html = raw_content

# 2. Inject Anton Font, Custom Cursor, Darker UI Text & Disciplined Crimson/Silver Palette
luxury_css = """
  <!-- Anton Font, Custom Luxury Cursor, Darker UI Text & No Yellow/Green Palette -->
  <style>
    @font-face {
      font-family: 'Anton';
      src: url('./anton.woff2') format('woff2');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }

    /* Override System Variables to eliminate yellow, green and cyan */
    :root {
      --accent-cyan: #d21424 !important;
      --accent-green: #e5283b !important;
      --accent-aws: #d21424 !important;
      --accent-neon-cyan: #d21424 !important;
      --accent-neon-green: #e5283b !important;
      --accent-neon-gold: #d21424 !important;
      --text-primary: #c8c8d2 !important; /* Darker, refined metallic silver instead of stark white */
      --text-secondary: #828290 !important; /* Darker graphite grey */
      --text-muted: #5a5a66 !important;
      --bg-black: #060408 !important;
      --bg-surface: #0e0c12 !important;
      --bg-surface-elevated: #141118 !important;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      overflow-x: clip !important;
      background-color: #060408 !important;
      color: var(--text-primary);
      position: relative;
    }

    /* ==========================================================================
       CUSTOM AWARDS CURSOR (DISCIPLINED CRIMSON & RING)
       ========================================================================== */
    @media (hover: hover) and (pointer: fine) {
      body, a, button, input, textarea, select, [role="button"], .scroll-indicator, .tilt-card {
        cursor: none !important;
      }
    }

    #custom-cursor-dot {
      position: fixed;
      top: 0;
      left: 0;
      width: 7px;
      height: 7px;
      background: #e5283b;
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999999;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 8px #e5283b, 0 0 2px #ffffff;
      transition: width 0.18s ease, height 0.18s ease, background-color 0.18s ease, opacity 0.25s ease;
    }

    #custom-cursor-ring {
      position: fixed;
      top: 0;
      left: 0;
      width: 36px;
      height: 36px;
      border: 1.5px solid rgba(229, 40, 59, 0.55);
      border-radius: 50%;
      pointer-events: none;
      z-index: 9999998;
      transform: translate(-50%, -50%);
      box-shadow: 0 0 12px rgba(163, 14, 25, 0.22);
      transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1), 
                  height 0.22s cubic-bezier(0.16, 1, 0.3, 1), 
                  border-color 0.22s ease, 
                  background-color 0.22s ease,
                  opacity 0.25s ease;
    }

    body.cursor-hover #custom-cursor-ring {
      width: 54px;
      height: 54px;
      border-color: rgba(229, 40, 59, 0.85);
      background-color: rgba(229, 40, 59, 0.12);
      box-shadow: 0 0 20px rgba(229, 40, 59, 0.4);
    }

    body.cursor-hover #custom-cursor-dot {
      width: 4px;
      height: 4px;
      background: #ffffff;
      box-shadow: 0 0 6px #ffffff;
    }

    body.cursor-active #custom-cursor-ring {
      width: 28px;
      height: 28px;
      border-color: #ff334b;
      background-color: rgba(229, 40, 59, 0.25);
    }

    /* ==========================================================================
       NAVBAR VISIBILITY CONTROL: HIDDEN DURING PHOTO SCROLL, VISIBLE AFTER REVEAL
       ========================================================================== */
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: var(--nav-height);
      background: rgba(10, 8, 14, 0.88) !important;
      backdrop-filter: blur(18px) !important;
      -webkit-backdrop-filter: blur(18px) !important;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
      z-index: 1000 !important;
      transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .navbar.navbar-hidden {
      opacity: 0 !important;
      pointer-events: none !important;
      transform: translateY(-100%) !important;
    }

    .nav-brand {
      color: #dedee8 !important;
    }
    .brand-monogram {
      background: rgba(22, 14, 20, 0.9) !important;
      border: 1px solid rgba(210, 20, 36, 0.4) !important;
      color: #ff4d63 !important;
    }

    .nav-links a {
      color: #8c8c9a !important;
      transition: all 0.25s ease;
    }
    .nav-links a:hover,
    .nav-links a.active {
      color: #dedee8 !important;
    }

    /* Top right button adjustments: pure crimson & silver */
    .nav-actions .btn-pill-terminal {
      background: rgba(20, 14, 20, 0.8) !important;
      border-color: rgba(210, 20, 36, 0.4) !important;
      color: #c8c8d2 !important;
      box-shadow: none !important;
    }
    .nav-actions .btn-pill-terminal:hover {
      border-color: rgba(235, 25, 45, 0.7) !important;
      color: #ffffff !important;
      box-shadow: 0 0 14px rgba(210, 20, 36, 0.35) !important;
    }

    /* Secret Terminal Hint pill: replace green dot with crimson */
    .secret-terminal-hint {
      background: rgba(16, 12, 18, 0.8) !important;
      border-color: rgba(210, 20, 36, 0.35) !important;
      color: #a0a0ae !important;
    }
    .hint-status-dot {
      background: #e5283b !important;
      box-shadow: 0 0 8px #e5283b !important;
    }

    /* ==========================================================================
       ATMOSPHERIC CYBER BACKGROUND: NEBULAE, GRID & CURSOR SPOTLIGHT
       ========================================================================== */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(circle at 18% 25%, rgba(163, 14, 25, 0.14) 0%, transparent 45%),
        radial-gradient(circle at 82% 65%, rgba(120, 10, 22, 0.10) 0%, transparent 50%),
        radial-gradient(circle at 50% 88%, rgba(163, 14, 25, 0.12) 0%, transparent 45%),
        linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 100% 100%, 54px 54px, 54px 54px;
      pointer-events: none;
      z-index: 1;
      opacity: 0.8;
    }

    #cursor-spotlight {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 2;
      background: radial-gradient(circle 420px at var(--mouse-x, 50vw) var(--mouse-y, 50vh), rgba(180, 15, 28, 0.07), transparent 70%);
      transition: opacity 0.3s ease;
    }

    /* Pinned Scroll Track: 140vh travel distance for 3D dot-to-photo reveal */
    .hero-scroll-track {
      position: relative;
      width: 100%;
      height: 240vh;
      background: #060408;
      z-index: 3;
    }

    .hero-sticky-stage {
      position: sticky;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      z-index: 3;
    }

    #webgl-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      pointer-events: auto;
    }

    #film-grain {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 3;
      opacity: 0.16;
      mix-blend-mode: overlay;
    }

    /* Preloader Ring */
    #preloader {
      position: absolute;
      inset: 0;
      background: #060408;
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.8s;
    }

    #preloader.hidden {
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
    }

    .ring-container {
      position: relative;
      width: 100px;
      height: 100px;
    }

    .ring-svg {
      width: 100%;
      height: 100%;
      transform: rotate(-90deg);
    }

    .ring-track {
      fill: none;
      stroke: rgba(255, 255, 255, 0.08);
      stroke-width: 5;
    }

    .ring-progress {
      fill: none;
      stroke: #a30e19;
      stroke-width: 5;
      stroke-linecap: round;
      stroke-dasharray: 289;
      stroke-dashoffset: 289;
      transition: stroke-dashoffset 0.15s ease-out;
      filter: drop-shadow(0 0 8px rgba(163, 14, 25, 0.7));
    }

    .ring-text {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
      font-weight: 500;
      letter-spacing: 0.04em;
      color: rgba(255, 255, 255, 0.85);
      font-variant-numeric: tabular-nums;
    }

    /* Scroll Pill Indicator */
    #ui-container {
      position: absolute;
      bottom: 34px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      pointer-events: auto;
      transition: opacity 0.35s ease, transform 0.35s ease;
    }

    .scroll-indicator {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 28px;
      background: rgba(18, 10, 16, 0.82);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(210, 20, 36, 0.45);
      border-radius: 9999px;
      color: #dedee8;
      font-size: 0.84rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      box-shadow: 0 4px 28px rgba(0, 0, 0, 0.7), 0 0 16px rgba(163, 14, 25, 0.3);
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }

    .scroll-indicator:hover {
      background: rgba(30, 14, 22, 0.95);
      border-color: rgba(235, 25, 45, 0.8);
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8), 0 0 25px rgba(210, 20, 36, 0.55);
    }

    .scroll-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #e5283b;
      box-shadow: 0 0 10px #e5283b;
      animation: pulse-dot 1.8s infinite;
    }

    @keyframes pulse-dot {
      0%, 100% { opacity: 0.45; transform: scale(0.85); }
      50% { opacity: 1; transform: scale(1.2); }
    }

    .scroll-progress-bar {
      width: 54px;
      height: 4px;
      background: rgba(255, 255, 255, 0.12);
      border-radius: 2px;
      overflow: hidden;
    }

    .scroll-progress-thumb {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #a30e19, #e5283b);
      transition: width 0.12s linear;
      box-shadow: 0 0 8px #e5283b;
    }

    /* ==========================================================================
       GIANT SECTION WATERMARK TYPOGRAPHY (ANTON SIGNATURE)
       ========================================================================== */
    .section-watermark {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-family: 'Anton', sans-serif;
      font-size: clamp(5.5rem, 13vw, 15rem);
      letter-spacing: -0.02em;
      line-height: 0.85;
      color: transparent;
      -webkit-text-stroke: 1px rgba(210, 20, 36, 0.07);
      text-shadow: 0 0 80px rgba(163, 14, 25, 0.05);
      white-space: nowrap;
      pointer-events: none;
      user-select: none;
      z-index: 1;
    }

    /* ==========================================================================
       HERO INTRO SECTION: "HI, I'M MUKESH KUMAR" (DARKER, DISCIPLINED PALETTE)
       ========================================================================== */
    .hero-intro-section {
      position: relative;
      z-index: 10;
      background: transparent;
      padding: 7rem 1.5rem 5rem 1.5rem;
      border-top: 1px solid rgba(210, 20, 36, 0.22);
      overflow: hidden;
    }

    .hero-intro-section::before {
      content: '';
      position: absolute;
      top: -1px;
      left: 50%;
      transform: translateX(-50%);
      width: 440px;
      height: 2px;
      background: linear-gradient(90deg, transparent, #e5283b, transparent);
      box-shadow: 0 0 12px #e5283b;
    }

    .hero-intro-card {
      position: relative;
      z-index: 2;
      max-width: 920px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 3.5rem 2.5rem;
      background: rgba(16, 12, 18, 0.75);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(210, 20, 36, 0.32);
      border-radius: 28px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 35px rgba(163, 14, 25, 0.18);
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .hero-intro-card:hover {
      border-color: rgba(235, 25, 45, 0.6);
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.85), 0 0 45px rgba(210, 20, 36, 0.3);
      transform: translateY(-3px);
    }

    .hero-intro-card::before,
    .project-card::before,
    .badge-card::before {
      content: '';
      position: absolute;
      top: 10px;
      left: 10px;
      width: 14px;
      height: 14px;
      border-top: 2px solid #e5283b;
      border-left: 2px solid #e5283b;
      pointer-events: none;
      opacity: 0.75;
    }

    .hero-intro-card::after,
    .project-card::after,
    .badge-card::after {
      content: '';
      position: absolute;
      bottom: 10px;
      right: 10px;
      width: 14px;
      height: 14px;
      border-bottom: 2px solid #a30e19;
      border-right: 2px solid #a30e19;
      pointer-events: none;
      opacity: 0.75;
    }

    .hero-intro-card .hero-status-tag {
      display: inline-flex;
      align-items: center;
      gap: 0.7rem;
      padding: 0.5rem 1.3rem;
      background: rgba(20, 12, 18, 0.85);
      border: 1px solid rgba(210, 20, 36, 0.38);
      border-radius: 9999px;
      font-family: var(--font-mono);
      font-size: 0.84rem;
      color: #b0b0c0;
      margin-bottom: 1.8rem;
    }

    /* Darker UI Headlines: Refined Metallic Silver */
    .hero-statement-title {
      font-size: clamp(2.4rem, 5vw, 4rem) !important;
      font-weight: 800 !important;
      letter-spacing: -0.04em !important;
      line-height: 1.15 !important;
      margin-bottom: 1.3rem !important;
      color: #c8c8d4 !important; /* Darker metallic silver */
      text-shadow: 0 4px 24px rgba(0, 0, 0, 0.85) !important;
    }

    /* Crimson/Silver Shimmer (Strictly NO Yellow, NO Green, NO Cyan) */
    .cyber-shimmer {
      background: linear-gradient(90deg, #d21424 0%, #ff556b 35%, #dedee6 50%, #ff556b 65%, #d21424 100%) !important;
      background-size: 200% auto !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
      animation: cyber-shimmer-anim 6s linear infinite !important;
    }

    .hero-typewriter-bar {
      font-family: var(--font-mono);
      font-size: clamp(0.92rem, 1.4vw, 1.12rem) !important;
      color: #d0d0dc !important; /* Muted silver text */
      margin-bottom: 1.6rem;
      min-height: 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
    }
    .typewriter-cursor {
      background-color: #e5283b !important;
      box-shadow: 0 0 8px #e5283b;
    }

    /* Cyber Spec HUD Bar: Strictly Dark Grey with Subtle Crimson Tones (NO Yellow, NO Green) */
    .cyber-specs-row {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.85rem;
      margin-bottom: 1.8rem;
    }

    .cyber-spec-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.45rem 1.05rem;
      background: rgba(16, 12, 18, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      color: #9292a0; /* Darker grey */
      backdrop-filter: blur(10px);
      transition: all 0.25s ease;
    }

    .cyber-spec-chip:hover {
      border-color: rgba(210, 20, 36, 0.45);
      color: #c8c8d2;
      box-shadow: 0 0 14px rgba(163, 14, 25, 0.2);
    }

    .cyber-spec-chip .chip-icon {
      color: #e5283b;
    }

    /* Darker UI Subtitles & Paragraphs */
    .hero-subtitle,
    .section-description,
    .footer-sub {
      font-size: clamp(0.98rem, 1.3vw, 1.12rem) !important;
      line-height: 1.78 !important;
      color: #828290 !important; /* Darker graphite grey */
      max-width: 740px !important;
      margin: 0 auto 2.5rem auto !important;
    }

    .section-title {
      font-size: clamp(2.2rem, 4.2vw, 3.4rem) !important;
      font-weight: 800 !important;
      letter-spacing: -0.03em !important;
      color: #c2c2ce !important; /* Darker metallic silver */
      text-shadow: 0 2px 20px rgba(0, 0, 0, 0.8) !important;
    }

    .section-label {
      color: #d21424 !important;
    }
    .section-label::before {
      background: #e5283b !important;
      box-shadow: 0 0 10px #e5283b !important;
    }

    /* Enhanced Buttons */
    .btn-pill-primary {
      background: linear-gradient(135deg, #a30e19 0%, #d21424 50%, #e5283b 100%) !important;
      border: 1px solid #ff4d63 !important;
      box-shadow: 0 4px 20px rgba(163, 14, 25, 0.55), 0 0 18px rgba(210, 20, 36, 0.3) !important;
      color: #ffffff !important;
    }
    .btn-pill-primary:hover {
      box-shadow: 0 6px 28px rgba(163, 14, 25, 0.8), 0 0 28px rgba(235, 25, 45, 0.55) !important;
      transform: translateY(-2px) scale(1.02) !important;
    }

    .btn-pill-terminal {
      background: rgba(18, 14, 20, 0.85) !important;
      border: 1px solid rgba(210, 20, 36, 0.42) !important;
      color: #c8c8d2 !important; /* Darker silver, no green */
      box-shadow: 0 0 12px rgba(163, 14, 25, 0.2) !important;
    }
    .btn-pill-terminal:hover {
      background: rgba(24, 16, 24, 0.95) !important;
      border-color: rgba(235, 25, 45, 0.7) !important;
      color: #ffffff !important;
      box-shadow: 0 0 20px rgba(210, 20, 36, 0.4) !important;
      transform: translateY(-2px) scale(1.02) !important;
    }

    .btn-pill-secondary {
      background: rgba(255, 255, 255, 0.04) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      color: #a0a0ae !important;
    }
    .btn-pill-secondary:hover {
      background: rgba(255, 255, 255, 0.08) !important;
      border-color: rgba(210, 20, 36, 0.4) !important;
      color: #dedee8 !important;
    }

    /* ==========================================================================
       OVERCHARGED CYBER MARQUEE TICKER (CRIMSON / SILVER - NO YELLOW/GREEN)
       ========================================================================== */
    .ticker-section {
      position: relative;
      z-index: 10;
      background: #08060a !important;
      border-top: 1px solid rgba(210, 20, 36, 0.28) !important;
      border-bottom: 1px solid rgba(210, 20, 36, 0.28) !important;
      box-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
      overflow: hidden;
    }
    .ticker-label {
      color: #727280 !important;
    }
    .ticker-item {
      font-family: var(--font-mono);
      font-size: 0.90rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      color: #a4a4b2 !important; /* Darker greyish text */
      text-transform: uppercase;
    }
    .ticker-dot {
      width: 7px;
      height: 7px;
      background: #e5283b !important;
      box-shadow: 0 0 8px #e5283b !important;
      border-radius: 50%;
    }

    /* ==========================================================================
       SECTIONS & BENTO GRID CARDS (DISCIPLINED DARK AESTHETIC)
       ========================================================================== */
    #projects,
    #about,
    #achievements,
    #aws-showcase,
    #contact {
      position: relative;
      z-index: 10;
      background: transparent !important;
      padding-top: 7rem;
      padding-bottom: 7rem;
      overflow: hidden;
    }

    .project-card,
    .spec-card,
    .info-story-col,
    .info-specs-col,
    .badge-card {
      position: relative;
      background: rgba(16, 12, 18, 0.78) !important;
      backdrop-filter: blur(20px) !important;
      -webkit-backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(210, 20, 36, 0.3) !important;
      border-radius: 22px !important;
      box-shadow: 0 15px 45px rgba(0, 0, 0, 0.7), 0 0 20px rgba(163, 14, 25, 0.12) !important;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
      transform-style: preserve-3d;
    }

    .project-card:hover,
    .badge-card:hover,
    .spec-card:hover {
      border-color: rgba(235, 25, 45, 0.65) !important;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.85), 0 0 35px rgba(210, 20, 36, 0.35) !important;
      transform: translateY(-5px) scale(1.015) !important;
    }

    .project-title,
    .badge-title {
      color: #c2c2ce !important; /* Darker metallic silver */
    }

    .project-desc,
    .badge-desc,
    .info-bio-text {
      color: #828290 !important; /* Darker graphite */
    }

    /* Project Tags: Dark slate with subtle borders, NO green/yellow */
    .tag-pill,
    .project-tag {
      background: rgba(255, 255, 255, 0.04) !important;
      border: 1px solid rgba(255, 255, 255, 0.09) !important;
      color: #9292a0 !important;
    }

    /* Filter pills */
    .filter-pill {
      background: rgba(255, 255, 255, 0.03) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      color: #828290 !important;
    }
    .filter-pill.active {
      background: rgba(210, 20, 36, 0.22) !important;
      border-color: #d21424 !important;
      color: #dedee8 !important;
      box-shadow: 0 0 14px rgba(210, 20, 36, 0.3) !important;
    }

    /* ==========================================================================
       IMAGE DARKENING: GOOGLE SKILLS BADGES & PROJECT SCREENSHOTS
       Transforms glaring white paper backgrounds into sleek, dark metallic grey
       ========================================================================== */
    .badge-card-visual {
      background: #0d0b10 !important;
      border-radius: 14px !important;
      overflow: hidden !important;
      position: relative !important;
      border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    .badge-card-visual::after {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(circle at center, transparent 35%, rgba(10, 8, 14, 0.5) 100%);
      pointer-events: none;
    }

    /* Darken Google Cloud White Certificate Paper into luxury white-greyish dark UI */
    .badge-cert-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      filter: brightness(0.72) contrast(1.15) grayscale(0.35) !important;
      transition: all 0.4s ease !important;
    }

    .badge-card:hover .badge-cert-img {
      filter: brightness(0.85) contrast(1.15) grayscale(0.12) !important;
      transform: scale(1.03);
    }

    /* Project Screenshots: Darker white-greyish tone */
    .project-card-visual,
    .project-card img {
      border-radius: 14px !important;
      filter: brightness(0.75) contrast(1.12) grayscale(0.28) !important;
      transition: all 0.4s ease !important;
    }

    .project-card:hover img {
      filter: brightness(0.88) contrast(1.12) grayscale(0.08) !important;
    }

    #modal-badge-img {
      filter: brightness(0.78) contrast(1.12) grayscale(0.25) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Badge tags: Remove green, use dark crimson/grey */
    .badge-verify-pill {
      background: rgba(22, 14, 20, 0.8) !important;
      border: 1px solid rgba(210, 20, 36, 0.35) !important;
      color: #a4a4b2 !important;
    }
    .badge-date-pill {
      background: rgba(255, 255, 255, 0.04) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      color: #7a7a88 !important;
    }

    /* ==========================================================================
       AWS CLOUD SHOWCASE: NO YELLOW/GREEN, SLEEK CRIMSON / SILVER
       ========================================================================== */
    .aws-showcase-container {
      background: rgba(16, 12, 18, 0.82) !important;
      backdrop-filter: blur(24px) !important;
      border: 1px solid rgba(210, 20, 36, 0.35) !important;
      border-radius: 28px !important;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(163, 14, 25, 0.15) !important;
    }

    .aws-badge-pill {
      background: rgba(22, 14, 20, 0.8) !important;
      border: 1px solid rgba(210, 20, 36, 0.35) !important;
      color: #ff8090 !important;
    }
    .aws-badge-pill span[style*="color:#00FF88"],
    .aws-badge-pill span[style*="color: #00FF88"],
    .aws-badge-pill span[style*="color:#10B981"] {
      color: #ff8090 !important;
    }

    .aws-tab-btn {
      color: #828290 !important;
    }
    .aws-tab-btn.active {
      background: linear-gradient(135deg, rgba(210, 20, 36, 0.25), rgba(130, 12, 22, 0.35)) !important;
      border-color: #d21424 !important;
      color: #dedee8 !important;
      box-shadow: 0 0 16px rgba(210, 20, 36, 0.35) !important;
    }

    .aws-pipeline-card {
      background: rgba(14, 10, 16, 0.8) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .aws-pipeline-card:hover {
      border-color: rgba(210, 20, 36, 0.45) !important;
    }
    .aws-card-step {
      color: #e5283b !important;
    }
    .aws-card-title {
      color: #c2c2ce !important;
    }
    .aws-card-detail {
      color: #727280 !important;
    }

    /* Terminal Window inside Project 1: Dark silver prompt, no green */
    .mini-term-prompt {
      color: #e5283b !important;
    }
    .mini-term-check {
      color: #d8d8e2 !important;
    }

    /* Footer & Contact */
    .footer-cta-section {
      border-top: 1px solid rgba(210, 20, 36, 0.25) !important;
    }
    .footer-statement {
      color: #c8c8d4 !important;
    }
  </style>
</head>
"""

html = html.replace("</head>", luxury_css)

# 3. Add Custom Cursor Elements before <nav class="navbar" id="navbar">
cursor_elements = """
  <!-- Custom Luxury Awwwards Cursor Elements -->
  <div id="custom-cursor-dot"></div>
  <div id="custom-cursor-ring"></div>
"""
html = html.replace('<nav class="navbar" id="navbar">', cursor_elements + '\n  <nav class="navbar navbar-hidden" id="navbar">')

# 4. Replace <section class="hero" id="hero"> with clean hero + intro section (disciplined chips, no yellow/green)
hero_replacement = """
  <!-- ==========================================================================
       HERO STAGE: PINNED 3D WEBGL BUST & FULL SCROLL REVEAL (CLEAN PHOTO STAGE)
       Navbar is HIDDEN during photo scrolling, and becomes visible AFTER reveal!
       ========================================================================== -->
  <div id="hero" class="hero-scroll-track">
    <div class="hero-sticky-stage">
      <!-- Three.js Canvas -->
      <canvas id="webgl-canvas"></canvas>

      <!-- Film Grain Overlay -->
      <div id="film-grain"></div>

      <!-- Preloader Ring -->
      <div id="preloader">
        <div class="ring-container">
          <svg class="ring-svg" viewBox="0 0 100 100">
            <circle class="ring-track" cx="50" cy="50" r="46"></circle>
            <circle id="ring-bar" class="ring-progress" cx="50" cy="50" r="46"></circle>
          </svg>
          <div id="ring-pct" class="ring-text">0%</div>
        </div>
      </div>

      <!-- Scroll Indicator Pill -->
      <div id="ui-container">
        <div id="scrollIndicator" class="scroll-indicator">
          <span class="scroll-dot"></span>
          <span id="scrollLabel">Scroll to reveal photo</span>
          <div class="scroll-progress-bar">
            <div id="scrollThumb" class="scroll-progress-thumb"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Full-Screen Interactive Cursor Glow Spotlight Overlay -->
  <div id="cursor-spotlight"></div>

  <!-- ==========================================================================
       HERO INTRO SECTION: "HI, I'M MUKESH KUMAR" (DARKER UI TEXT & POWER SPECS)
       Located directly below the photo with Anton Watermark & Clean Chips
       ========================================================================== -->
  <section class="hero-intro-section" id="intro">
    <div class="section-watermark">MUKESH KUMAR</div>
    <div class="container">
      <div class="hero-intro-card">
        <div class="hero-status-tag">
          <span class="status-pulse" style="background:#e5283b; box-shadow:0 0 10px #e5283b;"></span>
          <span>1ST YEAR BE-CSE • MIRAI SCHOOL OF TECHNOLOGY</span>
        </div>

        <h1 class="hero-statement-title">
          Hi, I'm Mukesh Kumar.<br>
          <span class="cyber-shimmer">I build for the web &amp; cloud.</span>
        </h1>

        <div class="hero-typewriter-bar">
          <span id="typewriter-text"></span>
          <span class="typewriter-cursor"></span>
        </div>

        <!-- Clean Power Spec Chips (Darker Grey & Crimson - No Yellow / Green) -->
        <div class="cyber-specs-row">
          <div class="cyber-spec-chip">
            <span class="chip-icon">⚡</span>
            <span>FRONTEND: SEMANTIC HTML5 &amp; CSS3</span>
          </div>
          <div class="cyber-spec-chip">
            <span class="chip-icon">⚙️</span>
            <span>CORE ENGINE: C++ &amp; DATA STRUCTURES</span>
          </div>
          <div class="cyber-spec-chip">
            <span class="chip-icon">☁️</span>
            <span>CLOUD DEPLOY: AWS AMPLIFY &amp; CLOUDFRONT</span>
          </div>
        </div>

        <p class="hero-subtitle">
          First-year engineering student learning modern web development with HTML &amp; CSS, and practicing Data Structures &amp; Algorithms in C++. This portfolio is my submission for the AWS Student Portfolio Hackathon, deployed on AWS Amplify.
        </p>

        <div class="hero-actions">
          <a href="#projects" class="btn-pill btn-pill-primary">
            <span>See My Projects</span>
            <span class="btn-arrow">↓</span>
          </a>

          <button id="hero-terminal-trigger" class="btn-pill btn-pill-terminal">
            <span>&gt;_</span>
            <span>Open Terminal [~]</span>
          </button>

          <button class="btn-pill btn-pill-secondary trigger-resume-modal">
            <span>Resume</span>
          </button>
        </div>
      </div>
    </div>
  </section>
"""

html = re.sub(r'<section class="hero" id="hero">[\s\S]*?</section>', hero_replacement, html)

# 5. Inject Giant Anton Watermarks into the remaining sections
html = html.replace('<section id="projects">', '<section id="projects">\n    <div class="section-watermark">SELECTED WORKS</div>')
html = html.replace('<section class="info-section" id="about">', '<section class="info-section" id="about">\n    <div class="section-watermark">ARCHITECT</div>')
html = html.replace('<section id="achievements">', '<section id="achievements">\n    <div class="section-watermark">CREDENTIALS</div>')
html = html.replace('<section id="aws-showcase">', '<section id="aws-showcase">\n    <div class="section-watermark">AWS CLOUD</div>')
html = html.replace('<section class="footer-cta-section" id="contact">', '<section class="footer-cta-section" id="contact">\n    <div class="section-watermark">TRANSMISSION</div>')

# 6. Inject three.min.js and WebGL Script + Navbar scroll toggle + Custom Cursor Engine before </body>
webgl_scripts = """
  <!-- Three.js Library -->
  <script src="./three.min.js"></script>

  <!-- 3D Crimson Surface Bust, Pinned Scroll, Dynamic Navbar Visibility & Custom Cursor -->
  <script>
    // --- Application Constants & Configuration ---
    const PHOTO_W = 1024.0;
    const PHOTO_H = 576.0;
    const N_DOTS = 78000;
    const CRIMSON_COLOR = new THREE.Color(0.64, 0.035, 0.055);
    const CIRCUMFERENCE = 2 * Math.PI * 46; // 289.026

    // --- State Variables ---
    let isLoaded = false;
    let hasMoved = false;

    let targetYaw = 0.0;
    let targetPitch = 0.0;
    let currentYaw = 0.0;
    let currentPitch = 0.0;
    let idleTime = 0.0;

    let mouseScreen = new THREE.Vector2(0.5, 0.5);
    let targetCursorWorld = new THREE.Vector2(512.0, 288.0);
    let currentCursorWorld = new THREE.Vector2(512.0, 288.0);

    let entranceTime = 0.0;
    let entranceSweep = -100.0;
    let entranceDone = false;

    let targetRevealProgress = 0.0;
    let revealProgress = 0.0; // 0.0 = dots mode, 1.0 = photo revealed

    // --- DOM Elements ---
    const canvas = document.getElementById('webgl-canvas');
    const preloader = document.getElementById('preloader');
    const ringBar = document.getElementById('ring-bar');
    const ringPct = document.getElementById('ring-pct');
    const uiContainer = document.getElementById('ui-container');
    const scrollIndicator = document.getElementById('scrollIndicator');
    const scrollThumb = document.getElementById('scrollThumb');
    const scrollLabel = document.getElementById('scrollLabel');
    const filmGrain = document.getElementById('film-grain');
    const heroStageEl = document.getElementById('hero');
    const navbarEl = document.getElementById('navbar');

    // Custom Cursor Elements
    const cursorDot = document.getElementById('custom-cursor-dot');
    const cursorRing = document.getElementById('custom-cursor-ring');
    let mouseX = -100, mouseY = -100;
    let ringX = -100, ringY = -100;

    // Generate animated film grain
    function initFilmGrain() {
      if (!filmGrain) return;
      const gCanvas = document.createElement('canvas');
      gCanvas.width = 128;
      gCanvas.height = 128;
      const gCtx = gCanvas.getContext('2d');
      const gImg = gCtx.createImageData(128, 128);
      for (let i = 0; i < 128 * 128 * 4; i += 4) {
        const val = (Math.random() * 255) | 0;
        gImg.data[i] = val;
        gImg.data[i+1] = val;
        gImg.data[i+2] = val;
        gImg.data[i+3] = 40;
      }
      gCtx.putImageData(gImg, 0, 0);
      filmGrain.style.backgroundImage = `url(${gCanvas.toDataURL()})`;
      filmGrain.style.backgroundRepeat = 'repeat';
    }
    initFilmGrain();

    // --- Three.js Setup ---
    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2.0));
    renderer.setSize(window.innerWidth, window.innerHeight);

    const scene = new THREE.Scene();

    // Orthographic Camera: portrait is 12% larger than fit-to-height
    const VISIBLE_HEIGHT = PHOTO_H / 1.12; // 514.2857
    const camera = new THREE.OrthographicCamera(
      -VISIBLE_HEIGHT / 2, VISIBLE_HEIGHT / 2,
      VISIBLE_HEIGHT / 2, -VISIBLE_HEIGHT / 2,
      0.1, 2000.0
    );
    camera.position.set(512.0, 288.0, 600.0);
    camera.lookAt(512.0, 288.0, 0.0);

    let visW = VISIBLE_HEIGHT * (window.innerWidth / window.innerHeight);
    let bannerMesh = null;

    function updateCamera() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      renderer.setSize(w, h);
      const aspect = w / h;
      visW = VISIBLE_HEIGHT * aspect;
      camera.left = -visW / 2.0;
      camera.right = visW / 2.0;
      camera.top = VISIBLE_HEIGHT / 2.0;
      camera.bottom = -VISIBLE_HEIGHT / 2.0;
      camera.updateProjectionMatrix();

      if (bannerMesh) {
        bannerMesh.geometry.dispose();
        bannerMesh.geometry = new THREE.PlaneGeometry(visW, 300);
      }
    }
    window.addEventListener('resize', updateCamera);
    updateCamera();

    // --- Materials & Shaders ---

    // 1. Photo Texture Loader
    const textureLoader = new THREE.TextureLoader();
    const photoTexture = textureLoader.load('./photo_cutout.png');
    photoTexture.minFilter = THREE.LinearFilter;
    photoTexture.magFilter = THREE.LinearFilter;
    photoTexture.generateMipmaps = false;

    // 2. Banner Canvas ([DEVELOPER] in Anton font)
    const bannerCanvas = document.createElement('canvas');
    bannerCanvas.width = 2048;
    bannerCanvas.height = 420;
    const bCtx = bannerCanvas.getContext('2d');
    
    function drawBannerText(isCrimson = 0.0) {
      bCtx.clearRect(0, 0, bannerCanvas.width, bannerCanvas.height);
      bCtx.font = '900 340px Anton, sans-serif';
      bCtx.textAlign = 'center';
      bCtx.textBaseline = 'middle';
      bCtx.letterSpacing = '-0.02em';
      
      const grad = bCtx.createLinearGradient(0, 40, 0, 380);
      if (isCrimson <= 0.01) {
        grad.addColorStop(0.0, 'rgba(160, 160, 170, 0.75)');
        grad.addColorStop(0.5, 'rgba(95, 95, 105, 0.40)');
        grad.addColorStop(1.0, 'rgba(15, 12, 18, 0.02)');
      } else {
        const c1 = THREE.MathUtils.lerp(160, 185, isCrimson);
        const c2 = THREE.MathUtils.lerp(160, 14, isCrimson);
        const c3 = THREE.MathUtils.lerp(170, 28, isCrimson);
        grad.addColorStop(0.0, `rgba(${c1|0}, ${c2|0}, ${c3|0}, 0.85)`);
        grad.addColorStop(0.5, `rgba(${(c1*0.45)|0}, ${(c2*0.4)|0}, ${(c3*0.4)|0}, 0.45)`);
        grad.addColorStop(1.0, 'rgba(8, 5, 10, 0.02)');
      }
      bCtx.fillStyle = grad;
      bCtx.fillText('[DEVELOPER]', bannerCanvas.width / 2, bannerCanvas.height / 2 + 10);
    }
    drawBannerText(0.0);

    const bannerTexture = new THREE.CanvasTexture(bannerCanvas);
    bannerTexture.minFilter = THREE.LinearFilter;

    // Banner Shader Material
    const bannerMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uTexture: { value: bannerTexture },
        uSweepY: { value: -200.0 },
        uRevealProgress: { value: 0.0 }
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vWorldPos;
        void main() {
          vUv = uv;
          vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D uTexture;
        uniform float uSweepY;
        uniform float uRevealProgress;
        varying vec2 vUv;
        varying vec3 vWorldPos;

        void main() {
          vec4 texColor = texture2D(uTexture, vUv);
          if (texColor.a < 0.01) discard;

          float sweepT = clamp((vWorldPos.y - uSweepY) / 50.0, 0.0, 1.0);
          vec3 crimson = vec3(0.68, 0.035, 0.055) * (1.0 - (1.0 - vUv.y) * 0.7);
          vec3 finalColor = mix(texColor.rgb, crimson, sweepT * uRevealProgress);
          float alpha = mix(texColor.a, texColor.a * 0.85, sweepT * uRevealProgress);

          gl_FragColor = vec4(finalColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false
    });

    const bannerGeo = new THREE.PlaneGeometry(visW, 300);
    bannerMesh = new THREE.Mesh(bannerGeo, bannerMaterial);
    bannerMesh.position.set(512.0, 315.0, -120.0);
    scene.add(bannerMesh);

    // 3. Photo Plane with Circular Grid Growing Reveal
    const photoMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uPhotoTexture: { value: photoTexture },
        uSweepY: { value: -100.0 },
        uRevealProgress: { value: 0.0 }
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vWorldPos;
        void main() {
          vUv = uv;
          vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D uPhotoTexture;
        uniform float uSweepY;
        uniform float uRevealProgress;
        varying vec2 vUv;
        varying vec3 vWorldPos;

        void main() {
          vec4 photoTex = texture2D(uPhotoTexture, vUv);
          if (photoTex.a < 0.02) discard;

          if (uRevealProgress <= 0.0001) {
            discard;
          }

          float S = 16.0;
          vec2 px = vec2(vUv.x * 1024.0, (1.0 - vUv.y) * 576.0);
          vec2 cellCenter = floor(px / S) * S + S * 0.5;
          float d = length(px - cellCenter);
          float maxRadius = S * 0.707106 * 1.08;

          float rowProgress = clamp((vWorldPos.y - uSweepY) / 36.0, 0.0, 1.0);
          if (uRevealProgress >= 0.999) {
            rowProgress = 1.0;
          }

          float curRadius = rowProgress * maxRadius;
          if (d > curRadius) {
            discard;
          }

          float edgeAlpha = smoothstep(curRadius, curRadius - 1.2, d);
          gl_FragColor = vec4(photoTex.rgb, photoTex.a * edgeAlpha);
        }
      `,
      transparent: true,
      depthWrite: false
    });

    const photoPlaneGeo = new THREE.PlaneGeometry(PHOTO_W, PHOTO_H);
    const photoPlane = new THREE.Mesh(photoPlaneGeo, photoMaterial);
    photoPlane.position.set(512.0, 288.0, -1.0);
    scene.add(photoPlane);

    // 4. Dust Particles
    const N_DUST = 700;
    const dustGeo = new THREE.BufferGeometry();
    const dustPos = new Float32Array(N_DUST * 3);
    const dustRand = new Float32Array(N_DUST);
    for (let i = 0; i < N_DUST; i++) {
      dustPos[i * 3 + 0] = 512.0 + (Math.random() - 0.5) * 1100.0;
      dustPos[i * 3 + 1] = 288.0 + (Math.random() - 0.5) * 650.0;
      dustPos[i * 3 + 2] = (Math.random() - 0.5) * 450.0;
      dustRand[i] = Math.random();
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    dustGeo.setAttribute('aRand', new THREE.BufferAttribute(dustRand, 1));

    const dustMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0.0 }
      },
      vertexShader: `
        attribute float aRand;
        uniform float uTime;
        varying float vAlpha;
        void main() {
          vec3 pos = position;
          pos.x += sin(uTime * 0.4 + aRand * 6.28) * 12.0;
          pos.y += cos(uTime * 0.3 + aRand * 6.28) * 15.0;
          pos.z += sin(uTime * 0.5 + aRand * 3.14) * 8.0;

          vAlpha = 0.15 + 0.35 * sin(uTime * 0.8 + aRand * 6.28);
          gl_PointSize = 1.5 + 2.0 * aRand;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        varying float vAlpha;
        void main() {
          float r = length(gl_PointCoord - vec2(0.5));
          if (r > 0.5) discard;
          float circle = smoothstep(0.5, 0.1, r);
          gl_FragColor = vec4(0.85, 0.4, 0.45, vAlpha * circle * 0.55);
        }
      `,
      blending: THREE.AdditiveBlending,
      transparent: true,
      depthWrite: false
    });
    const dustPoints = new THREE.Points(dustGeo, dustMaterial);
    scene.add(dustPoints);

    // 5. 78,000 Surface Dots Shader
    let dotsPoints = null;
    let dotsMaterial = null;

    function createDotsMesh(buffer) {
      const dataView = new Float32Array(buffer);
      const actualDots = (buffer.byteLength / 32) | 0;
      const count = Math.min(N_DOTS, actualDots);

      const pos = new Float32Array(count * 3);
      const ringPos = new Float32Array(count * 3);
      const normals = new Float32Array(count * 3);
      const randArr = new Float32Array(count);
      const brightArr = new Float32Array(count);

      const R_RING = 68.0;
      const RING_CX = 512.0;
      const RING_CY = 288.0;

      for (let i = 0; i < count; i++) {
        const offset = i * 8;
        const x = dataView[offset + 0];
        const y = dataView[offset + 1];
        const z = dataView[offset + 2];
        const nx = dataView[offset + 3];
        const ny = dataView[offset + 4];
        const nz = dataView[offset + 5];
        const rVal = dataView[offset + 6];
        const bVal = dataView[offset + 7];

        pos[i * 3 + 0] = x;
        pos[i * 3 + 1] = 576.0 - y;
        pos[i * 3 + 2] = z;

        normals[i * 3 + 0] = nx;
        normals[i * 3 + 1] = -ny;
        normals[i * 3 + 2] = nz;

        randArr[i] = rVal;
        brightArr[i] = bVal;

        const angle = rVal * Math.PI * 2.0;
        const radialOffset = (dataView[offset + 0] % 1.0 - 0.5) * 16.0;
        ringPos[i * 3 + 0] = RING_CX + (R_RING + radialOffset) * Math.cos(angle);
        ringPos[i * 3 + 1] = RING_CY + (R_RING + radialOffset) * Math.sin(angle);
        ringPos[i * 3 + 2] = (rVal - 0.5) * 14.0;
      }

      const dotsGeo = new THREE.BufferGeometry();
      dotsGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      dotsGeo.setAttribute('aRingPos', new THREE.BufferAttribute(ringPos, 3));
      dotsGeo.setAttribute('aNormal', new THREE.BufferAttribute(normals, 3));
      dotsGeo.setAttribute('aRand', new THREE.BufferAttribute(randArr, 1));
      dotsGeo.setAttribute('aBrightness', new THREE.BufferAttribute(brightArr, 1));

      dotsMaterial = new THREE.ShaderMaterial({
        uniforms: {
          uTime: { value: 0.0 },
          uYaw: { value: 0.0 },
          uPitch: { value: 0.0 },
          uCursorPos: { value: new THREE.Vector2(512.0, 288.0) },
          uEntranceTime: { value: 0.0 },
          uEntranceSweep: { value: -100.0 },
          uSweepY: { value: -200.0 },
          uRevealProgress: { value: 0.0 },
          uPhotoTexture: { value: photoTexture }
        },
        vertexShader: `
          attribute vec3 aRingPos;
          attribute vec3 aNormal;
          attribute float aRand;
          attribute float aBrightness;

          uniform float uTime;
          uniform float uYaw;
          uniform float uPitch;
          uniform float uEntranceTime;
          uniform float uSweepY;
          uniform float uRevealProgress;

          varying vec3 vNormal;
          varying vec3 vWorldPos;
          varying vec2 vPhotoUV;
          varying float vBrightness;
          varying float vRand;
          varying float vFlatten;

          const vec3 PIVOT = vec3(512.0, 290.0, 0.0);

          void main() {
            vBrightness = aBrightness;
            vRand = aRand;
            vPhotoUV = vec2(position.x / 1024.0, position.y / 576.0);

            float entT = clamp((uEntranceTime - aRand * 0.45) / 0.75, 0.0, 1.0);
            entT = 1.0 - pow(1.0 - entT, 3.0);
            vec3 sculptedPos = mix(aRingPos, position, entT);

            float flatten = 0.0;
            if (uRevealProgress > 0.0001) {
              flatten = clamp((sculptedPos.y - uSweepY) / 38.0, 0.0, 1.0);
            }
            vFlatten = flatten;
            sculptedPos.z = mix(sculptedPos.z, 0.0, flatten);

            float headWeight = smoothstep(120.0, 250.0, sculptedPos.y);
            float effYaw = uYaw * (0.22 + 0.78 * headWeight);
            float effPitch = uPitch * (0.20 + 0.80 * headWeight);

            vec3 p = sculptedPos - PIVOT;
            vec3 n = aNormal;

            float cx = cos(effPitch);
            float sx = sin(effPitch);
            mat3 rotX = mat3(
              1.0, 0.0, 0.0,
              0.0, cx, -sx,
              0.0, sx, cx
            );

            float cy = cos(effYaw);
            float sy = sin(effYaw);
            mat3 rotY = mat3(
              cy, 0.0, sy,
              0.0, 1.0, 0.0,
              -sy, 0.0, cy
            );

            p = rotY * rotX * p;
            n = rotY * rotX * n;

            vec3 worldPos = p + PIVOT;
            vWorldPos = worldPos;
            vNormal = normalize(n);

            float baseSize = 2.8 + 2.4 * aBrightness + 1.2 * aRand;
            baseSize *= mix(1.8, 1.0, entT);
            gl_PointSize = baseSize;

            gl_Position = projectionMatrix * modelViewMatrix * vec4(worldPos, 1.0);
          }
        `,
        fragmentShader: `
          uniform float uTime;
          uniform vec2 uCursorPos;
          uniform float uEntranceSweep;
          uniform float uSweepY;
          uniform float uRevealProgress;
          uniform sampler2D uPhotoTexture;

          varying vec3 vNormal;
          varying vec3 vWorldPos;
          varying vec2 vPhotoUV;
          varying float vBrightness;
          varying float vRand;
          varying float vFlatten;

          const vec3 CRIMSON = vec3(0.64, 0.035, 0.055);

          void main() {
            float r = length(gl_PointCoord - vec2(0.5));
            if (r > 0.5) discard;
            float circle = smoothstep(0.5, 0.06, r);

            vec3 L_key = normalize(vec3(-0.35, 0.55, 0.75));
            float key = max(0.0, dot(vNormal, L_key));
            float rim = pow(1.0 - max(0.0, abs(dot(vNormal, vec3(0.0, 0.0, 1.0)))), 2.4);

            float cursorDist = length(vWorldPos.xy - uCursorPos);
            float cursorLight = exp(-cursorDist * cursorDist / (2.0 * 165.0 * 165.0)) * 1.55;

            float ambient = 0.38;
            float lightIntensity = ambient + 0.58 * key + 0.32 * rim + cursorLight;
            float totalBright = (0.35 + 0.75 * vBrightness) * lightIntensity;

            vec3 dotColor = CRIMSON * (0.6 + 1.1 * totalBright);

            float entDist = abs(vWorldPos.y - uEntranceSweep);
            float entGlow = exp(-entDist * entDist / (2.0 * 22.0 * 22.0)) * 2.8;
            dotColor += vec3(0.85, 0.30, 0.35) * entGlow;

            vec4 photoColor = texture2D(uPhotoTexture, vPhotoUV);
            vec3 finalColor = mix(dotColor, photoColor.rgb, vFlatten);
            float dotAlpha = circle * mix(0.72 + 0.28 * vBrightness, 0.0, vFlatten);

            if (uRevealProgress > 0.001 && uRevealProgress < 0.999) {
              float revDist = abs(vWorldPos.y - uSweepY);
              float revGlow = exp(-revDist * revDist / (2.0 * 20.0 * 20.0)) * 2.2;
              finalColor += vec3(0.95, 0.45, 0.45) * revGlow;
              dotAlpha = max(dotAlpha, circle * revGlow * 0.9);
            }

            gl_FragColor = vec4(finalColor, dotAlpha);
          }
        `,
        blending: THREE.AdditiveBlending,
        transparent: true,
        depthWrite: false
      });

      dotsPoints = new THREE.Points(dotsGeo, dotsMaterial);
      scene.add(dotsPoints);
    }

    // --- Asset Loading with Real Progress ---
    async function loadDotData() {
      try {
        const response = await fetch('./dots.bin');
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);
        
        const contentLength = response.headers.get('content-length');
        const total = contentLength ? parseInt(contentLength, 10) : (N_DOTS * 32);
        
        const reader = response.body.getReader();
        let received = 0;
        const chunks = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
          received += value.length;
          
          const pct = Math.min(100, Math.round((received / total) * 100));
          const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
          if (ringBar) ringBar.style.strokeDashoffset = offset;
          if (ringPct) ringPct.textContent = `${pct}%`;
        }

        const allChunks = new Uint8Array(received);
        let pos = 0;
        for (const chunk of chunks) {
          allChunks.set(chunk, pos);
          pos += chunk.length;
        }

        if (ringBar) ringBar.style.strokeDashoffset = 0;
        if (ringPct) ringPct.textContent = '100%';

        createDotsMesh(allChunks.buffer);

        setTimeout(() => {
          if (preloader) preloader.classList.add('hidden');
          if (scrollIndicator) {
            scrollIndicator.style.opacity = '1';
            scrollIndicator.style.pointerEvents = 'auto';
          }
          isLoaded = true;
        }, 350);

      } catch (err) {
        console.error("Error loading dot buffer:", err);
        if (ringPct) ringPct.textContent = 'Err';
      }
    }
    loadDotData();

    // --- Full Page Custom Cursor & 3D Interactive Spotlight Engine ---
    window.addEventListener('mousemove', (e) => {
      hasMoved = true;
      mouseX = e.clientX;
      mouseY = e.clientY;
      mouseScreen.x = mouseX / window.innerWidth;
      mouseScreen.y = mouseY / window.innerHeight;

      // Update Custom Cursor Dot directly
      if (cursorDot) {
        cursorDot.style.left = `${mouseX}px`;
        cursorDot.style.top = `${mouseY}px`;
      }

      // Update full page cursor spotlight position
      document.documentElement.style.setProperty('--mouse-x', `${mouseX}px`);
      document.documentElement.style.setProperty('--mouse-y', `${mouseY}px`);

      if (revealProgress < 0.95) {
        const nx = (mouseScreen.x - 0.5) * 2.0;
        const ny = (mouseScreen.y - 0.5) * 2.0;

        targetYaw = nx * 0.523;
        targetPitch = -ny * 0.261;

        const aspect = window.innerWidth / window.innerHeight;
        const visW = VISIBLE_HEIGHT * aspect;
        const worldX = 512.0 + (mouseScreen.x - 0.5) * visW;
        const worldY = 288.0 - (mouseScreen.y - 0.5) * VISIBLE_HEIGHT;
        targetCursorWorld.set(worldX, worldY);
      }
    });

    // Animate trailing ring with smooth interpolation
    function updateCursorRing() {
      ringX += (mouseX - ringX) * 0.22;
      ringY += (mouseY - ringY) * 0.22;
      if (cursorRing) {
        cursorRing.style.left = `${ringX.toFixed(1)}px`;
        cursorRing.style.top = `${ringY.toFixed(1)}px`;
      }
      requestAnimationFrame(updateCursorRing);
    }
    requestAnimationFrame(updateCursorRing);

    // Hover detection on interactive elements
    document.addEventListener('mouseover', (e) => {
      const target = e.target.closest('a, button, input, textarea, select, [role="button"], .badge-card, .project-card, .scroll-indicator, .tilt-card');
      if (target) {
        document.body.classList.add('cursor-hover');
      } else {
        document.body.classList.remove('cursor-hover');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.add('cursor-active');
    });

    document.addEventListener('mouseup', () => {
      document.body.classList.remove('cursor-active');
    });

    document.addEventListener('mouseleave', () => {
      if (cursorDot) cursorDot.style.opacity = '0';
      if (cursorRing) cursorRing.style.opacity = '0';
    });
    document.addEventListener('mouseenter', () => {
      if (cursorDot) cursorDot.style.opacity = '1';
      if (cursorRing) cursorRing.style.opacity = '1';
    });

    // 3D Card Interactive Tilt for Bento Grid
    function initCardTilt() {
      const cards = document.querySelectorAll('.project-card, .badge-card, .spec-card, .hero-intro-card');
      cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          const rotateX = ((y - centerY) / centerY) * -5.0;
          const rotateY = ((x - centerX) / centerX) * 5.0;
          card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.015, 1.015, 1.015)`;
        });
        card.addEventListener('mouseleave', () => {
          card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
      });
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initCardTilt);
    } else {
      initCardTilt();
    }

    // --- Pinned Scroll Gating: First photo scrolls fully, then full website scrolls ---
    // --- Navbar is HIDDEN during photo scrolling, and becomes visible AFTER reveal ---
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      
      const revealDistance = vh * 1.0;

      if (scrollY <= 0) {
        targetRevealProgress = 0.0;
      } else if (scrollY < revealDistance) {
        targetRevealProgress = scrollY / revealDistance;
      } else {
        targetRevealProgress = 1.0;
      }

      // Dynamic Navbar Visibility:
      // When scrollY < revealDistance * 0.95: navbar is HIDDEN
      // When scrollY >= revealDistance * 0.95: navbar is VISIBLE
      if (navbarEl) {
        if (scrollY < revealDistance * 0.92) {
          navbarEl.classList.add('navbar-hidden');
        } else {
          navbarEl.classList.remove('navbar-hidden');
        }
      }

      // Scroll indicator updates or hides once user scrolls into the website sections
      if (uiContainer) {
        const trackHeight = heroStageEl ? heroStageEl.offsetHeight : (vh * 2.4);
        if (scrollY > trackHeight - vh * 0.3) {
          uiContainer.style.opacity = '0';
          uiContainer.style.pointerEvents = 'none';
        } else {
          uiContainer.style.opacity = '1';
          uiContainer.style.pointerEvents = 'auto';
        }
      }
    }

    window.addEventListener('scroll', updateHeroScrollState, { passive: true });
    window.addEventListener('resize', updateHeroScrollState, { passive: true });

    // Initial check on load: ensure navbar is hidden at top
    updateHeroScrollState();

    // Scroll Indicator Click Action
    if (scrollIndicator) {
      scrollIndicator.addEventListener('click', () => {
        if (!isLoaded) return;
        const vh = window.innerHeight;
        if (window.scrollY < vh * 0.8) {
          window.scrollTo({ top: vh * 1.0, behavior: 'smooth' });
        } else {
          const introSec = document.getElementById('intro') || document.getElementById('projects');
          if (introSec) {
            introSec.scrollIntoView({ behavior: 'smooth' });
          } else {
            window.scrollTo({ top: vh * 2.4, behavior: 'smooth' });
          }
        }
      });
    }

    // --- Main Animation Loop ---
    let lastTime = performance.now();

    function animate(now) {
      requestAnimationFrame(animate);

      const dt = Math.min((now - lastTime) / 1000.0, 0.1);
      lastTime = now;

      if (!isLoaded || !dotsMaterial) {
        renderer.render(scene, camera);
        return;
      }

      idleTime += dt;
      dotsMaterial.uniforms.uTime.value = idleTime;
      dustMaterial.uniforms.uTime.value = idleTime;

      // 1. Entrance Flight & Light Sweep Choreography
      if (!entranceDone) {
        entranceTime += dt * 0.95;
        dotsMaterial.uniforms.uEntranceTime.value = entranceTime;

        if (entranceTime >= 1.15) {
          entranceSweep += dt * 550.0;
          dotsMaterial.uniforms.uEntranceSweep.value = entranceSweep;
          if (entranceSweep > 650.0) {
            entranceDone = true;
            dotsMaterial.uniforms.uEntranceSweep.value = -200.0;
          }
        }
      }

      // 2. Idle Drift before first mouse move
      if (!hasMoved && revealProgress < 0.1) {
        targetYaw = Math.sin(idleTime * 0.75) * 0.07;
        targetPitch = Math.cos(idleTime * 0.55) * 0.04;
      }

      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;
      if (Math.abs(targetRevealProgress - revealProgress) < 0.0005) {
        revealProgress = targetRevealProgress;
      }

      // Update scroll indicator UI dynamically
      if (scrollThumb && scrollLabel) {
        scrollThumb.style.width = `${(revealProgress * 100).toFixed(1)}%`;
        if (revealProgress <= 0.04) {
          scrollLabel.textContent = 'Scroll to reveal photo';
        } else if (revealProgress >= 0.96) {
          scrollLabel.textContent = 'Photo revealed • Scroll for website ↓';
        } else {
          scrollLabel.textContent = `Revealing... ${(revealProgress * 100).toFixed(0)}%`;
        }
      }

      // Sweep moves from top (Y=610) to bottom (Y=-40) in Three.js coords
      const sweepY = THREE.MathUtils.lerp(610.0, -40.0, revealProgress);

      dotsMaterial.uniforms.uSweepY.value = sweepY;
      dotsMaterial.uniforms.uRevealProgress.value = revealProgress;

      photoMaterial.uniforms.uSweepY.value = sweepY;
      photoMaterial.uniforms.uRevealProgress.value = revealProgress;

      bannerMaterial.uniforms.uSweepY.value = sweepY;
      bannerMaterial.uniforms.uRevealProgress.value = revealProgress;

      // Cursor tracking & head turn:
      const trackingFactor = Math.max(0.0, 1.0 - revealProgress * 1.6);
      const easeFactor = 0.06;
      currentYaw += (targetYaw * trackingFactor - currentYaw) * easeFactor;
      currentPitch += (targetPitch * trackingFactor - currentPitch) * easeFactor;
      currentCursorWorld.lerp(targetCursorWorld, easeFactor);

      dotsMaterial.uniforms.uYaw.value = currentYaw;
      dotsMaterial.uniforms.uPitch.value = currentPitch;
      dotsMaterial.uniforms.uCursorPos.value.copy(currentCursorWorld);

      renderer.render(scene, camera);
    }

    requestAnimationFrame(animate);
  </script>
</body>
"""

html = html.replace("</body>", webgl_scripts)

# 7. Write to both Personal/index.html and PORTFOLIO/index.html
with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully generated LUXURY DARK {PERSONAL_HTML} (size: {len(html)} bytes)")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully generated LUXURY DARK {PORTFOLIO_HTML} (size: {len(html)} bytes)")
