/**
 * Cyber Audio Engine — Universal Web Audio Synthesizer & Controller
 * Features:
 * - Direct Autoplay Auto-Unlock (Zero Clicks Needed, unlocks on touch/wheel/pointer/key)
 * - Photo Reveal Sound: Dual-Layer (Envato "Scroll Data" stream + Procedural Granular Shimmer)
 * - Reveal Completion Holographic Lock-On Chime
 * - Cinematic Spatial Page Transition Whoosh
 * - Tactile Mechanical Clicks for all Buttons, Tabs & Pills
 * - Subtle Micro-Chirp Hover Feedback for Target Cursor
 * - Google Cloud Badge Verification Chime
 * - Terminal Sub-Bass Boom & Mechanical Keystroke Acoustics
 * - Floating Always-Visible Sound HUD with Live Animated Wave Equalizer
 */

(function() {
  'use strict';

  // Global State
  window.portfolioAudioMuted = false;

  let ctx = null;
  let masterGain = null;
  let isUnlocked = false;

  // Scroll Audio State
  let scrollDataBuffer = null;
  let scrollDataSource = null;
  let scrollDataGain = null;
  let scrollDataFilter = null;
  let isScrollDataLoading = false;
  let isScrollDataPlaying = false;

  // Synthesizer Nodes for Photo Reveal Granular Stream
  let synthOsc1 = null;
  let synthOsc2 = null;
  let synthGain = null;
  let synthFilter = null;
  let isSynthPlaying = false;

  // Last scroll tracker
  let lastScrollSoundTime = 0;
  let revealSoundFadeTimer = null;

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

  // Preload Envato Scroll Data audio
  function loadScrollDataAudio() {
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
      .catch(err => {
        console.warn('Scroll data audio load/decode error (synth fallback active):', err);
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
    } catch (e) {
      console.warn('setupScrollDataNodes error:', e);
    }
  }

  // Procedural Granular Synthesizer Setup (0ms latency fallback + harmonic shimmer)
  function setupSynthNodes() {
    if (!ctx || isSynthPlaying) return;
    try {
      const t = ctx.currentTime;

      // High-frequency harmonic pulse oscillator
      synthOsc1 = ctx.createOscillator();
      synthOsc1.type = 'sawtooth';
      synthOsc1.frequency.setValueAtTime(920, t);

      // Warm sub-harmonic body oscillator
      synthOsc2 = ctx.createOscillator();
      synthOsc2.type = 'triangle';
      synthOsc2.frequency.setValueAtTime(180, t);

      synthFilter = ctx.createBiquadFilter();
      synthFilter.type = 'bandpass';
      synthFilter.Q.setValueAtTime(4.5, t);
      synthFilter.frequency.setValueAtTime(1200, t);

      synthGain = ctx.createGain();
      synthGain.gain.setValueAtTime(0.0001, t);

      synthOsc1.connect(synthFilter);
      synthOsc2.connect(synthFilter);
      synthFilter.connect(synthGain);
      synthGain.connect(masterGain || ctx.destination);

      synthOsc1.start(0);
      synthOsc2.start(0);
      isSynthPlaying = true;
    } catch (e) {
      console.warn('setupSynthNodes error:', e);
    }
  }

  // ==========================================================================
  // AUTOPLAY AUTO-UNLOCK ENGINE (ZERO CLICKS REQUIRED)
  // Activates AudioContext on the very first touch, wheel, pointer or key event
  // ==========================================================================
  function unlockAudio() {
    if (isUnlocked && ctx && ctx.state === 'running') return;
    const c = getAudioContext();
    if (!c) return;

    if (c.state === 'suspended') {
      c.resume().then(() => {
        if (c.state === 'running') {
          isUnlocked = true;
          loadScrollDataAudio();
          setupSynthNodes();
        }
      }).catch(() => {});
    } else if (c.state === 'running') {
      isUnlocked = true;
      loadScrollDataAudio();
      setupSynthNodes();
    }
  }

  const UNLOCK_EVENTS = ['pointerdown', 'touchstart', 'touchmove', 'wheel', 'mousemove', 'keydown', 'scroll', 'click'];
  UNLOCK_EVENTS.forEach(evt => {
    window.addEventListener(evt, unlockAudio, { capture: true, passive: true });
  });

  // Also kick off immediately on script load
  try {
    getAudioContext();
    loadScrollDataAudio();
  } catch (e) {}

  // ==========================================================================
  // CORE SOUND FUNCTIONS
  // ==========================================================================

  const CyberAudio = {
    get context() {
      return getAudioContext();
    },

    unlock: unlockAudio,

    // 1. Photo Reveal Scrolling Sound (Called continuously as particles move)
    playRevealStep(progress, velocity = 0.5) {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      const now = c.currentTime;
      lastScrollSoundTime = performance.now();

      // Ensure nodes are initialized
      if (!scrollDataBuffer && !isScrollDataLoading) loadScrollDataAudio();
      if (scrollDataBuffer && !isScrollDataPlaying) setupScrollDataNodes();
      if (!isSynthPlaying) setupSynthNodes();

      const clampedProg = Math.max(0.0, Math.min(1.0, progress || 0));
      const clampedVel = Math.max(0.1, Math.min(1.0, velocity || 0.5));

      // Layer A: Envato Scroll Data audio loop (Volume 0.55 - 0.75 for clear cyber impact)
      if (scrollDataGain) {
        const targetVol = THREE_Math_clamp(0.48 + clampedVel * 0.28, 0.40, 0.78);
        scrollDataGain.gain.cancelScheduledValues(now);
        scrollDataGain.gain.setTargetAtTime(targetVol, now, 0.03);

        if (scrollDataSource && scrollDataSource.playbackRate) {
          const rate = 0.96 + clampedProg * 0.22;
          scrollDataSource.playbackRate.setTargetAtTime(rate, now, 0.04);
        }
      }

      // Layer B: Procedural Cyber Granular Synth (Ascending harmonic shimmer)
      if (synthGain && synthFilter && synthOsc1) {
        const synthVol = THREE_Math_clamp(0.12 + clampedVel * 0.14, 0.08, 0.26);
        synthGain.gain.cancelScheduledValues(now);
        synthGain.gain.setTargetAtTime(synthVol, now, 0.03);

        const centerFreq = 850 + clampedProg * 1150 + (Math.random() - 0.5) * 80;
        synthFilter.frequency.setTargetAtTime(centerFreq, now, 0.03);
        synthOsc1.frequency.setTargetAtTime(750 + clampedProg * 800, now, 0.03);
      }

      // Animate floating sound HUD equalizer bars
      animateEqualizerBars(true);

      // Auto fade-out when user stops scrolling
      clearTimeout(revealSoundFadeTimer);
      revealSoundFadeTimer = setTimeout(() => {
        CyberAudio.stopRevealSound();
      }, 110);
    },

    stopRevealSound() {
      const c = getAudioContext();
      if (!c) return;
      const now = c.currentTime;

      if (scrollDataGain) {
        scrollDataGain.gain.cancelScheduledValues(now);
        scrollDataGain.gain.setTargetAtTime(0.0001, now, 0.06);
      }
      if (synthGain) {
        synthGain.gain.cancelScheduledValues(now);
        synthGain.gain.setTargetAtTime(0.0001, now, 0.05);
      }

      animateEqualizerBars(false);
    },

    // 2. Photo Assembled 100% — Crystalline Holographic Lock-On Chime + Sub Punch
    playRevealComplete() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      CyberAudio.stopRevealSound();

      try {
        const t = c.currentTime;

        // Sub-bass physical impact punch (75Hz -> 28Hz)
        const subOsc = c.createOscillator();
        const subGain = c.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(78, t);
        subOsc.frequency.exponentialRampToValueAtTime(28, t + 0.35);
        subGain.gain.setValueAtTime(0.35, t);
        subGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.38);
        subOsc.connect(subGain);
        subGain.connect(masterGain || c.destination);
        subOsc.start(t);
        subOsc.stop(t + 0.40);

        // Triple harmonic crystal chime: D5 (587Hz), A5 (880Hz), D6 (1175Hz)
        const freqs = [587.33, 880.0, 1174.66, 1760.0];
        freqs.forEach((f, idx) => {
          const osc = c.createOscillator();
          const gain = c.createGain();
          const delay = idx * 0.045;
          osc.type = idx === 3 ? 'sine' : 'triangle';
          osc.frequency.setValueAtTime(f, t + delay);
          osc.frequency.exponentialRampToValueAtTime(f * 1.02, t + delay + 0.45);
          gain.gain.setValueAtTime(0.09 / (idx + 1), t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.55);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.58);
        });
      } catch (e) {
        console.warn('playRevealComplete error:', e);
      }
    },

    // 3. Cinematic Spatial Page Transition Whoosh (When moving from hero stage to #intro)
    playPageTransition() {
      if (window.portfolioAudioMuted) return;
      unlockAudio();
      const c = getAudioContext();
      if (!c || c.state !== 'running') return;

      try {
        const t = c.currentTime;
        const dur = 0.42;

        // Modulated noise sweep
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
        filter.Q.setValueAtTime(3.0, t);
        filter.frequency.setValueAtTime(260, t);
        filter.frequency.exponentialRampToValueAtTime(1450, t + dur * 0.45);
        filter.frequency.exponentialRampToValueAtTime(320, t + dur);

        const gain = c.createGain();
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.linearRampToValueAtTime(0.24, t + dur * 0.35);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(masterGain || c.destination);

        noise.start(t);
        noise.stop(t + dur + 0.02);
      } catch (e) {}
    },

    // 4. Tactile Mechanical Click (Buttons, Filter Pills, Modal Triggers)
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
        osc.frequency.setValueAtTime(1250, t);
        osc.frequency.exponentialRampToValueAtTime(280, t + 0.024);
        gain.gain.setValueAtTime(0.12, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.026);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.028);
      } catch (e) {}
    },

    // 5. Subtle Target Cursor Reticle Hover / Lock-On Blip
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
        osc.frequency.setValueAtTime(1680, t);
        osc.frequency.exponentialRampToValueAtTime(2150, t + 0.016);
        gain.gain.setValueAtTime(0.022, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.018);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.020);
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
          const delay = idx * 0.04;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, t + delay);
          gain.gain.setValueAtTime(0.08 / (idx + 1), t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.45);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.48);
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
        osc.frequency.setValueAtTime(940, t);
        osc.frequency.exponentialRampToValueAtTime(420, t + 0.022);
        gain.gain.setValueAtTime(0.06, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.024);
        osc.connect(gain);
        gain.connect(masterGain || c.destination);
        osc.start(t);
        osc.stop(t + 0.026);
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
          const delay = idx * 0.065;
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, t + delay);
          gain.gain.setValueAtTime(0.09, t + delay);
          gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + 0.38);
          osc.connect(gain);
          gain.connect(masterGain || c.destination);
          osc.start(t + delay);
          osc.stop(t + delay + 0.40);
        });
      } catch (e) {}
    },

    // 9. Sound Mode Toggle (Mute / Unmute)
    toggleMute(forceState) {
      const now = performance.now();
      if (typeof forceState !== 'boolean' && (now - lastToggleTime < 250)) {
        return; // Guard against rapid duplicate events (e.g. multi-delegation)
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
          window.showToast('🔇 Cyber audio muted');
        }
      } else {
        unlockAudio();
        if (masterGain && ctx) {
          masterGain.gain.setValueAtTime(1.0, ctx.currentTime);
        }
        if (typeof window.showToast === 'function') {
          window.showToast('🔊 Cyber audio enabled (Dual-layer active)');
        }
        // Play power-up confirmation chime
        CyberAudio.playBadgeOpen();
      }
    }
  };

  let lastToggleTime = 0;

  // Helper clamp
  function THREE_Math_clamp(val, min, max) {
    return Math.max(min, Math.min(max, val));
  }

  // Animate Equalizer Bars in HUD
  function animateEqualizerBars(isActive) {
    const bars = document.querySelectorAll('.sound-eq-bar');
    bars.forEach((b, i) => {
      if (isActive) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
  }

  // Update All Sound Buttons & HUD elements
  function updateSoundUI() {
    const isMuted = window.portfolioAudioMuted;
    
    // 1. Floating HUD
    const hud = document.getElementById('floating-sound-hud');
    if (hud) {
      hud.classList.toggle('muted', isMuted);
      const label = hud.querySelector('.sound-hud-label');
      if (label) {
        label.textContent = isMuted ? 'SOUND: OFF' : 'SOUND: ON';
      }
      hud.setAttribute('title', isMuted ? 'Sound Muted (Click to enable)' : 'Sound Enabled (Click to mute)');
    }

    // 2. Navbar button
    const navBtn = document.getElementById('sound-toggle-btn');
    if (navBtn) {
      navBtn.classList.toggle('muted', isMuted);
      navBtn.setAttribute('title', isMuted ? 'Sound Muted (Click to enable)' : 'Sound Enabled (Click to mute)');
      navBtn.innerHTML = isMuted
        ? `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path><path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`
        : `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
    }
  }

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

    // Sound toggle buttons
    const navBtn = document.getElementById('sound-toggle-btn');
    if (navBtn && !navBtn.dataset.soundBound) {
      navBtn.dataset.soundBound = 'true';
      navBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        CyberAudio.toggleMute();
      });
    }

    const hud = document.getElementById('floating-sound-hud');
    if (hud && !hud.dataset.soundBound) {
      hud.dataset.soundBound = 'true';
      hud.addEventListener('click', (e) => {
        e.stopPropagation();
        CyberAudio.toggleMute();
      });
    }
  }

  // Inject Floating Sound HUD Pill into DOM if not present
  function ensureFloatingSoundHUD() {
    if (document.getElementById('floating-sound-hud')) return;

    const hud = document.createElement('button');
    hud.id = 'floating-sound-hud';
    hud.className = 'floating-sound-hud';
    hud.setAttribute('title', 'Cyber Sound Engine (Click to mute/unmute)');
    hud.setAttribute('aria-label', 'Toggle Sound Mode');
    hud.innerHTML = `
      <div class="sound-eq-icon">
        <span class="sound-eq-bar b1"></span>
        <span class="sound-eq-bar b2"></span>
        <span class="sound-eq-bar b3"></span>
        <span class="sound-eq-bar b4"></span>
      </div>
      <span class="sound-hud-label">SOUND: ON</span>
    `;

    document.body.appendChild(hud);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      ensureFloatingSoundHUD();
      initInteractiveSoundListeners();
      updateSoundUI();
    });
  } else {
    ensureFloatingSoundHUD();
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
