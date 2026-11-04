import os
import re

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

def update_scroll_sound(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace scroll audio engine definition
    old_audio_pattern = r"(// ==========================================================================\s*// INTERACTIVE PHOTO SCROLL CYBER AUDIO ENGINE[\s\S]*?function playHoloChime\(reverse = false\) \{[\s\S]*?\n    \})"

    new_audio_code = '''    // ==========================================================================
    // INTERACTIVE PHOTO SCROLL CYBER AUDIO ENGINE (Web Audio API)
    // Produces silky aerodynamic air glide, tactile micro-ratchet & crystal chimes
    // ==========================================================================
    let scrollAudioCtx = null;
    let scrollAirGain = null;
    let scrollAirFilter = null;
    let scrollHarmonicGain = null;
    let scrollHarmonicFilter = null;
    let scrollOsc1 = null;
    let scrollOsc2 = null;
    let lastScrollY = window.scrollY;
    let lastScrollTime = performance.now();
    let scrollVelocity = 0.0;
    let isChimePlayed = false;
    let isReverseChimePlayed = false;
    let scrollAccumulator = 0;
    let lastRatchetTime = 0;

    function initScrollAudio() {
      if (scrollAudioCtx) return;
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        scrollAudioCtx = new AudioContext();

        // 1. Aerodynamic Velvet Pink Noise (Silky Air Whoosh — No buzzing!)
        const bufferSize = scrollAudioCtx.sampleRate * 2;
        const noiseBuffer = scrollAudioCtx.createBuffer(1, bufferSize, scrollAudioCtx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
        for (let i = 0; i < bufferSize; i++) {
          const white = Math.random() * 2 - 1;
          b0 = 0.99886 * b0 + white * 0.0555179;
          b1 = 0.99332 * b1 + white * 0.0750759;
          b2 = 0.96900 * b2 + white * 0.1538520;
          b3 = 0.86650 * b3 + white * 0.3104856;
          b4 = 0.55000 * b4 + white * 0.5329522;
          b5 = -0.7616 * b5 - white * 0.0168980;
          output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.07;
          b6 = white * 0.115926;
        }

        const noiseSource = scrollAudioCtx.createBufferSource();
        noiseSource.buffer = noiseBuffer;
        noiseSource.loop = true;

        scrollAirFilter = scrollAudioCtx.createBiquadFilter();
        scrollAirFilter.type = 'lowpass';
        scrollAirFilter.frequency.setValueAtTime(350.0, scrollAudioCtx.currentTime);

        scrollAirGain = scrollAudioCtx.createGain();
        scrollAirGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);

        noiseSource.connect(scrollAirFilter);
        scrollAirFilter.connect(scrollAirGain);
        scrollAirGain.connect(scrollAudioCtx.destination);
        noiseSource.start();

        // 2. Warm Celestial Sine Bed (Pure soft sines, absolutely NO harsh buzzing triangle waves)
        scrollHarmonicFilter = scrollAudioCtx.createBiquadFilter();
        scrollHarmonicFilter.type = 'lowpass';
        scrollHarmonicFilter.frequency.setValueAtTime(650.0, scrollAudioCtx.currentTime);

        scrollHarmonicGain = scrollAudioCtx.createGain();
        scrollHarmonicGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);

        scrollOsc1 = scrollAudioCtx.createOscillator();
        scrollOsc1.type = 'sine';
        scrollOsc1.frequency.setValueAtTime(216.0, scrollAudioCtx.currentTime);

        scrollOsc2 = scrollAudioCtx.createOscillator();
        scrollOsc2.type = 'sine';
        scrollOsc2.frequency.setValueAtTime(432.0, scrollAudioCtx.currentTime);

        scrollOsc1.connect(scrollHarmonicFilter);
        scrollOsc2.connect(scrollHarmonicFilter);
        scrollHarmonicFilter.connect(scrollHarmonicGain);
        scrollHarmonicGain.connect(scrollAudioCtx.destination);

        scrollOsc1.start();
        scrollOsc2.start();

        window.scrollAudioCtx = scrollAudioCtx;
        window.scrollDroneGain = scrollAirGain; // Compatibility alias
        window.scrollAirGain = scrollAirGain;
        window.scrollAirFilter = scrollAirFilter;
        window.scrollHarmonicGain = scrollHarmonicGain;
        window.scrollHarmonicFilter = scrollHarmonicFilter;
        window.scrollOsc1 = scrollOsc1;
        window.scrollOsc2 = scrollOsc2;
      } catch (e) {
        console.warn("AudioContext init error:", e);
      }
    }

    // Tactile Kinetic Micro-Ratchet Click (Silky Haptic Rotary Feel)
    function playScrollRatchetClick(progress = 0.5) {
      if (!scrollAudioCtx || window.portfolioAudioMuted) return;
      const nowMs = performance.now();
      if (nowMs - lastRatchetTime < 24) return; // Buttery debounce rate-limit
      lastRatchetTime = nowMs;

      try {
        const t = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();

        // Subtly ascending frequency as photo reveals (1600Hz -> 2600Hz)
        const baseFreq = 1600 + (progress || 0) * 1000 + (Math.random() - 0.5) * 80;
        osc.type = 'sine';
        osc.frequency.setValueAtTime(baseFreq, t);
        osc.frequency.exponentialRampToValueAtTime(380, t + 0.011);

        gain.gain.setValueAtTime(0.022, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.012);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.014);

        // Subtle sub-click body
        const subOsc = scrollAudioCtx.createOscillator();
        const subGain = scrollAudioCtx.createGain();
        subOsc.type = 'triangle';
        subOsc.frequency.setValueAtTime(320, t);
        subGain.gain.setValueAtTime(0.015, t);
        subGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.016);
        subOsc.connect(subGain);
        subGain.connect(scrollAudioCtx.destination);
        subOsc.start(t);
        subOsc.stop(t + 0.018);
      } catch (e) {}
    }

    // Crystalline Glass Spark (Pentatonic Particle Assembling Droplet)
    const CRYSTAL_NOTES = [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98, 2093.00];
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

        gain.gain.setValueAtTime(0.018, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.05);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.055);
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

    content = re.sub(old_audio_pattern, new_audio_code, content)

    # 2. Update handleScrollSound to track scrollAccumulator and trigger playScrollRatchetClick
    old_handle_sound = r"function handleScrollSound\(delta\) \{[\s\S]*?lastScrollTime = now;\s*\}\s*\}"
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

      // Accumulate scroll travel for tactile micro-ratchet click
      scrollAccumulator += Math.abs(delta || dy || 16);
      if (scrollAccumulator >= 18) {
        playScrollRatchetClick(window.revealProgress || 0.0);
        scrollAccumulator = 0;
      }
    }'''
    content = re.sub(old_handle_sound, new_handle_sound, content)

    # 3. Update animate audio modulation block
    old_animate_audio = r"(// --- Interactive Photo Scroll Audio Modulation Engine ---[\s\S]*?// Holographic Completion Chime)"
    new_animate_audio = '''// --- Interactive Photo Scroll Audio Modulation Engine ---
      // Silky pink noise air glide and celestial harmonic warmth track revealProgress
      if (scrollAudioCtx && scrollAirGain) {
        if (window.portfolioAudioMuted) {
          scrollAirGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);
          if (scrollHarmonicGain) scrollHarmonicGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);
        } else {
          const vh = window.innerHeight;
          const timeSinceScroll = performance.now() - lastScrollTime;
          const isHeroZone = window.scrollY <= vh * 1.5;
          const isParticlesMoving = (revealDelta > 0.0008 || timeSinceScroll < 120);

          if (isHeroZone && isParticlesMoving) {
            const audioNow = scrollAudioCtx.currentTime;

            // Silky Air Filter Cutoff: 380Hz -> 1600Hz as photo forms and scroll velocity surges
            const airFilterCutoff = THREE.MathUtils.lerp(380.0, 1600.0, Math.min(1.0, revealProgress * 0.7 + scrollVelocity * 0.5));
            scrollAirFilter.frequency.setTargetAtTime(airFilterCutoff, audioNow, 0.04);

            // Velvet Air Volume: Scales with scroll velocity and particle movement (whisper soft, max 0.038)
            const dynamicAirVol = Math.min(0.038, Math.max(scrollVelocity * 0.035, revealDelta * 1.8));
            scrollAirGain.gain.setTargetAtTime(dynamicAirVol, audioNow, 0.03);

            // Celestial Harmonic Bed: pure subtle sines (216Hz -> 432Hz)
            if (scrollHarmonicGain && scrollOsc1 && scrollOsc2) {
              const chordBase = THREE.MathUtils.lerp(216.0, 324.0, revealProgress);
              scrollOsc1.frequency.setTargetAtTime(chordBase, audioNow, 0.05);
              scrollOsc2.frequency.setTargetAtTime(chordBase * 2.0, audioNow, 0.05);
              scrollHarmonicGain.gain.setTargetAtTime(dynamicAirVol * 0.45, audioNow, 0.04);
            }

            // Crystalline glass sparkles as particles snap into 2D photo coords
            if (Math.random() < 0.22 && dynamicAirVol > 0.008) {
              playCrystalDrop(revealProgress);
            }
          } else {
            scrollAirGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
            if (scrollHarmonicGain) scrollHarmonicGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
          }
        }
      }

      // Holographic Completion Chime'''

    content = re.sub(old_animate_audio, new_animate_audio, content)

    # 4. In updateHeroScrollState, also trigger handleScrollSound(scrollY - lastScrollY)
    if "handleScrollSound(scrollY - lastScrollY);" not in content:
        content = content.replace("function updateHeroScrollState() {\n      if (!isLoaded) return;\n      const scrollY = window.scrollY;",
                                  "function updateHeroScrollState() {\n      if (!isLoaded) return;\n      const scrollY = window.scrollY;\n      handleScrollSound(scrollY - lastScrollY);")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path}")

update_scroll_sound(PERSONAL_HTML)
update_scroll_sound(PORTFOLIO_HTML)
