import os

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Refine handleScrollSound
old_handle = """    // Modulate sound based on scroll activity and reveal progress
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
    }"""

new_handle = """    // Modulate sound based on scroll activity and reveal progress
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

      // Track scroll velocity when scrolling inside or into hero zone
      if (scrollY <= vh * 1.5) {
        const now = performance.now();
        const dt = Math.max(1, now - lastScrollTime);
        const dy = Math.abs(scrollY - lastScrollY);
        scrollVelocity = Math.min(1.0, (dy / dt) * 0.2 + Math.abs(delta || 0) * 0.0028);

        lastScrollY = scrollY;
        lastScrollTime = now;
      }
    }"""

assert old_handle in content, "old_handle not found in content!"
content = content.replace(old_handle, new_handle)

# Refine animate audio block
old_animate = """      // Fade out scroll sound when scrolling ceases
      const timeSinceScroll = performance.now() - lastScrollTime;
      if (timeSinceScroll > 75 && scrollDroneGain && scrollAudioCtx) {
        scrollDroneGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
      }

      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;
      if (Math.abs(targetRevealProgress - revealProgress) < 0.0005) {
        revealProgress = targetRevealProgress;
      }"""

new_animate = """      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      const prevReveal = revealProgress;
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;
      if (Math.abs(targetRevealProgress - revealProgress) < 0.0005) {
        revealProgress = targetRevealProgress;
      }
      const revealDelta = Math.abs(revealProgress - prevReveal);

      // --- Interactive Photo Scroll Audio Modulation Engine ---
      // Frequencies, resonant bandpass and granular particle sparks track revealProgress in real-time
      if (scrollAudioCtx && scrollDroneGain) {
        if (window.portfolioAudioMuted) {
          scrollDroneGain.gain.setValueAtTime(0.0, scrollAudioCtx.currentTime);
        } else {
          const vh = window.innerHeight;
          const timeSinceScroll = performance.now() - lastScrollTime;
          const isHeroZone = window.scrollY <= vh * 1.5;
          const isParticlesMoving = (revealDelta > 0.0008 || timeSinceScroll < 120);

          if (isHeroZone && isParticlesMoving) {
            const audioNow = scrollAudioCtx.currentTime;
            // Modulate Fundamental: 120Hz -> 380Hz, Harmonic: 300Hz -> 950Hz, Bandpass: 300Hz -> 1400Hz
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
            }
          } else {
            scrollDroneGain.gain.setTargetAtTime(0.0, scrollAudioCtx.currentTime, 0.08);
          }
        }
      }

      // Holographic Completion Chime on 100% reveal or return to dots
      if (revealProgress >= 0.98 && !isChimePlayed) {
        isChimePlayed = true;
        isReverseChimePlayed = false;
        playHoloChime(false);
      } else if (revealProgress <= 0.05 && !isReverseChimePlayed && isChimePlayed) {
        isReverseChimePlayed = true;
        isChimePlayed = false;
        playHoloChime(true);
      }"""

assert old_animate in content, "old_animate not found in content!"
content = content.replace(old_animate, new_animate)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Refined audio engine in {PERSONAL_HTML}")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Refined audio engine in {PORTFOLIO_HTML}")
