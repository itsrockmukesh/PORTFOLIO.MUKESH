import os

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the old sound engine with the new Tactile Haptic Crown & Celestial Ambient Shimmer Engine
old_sound_engine = """    // ==========================================================================
    // INTERACTIVE PHOTO SCROLL CYBER AUDIO ENGINE (Web Audio API)
    // Produces a responsive cyber resonance, particle clicks & lock-in chimes
    // ==========================================================================
    let scrollAudioCtx = null;
    let scrollDroneGain = null;
    let scrollFilter = null;
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

        // Master Gain
        scrollDroneGain = scrollAudioCtx.createGain();
        scrollDroneGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);

        // Resonant Filter
        scrollFilter = scrollAudioCtx.createBiquadFilter();
        scrollFilter.type = 'bandpass';
        scrollFilter.frequency.setValueAtTime(320.0, scrollAudioCtx.currentTime);
        scrollFilter.Q.setValueAtTime(3.6, scrollAudioCtx.currentTime);

        // Sub Oscillator (Triangle)
        scrollOsc1 = scrollAudioCtx.createOscillator();
        scrollOsc1.type = 'triangle';
        scrollOsc1.frequency.setValueAtTime(140.0, scrollAudioCtx.currentTime);

        // Harmonic Resonance Oscillator (Sine)
        scrollOsc2 = scrollAudioCtx.createOscillator();
        scrollOsc2.type = 'sine';
        scrollOsc2.frequency.setValueAtTime(350.0, scrollAudioCtx.currentTime);

        // Wire nodes
        scrollOsc1.connect(scrollFilter);
        scrollOsc2.connect(scrollFilter);
        scrollFilter.connect(scrollDroneGain);
        scrollDroneGain.connect(scrollAudioCtx.destination);

        scrollOsc1.start();
        scrollOsc2.start();

        window.scrollAudioCtx = scrollAudioCtx;
        window.scrollDroneGain = scrollDroneGain;
        window.scrollFilter = scrollFilter;
        window.scrollOsc1 = scrollOsc1;
        window.scrollOsc2 = scrollOsc2;
      } catch (e) {
        console.warn("AudioContext init error:", e);
      }
    }

    // Granular Micro-Grain Sound (Flattening Particle Spark)
    function playParticleGrain(freq = 1200) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const now = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq + (Math.random() - 0.5) * 350, now);
        gain.gain.setValueAtTime(0.022, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.035);
        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.035);
      } catch (e) {}
    }

    // Futuristic Holographic Completion Chime
    function playHoloChime(reverse = false) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const now = scrollAudioCtx.currentTime;
        const notes = reverse ? [659.25, 523.25, 392.00] : [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
          const osc = scrollAudioCtx.createOscillator();
          const gain = scrollAudioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.055);
          gain.gain.setValueAtTime(0.045, now + idx * 0.055);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.055 + 0.42);
          osc.connect(gain);
          gain.connect(scrollAudioCtx.destination);
          osc.start(now + idx * 0.055);
          osc.stop(now + idx * 0.055 + 0.42);
        });
      } catch (e) {}
    }"""

new_sound_engine = """    // ==========================================================================
    // TACTILE DIGITAL CROWN & CELESTIAL AMBIENT SCROLL ENGINE (Web Audio API)
    // Silky mechanical haptic clicks + warm airy harmonic wash (non-fatiguing)
    // ==========================================================================
    let scrollAudioCtx = null;
    let scrollDroneGain = null;
    let scrollFilter = null;
    let scrollOsc1 = null;
    let scrollOsc2 = null;
    let lastScrollY = window.scrollY;
    let lastScrollTime = performance.now();
    let lastTickTime = 0;
    let scrollVelocity = 0.0;
    let isChimePlayed = false;
    let isReverseChimePlayed = false;

    function initScrollAudio() {
      if (scrollAudioCtx) return;
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        scrollAudioCtx = new AudioContext();

        // Master Gain for ambient wash
        scrollDroneGain = scrollAudioCtx.createGain();
        scrollDroneGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);

        // Smooth Low-Pass Filter (gentle, warm, zero buzzing)
        scrollFilter = scrollAudioCtx.createBiquadFilter();
        scrollFilter.type = 'lowpass';
        scrollFilter.frequency.setValueAtTime(600.0, scrollAudioCtx.currentTime);
        scrollFilter.Q.setValueAtTime(0.75, scrollAudioCtx.currentTime);

        // Warm Fundamental Sine Oscillator
        scrollOsc1 = scrollAudioCtx.createOscillator();
        scrollOsc1.type = 'sine';
        scrollOsc1.frequency.setValueAtTime(220.0, scrollAudioCtx.currentTime);

        // Harmonic Perfect-Fifth Shimmer Sine Oscillator
        scrollOsc2 = scrollAudioCtx.createOscillator();
        scrollOsc2.type = 'sine';
        scrollOsc2.frequency.setValueAtTime(330.0, scrollAudioCtx.currentTime);

        // Wire nodes through low-pass warmth filter
        scrollOsc1.connect(scrollFilter);
        scrollOsc2.connect(scrollFilter);
        scrollFilter.connect(scrollDroneGain);
        scrollDroneGain.connect(scrollAudioCtx.destination);

        scrollOsc1.start();
        scrollOsc2.start();

        window.scrollAudioCtx = scrollAudioCtx;
        window.scrollDroneGain = scrollDroneGain;
        window.scrollFilter = scrollFilter;
        window.scrollOsc1 = scrollOsc1;
        window.scrollOsc2 = scrollOsc2;
      } catch (e) {
        console.warn("AudioContext init error:", e);
      }
    }

    // Tactile Digital Crown Micro-Tick (Crisp Leica/Apple Watch mechanical haptic click)
    function playScrollTick(intensity = 1.0) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      const now = performance.now();
      if (now - lastTickTime < 24) return; // Smooth rate limiter
      lastTickTime = now;

      try {
        const t = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();

        // Elegant damped micro-click
        const pitch = 820 + Math.random() * 120 + revealProgress * 450;
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(pitch, t);
        osc.frequency.exponentialRampToValueAtTime(pitch * 0.45, t + 0.014);

        const clickVol = Math.min(0.028, 0.015 * intensity);
        gain.gain.setValueAtTime(clickVol, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.015);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.016);
      } catch (e) {}
    }

    // Delicate Star Particle Grain
    function playParticleGrain(freq = 1200) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const now = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now);
        gain.gain.setValueAtTime(0.016, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.028);
        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.03);
      } catch (e) {}
    }

    // Crystal Glass Chord (Ambient E-Minor 9th / Luxury Awwwards Finish)
    function playHoloChime(reverse = false) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      try {
        const now = scrollAudioCtx.currentTime;
        const notes = reverse ? [783.99, 659.25, 493.88, 329.63] : [329.63, 493.88, 659.25, 987.77, 1318.51];
        notes.forEach((freq, idx) => {
          const osc = scrollAudioCtx.createOscillator();
          const gain = scrollAudioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.048);
          gain.gain.setValueAtTime(0.035, now + idx * 0.048);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.048 + 0.55);
          osc.connect(gain);
          gain.connect(scrollAudioCtx.destination);
          osc.start(now + idx * 0.048);
          osc.stop(now + idx * 0.048 + 0.55);
        });
      } catch (e) {}
    }"""

assert old_sound_engine in content, "old_sound_engine not found!"
content = content.replace(old_sound_engine, new_sound_engine)

# Update handleScrollSound to trigger playScrollTick
old_handle = """      // Track scroll velocity when scrolling inside or into hero zone
      if (scrollY <= vh * 1.5) {
        const now = performance.now();
        const dt = Math.max(1, now - lastScrollTime);
        const dy = Math.abs(scrollY - lastScrollY);
        scrollVelocity = Math.min(1.0, (dy / dt) * 0.2 + Math.abs(delta || 0) * 0.0028);

        lastScrollY = scrollY;
        lastScrollTime = now;
      }"""

new_handle = """      // Track scroll velocity and fire tactile haptic ticks
      if (scrollY <= vh * 1.5) {
        const now = performance.now();
        const dt = Math.max(1, now - lastScrollTime);
        const dy = Math.abs(scrollY - lastScrollY);
        scrollVelocity = Math.min(1.0, (dy / dt) * 0.2 + Math.abs(delta || 0) * 0.0028);

        lastScrollY = scrollY;
        lastScrollTime = now;

        // Fire crisp tactile haptic tick proportional to scroll movement
        playScrollTick(Math.max(1.0, scrollVelocity * 3.5));
      }"""

assert old_handle in content, "old_handle not found!"
content = content.replace(old_handle, new_handle)

# Update animate modulation for airy warmth
old_mod = """            // Modulate Fundamental: 120Hz -> 380Hz, Harmonic: 300Hz -> 950Hz, Bandpass: 300Hz -> 1400Hz
            const fundFreq = THREE.MathUtils.lerp(120.0, 380.0, revealProgress);
            const harmFreq = fundFreq * 2.5;
            const filterFreq = THREE.MathUtils.lerp(300.0, 1400.0, revealProgress);

            scrollOsc1.frequency.setTargetAtTime(fundFreq, audioNow, 0.04);
            scrollOsc2.frequency.setTargetAtTime(harmFreq, audioNow, 0.04);
            scrollFilter.frequency.setTargetAtTime(filterFreq, audioNow, 0.04);

            // Volume smoothly balances scroll velocity and visual particle lerp speed
            const dynamicVol = Math.min(0.075, Math.max(scrollVelocity * 0.065, revealDelta * 2.2));
            scrollDroneGain.gain.setTargetAtTime(dynamicVol, audioNow, 0.03);

            // Granular micro-grain sparks as dots snap into 2D photo coords
            if (Math.random() < 0.28 && dynamicVol > 0.012) {
              playParticleGrain(fundFreq * 3.8);
            }"""

new_mod = """            // Warm airy harmonic wash: 220Hz (A3) -> 440Hz (A4), Filter: 500Hz -> 2000Hz
            const fundFreq = THREE.MathUtils.lerp(220.0, 440.0, revealProgress);
            const fifthFreq = fundFreq * 1.5; // Pure harmonic fifth
            const filterFreq = THREE.MathUtils.lerp(500.0, 2200.0, revealProgress);

            scrollOsc1.frequency.setTargetAtTime(fundFreq, audioNow, 0.05);
            scrollOsc2.frequency.setTargetAtTime(fifthFreq, audioNow, 0.05);
            scrollFilter.frequency.setTargetAtTime(filterFreq, audioNow, 0.05);

            // Soft non-fatiguing ambient volume
            const dynamicVol = Math.min(0.045, Math.max(scrollVelocity * 0.04, revealDelta * 1.6));
            scrollDroneGain.gain.setTargetAtTime(dynamicVol, audioNow, 0.04);

            // Subtle haptic tick as particles lerp smoothly
            if (revealDelta > 0.008 && Math.random() < 0.35) {
              playScrollTick(1.2);
            }"""

assert old_mod in content, "old_mod not found!"
content = content.replace(old_mod, new_mod)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PERSONAL_HTML} with new tactile haptic scroll sound")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PORTFOLIO_HTML} with new tactile haptic scroll sound")
