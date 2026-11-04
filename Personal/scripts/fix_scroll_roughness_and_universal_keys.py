import os
import re

PERSONAL_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal"
PORTFOLIO_DIR = "/Users/mukeshkumar/PORTFOLIO"

def update_terminal_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Enhance playTypingSound into a universal, ultra-crisp playKeyboardClickSound
    old_typing_func = r"(// Crisp Mechanical Keyboard Typing Sound[\s\S]*?window\.playTypingSound = playTypingSound;)"
    
    new_typing_func = '''  // ==========================================================================
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
  window.playTypingSound = playKeyboardClickSound; // Backwards compatible alias'''

    content = re.sub(old_typing_func, new_typing_func, content)

    # Replace the old document keydown listener with a universal capture listener on window
    old_listener_pattern = r"(// Global mechanical typing sound[\s\S]*?document\.addEventListener\('keydown',[\s\S]*?\}\);\s*\}\s*,\s*\{\s*passive:\s*true\s*\}\);)"
    new_listener = '''// Universal keyboard click sound on EVERY key pressed anywhere on the page
  window.addEventListener('keydown', (e) => {
    playKeyboardClickSound(e.key);
  }, { capture: true, passive: true });'''

    if re.search(old_listener_pattern, content):
        content = re.sub(old_listener_pattern, new_listener, content)
    elif "Universal keyboard click sound on EVERY key" not in content:
        content = content.replace("window.openSecretTerminal = openTerminal;", new_listener + "\n  window.openSecretTerminal = openTerminal;")

    # Remove the redundant playTypingSound call inside cliInput.addEventListener('keydown') if window capture already handles it
    content = content.replace("cliInput.addEventListener('keydown', (e) => {\n    if (!['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(e.key)) {\n      playTypingSound(e.key);\n    }\n", "cliInput.addEventListener('keydown', (e) => {\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filepath}")


def update_html_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace scroll audio engine in index.html:
    # Completely remove playScrollRatchetClick and rough mouse scrolling clicks!
    # Instead, use a silky, smooth, fluid, warm harmonic energy glide.
    old_engine_pattern = r"(// ==========================================================================\s*// INTERACTIVE PHOTO SCROLL CYBER AUDIO ENGINE[\s\S]*?function playHoloChime\(reverse = false\) \{[\s\S]*?\n    \})"

    new_engine_code = '''    // ==========================================================================
    // INTERACTIVE PHOTO SCROLL SILKY AUDIO ENGINE (Web Audio API)
    // Produces a buttery-smooth, fluid, futuristic harmonic glide (NO rough clicks!)
    // ==========================================================================
    let scrollAudioCtx = null;
    let scrollAirGain = null;
    let scrollAirFilter = null;
    let scrollOsc1 = null;
    let scrollOsc2 = null;
    let lastScrollY = window.scrollY;
    let lastScrollTime = performance.now();
    let scrollVelocity = 0.0;
    let isChimePlayed = false;
    let isReverseChimePlayed = false;

    function initScrollAudio() {
      if (scrollAudioCtx) return;
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        scrollAudioCtx = new AudioContext();

        // 1. Smooth, Gentle Velvet Resonant Filter (Lowpass, warmth & zero roughness)
        scrollAirFilter = scrollAudioCtx.createBiquadFilter();
        scrollAirFilter.type = 'lowpass';
        scrollAirFilter.frequency.setValueAtTime(360.0, scrollAudioCtx.currentTime);
        scrollAirFilter.Q.setValueAtTime(1.2, scrollAudioCtx.currentTime); // Soft, gentle Q

        // Master Smooth Glide Gain
        scrollAirGain = scrollAudioCtx.createGain();
        scrollAirGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);

        // 2. Pure Warm Celestial Sines (A3 220Hz + A4 440Hz — Pure soothing harmony, NO buzzing!)
        scrollOsc1 = scrollAudioCtx.createOscillator();
        scrollOsc1.type = 'sine';
        scrollOsc1.frequency.setValueAtTime(220.0, scrollAudioCtx.currentTime);

        scrollOsc2 = scrollAudioCtx.createOscillator();
        scrollOsc2.type = 'sine';
        scrollOsc2.frequency.setValueAtTime(440.0, scrollAudioCtx.currentTime);

        scrollOsc1.connect(scrollAirFilter);
        scrollOsc2.connect(scrollAirFilter);
        scrollAirFilter.connect(scrollAirGain);
        scrollAirGain.connect(scrollAudioCtx.destination);

        scrollOsc1.start();
        scrollOsc2.start();

        window.scrollAudioCtx = scrollAudioCtx;
        window.scrollDroneGain = scrollAirGain;
        window.scrollAirGain = scrollAirGain;
        window.scrollAirFilter = scrollAirFilter;
        window.scrollOsc1 = scrollOsc1;
        window.scrollOsc2 = scrollOsc2;
      } catch (e) {
        console.warn("AudioContext init error:", e);
      }
    }

    // Crystalline Glass Spark (Pentatonic Particle Assembling Droplet)
    const CRYSTAL_NOTES = [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98];
    function playCrystalDrop(progress = 0.5) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const t = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();

        const noteIndex = Math.min(CRYSTAL_NOTES.length - 1, Math.max(0, Math.floor((progress || 0) * CRYSTAL_NOTES.length)));
        const freq = CRYSTAL_NOTES[noteIndex];

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, t);

        gain.gain.setValueAtTime(0.016, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.055);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.06);
      } catch (e) {}
    }

    function playParticleGrain(freq) {
      playCrystalDrop(window.revealProgress || 0.5);
    }

    // Futuristic Holographic Completion Chime (Lush 5-Note Crystalline Arpeggio)
    function playHoloChime(reverse = false) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const now = scrollAudioCtx.currentTime;
        const notes = reverse
          ? [783.99, 659.25, 523.25, 392.00]
          : [523.25, 659.25, 783.99, 987.77, 1046.50];

        notes.forEach((freq, idx) => {
          const osc = scrollAudioCtx.createOscillator();
          const gain = scrollAudioCtx.createGain();
          osc.type = 'sine';
          const startTime = now + idx * 0.058;
          osc.frequency.setValueAtTime(freq, startTime);
          gain.gain.setValueAtTime(0.045, startTime);
          gain.gain.exponentialRampToValueAtTime(0.0001, startTime + 0.5);
          osc.connect(gain);
          gain.connect(scrollAudioCtx.destination);
          osc.start(startTime);
          osc.stop(startTime + 0.5);
        });
      } catch (e) {}
    }'''

    content = re.sub(old_engine_pattern, new_engine_code, content)

    # 2. In handleScrollSound: REMOVE scrollAccumulator and playScrollRatchetClick!
    old_handle_sound = r"function handleScrollSound\(delta\) \{[\s\S]*?lastScrollTime = now;[\s\S]*?\}\s*\}"
    new_handle_sound = '''function handleScrollSound(delta) {
      if (window.portfolioAudioMuted) return;
      if (!scrollAudioCtx) {
        initScrollAudio();
      }
      if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') {
        scrollAudioCtx.resume();
      }
      if (!scrollAudioCtx) return;

      const vh = window.innerHeight;
      const scrollY = window.scrollY;

      const now = performance.now();
      const dt = Math.max(1, now - lastScrollTime);
      const dy = Math.abs(scrollY - lastScrollY);
      scrollVelocity = Math.min(1.0, (dy / dt) * 0.2 + Math.abs(delta || 0) * 0.0028);

      lastScrollY = scrollY;
      lastScrollTime = now;
    }'''
    content = re.sub(old_handle_sound, new_handle_sound, content)

    # 3. In animate(): Modulate smooth harmonic glide with zero clicks
    old_animate_audio = r"(// --- Interactive Photo Scroll Audio Modulation Engine ---[\s\S]*?// Holographic Completion Chime)"
    new_animate_audio = '''// --- Interactive Photo Scroll Audio Modulation Engine ---
      // Buttery-smooth, soothing harmonic glide (pure sine tones smoothly tracking revealProgress)
      if (scrollAudioCtx && scrollAirGain) {
        if (window.portfolioAudioMuted) {
          scrollAirGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);
        } else {
          const vh = window.innerHeight;
          const timeSinceScroll = performance.now() - lastScrollTime;
          const isHeroZone = window.scrollY <= vh * 1.5;
          const isParticlesMoving = (revealDelta > 0.0008 || timeSinceScroll < 120);

          if (isHeroZone && isParticlesMoving) {
            const audioNow = scrollAudioCtx.currentTime;

            // Pitch glides smoothly upwards as photo reveals: A3 (220Hz) -> E4 (330Hz)
            const baseFreq = THREE.MathUtils.lerp(220.0, 330.0, revealProgress);
            scrollOsc1.frequency.setTargetAtTime(baseFreq, audioNow, 0.04);
            scrollOsc2.frequency.setTargetAtTime(baseFreq * 2.0, audioNow, 0.04);

            // Filter smoothly opens: 320Hz -> 780Hz
            const filterFreq = THREE.MathUtils.lerp(320.0, 780.0, revealProgress);
            scrollAirFilter.frequency.setTargetAtTime(filterFreq, audioNow, 0.04);

            // Volume: gentle, whisper-soft, perfectly fluid (max 0.024)
            const dynamicVol = Math.min(0.024, Math.max(scrollVelocity * 0.02, revealDelta * 1.4));
            scrollAirGain.gain.setTargetAtTime(dynamicVol, audioNow, 0.035);

            // Gentle crystalline glass sparkle as particles snap into photo coordinates
            if (Math.random() < 0.18 && dynamicVol > 0.006) {
              playCrystalDrop(revealProgress);
            }
          } else {
            scrollAirGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.09);
          }
        }
      }

      // Holographic Completion Chime'''

    content = re.sub(old_animate_audio, new_animate_audio, content)

    # 4. Also add the universal keyboard sound listener directly in index.html for instant response
    keyboard_listener_code = '''
    // Universal Keyboard Click Sound: triggers on EVERY key of the keyboard pressed
    window.addEventListener('keydown', (e) => {
      if (typeof window.playKeyboardClickSound === 'function') {
        window.playKeyboardClickSound(e.key);
      }
    }, { capture: true, passive: true });
'''
    if "Universal Keyboard Click Sound: triggers on EVERY key" not in content:
        content = content.replace("window.addEventListener('scroll', updateHeroScrollState, { passive: true });",
                                  "window.addEventListener('scroll', updateHeroScrollState, { passive: true });\n" + keyboard_listener_code)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {filepath}")


update_terminal_file(os.path.join(PERSONAL_DIR, "js/terminal.js"))
update_terminal_file(os.path.join(PORTFOLIO_DIR, "js/terminal.js"))

update_html_file(os.path.join(PERSONAL_DIR, "index.html"))
update_html_file(os.path.join(PORTFOLIO_DIR, "index.html"))
