import os

PERSONAL_HTML = "/Users/mukeshkumar/PORTFOLIO/Personal/index.html"
PORTFOLIO_HTML = "/Users/mukeshkumar/PORTFOLIO/index.html"

with open(PERSONAL_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update checkHeroLockState to keep navbar hidden on hero even when 100% revealed
old_lock_fn = """    function checkHeroLockState() {
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
    }"""

new_lock_fn = """    function checkHeroLockState() {
      // Unlock page scrolling only when photo is fully revealed
      // NOTE: Navbar remains HIDDEN on photo; it only appears after photo ends and we arrive at next page
      if (targetRevealProgress >= 0.98 && revealProgress >= 0.96) {
        if (isHeroLocked) {
          isHeroLocked = false;
          document.body.classList.remove('hero-locked');
        }
      } else {
        // Re-lock at the top if photo is being returned to dots
        if (window.scrollY <= 5 && !isHeroLocked) {
          isHeroLocked = true;
          document.body.classList.add('hero-locked');
          if (navbarEl) navbarEl.classList.add('navbar-hidden');
        }
      }
    }"""

assert old_lock_fn in content, "old_lock_fn not found in content!"
content = content.replace(old_lock_fn, new_lock_fn)

# 2. Update updateHeroScrollState so navbar is ONLY visible when scrollY > 60 (arriving at next page)
old_scroll_fn = """    // Native Page Scroll Listener for Website Sections
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
    }"""

new_scroll_fn = """    // Native Page Scroll Listener for Website Sections
    function updateHeroScrollState() {
      if (!isLoaded) return;
      const scrollY = window.scrollY;

      // NAVBAR VISIBILITY RULE:
      // When photo is fully revealed at the top, navbar DOES NOT show.
      // After photo is ended and we arrive at another page (scrollY > 60), navbar shows!
      if (scrollY > 60) {
        if (navbarEl) navbarEl.classList.remove('navbar-hidden');
      } else {
        if (navbarEl) navbarEl.classList.add('navbar-hidden');
      }

      if (uiContainer) {
        if (scrollY > window.innerHeight * 0.25) {
          uiContainer.style.opacity = '0';
          uiContainer.style.pointerEvents = 'none';
        } else {
          uiContainer.style.opacity = '1';
          uiContainer.style.pointerEvents = 'auto';
        }
      }
    }"""

assert old_scroll_fn in content, "old_scroll_fn not found in content!"
content = content.replace(old_scroll_fn, new_scroll_fn)

# 3. Clean up nav links click handler
old_nav_links = """    // Nav Links Unlock Page Immediately if Clicked
    document.querySelectorAll('.nav-link, .btn-pill, .trigger-resume-modal').forEach(link => {
      link.addEventListener('click', () => {
        targetRevealProgress = 1.0;
        revealProgress = 1.0;
        isHeroLocked = false;
        document.body.classList.remove('hero-locked');
        if (navbarEl) navbarEl.classList.remove('navbar-hidden');
      });
    });"""

new_nav_links = """    // Nav Links Unlock Page Immediately if Clicked
    document.querySelectorAll('.nav-link, .btn-pill, .trigger-resume-modal').forEach(link => {
      link.addEventListener('click', () => {
        targetRevealProgress = 1.0;
        revealProgress = 1.0;
        isHeroLocked = false;
        document.body.classList.remove('hero-locked');
      });
    });"""

if old_nav_links in content:
    content = content.replace(old_nav_links, new_nav_links)

with open(PERSONAL_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PERSONAL_HTML} with delayed navbar reveal rule")

with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Updated {PORTFOLIO_HTML} with delayed navbar reveal rule")
