/**
 * Main Application Logic & Interactivity
 * Mukesh Kumar Portfolio — AWS Student Portfolio Hackathon
 * 1st Year BE-CSE @ Mirai School of Technology
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global Audio Mute State (default: false / subtle audio enabled)
  window.portfolioAudioMuted = false;

  // Initialize Modules
  initTypewriter();
  initNavbar();
  initProjectsFilter();
  initArchTabs();
  initResumeModal();
  initBadgeModal();
  initContactForm();
  initSoundToggle();
  initCardTilt();
  initGameStartGate();
  initCyberHackMiniGame();
});

/* ==========================================================================
   1. DYNAMIC TYPEWRITER EFFECT
   ========================================================================== */
function initTypewriter() {
  const targetEl = document.getElementById('typewriter-text');
  if (!targetEl) return;

  const roles = [
    'Learning Web Development with HTML & CSS',
    'Solving Data Structures & Algorithms in C++',
    '1st Year BE-CSE @ Mirai School of Technology',
    'Building for the AWS Student Portfolio Hackathon',
    'Holder of 5 Google Cloud Skill Badges'
  ];

  let roleIdx = 0;
  let charIdx = 0;
  let isDeleting = false;
  let typingSpeed = 85;

  function type() {
    const currentRole = roles[roleIdx];

    if (isDeleting) {
      targetEl.textContent = currentRole.substring(0, charIdx - 1);
      charIdx--;
      typingSpeed = 35;
    } else {
      targetEl.textContent = currentRole.substring(0, charIdx + 1);
      charIdx++;
      typingSpeed = 85;
    }

    if (!isDeleting && charIdx === currentRole.length) {
      typingSpeed = 1900;
      isDeleting = true;
    } else if (isDeleting && charIdx === 0) {
      isDeleting = false;
      roleIdx = (roleIdx + 1) % roles.length;
      typingSpeed = 400;
    }

    setTimeout(type, typingSpeed);
  }

  type();
}

/* ==========================================================================
   2. NAVBAR & SCROLLSPY
   ========================================================================== */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const navLinks = document.querySelectorAll('.nav-link');
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navLinksContainer = document.querySelector('.nav-links');
  const sections = document.querySelectorAll('section[id]');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    const scrollPos = window.scrollY + 120;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');

      if (scrollPos >= top && scrollPos < top + height) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  });

  if (mobileMenuBtn && navLinksContainer) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinksContainer.classList.toggle('open');
    });

    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navLinksContainer.classList.remove('open');
      });
    });
  }
}

/* ==========================================================================
   3. SOUND TOGGLE & SYNTHESIZER
   ========================================================================== */
function initSoundToggle() {
  const soundBtn = document.getElementById('sound-toggle-btn');
  if (!soundBtn) return;

  soundBtn.addEventListener('click', () => {
    window.portfolioAudioMuted = !window.portfolioAudioMuted;
    soundBtn.classList.toggle('muted', window.portfolioAudioMuted);

    if (window.portfolioAudioMuted) {
      soundBtn.setAttribute('title', 'Sound Muted (Click to enable)');
      showToast('🔇 Cyber audio muted');
    } else {
      soundBtn.setAttribute('title', 'Sound Enabled (Click to mute)');
      showToast('🔊 Cyber audio enabled');
      playHapticTone(660);
    }
  });
}

function playHapticTone(freq = 520) {
  if (window.portfolioAudioMuted) return;
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.08);
  } catch (e) {}
}

/* ==========================================================================
   4. PROJECTS FILTERING
   ========================================================================== */
function initProjectsFilter() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      playHapticTone(700);

      const filter = btn.getAttribute('data-filter');

      projectCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filter === 'all' || category === filter || category.includes(filter)) {
          card.style.display = '';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(15px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 250);
        }
      });
    });
  });
}

/* ==========================================================================
   4B. AWS ARCHITECTURE TABS SWITCHER
   ========================================================================== */
function initArchTabs() {
  const tabBtns = document.querySelectorAll('.aws-tab-btn');
  const tabPanes = document.querySelectorAll('.aws-tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add('active');
      }
      playHapticTone(650);
    });
  });
}

/* ==========================================================================
   5. RESUME MODAL & PRINT/DOWNLOAD
   ========================================================================== */
function initResumeModal() {
  const openBtns = document.querySelectorAll('.trigger-resume-modal');
  const modal = document.getElementById('resume-modal');
  const closeBtn = document.getElementById('resume-modal-close');
  const printBtn = document.getElementById('resume-print-btn');

  if (!modal) return;

  openBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
      playHapticTone(800);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('active');
    }
  });

  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

/* ==========================================================================
   6. GOOGLE CLOUD BADGE VERIFICATION MODAL
   ========================================================================== */
function initBadgeModal() {
  const badgeVerifyBtns = document.querySelectorAll('.badge-verify-btn');
  const badgeModal = document.getElementById('badge-modal');
  const closeBtn = document.getElementById('badge-modal-close');
  const modalBadgeImg = document.getElementById('modal-badge-img');
  const modalBadgeTitle = document.getElementById('modal-badge-title');
  const modalBadgeMeta = document.getElementById('modal-badge-meta');
  const modalBadgeDesc = document.getElementById('modal-badge-desc');
  const modalBadgeSkills = document.getElementById('modal-badge-skills');

  if (!badgeModal) return;

  const badgeDetailsMap = {
    'compute': {
      title: 'The Basics of Google Cloud Compute',
      meta: 'Track: Infrastructure Modernization • Earned: Oct 23, 2026 • Recipient: Mukesh Kumar',
      desc: 'Demonstrates proficiency in Google Cloud Compute Engine, including virtual machine (VM) creation, persistent disk configuration, custom network firewall rules, and startup script automation.',
      img: 'assets/badges/compute-cert.png',
      skills: ['Compute Engine', 'Virtual Machines', 'Cloud VPC', 'Firewall Rules', 'Startup Scripts']
    },
    'iam': {
      title: 'Configure Service Accounts and IAM Roles for Google Cloud',
      meta: 'Track: Security • Earned: Oct 23, 2026 • Recipient: Mukesh Kumar',
      desc: 'Validates mastery over cloud security policies, IAM user and service account provisioning, granular custom role definitions, and principle of least privilege auditing.',
      img: 'assets/badges/iam-cert.png',
      skills: ['Cloud IAM', 'Service Accounts', 'Least Privilege Security', 'IAM Roles & Bindings', 'Audit Logs']
    },
    'data': {
      title: 'Store, Process, and Manage Data on Google Cloud – Console',
      meta: 'Track: Data Management • Earned: Oct 24, 2026 • Recipient: Mukesh Kumar',
      desc: 'Covers practical implementation of structured and unstructured data storage, Google Cloud Storage bucket lifecycles, and BigQuery data exploration via the GCP Console.',
      img: 'assets/badges/data-cert.png',
      skills: ['Cloud Storage (GCS)', 'BigQuery SQL', 'Cloud SQL', 'Console Management', 'Data Pipelines']
    },
    'ai-studio': {
      title: 'Develop AI-Powered Prototypes in Google AI Studio',
      meta: 'Track: Artificial Intelligence • Earned: Oct 21, 2026 • Recipient: Mukesh Kumar',
      desc: 'Validates practical skills in rapid prototyping of Generative AI applications using Google AI Studio, multi-turn system prompts, few-shot tuning, and Gemini API integration.',
      img: 'assets/badges/ai-studio-cert.png',
      skills: ['Google AI Studio', 'Prompt Engineering', 'Gemini 1.5 Pro', 'Few-Shot Learning', 'Python AI SDK']
    },
    'gemini': {
      title: 'Create Your First Gemini Enterprise Application',
      meta: 'Track: Artificial Intelligence • Earned: Oct 21, 2026 • Recipient: Mukesh Kumar',
      desc: 'Focuses on building production-ready applications powered by the Gemini multimodal foundation model, API authentication, and robust end-to-end cloud deployment.',
      img: 'assets/badges/gemini-cert.png',
      skills: ['Gemini Multimodal API', 'Enterprise GenAI', 'Cloud App Deployment', 'REST Endpoints', 'Response Streaming']
    }
  };

  badgeVerifyBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const badgeKey = btn.getAttribute('data-badge');
      const data = badgeDetailsMap[badgeKey];

      if (data) {
        if (modalBadgeImg) modalBadgeImg.src = data.img;
        if (modalBadgeTitle) modalBadgeTitle.textContent = data.title;
        if (modalBadgeMeta) modalBadgeMeta.textContent = data.meta;
        if (modalBadgeDesc) modalBadgeDesc.textContent = data.desc;
        if (modalBadgeSkills) {
          modalBadgeSkills.innerHTML = data.skills
            .map(s => `<span class="badge-skill-tag" style="background:rgba(66,133,244,0.15); color:#60A5FA; border:1px solid rgba(66,133,244,0.3); padding:0.25rem 0.65rem; border-radius:9999px; font-size:0.75rem; font-family:var(--font-mono);">${s}</span>`)
            .join('');
        }
        badgeModal.classList.add('active');
        playHapticTone(780);
      }
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      badgeModal.classList.remove('active');
    });
  }

  badgeModal.addEventListener('click', (e) => {
    if (e.target === badgeModal) {
      badgeModal.classList.remove('active');
    }
  });
}

/* ==========================================================================
   7. CONTACT FORM HANDLER & COPY EMAIL
   ========================================================================== */
function initContactForm() {
  const contactForm = document.getElementById('contact-form');
  const feedbackEl = document.getElementById('form-feedback');
  const copyBtns = document.querySelectorAll('.copy-email-btn');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('contact-name').value.trim();
      const email = document.getElementById('contact-email').value.trim();
      const subject = document.getElementById('contact-subject').value.trim();
      const message = document.getElementById('contact-message').value.trim();

      if (!name || !email || !message) {
        if (feedbackEl) {
          feedbackEl.className = 'form-feedback error';
          feedbackEl.textContent = 'Please fill out all required fields.';
        }
        return;
      }

      const mailtoUrl = `mailto:techmukesh3124@gmail.com?subject=${encodeURIComponent(subject || 'Portfolio Inquiry from ' + name)}&body=${encodeURIComponent('From: ' + name + ' (' + email + ')\n\n' + message)}`;

      if (feedbackEl) {
        feedbackEl.className = 'form-feedback success';
        feedbackEl.innerHTML = `✓ Thank you <strong>${escapeHtml(name)}</strong>! Opening your email client to send message...`;
      }

      playHapticTone(880);
      showToast('🚀 Opening email client to deliver your message!');

      setTimeout(() => {
        window.location.href = mailtoUrl;
      }, 700);

      contactForm.reset();
    });
  }

  // Copy Email Button
  copyBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const email = 'techmukesh3124@gmail.com';
      navigator.clipboard.writeText(email).then(() => {
        showToast('📋 Email copied to clipboard: ' + email);
        playHapticTone(900);
      });
    });
  });
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, function(m) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
  });
}

/* ==========================================================================
   8. TOAST NOTIFICATION UTILITY
   ========================================================================== */
let toastTimeout;
function showToast(message) {
  let toast = document.getElementById('toast-notification');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.className = 'toast-notification';
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.classList.add('active');

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove('active');
  }, 3200);
}

/* ==========================================================================
   9. CARD 3D TILT EFFECT
   ========================================================================== */
function initCardTilt() {
  const cards = document.querySelectorAll('.tilt-card');
  if (window.innerWidth < 768) return;

  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -5;
      const rotateY = ((x - centerX) / centerX) * 5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
    });
  });
}

/* ==========================================================================
   10. GAMING PORTFOLIO EXPERIENCE — THE OPENING GATE
   ========================================================================== */
function initGameStartGate() {
  const gate = document.getElementById('game-start-gate');
  const startBtn = document.getElementById('press-start-btn');
  const skipBtn = document.getElementById('quick-enter-btn');
  if (!gate) return;

  function openGate() {
    if (typeof window.enterGameRealm === 'function') {
      window.enterGameRealm();
    } else {
      gate.classList.add('opened');
      gate.style.display = 'none';
    }
  }

  if (startBtn) startBtn.addEventListener('click', openGate);
  if (skipBtn) skipBtn.addEventListener('click', openGate);

  // Auto-open on scroll
  let scrolled = false;
  window.addEventListener('scroll', () => {
    if (!scrolled && window.scrollY > 30) {
      scrolled = true;
      openGate();
    }
  }, { passive: true });
}

/* ==========================================================================
   11. CYBER HACK MINI-GAME & SECRET TOOL (CREATIVE FEATURE)
   ========================================================================== */
function initCyberHackMiniGame() {
  const modal = document.getElementById('cyber-hack-modal');
  const closeBtn = document.getElementById('hack-close-btn');
  const core1 = document.getElementById('core-1');
  const core2 = document.getElementById('core-2');
  const core3 = document.getElementById('core-3');
  const cores = [core1, core2, core3];
  const progressFill = document.getElementById('hack-progress-fill');
  const progressPct = document.getElementById('hack-progress-pct');
  const equipToolBtn = document.getElementById('equip-secret-tool-btn');
  const stream = document.getElementById('hack-terminal-stream');

  // Trigger buttons across navbar, hero, callouts, and footer
  const triggers = [
    document.getElementById('nav-hack-trigger'),
    document.getElementById('hero-hack-trigger'),
    document.getElementById('callout-hack-trigger'),
    document.getElementById('cyber-hack-hint-trigger'),
    document.getElementById('skills-hack-trigger'),
    document.getElementById('footer-hack-trigger')
  ].filter(Boolean);

  if (!modal) return;

  let activatedCores = new Set();
  let isBreached = false;

  function openModal() {
    isBreached = false;
    activatedCores.clear();
    resetCores();
    modal.classList.add('active');
    playHapticTone(440);
    logStream('> [FIREWALL]: Security checkpoint active. Breach cores or equip Secret Tool.');
  }

  function closeModal() {
    modal.classList.remove('active');
  }

  function resetCores() {
    cores.forEach(c => {
      if (c) {
        c.classList.remove('activated');
        const st = c.querySelector('.core-status');
        if (st) st.textContent = 'LOCKED';
      }
    });
    if (progressFill) progressFill.style.width = '0%';
    if (progressPct) progressPct.textContent = '100% LOCKED 🔒';
  }

  function logStream(msg) {
    if (!stream) return;
    const line = document.createElement('span');
    line.className = 'stream-line';
    line.textContent = msg;
    stream.appendChild(line);
    stream.scrollTop = stream.scrollHeight;
  }

  triggers.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Handle Core clicks
  cores.forEach((coreBtn, idx) => {
    if (!coreBtn) return;
    coreBtn.addEventListener('click', () => {
      if (isBreached) return;
      const coreNum = idx + 1;
      if (activatedCores.has(coreNum)) return;

      activatedCores.add(coreNum);
      coreBtn.classList.add('activated');
      const st = coreBtn.querySelector('.core-status');
      if (st) st.textContent = 'OVERLOADED';

      playHapticTone(520 + coreNum * 120);

      const count = activatedCores.size;
      const pct = Math.round((count / 3) * 100);
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (progressPct) progressPct.textContent = `${100 - pct}% INTEGRITY`;

      logStream(`> [CORE ${coreNum}]: Overloaded successfully! (${count}/3 Cores offline)`);

      if (count === 3) {
        triggerBreachSuccess('CORES OVERLOADED!');
      }
    });
  });

  // Handle Secret Bypass Tool
  if (equipToolBtn) {
    equipToolBtn.addEventListener('click', () => {
      if (isBreached) return;
      playHapticTone(880);
      setTimeout(() => playHapticTone(1050), 120);
      logStream('> [SECRET TOOL]: EMP Cyber Key equipped! Security protocols bypassed!');
      
      cores.forEach(c => {
        if (c) {
          c.classList.add('activated');
          const st = c.querySelector('.core-status');
          if (st) st.textContent = 'BYPASSED';
        }
      });
      if (progressFill) progressFill.style.width = '100%';
      if (progressPct) progressPct.textContent = '0% INTEGRITY (BREACHED)';

      triggerBreachSuccess('SECRET TOOL OVERRIDE!');
    });
  }

  function triggerBreachSuccess(method) {
    isBreached = true;
    logStream(`> [ALERT]: FIREWALL CRACKED VIA ${method}! ACCESS GRANTED!`);
    if (progressPct) progressPct.textContent = 'ACCESS GRANTED! 🔓';

    // Victory sound fanfare
    playHapticTone(520);
    setTimeout(() => playHapticTone(650), 120);
    setTimeout(() => playHapticTone(780), 240);
    setTimeout(() => playHapticTone(1040), 380);

    showToast('🔥 ACCESS GRANTED: Root Terminal Unlocked!');

    setTimeout(() => {
      closeModal();
      if (typeof window.openSecretTerminal === 'function') {
        window.openSecretTerminal('help');
      }
    }, 850);
  }
}

