/**
 * Cyber Audio Engine — Zero-Latency, Soft Ambiance & Interactive SFX Synthesizer
 * 
 * Updates:
 * - Instantaneous 0ms latency: Pure Web Audio synthesis (No network loading delays)
 * - Ultra-soft, gentle volume: Subtle modern cyber micro-grain pulses (non-intrusive)
 * - Zero trailing lag: Sounds play strictly while the user is actively scrolling and cut off instantly on pause
 * - Sound mode button hidden from UI as requested (Audio active in background by default)
 */

(function() {
  'use strict';

  // Global State
  window.portfolioAudioMuted = false;

  let ctx = null;
  let masterGain = null;
  let isUnlocked = false;
  let lastScrollTickTime = 0;
  let lastToggleTime = 0;

  function getAudioContext() {
    if (!ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        ctx = new AudioCtx();
        masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(1.0, ctx.currentTime);
        masterGain.connect(ctx.destination);
        window.scrollAudioCtx = ctx;
      }
    }
    if (ctx && ctx.state === 'suspended') {
      ctx.resume().catch(() => {});
    }
    return ctx;
  }

  // ==========================================================================
  // AUTOPLAY AUTO-UNLOCK ENGINE (ZERO CLICKS REQUIRED)
  // Activates AudioContext instantly on the very first touch, wheel, pointer or key event
  // ==========================================================================
  function unlockAudio() {
    if (isUnlocked && ctx && ctx.state === 'running') return;
    const c = getAudioContext();
    if (!c) return;

    if (c.state === 'suspended') {
      c.resume().then(() => {
        if (c.state === 'running') {
          isUnlocked = true;
        }
      }).catch(() => {});
    } else if (c.state === 'running') {
      isUnlocked = true;
    }
  }

  const UNLOCK_EVENTS = ['pointerdown', 'touchstart', 'touchmove', 'wheel', 'mousemove', 'keydown', 'scroll', 'click'];
  UNLOCK_EVENTS.forEach(evt => {
    window.addEventListener(evt, unlockAudio, { capture: true, passive: true });
  });

  // Pre-initialize
  try {
    getAudioContext();
  } catch (e) {}

  // ==========================================================================
  // CORE SOUND FUNCTIONS
  // ==========================================================================

  const CyberAudio = {
    get context() {
      return getAudioContext();
    },

    unlock: unlockAudio,

    // 1. Photo Reveal Scrolling Sound:
    // Pure synthesized micro-grain pulse (0ms latency, warm frequencies, gentle volume)
    playRevealStep(progress = 0, velocity = 0.5) {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      const now = c.currentTime;

      // Throttle micro-ticks to 26ms so rapid trackpad events don't crackle
      if (now - lastScrollTickTime < 0.026) return;
      lastScrollTickTime = now;

      try {
        const clampedProg = Math.max(0.0, Math.min(1.0, progress || 0));
        const clampedVel = Math.max(0.1, Math.min(1.0, velocity || 0.5));

        // Soft, gentle cyber frequency (360Hz base to 580Hz as photo resolves)
        const baseFreq = 360 + clampedProg * 220;
        const tickDuration = 0.038; // 38ms micro-pulse: stops immediately with the finger

        // Dual soft oscillators (warm sine + subtle triangle)
        const osc1 = c.createOscillator();
        const osc2 = c.createOscillator();
        osc1.type = 'sine';
        osc2.type = 'triangle';
        osc1.frequency.setValueAtTime(baseFreq, now);
        osc2.frequency.setValueAtTime(baseFreq * 1.5, now);

        // Low-pass filter to remove any harshness or buzz
        const filter = c.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(800 + clampedProg * 350, now);
        filter.Q.setValueAtTime(1.0, now);

        // Very soft, quiet gain (0.025 - 0.055 peak, comfortable and pleasant)
        const gain = c.createGain();
        const peakGain = 0.025 + clampedVel * 0.028;
        gain.gain.setValueAtTime(0.0001, now);
        gain.gain.linearRampToValueAtTime(peakGain, now + 0.004); // 4ms soft attack
        gain.gain.exponentialRampToValueAtTime(0.0001, now + tickDuration); // 34ms decay

        osc1.connect(filter);
        osc2.connect(filter);
        filter.connect(gain);
        gain.connect(masterGain || c.destination);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + tickDuration + 0.005);
        osc2.stop(now + tickDuration + 0.005);
      } catch (e) {}
    },

    stopRevealSound() {
      // Micro-pulses decay automatically in 38ms with zero hanging latency
    },

    // 2. Photo Assembled 100% — Gentle Holographic Lock-On Chime
    playRevealComplete() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;

        // Gentle sub-bass pulse (55Hz -> 28Hz) - soft 0.08 gain
        const subOsc = c.createOscillator();
        const subGain = c.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(55, t);
        subOsc.frequency.exponentialRampToValueAtTime(28, t + 0.25);
        subGain.gain.setValueAtTime(0.08, t);
        subGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.28);
        subOsc.connect(subGain);
        subGain.connect(masterGain || c.destination);
        subOsc.start(t);
        subOsc.stop(t + 0.30);

        // Soft harmonic chime (E5, B5, E6) - gentle 0.035 gain
        const freqs = [659.25, 987.77, 1318.51];
        freqs.forEach((f, idx) => {
          const osc = c.createOscillator();
          const gain = c.createGain();
          const delay = idx * 0.04;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, t + delay);
          gain.gain.setValueAtTime(0.035 / (idx + 1), t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.32);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.35);
        });
      } catch (e) {}
    },

    // 3. Soft Spatial Page Transition Whoosh (When advancing to #intro)
    playPageTransition() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const dur = 0.32;

        const bufferSize = c.sampleRate * dur;
        const buffer = c.createBuffer(1, bufferSize, c.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
          data[i] = Math.random() * 2 - 1;
        }

        const noise = c.createBufferSource();
        noise.buffer = buffer;

        const filter = c.createBiquadFilter();
        filter.type = 'bandpass';
        filter.Q.setValueAtTime(2.0, t);
        filter.frequency.setValueAtTime(240, t);
        filter.frequency.exponentialRampToValueAtTime(950, t + dur * 0.4);
        filter.frequency.exponentialRampToValueAtTime(280, t + dur);

        const gain = c.createGain();
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.linearRampToValueAtTime(0.045, t + dur * 0.3); // Soft 0.045 gain
        gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(masterGain || c.destination);

        noise.start(t);
        noise.stop(t + dur + 0.01);
      } catch (e) {}
    },

    // 4. Subtle Tactile Mechanical Click (Buttons & Pills)
    playClick() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const osc = c.createOscillator();
        const gain = c.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1150, t);
        osc.frequency.exponentialRampToValueAtTime(260, t + 0.022);
        gain.gain.setValueAtTime(0.038, t); // Soft 0.038 gain
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.024);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.026);
      } catch (e) {}
    },

    // 5. Subtle Target Cursor Reticle Hover Blip
    playHover() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const osc = c.createOscillator();
        const gain = c.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1600, t);
        osc.frequency.exponentialRampToValueAtTime(2000, t + 0.014);
        gain.gain.setValueAtTime(0.012, t); // Very gentle 0.012 gain
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.016);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.018);
      } catch (e) {}
    },

    // 6. Google Cloud Badge Verification Chime
    playBadgeOpen() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const chord = [659.25, 830.61, 987.77, 1318.51];
        chord.forEach((freq, idx) => {
          const osc = c.createOscillator();
          const gain = c.createGain();
          const delay = idx * 0.035;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, t + delay);
          gain.gain.setValueAtTime(0.035 / (idx + 1), t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.35);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.38);
        });
      } catch (e) {}
    },

    // 7. AWS Tab Switch Relay Click
    playTabSwitch() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const osc = c.createOscillator();
        const gain = c.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(820, t);
        osc.frequency.exponentialRampToValueAtTime(380, t + 0.020);
        gain.gain.setValueAtTime(0.028, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.022);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.024);
      } catch (e) {}
    },

    // 8. Contact Form Success Sonic Burst
    playSuccess() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const notes = [523.25, 659.25, 783.99, 1046.5];
        notes.forEach((freq, idx) => {
          const osc = c.createOscillator();
          const gain = c.createGain();
          const delay = idx * 0.055;
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, t + delay);
          gain.gain.setValueAtTime(0.04, t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.32);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.34);
        });
      } catch (e) {}
    },

    // 9. Sound Mode Toggle (Maintained for programmatic use if needed)
    toggleMute(forceState) {
      const now = performance.now();
      if (typeof forceState !== 'boolean' && (now - lastToggleTime < 250)) {
        return;
      }
      lastToggleTime = now;

      if (typeof forceState === 'boolean') {
        window.portfolioAudioMuted = forceState;
      } else {
        window.portfolioAudioMuted = !window.portfolioAudioMuted;
      }

      if (window.portfolioAudioMuted) {
        if (masterGain && ctx) {
          masterGain.gain.setValueAtTime(0.0001, ctx.currentTime);
        }
      } else {
        unlockAudio();
        if (masterGain && ctx) {
          masterGain.gain.setValueAtTime(1.0, ctx.currentTime);
        }
      }
    }
  };

  // Attach click listeners to all buttons and interactive cards
  function initInteractiveSoundListeners() {
    // Buttons click
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('button, .btn-pill, .filter-btn, .aws-tab-btn, .badge-verify-btn, a[href^="#"]');
      if (btn && !btn.id?.includes('sound-toggle')) {
        CyberAudio.playClick();
      }
    }, { capture: true, passive: true });

    // Hover blip for desktop
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      let lastHoverTime = 0;
      document.addEventListener('mouseover', (e) => {
        const item = e.target.closest('.project-card, .badge-item-card, .cyber-spec-chip, .btn-pill, .filter-btn, .aws-tab-btn');
        const now = performance.now();
        if (item && now - lastHoverTime > 90) {
          lastHoverTime = now;
          CyberAudio.playHover();
        }
      }, { passive: true });
    }

    // Ensure any sound buttons in DOM are hidden as requested
    hideSoundButtons();
  }

  function hideSoundButtons() {
    const soundBtn = document.getElementById('sound-toggle-btn');
    if (soundBtn) {
      soundBtn.style.display = 'none';
      soundBtn.setAttribute('aria-hidden', 'true');
    }
    const hud = document.getElementById('floating-sound-hud');
    if (hud) {
      hud.style.display = 'none';
      hud.setAttribute('aria-hidden', 'true');
    }
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initInteractiveSoundListeners();
      hideSoundButtons();
    });
  } else {
    initInteractiveSoundListeners();
    hideSoundButtons();
  }

  // Export to window
  window.CyberAudio = CyberAudio;
  window.handleScrollSound = (delta) => {
    CyberAudio.playRevealStep(window.revealProgress || 0, Math.min(1.0, Math.abs(delta || 100) / 140));
  };
  window.unlockAudio = unlockAudio;
  window.playTactileClick = () => CyberAudio.playClick();
  window.playTactileHover = () => CyberAudio.playHover();

})();
