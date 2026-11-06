/**
 * Cyber Audio Engine — Precision Optical Focus & Ambient Digital Sound
 * 
 * Features:
 * - Authentic Envato "Scroll Data" stream at calibrated, comfortable volume (0.08 - 0.15)
 * - Microscopic optical camera focus ratchet ticks per scroll notch (18ms micro-pulse)
 * - Authentic camera shutter focus lock (*snap*) on 100% photo reveal completion
 * - Preloaded in memory at startup for instantaneous 0ms latency
 * - Instant fade to silence (35ms) when scrolling pauses — zero trailing lag
 * - Sound mode buttons completely hidden from UI (active by default in background)
 */

(function() {
  'use strict';

  // Global State
  window.portfolioAudioMuted = false;

  let ctx = null;
  let masterGain = null;
  let isUnlocked = false;

  // Scroll Audio Buffer State (Preloaded Envato Stream)
  let scrollDataBuffer = null;
  let scrollDataSource = null;
  let scrollDataGain = null;
  let scrollDataFilter = null;
  let isScrollDataLoading = false;
  let isScrollDataPlaying = false;

  let lastScrollTickTime = 0;
  let revealFadeTimer = null;
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

  // Preload and decode Envato audio immediately on startup
  function preloadScrollDataAudio() {
    if (scrollDataBuffer || isScrollDataLoading) return;
    const c = getAudioContext();
    if (!c) return;

    isScrollDataLoading = true;
    fetch('assets/scroll-data.m4a')
      .then(res => {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.arrayBuffer();
      })
      .then(buf => c.decodeAudioData(buf))
      .then(decoded => {
        scrollDataBuffer = decoded;
        isScrollDataLoading = false;
        setupScrollDataNodes();
      })
      .catch(() => {
        isScrollDataLoading = false;
      });
  }

  function setupScrollDataNodes() {
    if (!ctx || !scrollDataBuffer || isScrollDataPlaying) return;
    try {
      scrollDataSource = ctx.createBufferSource();
      scrollDataSource.buffer = scrollDataBuffer;
      scrollDataSource.loop = true;

      scrollDataFilter = ctx.createBiquadFilter();
      scrollDataFilter.type = 'highpass';
      scrollDataFilter.frequency.setValueAtTime(120.0, ctx.currentTime);

      scrollDataGain = ctx.createGain();
      scrollDataGain.gain.setValueAtTime(0.0001, ctx.currentTime);

      scrollDataSource.connect(scrollDataFilter);
      scrollDataFilter.connect(scrollDataGain);
      scrollDataGain.connect(masterGain || ctx.destination);

      scrollDataSource.start(0);
      isScrollDataPlaying = true;
    } catch (e) {}
  }

  // Subtle Optical Focus Micro-Tick (Simulates precision camera lens ring ratchet)
  function playFocusTick(prog, vel) {
    if (!ctx || ctx.state !== 'running') return;
    const now = ctx.currentTime;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      osc.type = 'triangle';
      const freq = 1200 + prog * 420;
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(280, now + 0.016);

      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(1450, now);
      filter.Q.setValueAtTime(2.5, now);

      const peak = 0.018 + vel * 0.016; // Soft 0.018 - 0.034 max
      gain.gain.setValueAtTime(peak, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.018);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(masterGain || ctx.destination);

      osc.start(now);
      osc.stop(now + 0.020);
    } catch (e) {}
  }

  // ==========================================================================
  // AUTOPLAY AUTO-UNLOCK ENGINE (ZERO CLICKS REQUIRED)
  // ==========================================================================
  function unlockAudio() {
    if (isUnlocked && ctx && ctx.state === 'running') return;
    const c = getAudioContext();
    if (!c) return;

    if (c.state === 'suspended') {
      c.resume().then(() => {
        if (c.state === 'running') {
          isUnlocked = true;
          preloadScrollDataAudio();
        }
      }).catch(() => {});
    } else if (c.state === 'running') {
      isUnlocked = true;
      preloadScrollDataAudio();
    }
  }

  const UNLOCK_EVENTS = ['pointerdown', 'touchstart', 'touchmove', 'wheel', 'mousemove', 'keydown', 'scroll', 'click'];
  UNLOCK_EVENTS.forEach(evt => {
    window.addEventListener(evt, unlockAudio, { capture: true, passive: true });
  });

  // Start preloading immediately
  try {
    getAudioContext();
    preloadScrollDataAudio();
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
    // Blend of authentic digital data stream at gentle volume (0.08 - 0.15) + optical focus micro-ticks
    playRevealStep(progress = 0, velocity = 0.5) {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      const now = c.currentTime;
      const clampedProg = Math.max(0.0, Math.min(1.0, progress || 0));
      const clampedVel = Math.max(0.1, Math.min(1.0, velocity || 0.5));

      // Layer A: Preloaded Envato Stream at comfortable, non-intrusive volume
      if (!scrollDataBuffer && !isScrollDataLoading) preloadScrollDataAudio();
      if (scrollDataBuffer && !isScrollDataPlaying) setupScrollDataNodes();

      if (scrollDataGain) {
        const targetVol = 0.075 + clampedVel * 0.065; // Soft 0.075 - 0.14 max
        scrollDataGain.gain.cancelScheduledValues(now);
        scrollDataGain.gain.setTargetAtTime(targetVol, now, 0.02);

        if (scrollDataSource && scrollDataSource.playbackRate) {
          const rate = 0.96 + clampedProg * 0.15;
          scrollDataSource.playbackRate.setTargetAtTime(rate, now, 0.03);
        }
      }

      // Layer B: Subtle Optical Focus Micro-Tick per notch (no artificial beep tones)
      if (now - lastScrollTickTime >= 0.024) {
        lastScrollTickTime = now;
        playFocusTick(clampedProg, clampedVel);
      }

      // Cut off immediately within 50ms when scrolling pauses (zero trailing lag)
      clearTimeout(revealFadeTimer);
      revealFadeTimer = setTimeout(() => {
        CyberAudio.stopRevealSound();
      }, 50);
    },

    stopRevealSound() {
      const c = getAudioContext();
      if (!c) return;
      const now = c.currentTime;
      if (scrollDataGain) {
        scrollDataGain.gain.cancelScheduledValues(now);
        scrollDataGain.gain.setTargetAtTime(0.0001, now, 0.035);
      }
    },

    // 2. Photo Assembled 100% — Camera Shutter Focus Snap (*kchhk*) + subtle chime
    playRevealComplete() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      CyberAudio.stopRevealSound();

      try {
        const t = c.currentTime;

        // Shutter Blade 1 (Primary focus click)
        const osc1 = c.createOscillator();
        const g1 = c.createGain();
        osc1.type = 'triangle';
        osc1.frequency.setValueAtTime(1600, t);
        osc1.frequency.exponentialRampToValueAtTime(320, t + 0.020);
        g1.gain.setValueAtTime(0.045, t);
        g1.gain.exponentialRampToValueAtTime(0.0001, t + 0.022);
        osc1.connect(g1);
        g1.connect(masterGain || c.destination);
        osc1.start(t);
        osc1.stop(t + 0.025);

        // Shutter Blade 2 (Mechanical snap after 38ms)
        const osc2 = c.createOscillator();
        const g2 = c.createGain();
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(1180, t + 0.038);
        osc2.frequency.exponentialRampToValueAtTime(240, t + 0.065);
        g2.gain.setValueAtTime(0.05, t + 0.038);
        g2.gain.exponentialRampToValueAtTime(0.0001, t + 0.068);
        osc2.connect(g2);
        g2.connect(masterGain || c.destination);
        osc2.start(t + 0.038);
        osc2.stop(t + 0.072);

        // Camera Body Resonance (Soft 55Hz acoustic thump)
        const sub = c.createOscillator();
        const subG = c.createGain();
        sub.type = 'sine';
        sub.frequency.setValueAtTime(58, t + 0.038);
        sub.frequency.exponentialRampToValueAtTime(26, t + 0.18);
        subG.gain.setValueAtTime(0.06, t + 0.038);
        subG.gain.exponentialRampToValueAtTime(0.0001, t + 0.20);
        sub.connect(subG);
        subG.connect(masterGain || c.destination);
        sub.start(t + 0.038);
        sub.stop(t + 0.22);

        // Subtle crystal focus confirmation harmonic (E6: 1318.5Hz)
        const chime = c.createOscillator();
        const chimeG = c.createGain();
        chime.type = 'sine';
        chime.frequency.setValueAtTime(1318.5, t + 0.055);
        chimeG.gain.setValueAtTime(0.025, t + 0.055);
        chimeG.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
        chime.connect(chimeG);
        chimeG.connect(masterGain || c.destination);
        chime.start(t + 0.055);
        chime.stop(t + 0.38);
      } catch (e) {}
    },

    // 3. Soft Spatial Page Transition Whoosh
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
        gain.gain.linearRampToValueAtTime(0.045, t + dur * 0.3);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(masterGain || c.destination);

        noise.start(t);
        noise.stop(t + dur + 0.01);
      } catch (e) {}
    },

    // 4. Subtle Tactile Mechanical Click
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
        gain.gain.setValueAtTime(0.038, t);
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
        gain.gain.setValueAtTime(0.012, t);
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

    // 9. Sound Mode Toggle (For programmatic usage)
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

      updateSoundUI();

      if (window.portfolioAudioMuted) {
        CyberAudio.stopRevealSound();
        if (masterGain && ctx) {
          masterGain.gain.setValueAtTime(0.0001, ctx.currentTime);
        }
        if (typeof window.showToast === 'function') {
          window.showToast('🔇 Sound: OFF');
        }
      } else {
        unlockAudio();
        if (masterGain && ctx) {
          masterGain.gain.setValueAtTime(1.0, ctx.currentTime);
        }
        if (typeof window.showToast === 'function') {
          window.showToast('🔊 Sound: ON');
        }
        CyberAudio.playClick();
      }
    }
  };

  // Synchronize all Sound On/Off Buttons across the page
  function updateSoundUI() {
    const isMuted = !!window.portfolioAudioMuted;
    const soundBtns = document.querySelectorAll('.sound-toggle-btn, #sound-toggle-btn, #floating-sound-btn');
    soundBtns.forEach(btn => {
      btn.classList.toggle('muted', isMuted);
      const textEl = btn.querySelector('.sound-label-text');
      if (textEl) {
        textEl.textContent = isMuted ? 'SOUND OFF' : 'SOUND ON';
      }
      btn.setAttribute('title', isMuted ? 'Sound is OFF (Click to turn ON)' : 'Sound is ON (Click to turn OFF)');
      btn.setAttribute('aria-label', isMuted ? 'Turn Sound ON' : 'Turn Sound OFF');
    });
  }

  // Attach click listeners to all buttons and interactive cards
  function initInteractiveSoundListeners() {
    // Sound Toggle Button click listener (Delegated for all instances)
    document.addEventListener('click', (e) => {
      const soundBtn = e.target.closest('.sound-toggle-btn, #sound-toggle-btn, #floating-sound-btn');
      if (soundBtn) {
        e.stopPropagation();
        CyberAudio.toggleMute();
      }
    });

    // Regular buttons click sound
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('button, .btn-pill, .filter-btn, .aws-tab-btn, .badge-verify-btn, a[href^="#"]');
      if (btn && !btn.closest('.sound-toggle-btn, #sound-toggle-btn, #floating-sound-btn')) {
        CyberAudio.playClick();
      }
    }, { capture: true, passive: true });

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
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initInteractiveSoundListeners();
      updateSoundUI();
    });
  } else {
    initInteractiveSoundListeners();
    updateSoundUI();
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
