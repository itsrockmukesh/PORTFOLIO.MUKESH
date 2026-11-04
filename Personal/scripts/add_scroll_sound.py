import os
import re

CONTENT_FILE = "/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41/.system_generated/steps/572/content.md"
PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Let's inspect where updateHeroScrollState is in html and inject the scroll sound engine
sound_engine_code = """
    // ==========================================================================
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
    }

    // Modulate sound based on scroll activity and reveal progress
    function handleScrollSound(delta) {
      if (window.portfolioAudioMuted) return;
      if (!scrollAudioCtx) {
        initScrollAudio();
      }
      if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') {
        scrollAudioCtx.resume();
      }
      if (!scrollAudioCtx || !scrollDroneGain) return;

      const vh = window.innerHeight;
      const scrollY = window.scrollY;

      // Only produce sound while scrolling through the photo hero reveal zone
      if (scrollY <= vh * 1.5) {
        const now = performance.now();
        const dt = Math.max(1, now - lastScrollTime);
        const dy = Math.abs(scrollY - lastScrollY);
        scrollVelocity = Math.min(1.0, (dy / dt) * 0.18 + Math.abs(delta || 0) * 0.0025);

        lastScrollY = scrollY;
        lastScrollTime = now;

        const audioNow = scrollAudioCtx.currentTime;

        // Modulate Frequency with revealProgress: 120Hz -> 380Hz for fundamental, 300Hz -> 1400Hz for filter
        const fundFreq = THREE.MathUtils.lerp(120.0, 380.0, revealProgress);
        const harmFreq = fundFreq * 2.5;
        const filterFreq = THREE.MathUtils.lerp(300.0, 1400.0, revealProgress);

        scrollOsc1.frequency.setTargetAtTime(fundFreq, audioNow, 0.04);
        scrollOsc2.frequency.setTargetAtTime(harmFreq, audioNow, 0.04);
        scrollFilter.frequency.setTargetAtTime(filterFreq, audioNow, 0.04);

        // Volume scales smoothly with scroll velocity
        const targetVol = Math.min(0.07, scrollVelocity * 0.06);
        scrollDroneGain.gain.setTargetAtTime(targetVol, audioNow, 0.03);

        // Particle click sparks
        if (Math.random() < 0.32 && scrollVelocity > 0.04) {
          playParticleGrain(fundFreq * 3.8);
        }

        // Lock-in chime on 100% reveal or return to dots
        if (revealProgress >= 0.98 && !isChimePlayed) {
          isChimePlayed = true;
          isReverseChimePlayed = false;
          playHoloChime(false);
        } else if (revealProgress <= 0.05 && !isReverseChimePlayed && isChimePlayed) {
          isReverseChimePlayed = true;
          isChimePlayed = false;
          playHoloChime(true);
        }
      } else {
        if (scrollDroneGain) {
          scrollDroneGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
        }
      }
    }

    // Unlock AudioContext on first user interaction
    ['click', 'keydown', 'wheel', 'touchstart', 'scroll'].forEach(evt => {
      window.addEventListener(evt, () => {
        if (!scrollAudioCtx) initScrollAudio();
        if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') {
          scrollAudioCtx.resume();
        }
      }, { once: true, passive: true });
    });
"""

# Inject before updateHeroScrollState
target_str = "// --- Pinned Scroll Gating: First photo scrolls fully, then full website scrolls ---"
if target_str in html:
    html = html.replace(target_str, sound_engine_code + "\n    " + target_str)
else:
    print("Warning: target_str not found, checking function updateHeroScrollState")
    html = html.replace("function updateHeroScrollState() {", sound_engine_code + "\n    function updateHeroScrollState() {")

# Hook handleScrollSound inside updateHeroScrollState
old_update = """      if (scrollY <= 0) {
        targetRevealProgress = 0.0;
      } else if (scrollY < revealDistance) {
        targetRevealProgress = scrollY / revealDistance;
      } else {
        targetRevealProgress = 1.0;
      }"""

new_update = """      if (scrollY <= 0) {
        targetRevealProgress = 0.0;
      } else if (scrollY < revealDistance) {
        targetRevealProgress = scrollY / revealDistance;
      } else {
        targetRevealProgress = 1.0;
      }
      handleScrollSound();"""

html = html.replace(old_update, new_update)

# Add wheel listener with delta
wheel_hook = """
    window.addEventListener('wheel', (e) => {
      handleScrollSound(e.deltaY);
    }, { passive: true });
"""
html = html.replace("window.addEventListener('scroll', updateHeroScrollState, { passive: true });", "window.addEventListener('scroll', updateHeroScrollState, { passive: true });\n" + wheel_hook)

# In the animate function, fade out sound when scrolling stops
old_animate = """      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;"""

new_animate = """      // Fade out scroll sound when scrolling ceases
      const timeSinceScroll = performance.now() - lastScrollTime;
      if (timeSinceScroll > 75 && scrollDroneGain && scrollAudioCtx) {
        scrollDroneGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
      }

      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;"""

html = html.replace(old_animate, new_animate)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully updated {PERSONAL_HTML} with Photo Scroll Audio Engine")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Successfully updated {PORTFOLIO_HTML} with Photo Scroll Audio Engine")
