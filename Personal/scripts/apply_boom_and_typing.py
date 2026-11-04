import os
import re

PERSONAL_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal"
PORTFOLIO_DIR = "/Users/mukeshkumar/PORTFOLIO"

# 1. Update js/terminal.js with Boom sound on open and Typing sound on typing
def update_terminal_js(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace sound synthesizer section with cinematic Boom & mechanical Typing sounds
    old_sound_pattern = r"(// Sound Synthesizer via Web Audio API[\s\S]*?function playBeep\([^)]*\) \{[\s\S]*?\n  \})"
    
    new_sound_code = '''  // ==========================================================================
  // CINEMATIC TERMINAL SOUND SYSTEM (Web Audio API)
  // High-impact sub-bass BOOM on open, crisp mechanical keyboard typing sounds
  // ==========================================================================
  let audioCtx = null;

  function getAudioContext() {
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

  // Crisp Mechanical Keyboard Typing Sound
  let lastTypingTime = 0;
  function playTypingSound(key = 'a') {
    if (window.portfolioAudioMuted) return;
    const nowMs = performance.now();
    if (nowMs - lastTypingTime < 22) return; // Debounce rapid repeats
    lastTypingTime = nowMs;

    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const t = ctx.currentTime;

      if (key === ' ' || key === 'Space' || key === 'Spacebar') {
        // Spacebar: deeper, chunkier mechanical switch thud
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(260 + Math.random() * 20, t);
        osc.frequency.exponentialRampToValueAtTime(95, t + 0.024);
        gain.gain.setValueAtTime(0.038, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.026);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.028);

        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'sine';
        clickOsc.frequency.setValueAtTime(1450, t);
        clickOsc.frequency.exponentialRampToValueAtTime(400, t + 0.012);
        clickGain.gain.setValueAtTime(0.025, t);
        clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.014);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start(t);
        clickOsc.stop(t + 0.015);
      } else if (key === 'Enter') {
        // Enter: crisp mechanical clack with confirmation chirp
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(540, t);
        osc.frequency.exponentialRampToValueAtTime(180, t + 0.032);
        gain.gain.setValueAtTime(0.045, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.034);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.035);

        const chimeOsc = ctx.createOscillator();
        const chimeGain = ctx.createGain();
        chimeOsc.type = 'sine';
        chimeOsc.frequency.setValueAtTime(1180, t);
        chimeGain.gain.setValueAtTime(0.022, t);
        chimeGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
        chimeOsc.connect(chimeGain);
        chimeGain.connect(ctx.destination);
        chimeOsc.start(t);
        chimeOsc.stop(t + 0.042);
      } else if (key === 'Backspace' || key === 'Delete') {
        // Backspace: snappy mechanical key release
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(2600, t);
        osc.frequency.exponentialRampToValueAtTime(850, t + 0.016);
        gain.gain.setValueAtTime(0.03, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.018);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.02);
      } else {
        // Standard Key: Authentic mechanical switch click (dual-stage: click + thud)
        const jitter = (Math.random() - 0.5) * 140;
        const clickFreq = 2100 + jitter;

        const clickOsc = ctx.createOscillator();
        const clickGain = ctx.createGain();
        clickOsc.type = 'sine';
        clickOsc.frequency.setValueAtTime(clickFreq, t);
        clickOsc.frequency.exponentialRampToValueAtTime(620, t + 0.012);
        clickGain.gain.setValueAtTime(0.026, t);
        clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.014);
        clickOsc.connect(clickGain);
        clickGain.connect(ctx.destination);
        clickOsc.start(t);
        clickOsc.stop(t + 0.015);

        // Switch bottom bottom-out thud
        const bodyOsc = ctx.createOscillator();
        const bodyGain = ctx.createGain();
        bodyOsc.type = 'triangle';
        bodyOsc.frequency.setValueAtTime(360 + jitter * 0.3, t);
        bodyOsc.frequency.exponentialRampToValueAtTime(140, t + 0.018);
        bodyGain.gain.setValueAtTime(0.024, t);
        bodyGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.02);
        bodyOsc.connect(bodyGain);
        bodyGain.connect(ctx.destination);
        bodyOsc.start(t);
        bodyOsc.stop(t + 0.022);
      }
    } catch (e) {}
  }

  window.playTerminalBoomSound = playTerminalBoomSound;
  window.playTypingSound = playTypingSound;'''

    content = re.sub(old_sound_pattern, new_sound_code, content)

    # In openTerminal: replace playBeep with playTerminalBoomSound
    content = content.replace("playBeep(880, 0.08, 'triangle');", "playTerminalBoomSound();")

    # In cliInput keydown: add playTypingSound(e.key)
    cli_keydown_needle = "cliInput.addEventListener('keydown', (e) => {"
    if cli_keydown_needle in content and "playTypingSound" not in content[content.find(cli_keydown_needle):content.find(cli_keydown_needle)+200]:
        content = content.replace(cli_keydown_needle, cli_keydown_needle + "\n    if (!['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(e.key)) {\n      playTypingSound(e.key);\n    }")

    # Add global typing sound listener for all inputs/textareas
    global_typing_listener = '''
  // Global mechanical typing sound on all form inputs and textareas
  document.addEventListener('keydown', (e) => {
    const t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA') && t !== cliInput) {
      if (!['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(e.key)) {
        playTypingSound(e.key);
      }
    }
  }, { passive: true });
'''
    if "Global mechanical typing sound" not in content:
        content = content.replace("window.openSecretTerminal = openTerminal;", global_typing_listener + "\n  window.openSecretTerminal = openTerminal;")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path}")

update_terminal_js(os.path.join(PERSONAL_DIR, "js/terminal.js"))
update_terminal_js(os.path.join(PORTFOLIO_DIR, "js/terminal.js"))
