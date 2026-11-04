import os

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Define cursor sound functions right after playHoloChime
cursor_audio_defs = """
    // ==========================================================================
    // TACTILE CURSOR SOUND ENGINE (Hover & Click Micro-Acoustics)
    // Produces subtle, luxury micro-haptic chirps & crisp mechanical clicks
    // ==========================================================================
    let lastHoveredElement = null;
    let lastHoverTime = 0;

    function playCursorHoverSound(target) {
      if (window.portfolioAudioMuted) return;
      const now = performance.now();
      if (target === lastHoveredElement && (now - lastHoverTime) < 220) return;
      if ((now - lastHoverTime) < 45) return; // Debounce rapid movements
      lastHoveredElement = target;
      lastHoverTime = now;

      if (!scrollAudioCtx) initScrollAudio();
      if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') {
        scrollAudioCtx.resume();
      }
      if (!scrollAudioCtx) return;

      try {
        const t = scrollAudioCtx.currentTime;
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();

        // High-tech subtle tactile micro-chirp (visionOS / luxury tactile feedback)
        const baseFreq = 1050 + Math.random() * 90;
        osc.type = 'sine';
        osc.frequency.setValueAtTime(baseFreq, t);
        osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.3, t + 0.022);

        gain.gain.setValueAtTime(0.018, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.024);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.025);
      } catch (e) {}
    }

    // Crisp Tactile Cursor Placement / Click Sound
    function playCursorClickSound(target) {
      if (window.portfolioAudioMuted) return;
      if (!scrollAudioCtx) initScrollAudio();
      if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') {
        scrollAudioCtx.resume();
      }
      if (!scrollAudioCtx) return;

      try {
        const t = scrollAudioCtx.currentTime;
        // Dual component mechanical cyber click
        const osc = scrollAudioCtx.createOscillator();
        const gain = scrollAudioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1380, t);
        osc.frequency.exponentialRampToValueAtTime(280, t + 0.028);

        gain.gain.setValueAtTime(0.026, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.028);

        osc.connect(gain);
        gain.connect(scrollAudioCtx.destination);
        osc.start(t);
        osc.stop(t + 0.03);

        const subOsc = scrollAudioCtx.createOscillator();
        const subGain = scrollAudioCtx.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(240, t);
        subGain.gain.setValueAtTime(0.02, t);
        subGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.032);
        subOsc.connect(subGain);
        subGain.connect(scrollAudioCtx.destination);
        subOsc.start(t);
        subOsc.stop(t + 0.032);
      } catch (e) {}
    }

    window.playCursorHoverSound = playCursorHoverSound;
    window.playCursorClickSound = playCursorClickSound;
"""

target_after_holo = "        osc.stop(now + idx * 0.055 + 0.42);\n        });\n      } catch (e) {}\n    }"
assert target_after_holo in content, "target_after_holo not found!"
content = content.replace(target_after_holo, target_after_holo + "\n" + cursor_audio_defs)

# 2. Update hover detection and mousedown in cursor listeners
old_hover_block = """    // Hover detection on interactive elements
    document.addEventListener('mouseover', (e) => {
      const target = e.target.closest('a, button, input, textarea, select, [role="button"], .badge-card, .project-card, .scroll-indicator, .tilt-card');
      if (target) {
        document.body.classList.add('cursor-hover');
      } else {
        document.body.classList.remove('cursor-hover');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.add('cursor-active');
    });"""

new_hover_block = """    // Interactive hover & placement detection with tactile audio feedback
    const INTERACTIVE_SELECTOR = 'a, button, input, textarea, select, [role="button"], .badge-card, .project-card, .scroll-indicator, .tilt-card, .spec-chip, .filter-btn, .pill-tag, .social-icon-btn, .nav-link, .hero-chip, .code-preview-frame, .badge-item, .work-card, .btn-pill, .status-pill';

    document.addEventListener('mouseover', (e) => {
      const target = e.target.closest(INTERACTIVE_SELECTOR);
      if (target) {
        document.body.classList.add('cursor-hover');
        playCursorHoverSound(target);
      } else {
        document.body.classList.remove('cursor-hover');
      }
    });

    document.addEventListener('mousedown', (e) => {
      document.body.classList.add('cursor-active');
      playCursorClickSound(e.target);
    });"""

assert old_hover_block in content, "old_hover_block not found!"
content = content.replace(old_hover_block, new_hover_block)

# 3. Add delicate particle grain spark when cursor moves over 3D bust before full reveal
old_pointermove = """        targetCursorWorld.set(worldX, worldY);
      }
    });"""

new_pointermove = """        targetCursorWorld.set(worldX, worldY);

        // Micro-spark sound when placing cursor over 3D particle face
        if (Math.random() < 0.04) {
          playParticleGrain(750 + Math.random() * 500);
        }
      }
    });"""

assert old_pointermove in content, "old_pointermove not found!"
content = content.replace(old_pointermove, new_pointermove)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PERSONAL_HTML} with cursor placement audio")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PORTFOLIO_HTML} with cursor placement audio")
