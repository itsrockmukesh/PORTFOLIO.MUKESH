/**
 * Secret Developer Terminal Engine
 * Interactive retro/cyber terminal for AWS Student Portfolio Hackathon
 * Tailored for Mukesh Kumar (1st Year BE-CSE, Mirai School of Technology)
 */

(function() {
  // DOM Elements
  const modalOverlay = document.getElementById('terminal-modal');
  const terminalWindow = document.querySelector('.terminal-window');
  const commandLog = document.getElementById('terminal-log');
  const cliInput = document.getElementById('terminal-input');
  const closeBtn = document.getElementById('term-close-btn');
  const maxBtn = document.getElementById('term-max-btn');
  const clearToolBtn = document.getElementById('term-clear-btn');
  const copyToolBtn = document.getElementById('term-copy-btn');
  const hintTrigger = document.getElementById('terminal-hint-trigger');
  const navTrigger = document.getElementById('nav-terminal-trigger');
  const heroTrigger = document.getElementById('hero-terminal-trigger');
  const quickChips = document.querySelectorAll('.term-chip-btn');

  if (!modalOverlay || !cliInput) return;

  // Command History State
  let commandHistory = [];
  let historyIndex = -1;

    // ==========================================================================
  // CINEMATIC TERMINAL SOUND SYSTEM (Web Audio API)
  // High-impact sub-bass BOOM on open, crisp mechanical keyboard typing sounds
  // ==========================================================================
  let audioCtx = null;

  function getAudioContext() {
    if (window.CyberAudio && window.CyberAudio.context) {
      if (window.CyberAudio.context.state === 'suspended') {
        window.CyberAudio.unlock();
      }
      return window.CyberAudio.context;
    }
    if (!audioCtx) {
      audioCtx = window.scrollAudioCtx || new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playBeep(freq = 600, duration = 0.05, type = 'sine') {
    if (window.portfolioAudioMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {}
  }

  // Cinematic Sci-Fi Terminal Open Boom Sound
  function playTerminalBoomSound() {
    if (window.portfolioAudioMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;

      // 1. Heavy Sub-Bass Cinematic Boom (145Hz -> 28Hz over 0.78s)
      const subOsc = ctx.createOscillator();
      const subGain = ctx.createGain();
      subOsc.type = 'sine';
      subOsc.frequency.setValueAtTime(145, now);
      subOsc.frequency.exponentialRampToValueAtTime(28, now + 0.75);

      subGain.gain.setValueAtTime(0.24, now);
      subGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.78);

      subOsc.connect(subGain);
      subGain.connect(ctx.destination);
      subOsc.start(now);
      subOsc.stop(now + 0.8);

      // 2. Punch Transient / Mechanical Slam (240Hz -> 45Hz over 0.07s)
      const punchOsc = ctx.createOscillator();
      const punchGain = ctx.createGain();
      punchOsc.type = 'triangle';
      punchOsc.frequency.setValueAtTime(240, now);
      punchOsc.frequency.exponentialRampToValueAtTime(45, now + 0.065);

      punchGain.gain.setValueAtTime(0.18, now);
      punchGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.07);

      punchOsc.connect(punchGain);
      punchGain.connect(ctx.destination);
      punchOsc.start(now);
      punchOsc.stop(now + 0.075);

      // 3. Shockwave Air Sweep (Filtered Noise Burst sweeping down)
      const bufferSize = Math.floor(ctx.sampleRate * 0.45);
      const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        output[i] = (Math.random() * 2 - 1) * 0.12;
      }
      const noiseSource = ctx.createBufferSource();
      noiseSource.buffer = noiseBuffer;

      const noiseFilter = ctx.createBiquadFilter();
      noiseFilter.type = 'lowpass';
      noiseFilter.frequency.setValueAtTime(2200, now);
      noiseFilter.frequency.exponentialRampToValueAtTime(120, now + 0.42);

      const noiseGain = ctx.createGain();
      noiseGain.gain.setValueAtTime(0.14, now);
      noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.44);

      noiseSource.connect(noiseFilter);
      noiseFilter.connect(noiseGain);
      noiseGain.connect(ctx.destination);
      noiseSource.start(now);
      noiseSource.stop(now + 0.45);

      // 4. Futuristic High-Tech Resonance Shimmer (1350Hz -> 480Hz)
      const cyberOsc = ctx.createOscillator();
      const cyberGain = ctx.createGain();
      cyberOsc.type = 'sine';
      cyberOsc.frequency.setValueAtTime(1350, now);
      cyberOsc.frequency.exponentialRampToValueAtTime(480, now + 0.28);

      cyberGain.gain.setValueAtTime(0.045, now);
      cyberGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);

      cyberOsc.connect(cyberGain);
      cyberGain.connect(ctx.destination);
      cyberOsc.start(now);
      cyberOsc.stop(now + 0.3);

    } catch (e) {
      console.warn("Terminal boom error:", e);
    }
  }

    // ==========================================================================
  // UNIVERSAL MECHANICAL KEYBOARD CLICK ENGINE (Web Audio API)
  // Produces instant, crisp, tactile switch clicks on EVERY key of the keyboard
  // ==========================================================================
  let lastKeyTime = 0;

  function playKeyboardClickSound(key = 'a') {
    if (window.portfolioAudioMuted) return;
    const nowMs = performance.now();
    if (nowMs - lastKeyTime < 10) return; // Prevent audio buffer saturation on hyper-fast repeat
    lastKeyTime = nowMs;

    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const t = ctx.currentTime;

      // Random micro-pitch jitter (±6%) gives authentic physical variance to each switch
      const jitter = (Math.random() - 0.5) * 160;

      if (key === ' ' || key === 'Space' || key === 'Spacebar') {
        // Spacebar: deep, solid mechanical switch bar thud
        const bodyOsc = ctx.createOscillator();
        const bodyGain = ctx.createGain();
        bodyOsc.type = 'triangle';
        bodyOsc.frequency.setValueAtTime(220 + jitter * 0.2, t);
        bodyOsc.frequency.exponentialRampToValueAtTime(75, t + 0.026);
        bodyGain.gain.setValueAtTime(0.042, t);
        bodyGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.028);
        bodyOsc.connect(bodyGain);
        bodyGain.connect(ctx.destination);
        bodyOsc.start(t);
        bodyOsc.stop(t + 0.03);

        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'sine';
        clickOsc.frequency.setValueAtTime(1400 + jitter, t);
        clickOsc.frequency.exponentialRampToValueAtTime(350, t + 0.012);
        clickGain.gain.setValueAtTime(0.028, t);
        clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.014);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start(t);
        clickOsc.stop(t + 0.015);

      } else if (key === 'Enter') {
        // Enter: punchy mechanical switch clack + confirmation chirp
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(560 + jitter, t);
        osc.frequency.exponentialRampToValueAtTime(160, t + 0.032);
        gain.gain.setValueAtTime(0.048, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.034);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.036);

        const chirpOsc = ctx.createOscillator();
        const chirpGain = ctx.createGain();
        chirpOsc.type = 'sine';
        chirpOsc.frequency.setValueAtTime(1250, t);
        chirpGain.gain.setValueAtTime(0.024, t);
        chirpGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.038);
        chirpOsc.connect(chirpGain);
        chirpGain.connect(ctx.destination);
        chirpOsc.start(t);
        chirpOsc.stop(t + 0.04);

      } else if (key === 'Backspace' || key === 'Delete') {
        // Backspace: snappy mechanical key release
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(2800 + jitter, t);
        osc.frequency.exponentialRampToValueAtTime(750, t + 0.016);
        gain.gain.setValueAtTime(0.034, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.018);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.02);

      } else if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab', 'Escape'].includes(key)) {
        // Modifier / Navigation keys: crisp subtle tactile click
        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'sine';
        clickOsc.frequency.setValueAtTime(1750 + jitter, t);
        clickOsc.frequency.exponentialRampToValueAtTime(520, t + 0.011);
        clickGain.gain.setValueAtTime(0.022, t);
        clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.013);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start(t);
        clickOsc.stop(t + 0.014);

      } else {
        // All Standard Keys (letters, numbers, symbols, arrows):
        // Dual-stage mechanical click: crisp contact transient + solid bottom-out thud
        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'sine';
        clickOsc.frequency.setValueAtTime(2250 + jitter, t);
        clickOsc.frequency.exponentialRampToValueAtTime(580, t + 0.011);
        clickGain.gain.setValueAtTime(0.032, t);
        clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.013);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start(t);
        clickOsc.stop(t + 0.014);

        const bodyOsc = ctx.createOscillator();
        const bodyGain = ctx.createGain();
        bodyOsc.type = 'triangle';
        bodyOsc.frequency.setValueAtTime(380 + jitter * 0.3, t);
        bodyOsc.frequency.exponentialRampToValueAtTime(130, t + 0.018);
        bodyGain.gain.setValueAtTime(0.028, t);
        bodyGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.02);
        bodyOsc.connect(bodyGain);
        bodyGain.connect(ctx.destination);
        bodyOsc.start(t);
        bodyOsc.stop(t + 0.022);
      }
    } catch (e) {}
  }

  window.playKeyboardClickSound = playKeyboardClickSound;
  window.playTypingSound = playKeyboardClickSound; // Backwards compatible alias

  // Available commands database
  const COMMANDS = {
    help: {
      desc: 'List all available terminal commands',
      execute: () => {
        return `
\x1b[36m╔══════════════════════════════════════════════════════════════════╗\x1b[0m
\x1b[36m║                  AVAILABLE TERMINAL COMMANDS                     ║\x1b[0m
\x1b[36m╚══════════════════════════════════════════════════════════════════╝\x1b[0m

  \x1b[32mhelp\x1b[0m          - Show this command reference
  \x1b[32mabout\x1b[0m         - Reveal Mukesh's journey at Mirai School of Tech
  \x1b[32mskills\x1b[0m        - Technical superpowers (HTML/CSS, C++ DSA, Cloud, AI)
  \x1b[32mvending\x1b[0m       - 🎰 Superpower Vending Machine (Dispense secret motto/story)
  \x1b[32mprojects\x1b[0m      - Inspect Mukesh's real projects on GitHub
  \x1b[32machievements\x1b[0m  - View 5 verified Google Cloud Skill Badges
  \x1b[32mcontact\x1b[0m       - Direct communication channels & GitHub profile
  \x1b[32mfunfact\x1b[0m       - Coding journey trivia & insights
  \x1b[32maws\x1b[0m           - Display AWS Cloud architecture & Amplify setup
  \x1b[32mtheme\x1b[0m         - Cycle terminal themes (matrix / synthwave / cyan)
  \x1b[32mclear\x1b[0m         - Clear the terminal screen output
  \x1b[32mexit\x1b[0m          - Close this secret developer terminal

\x1b[90mTip: Use \x1b[37m[Tab]\x1b[90m for auto-complete, and \x1b[37m[↑/↓]\x1b[90m for command history.\x1b[0m`;
      }
    },

    about: {
      desc: 'Reveal hidden personal introduction & mission',
      execute: () => {
        return `
\x1b[35m=== [ IDENTITY VERIFIED: MUKESH KUMAR ] ===\x1b[0m

\x1b[33mName:\x1b[0m       Mukesh Kumar
\x1b[33mEducation:\x1b[0m  1st Year BE (Computer Science & Engineering)
\x1b[33mCollege:\x1b[0m    Mirai School of Technology
\x1b[33mGitHub:\x1b[0m     https://github.com/itsrockmukesh

\x1b[36m"I am a first-year engineering student dedicated to mastering the foundations
of computer science—from learning web development with semantic HTML and CSS,
to cracking Data Structures and Algorithms in C++, and deploying scalable
cloud applications on AWS and Google Cloud."\x1b[0m

\x1b[32m[CREDENTIALS]\x1b[0m Holder of 5 Google Cloud Skill Badges in Compute, IAM & AI.
\x1b[32m[HACKATHON]\x1b[0m Official entry for the AWS Student Portfolio Hackathon 2026.`;
      }
    },

    skills: {
      desc: 'Reveal technical superpowers',
      execute: () => {
        return `
\x1b[36m=== TECHNICAL SUPERPOWERS & CURRENT FOCUS ===\x1b[0m

  \x1b[34m[Core Programming & Algorithms]\x1b[0m
  • C++ & Data Structures & Algorithms (DSA)   : [████████████████░░] 85%
  • Problem Solving & Logic Building          : [████████████████░░] 86%

  \x1b[35m[Web Development]\x1b[0m
  • HTML5 (Semantic Structure, Accessible UI)  : [██████████████████] 95%
  • CSS3 (Flexbox, Grid, Animations, Styles)   : [█████████████████░] 90%
  • JavaScript (ES6+, DOM Manipulation)        : [███████████████░░░] 80%

  \x1b[32m[Cloud Computing & Artificial Intelligence]\x1b[0m
  • AWS Amplify Hosting & Continuous CI/CD     : [█████████████████░] 88%
  • Google Cloud Platform (5 Skill Badges)     : [█████████████████░] 92%
  • Google AI Studio & Gemini Pro Prototypes   : [████████████████░░] 87%
  • Git & GitHub Version Control               : [█████████████████░] 89%`;
      }
    },

    projects: {
      desc: 'Show featured projects',
      execute: () => {
        return `
\x1b[36m=== MUKESH'S GITHUB PROJECTS & HACKATHON WORK ===\x1b[0m

\x1b[33m1. DevTerminal — Interactive Cyber Portfolio (AWS Hackathon Flagship)\x1b[0m
   • Tech: AWS Amplify, Vanilla CSS3, Web Audio API, ES6+ JavaScript
   • Description: Retro hacker portfolio with live CLI terminal and Google Cloud badges.
   • URL: https://github.com/itsrockmukesh

\x1b[35m2. Personal-Website (HTML & CSS)\x1b[0m
   • Tech: CSS3, HTML5, Responsive Design
   • Description: Elegant personal developer webpage showcasing profile and skills.
   • URL: https://github.com/itsrockmukesh/Personal-Website

\x1b[32m3. Wikipedia (HTML Web Layout Recreation)\x1b[0m
   • Tech: HTML5 Semantic Markup, Structured Content Hierarchy
   • Description: Clean recreation of Wikipedia's informational encyclopedia layout.
   • URL: https://github.com/itsrockmukesh/Wikipedia

\x1b[34m4. Data Structures & Algorithms in C++\x1b[0m
   • Tech: C++20, STL, Arrays, Pointers, Linked Lists, Trees, Recursion
   • Description: Algorithmic problem solving and optimized data structure implementations.
   • URL: https://github.com/itsrockmukesh`;
      }
    },

    achievements: {
      desc: 'Reveal Google Cloud Skill Badges & certifications',
      execute: () => {
        return `
\x1b[32m=== GOOGLE CLOUD SKILL BADGES (5 VERIFIED) ===\x1b[0m

\x1b[34m[1]\x1b[0m The Basics of Google Cloud Compute
    → Provisioning Compute Engine VMs, persistent disks, and network rules.

\x1b[31m[2]\x1b[0m Configure Service Accounts and IAM Roles for Google Cloud
    → Least-privilege access, custom IAM roles, credential key security.

\x1b[32m[3]\x1b[0m Store, Process, and Manage Data on Google Cloud – Console
    → Cloud Storage buckets, BigQuery analytics, and database management.

\x1b[35m[4]\x1b[0m Develop AI-Powered Prototypes in Google AI Studio
    → Designing multi-turn prompts, system instructions, and tuning parameters.

\x1b[36m[5]\x1b[0m Create Your First Gemini Enterprise Application
    → Deploying Gemini enterprise multimodal endpoints into live web apps.

\x1b[33m[★] AWS Student Portfolio Hackathon 2026 Entry\x1b[0m
    → Built with AWS Amplify Hosting, interactive terminal, and 100% responsiveness.`;
      }
    },

    contact: {
      desc: 'Show contact information',
      execute: () => {
        return `
\x1b[36m=== CONNECT WITH MUKESH KUMAR ===\x1b[0m

  \x1b[33mName:\x1b[0m     Mukesh Kumar (1st Year BE-CSE)
  \x1b[33mCollege:\x1b[0m  Mirai School of Technology
  \x1b[35mGitHub:\x1b[0m   https://github.com/itsrockmukesh
  \x1b[34mLinkedIn:\x1b[0m https://www.linkedin.com/in/mukesh-kumar-06485222a
  \x1b[32mEmail:\x1b[0m    techmukesh3124@gmail.com

Feel free to send a message via the website contact form or connect on LinkedIn / GitHub!`;
      }
    },

    funfact: {
      desc: 'Reveal a fun fact about me',
      execute: () => {
        const facts = [
          "⚡ Fun Fact: As a 1st year engineering student at Mirai School of Technology, I balance solving DSA in C++ by day and building web apps by night!",
          "☁️ Fun Fact: I earned 5 Google Cloud Skill Badges in my very first year of college!",
          "💻 Fun Fact: My first projects on GitHub were building clean websites with HTML & CSS to understand the foundations before frameworks.",
          "🚀 Fun Fact: AWS Amplify lets you deploy a full portfolio from GitHub in under 30 seconds with global CloudFront CDN edge delivery!"
        ];
        const randomFact = facts[Math.floor(Math.random() * facts.length)];
        return `\x1b[33m${randomFact}\x1b[0m`;
      }
    },

    aws: {
      desc: 'AWS Cloud architecture details',
      execute: () => {
        return `
\x1b[33m=== AWS CLOUD ARCHITECTURE & HACKATHON STACK ===\x1b[0m

  • \x1b[33mHosting:\x1b[0m AWS Amplify Hosting (Continuous Deployment via GitHub)
  • \x1b[33mRepo:\x1b[0m https://github.com/itsrockmukesh
  • \x1b[33mEdge CDN:\x1b[0m Amazon CloudFront global edge caching with SSL/HTTPS
  • \x1b[33mPerformance:\x1b[0m Zero bloated dependencies, 100/100 Lighthouse speed
  • \x1b[33mSecurity:\x1b[0m Zero exposed access keys or backend secrets`;
      }
    },

    theme: {
      desc: 'Switch terminal color scheme',
      execute: () => {
        if (terminalWindow.classList.contains('theme-purple')) {
          terminalWindow.classList.remove('theme-purple');
          terminalWindow.classList.add('theme-cyan');
          return "Switched terminal theme to \x1b[36m[CYAN OCEAN]\x1b[0m.";
        } else if (terminalWindow.classList.contains('theme-cyan')) {
          terminalWindow.classList.remove('theme-cyan');
          return "Switched terminal theme to \x1b[32m[MATRIX GREEN]\x1b[0m.";
        } else {
          terminalWindow.classList.add('theme-purple');
          return "Switched terminal theme to \x1b[35m[SYNTHWAVE PURPLE]\x1b[0m.";
        }
      }
    },

    whoami: {
      desc: 'Print current session identity',
      execute: () => "guest@mukesh-cloud-portfolio (Visitor / AWS Hackathon Judge)"
    },

    date: {
      desc: 'Print current timestamp',
      execute: () => new Date().toUTCString()
    },

    sudo: {
      desc: 'Superuser command',
      execute: () => "\x1b[31m[PERMISSION DENIED]\x1b[0m Nice try, hacker! But Mukesh has locked this cloud shell with AWS IAM least-privilege policies. 😉"
    },

    clear: {
      desc: 'Clear terminal screen',
      execute: () => {
        commandLog.innerHTML = '';
        return null;
      }
    },

    vending: {
      desc: 'Superpower Vending Machine (Dispense random superpower or story)',
      execute: () => {
        const items = [
          "🥫 [DISPENSED: C++ Memory Master] — 'I understand pointers, heap vs stack, and time complexity from the ground up!'",
          "⚡ [DISPENSED: Standards-First Builder] — 'I mastered semantic HTML5 and responsive CSS3 Grid before touching frameworks.'",
          "☁️ [DISPENSED: AWS Cloud Builder] — 'Attended AWS Builder Center, earned 5 Google Cloud Badges, and deployed this hackathon project continuously on AWS Amplify!'",
          "🧠 [DISPENSED: Algorithmic Grit] — 'Solving recursion, binary trees, and linked list challenges daily at Mirai School of Technology.'",
          "🎯 [DISPENSED: Engineering Philosophy] — 'Master fundamentals first. Build real things with zero fluff.'"
        ];
        const pick = items[Math.floor(Math.random() * items.length)];
        return `
\x1b[35m╔══════════════════════════════════════════════════════════════════╗\x1b[0m
\x1b[35m║             🎰 SUPERPOWER VENDING MACHINE 🎰                   ║\x1b[0m
\x1b[35m╚══════════════════════════════════════════════════════════════════╝\x1b[0m
\x1b[33m*CLINK... RUMBLE... THUD!* [Dispensing secret item for AWS Hackathon Judge...]\x1b[0m

\x1b[32m${pick}\x1b[0m

\x1b[90m(Tip: Type 'vending' again to dispense another secret story!)\x1b[0m`;
      }
    },

    superpower: {
      desc: 'Alias for vending command',
      execute: () => {
        return COMMANDS.vending.execute();
      }
    },

    exit: {
      desc: 'Close terminal',
      execute: () => {
        closeTerminal();
        return "Closing terminal session... Goodbye!";
      }
    }
  };

  // Convert ANSI color codes to styled HTML spans
  function formatAnsi(str) {
    if (!str) return '';
    let html = str
      .replace(/\x1b\[31m/g, '<span style="color:#EF4444;">')
      .replace(/\x1b\[32m/g, '<span style="color:#10B981;">')
      .replace(/\x1b\[33m/g, '<span style="color:#F59E0B;">')
      .replace(/\x1b\[34m/g, '<span style="color:#3B82F6;">')
      .replace(/\x1b\[35m/g, '<span style="color:#C084FC;">')
      .replace(/\x1b\[36m/g, '<span style="color:#06B6D4;">')
      .replace(/\x1b\[37m/g, '<span style="color:#F8FAFC;">')
      .replace(/\x1b\[90m/g, '<span style="color:#64748B;">')
      .replace(/\x1b\[0m/g, '</span>');

    // Convert URLs into clickable terminal links
    html = html.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" style="color:#38BDF8; text-decoration:underline;">$1</a>');
    return html;
  }

  // Open / Close Functions
  function openTerminal(initialCmd) {
    modalOverlay.classList.add('active');
    playTerminalBoomSound();
    setTimeout(() => {
      cliInput.focus();
      if (initialCmd && typeof initialCmd === 'string') {
        cliInput.value = initialCmd;
        executeCommand(initialCmd);
      }
    }, 150);
  }

  function closeTerminal() {
    modalOverlay.classList.remove('active');
    playBeep(440, 0.06, 'sine');
  }

  // Execute Command
  function executeCommand(rawInput) {
    const trimmed = rawInput.trim();
    if (!trimmed) return;

    playBeep(720, 0.04, 'square');

    // Add to history
    commandHistory.push(trimmed);
    historyIndex = commandHistory.length;

    // Parse command
    const parts = trimmed.split(' ');
    const cmd = parts[0].toLowerCase();

    // Create entry log item
    const entryEl = document.createElement('div');
    entryEl.className = 'term-entry';

    const cmdHeader = document.createElement('div');
    cmdHeader.className = 'term-entry-cmd';
    cmdHeader.innerHTML = `<span class="term-entry-prompt">guest@mukesh-cloud:~$</span> <span class="term-entry-text">${escapeHtml(trimmed)}</span>`;
    entryEl.appendChild(cmdHeader);

    if (COMMANDS[cmd]) {
      const output = COMMANDS[cmd].execute();
      if (output !== null) {
        const resultEl = document.createElement('div');
        resultEl.className = 'term-entry-result';
        resultEl.innerHTML = formatAnsi(output);
        entryEl.appendChild(resultEl);
      }
    } else {
      const errEl = document.createElement('div');
      errEl.className = 'term-entry-result';
      errEl.innerHTML = `<span style="color:#EF4444;">zsh: command not found: ${escapeHtml(cmd)}</span>\nType <span style="color:#34D399; font-weight:bold;">help</span> to see all available commands.`;
      entryEl.appendChild(errEl);
    }

    commandLog.appendChild(entryEl);

    // Auto scroll to bottom
    const terminalBody = document.querySelector('.terminal-body');
    if (terminalBody) {
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }

    cliInput.value = '';
  }

  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  // Keyboard navigation & Shortcuts
  cliInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      executeCommand(cliInput.value);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex > 0) {
        historyIndex--;
        cliInput.value = commandHistory[historyIndex] || '';
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        historyIndex++;
        cliInput.value = commandHistory[historyIndex] || '';
      } else {
        historyIndex = commandHistory.length;
        cliInput.value = '';
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      const current = cliInput.value.toLowerCase().trim();
      if (!current) return;
      const matches = Object.keys(COMMANDS).filter(c => c.startsWith(current));
      if (matches.length === 1) {
        cliInput.value = matches[0];
        playBeep(900, 0.03, 'sine');
      } else if (matches.length > 1) {
        const entryEl = document.createElement('div');
        entryEl.className = 'term-entry';
        const resultEl = document.createElement('div');
        resultEl.className = 'term-entry-result';
        resultEl.innerHTML = `<span style="color:#64748B;">Matches: </span>` + matches.map(m => `<span style="color:#38BDF8; margin-right:12px;">${m}</span>`).join('');
        entryEl.appendChild(resultEl);
        commandLog.appendChild(entryEl);
        const terminalBody = document.querySelector('.terminal-body');
        if (terminalBody) terminalBody.scrollTop = terminalBody.scrollHeight;
      }
    }
  });

  // Global Keyboard shortcut: `~` or ` (backtick) or Escape to close
  window.addEventListener('keydown', (e) => {
    const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
    const isEditingField = (activeTag === 'input' || activeTag === 'textarea') && document.activeElement !== cliInput;

    if ((e.key === '`' || e.key === '~') && !isEditingField) {
      e.preventDefault();
      if (modalOverlay.classList.contains('active')) {
        closeTerminal();
      } else {
        openTerminal();
      }
    } else if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
      closeTerminal();
    }
  });

  // Hint Display Function (Clicking only shows hint, does NOT launch terminal)
  function showTerminalHintOnly() {
    if (hintTrigger) {
      hintTrigger.classList.remove('pulse-hint');
      void hintTrigger.offsetWidth;
      hintTrigger.classList.add('pulse-hint');
    }
    if (typeof window.showToast === 'function') {
      window.showToast('⌨️ Hint: Press <strong>[~]</strong> or <strong>[`]</strong> on your keyboard to open Secret Terminal');
    }
    playBeep(880, 0.08, 'sine');
  }
  window.showTerminalHint = showTerminalHintOnly;

  // Click Triggers: On touch / mobile (<860px or touchscreen), directly open terminal! On desktop, show hint.
  function handleTriggerInteraction(e) {
    e.preventDefault();
    e.stopPropagation();
    const isTouchOrMobile = window.innerWidth <= 860 || ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    if (isTouchOrMobile) {
      openTerminal();
    } else {
      showTerminalHintOnly();
    }
  }

  if (hintTrigger) {
    hintTrigger.addEventListener('click', handleTriggerInteraction);
  }
  if (navTrigger) {
    navTrigger.addEventListener('click', handleTriggerInteraction);
  }
  if (heroTrigger) {
    heroTrigger.addEventListener('click', handleTriggerInteraction);
  }
  if (closeBtn) closeBtn.addEventListener('click', closeTerminal);

  if (maxBtn) {
    maxBtn.addEventListener('click', () => {
      terminalWindow.classList.toggle('maximized');
    });
  }

  if (clearToolBtn) {
    clearToolBtn.addEventListener('click', () => {
      commandLog.innerHTML = '';
      cliInput.focus();
    });
  }

  if (copyToolBtn) {
    copyToolBtn.addEventListener('click', () => {
      const textToCopy = commandLog.innerText || '';
      navigator.clipboard.writeText(textToCopy).then(() => {
        copyToolBtn.innerText = 'COPIED!';
        setTimeout(() => { copyToolBtn.innerText = 'COPY LOG'; }, 1800);
      });
    });
  }

  // Quick Chips in Footer
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const cmd = chip.getAttribute('data-cmd');
      if (cmd) {
        cliInput.value = cmd;
        executeCommand(cmd);
        cliInput.focus();
      }
    });
  });

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      closeTerminal();
    }
  });

  
  // Universal keyboard click sound on EVERY key pressed anywhere on the page
  window.addEventListener('keydown', (e) => {
    playKeyboardClickSound(e.key);
  }, { capture: true, passive: true });

  window.playTerminalBoomSound = playTerminalBoomSound;
  window.playKeyboardClickSound = playKeyboardClickSound;
  window.playTypingSound = playKeyboardClickSound;
  window.openSecretTerminal = openTerminal;
})();
