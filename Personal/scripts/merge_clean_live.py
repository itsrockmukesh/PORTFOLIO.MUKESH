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

# 2. Inject Anton Font and WebGL Hero Styles into <head>
hero_css = """
  <!-- Anton Font & 3D WebGL Pinned Scroll Hero Styles -->
  <style>
    @font-face {
      font-family: 'Anton';
      src: url('./anton.woff2') format('woff2');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      overflow-x: clip !important;
    }

    /* Pinned Scroll Track: Gives 150vh of dedicated scroll distance for dot-to-photo reveal */
    .hero-scroll-track {
      position: relative;
      width: 100%;
      height: 240vh;
      background: #060408;
    }

    /* Pinned stage: stays locked at top:0 during the reveal scroll */
    .hero-sticky-stage {
      position: sticky;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      z-index: 2;
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
      padding: 12px 26px;
      background: rgba(18, 12, 16, 0.76);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(163, 14, 25, 0.42);
      border-radius: 9999px;
      color: rgba(255, 255, 255, 0.92);
      font-size: 0.84rem;
      font-weight: 500;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.6), 0 0 14px rgba(163, 14, 25, 0.3);
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
      user-select: none;
    }

    .scroll-indicator:hover {
      background: rgba(30, 16, 22, 0.92);
      border-color: rgba(210, 20, 36, 0.75);
      transform: translateY(-2px);
      box-shadow: 0 6px 28px rgba(0, 0, 0, 0.7), 0 0 20px rgba(163, 14, 25, 0.5);
    }

    .scroll-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #d21424;
      box-shadow: 0 0 8px #d21424;
      animation: pulse-dot 2s infinite;
    }

    @keyframes pulse-dot {
      0%, 100% { opacity: 0.45; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.15); }
    }

    .scroll-progress-bar {
      width: 52px;
      height: 4px;
      background: rgba(255, 255, 255, 0.14);
      border-radius: 2px;
      overflow: hidden;
    }

    .scroll-progress-thumb {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #a30e19, #e5283b);
      transition: width 0.12s linear;
    }

    /* ==========================================================================
       HERO INTRO SECTION ("HII IAM MUKESH KUMAR") - LOCATED BELOW THE PHOTO
       ========================================================================== */
    .hero-intro-section {
      position: relative;
      z-index: 10;
      background: var(--bg-black, #0a0a0c);
      padding: 6rem 1.5rem 4.5rem 1.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      position: relative;
    }

    .hero-intro-section::before {
      content: '';
      position: absolute;
      top: -1px;
      left: 50%;
      transform: translateX(-50%);
      width: 320px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(163, 14, 25, 0.8), transparent);
    }

    .hero-intro-card {
      max-width: 880px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    .hero-intro-card .hero-status-tag {
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.45rem 1.15rem;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.10);
      border-radius: 9999px;
      font-family: var(--font-mono);
      font-size: 0.86rem;
      color: var(--text-secondary);
      margin-bottom: 1.6rem;
    }

    .hero-intro-card .hero-statement-title {
      font-size: clamp(2.4rem, 5vw, 3.8rem);
      font-weight: 700;
      letter-spacing: -0.04em;
      line-height: 1.15;
      margin-bottom: 1.25rem;
      color: var(--text-primary);
    }

    .hero-intro-card .hero-typewriter-bar {
      font-family: var(--font-mono);
      font-size: clamp(0.92rem, 1.4vw, 1.12rem);
      color: var(--accent-cyan, #00f0ff);
      margin-bottom: 1.6rem;
      min-height: 1.8rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
    }

    .hero-intro-card .hero-subtitle {
      font-size: clamp(1.02rem, 1.35vw, 1.15rem);
      line-height: 1.75;
      color: var(--text-secondary, #94949e);
      max-width: 740px;
      margin: 0 auto 2.4rem auto;
    }

    .hero-intro-card .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      justify-content: center;
      align-items: center;
    }

    /* Ensure lower sections scroll smoothly over with a solid dark backdrop */
    .ticker-section,
    #projects,
    #about,
    #achievements,
    #aws-showcase,
    #contact,
    footer {
      position: relative;
      z-index: 10;
      background: var(--bg-black, #0a0a0c);
    }
  </style>
</head>
"""

html = html.replace("</head>", hero_css)

# 3. Replace <section class="hero" id="hero"> with:
#    (A) The clean 3D Pinned Hero Stage (photo & bust ONLY, no overlapping text!)
#    (B) The "Hii I am Mukesh Kumar" intro section placed BELOW the photo!
hero_replacement = """
  <!-- ==========================================================================
       HERO STAGE: PINNED 3D WEBGL BUST & FULL SCROLL REVEAL (CLEAN PHOTO STAGE)
       When you scroll: First photo is scrolled fully (0 -> 100%), then full website scrolls!
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

  <!-- ==========================================================================
       HERO INTRO SECTION: "HI, I'M MUKESH KUMAR" (PLACED BELOW THE PHOTO)
       ========================================================================== -->
  <section class="hero-intro-section" id="intro">
    <div class="container">
      <div class="hero-intro-card">
        <div class="hero-status-tag">
          <span class="status-pulse"></span>
          <span>1st Year BE-CSE • Mirai School of Technology</span>
        </div>

        <h1 class="hero-statement-title">
          Hi, I'm Mukesh Kumar.<br>
          <span class="hero-title-highlight">I build for the web &amp; cloud.</span>
        </h1>

        <div class="hero-typewriter-bar">
          <span id="typewriter-text"></span>
          <span class="typewriter-cursor"></span>
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

# 4. Inject three.min.js and WebGL Script before </body>
webgl_scripts = """
  <!-- Three.js Library -->
  <script src="./three.min.js"></script>

  <!-- 3D Crimson Surface Bust, Interactive Cursor Light, and Pinned Scroll Engine -->
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

    // --- Cursor & Interaction Handling ---
    window.addEventListener('mousemove', (e) => {
      hasMoved = true;
      mouseScreen.x = e.clientX / window.innerWidth;
      mouseScreen.y = e.clientY / window.innerHeight;

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

    // --- Pinned Scroll Gating: First photo scrolls fully, then full website scrolls ---
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      
      // Reveal distance: Exactly 1.0 * vh
      // While scrollY <= revealDistance: sticky stage stays pinned at top:0, photo reveals 0% -> 100%
      const revealDistance = vh * 1.0;

      if (scrollY <= 0) {
        targetRevealProgress = 0.0;
      } else if (scrollY < revealDistance) {
        targetRevealProgress = scrollY / revealDistance;
      } else {
        targetRevealProgress = 1.0;
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

# 5. Write to both Personal/index.html and PORTFOLIO/index.html
with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully generated {PERSONAL_HTML} (size: {len(html)} bytes)")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully generated {PORTFOLIO_HTML} (size: {len(html)} bytes)")
