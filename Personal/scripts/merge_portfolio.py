import os
import re

PORTFOLIO_DIR = "/Users/mukeshkumar/PORTFOLIO"
PERSONAL_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal"

print("Reading PORTFOLIO/index.html...")
with open(os.path.join(PORTFOLIO_DIR, "index.html"), "r", encoding="utf-8") as f:
    portfolio_html = f.read()

print("Reading Personal/index.html...")
with open(os.path.join(PERSONAL_DIR, "index.html"), "r", encoding="utf-8") as f:
    personal_html = f.read()

# 1. Clean up original portfolio_html:
# Remove game-start-gate script and markup if present, so the 3D WebGL hero is the primary grand opening
portfolio_html = re.sub(r'<script>[\s\S]*?window\.enterGameRealm[\s\S]*?</script>', '', portfolio_html)
portfolio_html = re.sub(r'<!--\s*=*\s*CINEMATIC GAME OPENING SCREEN[\s\S]*?id="game-start-gate"[\s\S]*?</div>\s*</div>\s*</div>', '', portfolio_html)

# Also remove any previous injected hero-stage or extra scripts if re-running
portfolio_html = re.sub(r'<!--\s*=*\s*FULL-SCREEN 3D WEBGL HERO[\s\S]*?<!--\s*=*\s*INFINITE MARQUEE TICKER', '<!-- INFINITE MARQUEE TICKER', portfolio_html)
portfolio_html = re.sub(r'<!--\s*=*\s*HERO SECTION[\s\S]*?<!--\s*=*\s*INFINITE MARQUEE TICKER', '<!-- INFINITE MARQUEE TICKER', portfolio_html)

# 2. Extract WebGL Three.js script from personal_html
script_start = personal_html.find("<script>")
script_end = personal_html.rfind("</script>")
webgl_script_content = personal_html[script_start + 8 : script_end].strip()

# 3. Create Hero Stage Section in HTML
hero_stage_html = """
  <!-- ==========================================================================
       FULL-SCREEN 3D WEBGL HERO & SCROLL REVEAL STAGE
       ========================================================================== -->
  <div id="hero" class="hero-stage">
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

    <!-- Hero HUD Content Overlay -->
    <div class="hero-hud-overlay">
      <div class="hero-hud-top-left">
        <div class="hero-status-tag">
          <span class="status-pulse"></span>
          <span>PLAYER_01 // LVL 01 BE-CSE • Mirai School of Technology</span>
        </div>
      </div>

      <div class="hero-hud-bottom-content">
        <div class="hero-headline-wrap">
          <h1 class="hero-statement-title">
            Hi, I'm Mukesh Kumar.<br>
            <span class="hero-title-highlight">Leveling up in Web &amp; Cloud.</span>
          </h1>

          <div class="hero-typewriter-bar">
            <span id="typewriter-text"></span>
            <span class="typewriter-cursor"></span>
          </div>

          <!-- RPG Stats Bar -->
          <div class="game-stats-row" style="margin: 0.8rem 0 1.1rem 0;">
            <div class="stat-pill"><span class="stat-label">HP:</span> <span class="stat-val" style="color:#00FF88;">100% CLEAN CODE</span></div>
            <div class="stat-pill"><span class="stat-label">MP:</span> <span class="stat-val" style="color:#00F0FF;">100% C++ LOGIC</span></div>
            <div class="stat-pill"><span class="stat-label">EXP:</span> <span class="stat-val" style="color:#FF9900;">2,450 / 3,000</span></div>
          </div>

          <div class="hero-actions">
            <a href="#about" class="btn-pill btn-pill-primary">
              <span>👤 Profile &amp; Bio</span>
              <span class="btn-arrow">↓</span>
            </a>
            <a href="#projects" class="btn-pill btn-pill-secondary">
              <span>⚔️ View Missions</span>
            </a>
            <button id="hero-hack-trigger" class="btn-pill btn-pill-hack">
              <span>🎮 Play Cyber Hack 🔒</span>
            </button>
            <button class="btn-pill btn-pill-secondary trigger-resume-modal">
              <span>📜 Dossier</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll Reveal Indicator -->
    <div id="ui-container">
      <div id="scrollIndicator" class="scroll-indicator" style="opacity: 0; pointer-events: none;">
        <div class="scroll-track">
          <div id="scrollThumb" class="scroll-thumb"></div>
        </div>
        <span id="scrollLabel" class="scroll-label">Scroll to reveal photo</span>
      </div>
    </div>
  </div>
"""

# Insert hero_stage_html right before <!-- INFINITE MARQUEE TICKER
marker = "<!-- INFINITE MARQUEE TICKER"
idx = portfolio_html.find(marker)
if idx != -1:
    portfolio_merged = portfolio_html[:idx] + hero_stage_html + "\n\n  <!-- ==========================================================================\n       INFINITE MARQUEE TICKER\n       ========================================================================== -->\n  " + portfolio_html[idx:]
else:
    # Try finding ticker-section
    idx = portfolio_html.find('<div class="ticker-section">')
    portfolio_merged = portfolio_html[:idx] + hero_stage_html + "\n\n  " + portfolio_html[idx:]

# 4. Insert WebGL CSS into <head> (remove previous extra_css if present)
portfolio_merged = re.sub(r'<!--\s*=*\s*Anton Font for 3D Banner[\s\S]*?</style>', '', portfolio_merged)

extra_css = """
  <!-- Anton Font for 3D Banner & WebGL Hero Styles -->
  <style>
    @font-face {
      font-family: 'Anton';
      src: url('./anton.woff2') format('woff2');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }

    .hero-stage {
      position: relative;
      width: 100%;
      height: 190vh; /* Scroll track for 3D dot-to-photo reveal */
      background: #060408;
    }

    #webgl-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 1;
      pointer-events: auto;
      transition: opacity 0.4s ease;
    }

    #film-grain {
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 3;
      opacity: 0.16;
      mix-blend-mode: overlay;
      transition: opacity 0.4s ease;
    }

    /* Preloader Ring */
    #preloader {
      position: fixed;
      inset: 0;
      background: #070508;
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
      filter: drop-shadow(0 0 8px rgba(163, 14, 25, 0.6));
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
      color: rgba(255, 255, 255, 0.9);
      font-variant-numeric: tabular-nums;
    }

    /* Scroll Indicator */
    #ui-container {
      position: fixed;
      bottom: 34px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 30;
      pointer-events: auto;
      transition: opacity 0.4s ease, transform 0.4s ease;
    }

    .scroll-indicator {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 11px 24px;
      background: rgba(18, 12, 16, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(163, 14, 25, 0.38);
      border-radius: 9999px;
      color: rgba(255, 255, 255, 0.92);
      font-size: 0.82rem;
      font-weight: 500;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.55), 0 0 14px rgba(163, 14, 25, 0.25);
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
      user-select: none;
    }

    .scroll-indicator:hover {
      background: rgba(28, 15, 20, 0.92);
      border-color: rgba(210, 20, 36, 0.65);
      transform: translateY(-2px);
      box-shadow: 0 6px 30px rgba(0, 0, 0, 0.65), 0 0 20px rgba(163, 14, 25, 0.45);
    }

    .scroll-track {
      width: 36px;
      height: 4px;
      background: rgba(255, 255, 255, 0.18);
      border-radius: 2px;
      overflow: hidden;
      position: relative;
    }

    .scroll-thumb {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 0%;
      background: #e21c32;
      border-radius: 2px;
      box-shadow: 0 0 8px #e21c32;
      transition: width 0.08s linear;
    }

    .scroll-label {
      font-size: 0.80rem;
      letter-spacing: 0.09em;
    }

    /* Hero HUD Overlay */
    .hero-hud-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100vh;
      pointer-events: none;
      z-index: 20;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: calc(var(--nav-height) + 1.25rem) 2.5rem 6.5rem 2.5rem;
      box-sizing: border-box;
      transition: opacity 0.4s ease;
    }

    .hero-hud-overlay * {
      pointer-events: auto;
    }

    .hero-headline-wrap {
      max-width: 520px;
      background: rgba(10, 8, 12, 0.60);
      padding: 1.5rem 2rem;
      border-radius: 20px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }

    .hero-headline-wrap .hero-statement-title {
      font-size: clamp(1.8rem, 3.2vw, 2.5rem);
      margin-bottom: 0.5rem;
    }

    /* Content sections flow smoothly above canvas */
    main > section, .ticker-section {
      position: relative;
      z-index: 10;
      background: var(--bg-black);
    }

    @media (max-width: 768px) {
      .hero-hud-overlay {
        padding: calc(var(--nav-height) + 1rem) 1rem 5.5rem 1rem;
      }
      .hero-headline-wrap {
        max-width: 100%;
        padding: 1.2rem;
      }
    }
  </style>
"""

head_end = portfolio_merged.find("</head>")
portfolio_merged = portfolio_merged[:head_end] + extra_css + portfolio_merged[head_end:]

# 5. Remove any previous WebGL Three.js script injection before injecting clean version
portfolio_merged = re.sub(r'<!--\s*Three\.js Library[\s\S]*?<!--\s*WebGL 3D Bust Dots[\s\S]*?</script>', '', portfolio_merged)

# Add robust scroll logic with uiContainer properly defined
unified_webgl_code = webgl_script_content.replace(
    "const filmGrain = document.getElementById('film-grain');",
    """const filmGrain = document.getElementById('film-grain');
    const uiContainer = document.getElementById('ui-container');
    const heroStageEl = document.getElementById('hero');
    const heroHudEl = document.querySelector('.hero-hud-overlay');
    const webglCanvasEl = document.getElementById('webgl-canvas');"""
)

# Update scroll listener in WebGL code
old_scroll_code = """    // --- Scroll & Gesture Driven Reveal ---
    // 1. Mouse wheel / trackpad scrolling
    window.addEventListener('wheel', (e) => {
      if (!isLoaded) return;
      // Smooth natural scroll progression
      const delta = e.deltaY * 0.0012;
      targetRevealProgress = THREE.MathUtils.clamp(targetRevealProgress + delta, 0.0, 1.0);
    }, { passive: true });"""

new_scroll_code = """    // --- Unified Scroll & Gesture Driven Reveal ---
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      const revealEnd = vh * 0.95;  // By 95% of viewport height, photo is 100% revealed
      const stageEnd = vh * 1.55;  // Past 155vh, scroll smoothly into About Me

      // 1. Map scroll within hero track to revealProgress [0.0 .. 1.0]
      if (scrollY <= revealEnd) {
        targetRevealProgress = Math.min(1.0, Math.max(0.0, scrollY / revealEnd));
      } else {
        targetRevealProgress = 1.0;
      }

      // 2. Manage canvas visibility and interaction when scrolling past the hero
      if (scrollY >= stageEnd) {
        if (webglCanvasEl) {
          webglCanvasEl.style.opacity = '0';
          webglCanvasEl.style.pointerEvents = 'none';
        }
        if (filmGrain) filmGrain.style.opacity = '0';
        if (uiContainer) uiContainer.style.opacity = '0';
        if (heroHudEl) heroHudEl.style.opacity = '0';
      } else {
        if (webglCanvasEl) {
          const fadeOut = Math.max(0.0, Math.min(1.0, 1.0 - (scrollY - revealEnd) / (stageEnd - revealEnd)));
          webglCanvasEl.style.opacity = fadeOut.toFixed(2);
          webglCanvasEl.style.pointerEvents = scrollY < revealEnd ? 'auto' : 'none';
        }
        if (filmGrain) filmGrain.style.opacity = '0.16';
        if (uiContainer) uiContainer.style.opacity = '1';
        if (heroHudEl) {
          const hudFade = Math.max(0.0, Math.min(1.0, 1.0 - scrollY / (vh * 0.45)));
          heroHudEl.style.opacity = hudFade.toFixed(2);
          heroHudEl.style.pointerEvents = hudFade > 0.1 ? 'auto' : 'none';
        }
      }
    }

    window.addEventListener('scroll', updateHeroScrollState, { passive: true });
    window.addEventListener('resize', updateHeroScrollState, { passive: true });

    // Also support mouse wheel directly for instant response
    window.addEventListener('wheel', (e) => {
      if (!isLoaded) return;
      if (window.scrollY < window.innerHeight * 1.2) {
        const delta = e.deltaY * 0.0012;
        targetRevealProgress = THREE.MathUtils.clamp(targetRevealProgress + delta, 0.0, 1.0);
      }
    }, { passive: true });"""

unified_webgl_code = unified_webgl_code.replace(old_scroll_code, new_scroll_code)

adapted_webgl_js = f"""
  <!-- Three.js Library -->
  <script src="./three.min.js"></script>

  <!-- WebGL 3D Bust Dots & Scroll-Driven Reveal Engine -->
  <script>
{unified_webgl_code}
  </script>
"""

body_end = portfolio_merged.rfind("</body>")
portfolio_merged = portfolio_merged[:body_end] + "\n" + adapted_webgl_js + "\n" + portfolio_merged[body_end:]

# 6. Save clean merged HTML
dest_portfolio = os.path.join(PORTFOLIO_DIR, "index.html")
dest_personal = os.path.join(PERSONAL_DIR, "index.html")

with open(dest_portfolio, "w", encoding="utf-8") as f:
    f.write(portfolio_merged)
print(f"Saved merged portfolio to {dest_portfolio} ({os.path.getsize(dest_portfolio)/1024:.1f} KB)")

with open(dest_personal, "w", encoding="utf-8") as f:
    f.write(portfolio_merged)
print(f"Saved copy to {dest_personal} ({os.path.getsize(dest_personal)/1024:.1f} KB)")
