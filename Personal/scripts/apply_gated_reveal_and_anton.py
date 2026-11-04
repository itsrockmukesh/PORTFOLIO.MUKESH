import os
import re

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Ensure Anton @font-face supports weights 100 to 900
old_font_face = """    @font-face {
      font-family: 'Anton';
      src: url('./anton.woff2') format('woff2');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }"""

new_font_face = """    @font-face {
      font-family: 'Anton';
      src: url('./anton.woff2') format('woff2');
      font-weight: 100 900;
      font-style: normal;
      font-display: swap;
    }

    /* Body lock during hero photo reveal */
    body.hero-locked {
      overflow-y: hidden !important;
    }"""

if old_font_face in content:
    content = content.replace(old_font_face, new_font_face)
else:
    # If font-weight was already changed, add body.hero-locked if not present
    if "body.hero-locked" not in content:
        content = content.replace("@font-face {", "/* Body lock during hero photo reveal */\n    body.hero-locked {\n      overflow-y: hidden !important;\n    }\n\n    @font-face {")

# 2. Update .hero-scroll-track CSS to 100vh clean stage
old_track_css = """    .hero-scroll-track {
      position: relative;
      width: 100%;
      height: 240vh;
      background: #060408;
      z-index: 3;
    }

    .hero-sticky-stage {
      position: sticky;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      z-index: 3;
    }"""

new_track_css = """    .hero-scroll-track {
      position: relative;
      width: 100%;
      height: 100vh;
      background: #060408;
      z-index: 3;
    }

    .hero-sticky-stage {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      z-index: 3;
    }"""

if old_track_css in content:
    content = content.replace(old_track_css, new_track_css)

# 3. Ensure drawBannerText uses '900 340px Anton, sans-serif' and '[DEVELOPER]'
old_banner_draw = """    function drawBannerText(isCrimson = 0.0) {
      bCtx.clearRect(0, 0, bannerCanvas.width, bannerCanvas.height);
      bCtx.font = '900 340px sans-serif';
      bCtx.textAlign = 'center';
      bCtx.textBaseline = 'middle';
      bCtx.letterSpacing = '-0.02em';"""

new_banner_draw = """    function drawBannerText(isCrimson = 0.0) {
      bCtx.clearRect(0, 0, bannerCanvas.width, bannerCanvas.height);
      bCtx.font = '900 340px Anton, sans-serif';
      bCtx.textAlign = 'center';
      bCtx.textBaseline = 'middle';
      bCtx.letterSpacing = '-0.02em';"""

if old_banner_draw in content:
    content = content.replace(old_banner_draw, new_banner_draw)
elif "bCtx.font = '900 340px Anton, sans-serif';" not in content:
    content = re.sub(r"bCtx\.font\s*=\s*'[^']+';", "bCtx.font = '900 340px Anton, sans-serif';", content, count=1)

# Ensure font reload when Anton is ready
font_ready_hook = """    drawBannerText(0.0);
    if (document.fonts) {
      document.fonts.load('340px Anton').then(() => {
        drawBannerText(0.0);
        if (bannerTexture) bannerTexture.needsUpdate = true;
      });
      document.fonts.ready.then(() => {
        drawBannerText(0.0);
        if (bannerTexture) bannerTexture.needsUpdate = true;
      });
    }"""

if "document.fonts.load('340px Anton')" not in content:
    content = content.replace("drawBannerText(0.0);", font_ready_hook, 1)

# 4. Replace the old updateHeroScrollState & wheel listener with the Bulletproof Virtual Gating Engine
old_scroll_logic = """    // --- Pinned Scroll Gating: First photo scrolls fully, then full website scrolls ---
    // --- Navbar is HIDDEN during photo scrolling, and becomes visible AFTER reveal ---
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      
      const revealDistance = vh * 1.0;

      if (scrollY <= 0) {
        targetRevealProgress = 0.0;
      } else if (scrollY < revealDistance) {
        targetRevealProgress = scrollY / revealDistance;
      } else {
        targetRevealProgress = 1.0;
      }
      handleScrollSound();

      // Dynamic Navbar Visibility:
      // When scrollY < revealDistance * 0.95: navbar is HIDDEN
      // When scrollY >= revealDistance * 0.95: navbar is VISIBLE
      if (navbarEl) {
        if (scrollY < revealDistance * 0.92) {
          navbarEl.classList.add('navbar-hidden');
        } else {
          navbarEl.classList.remove('navbar-hidden');
        }
      }

      // Scroll indicator updates or hides once user scrolls into the website sections
      if (uiContainer) {
        const trackHeight = heroStageEl ? heroStageEl.offsetHeight : (vh * 2.4);
        if (scrollY > trackHeight - vh * 0.3) {
          uiContainer.style.opacity = '0';
          uiContainer.style.pointerEvents = 'none';
        } else {
          uiContainer.style.opacity = '1';
          uiContainer.style.pointerEvents = 'auto';
        }
      }
    }

    window.addEventListener('scroll', updateHeroScrollState, { passive: true });

    window.addEventListener('wheel', (e) => {
      handleScrollSound(e.deltaY);
    }, { passive: true });

    window.addEventListener('resize', updateHeroScrollState, { passive: true });

    // Initial check on load: ensure navbar is hidden at top
    updateHeroScrollState();

    // Scroll Indicator Click Action
    if (scrollIndicator) {
      scrollIndicator.addEventListener('click', () => {
        if (!isLoaded) return;
        const vh = window.innerHeight;
        if (window.scrollY < vh * 0.8) {
          window.scrollTo({ top: vh * 1.0, behavior: 'smooth' });
        } else {
          const introSec = document.getElementById('intro') || document.getElementById('projects');
          if (introSec) {
            introSec.scrollIntoView({ behavior: 'smooth' });
          } else {
            window.scrollTo({ top: vh * 2.4, behavior: 'smooth' });
          }
        }
      });
    }"""

new_scroll_logic = """    // ==========================================================================
    // BULLETPROOF GATED PHOTO REVEAL ENGINE
    // The next page CANNOT scroll until the full photo is 100% revealed & visible!
    // ==========================================================================
    let isHeroLocked = true;
    document.body.classList.add('hero-locked');

    function checkHeroLockState() {
      // Unlock only when photo is fully revealed
      if (targetRevealProgress >= 0.98 && revealProgress >= 0.96) {
        if (isHeroLocked) {
          isHeroLocked = false;
          document.body.classList.remove('hero-locked');
          if (navbarEl) navbarEl.classList.remove('navbar-hidden');
        }
      } else {
        // Re-lock at the top if photo is being returned to dots
        if (window.scrollY <= 5 && !isHeroLocked) {
          isHeroLocked = true;
          document.body.classList.add('hero-locked');
          if (navbarEl) navbarEl.classList.add('navbar-hidden');
        }
      }
    }

    // Intercept Wheel Gestures for Strict Hero Reveal Gating
    window.addEventListener('wheel', (e) => {
      const scrollY = window.scrollY;

      // 1. If at the top and photo is not fully revealed:
      if (scrollY <= 5 && targetRevealProgress < 0.999) {
        if (e.deltaY > 0) {
          // Scrolling down advances photo reveal
          e.preventDefault();
          const speed = 0.0022; // Smooth ~450px scroll travel to 100%
          targetRevealProgress = Math.min(1.0, targetRevealProgress + Math.abs(e.deltaY) * speed);
          handleScrollSound(e.deltaY);
          if (targetRevealProgress >= 1.0) checkHeroLockState();
          return;
        } else if (e.deltaY < 0 && targetRevealProgress > 0.0) {
          // Scrolling up reduces photo reveal back to dots
          e.preventDefault();
          const speed = 0.0022;
          targetRevealProgress = Math.max(0.0, targetRevealProgress - Math.abs(e.deltaY) * speed);
          handleScrollSound(e.deltaY);
          checkHeroLockState();
          return;
        }
      }

      // 2. If at top and photo is fully revealed:
      if (scrollY <= 5 && targetRevealProgress >= 0.98) {
        if (e.deltaY < 0 && scrollY <= 0) {
          // Scrolling up while at top reverses photo back to dots
          e.preventDefault();
          const speed = 0.0022;
          targetRevealProgress = Math.max(0.0, targetRevealProgress - Math.abs(e.deltaY) * speed);
          handleScrollSound(e.deltaY);
          checkHeroLockState();
          return;
        }
        // Scrolling down naturally scrolls the page into the website
        handleScrollSound(e.deltaY);
      } else {
        handleScrollSound(e.deltaY);
      }
    }, { passive: false });

    // Touch Event Handling for Mobile / Trackpad Swiping
    let touchStartY = 0;
    window.addEventListener('touchstart', (e) => {
      touchStartY = e.touches[0].clientY;
      if (!scrollAudioCtx) initScrollAudio();
      if (scrollAudioCtx && scrollAudioCtx.state === 'suspended') scrollAudioCtx.resume();
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      const scrollY = window.scrollY;
      const currentY = e.touches[0].clientY;
      const deltaY = touchStartY - currentY; // positive = swipe up = scroll down

      if (scrollY <= 5 && (targetRevealProgress < 0.999 || (deltaY < 0 && targetRevealProgress > 0.0))) {
        e.preventDefault();
        const speed = 0.0035;
        targetRevealProgress = Math.min(1.0, Math.max(0.0, targetRevealProgress + deltaY * speed));
        touchStartY = currentY;
        handleScrollSound(deltaY);
        if (targetRevealProgress >= 1.0) checkHeroLockState();
      } else {
        touchStartY = currentY;
        handleScrollSound(deltaY);
      }
    }, { passive: false });

    // Keyboard Navigation (ArrowDown, ArrowUp, Space, PageDown, PageUp)
    window.addEventListener('keydown', (e) => {
      const scrollY = window.scrollY;
      if (scrollY <= 5 && targetRevealProgress < 0.999) {
        if (e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown') {
          e.preventDefault();
          targetRevealProgress = Math.min(1.0, targetRevealProgress + 0.18);
          handleScrollSound(100);
          if (targetRevealProgress >= 1.0) checkHeroLockState();
        }
      }
      if (scrollY <= 5 && targetRevealProgress > 0.001) {
        if (e.key === 'ArrowUp' || e.key === 'PageUp') {
          e.preventDefault();
          targetRevealProgress = Math.max(0.0, targetRevealProgress - 0.18);
          handleScrollSound(-100);
          checkHeroLockState();
        }
      }
    });

    // Native Page Scroll Listener for Website Sections
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;

      if (scrollY <= 2) {
        if (targetRevealProgress >= 0.98 && revealProgress >= 0.96) {
          if (navbarEl) navbarEl.classList.remove('navbar-hidden');
        } else {
          if (navbarEl) navbarEl.classList.add('navbar-hidden');
        }
      } else {
        if (navbarEl) navbarEl.classList.remove('navbar-hidden');
      }

      if (uiContainer) {
        if (scrollY > window.innerHeight * 0.3) {
          uiContainer.style.opacity = '0';
          uiContainer.style.pointerEvents = 'none';
        } else {
          uiContainer.style.opacity = '1';
          uiContainer.style.pointerEvents = 'auto';
        }
      }
    }

    window.addEventListener('scroll', updateHeroScrollState, { passive: true });
    window.addEventListener('resize', updateHeroScrollState, { passive: true });

    // Initial check on load: ensure hero is locked and navbar is hidden
    checkHeroLockState();
    updateHeroScrollState();

    // Scroll Indicator Click Action
    if (scrollIndicator) {
      scrollIndicator.addEventListener('click', () => {
        if (!isLoaded) return;
        if (targetRevealProgress < 0.98) {
          targetRevealProgress = 1.0;
        } else {
          isHeroLocked = false;
          document.body.classList.remove('hero-locked');
          const introSec = document.getElementById('intro');
          if (introSec) introSec.scrollIntoView({ behavior: 'smooth' });
        }
      });
    }

    // Nav Links Unlock Page Immediately if Clicked
    document.querySelectorAll('.nav-link, .btn-pill, .trigger-resume-modal').forEach(link => {
      link.addEventListener('click', () => {
        targetRevealProgress = 1.0;
        revealProgress = 1.0;
        isHeroLocked = false;
        document.body.classList.remove('hero-locked');
        if (navbarEl) navbarEl.classList.remove('navbar-hidden');
      });
    });"""

assert old_scroll_logic in content, "old_scroll_logic not found!"
content = content.replace(old_scroll_logic, new_scroll_logic)

# In animate(), checkHeroLockState as revealProgress lerps
old_lerp_block = """      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      const prevReveal = revealProgress;
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;
      if (Math.abs(targetRevealProgress - revealProgress) < 0.0005) {
        revealProgress = targetRevealProgress;
      }
      const revealDelta = Math.abs(revealProgress - prevReveal);"""

new_lerp_block = """      // 3. Smooth Lerp on Reveal Progress Driven by Scroll
      const prevReveal = revealProgress;
      revealProgress += (targetRevealProgress - revealProgress) * 0.095;
      if (Math.abs(targetRevealProgress - revealProgress) < 0.0005) {
        revealProgress = targetRevealProgress;
      }
      const revealDelta = Math.abs(revealProgress - prevReveal);

      // Continuously evaluate hero lock state as revealProgress lerps
      checkHeroLockState();"""

assert old_lerp_block in content, "old_lerp_block not found!"
content = content.replace(old_lerp_block, new_lerp_block)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PERSONAL_HTML} with Anton font & strict gated reveal!")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PORTFOLIO_HTML} with Anton font & strict gated reveal!")
