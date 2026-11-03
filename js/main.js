/**
 * Main Application Logic & Interactivity
 * Mukesh Kumar Portfolio — AWS Student Portfolio Hackathon
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global Audio Mute State (default: false / subtle audio enabled)
  window.portfolioAudioMuted = false;

  // Initialize Modules
  initTypewriter();
  initNavbar();
  initProjectsFilter();
  initResumeModal();
  initBadgeModal();
  initContactForm();
  initSoundToggle();
  initCardTilt();
});

/* ==========================================================================
   1. DYNAMIC TYPEWRITER EFFECT
   ========================================================================== */
function initTypewriter() {
  const targetEl = document.getElementById('typewriter-text');
  if (!targetEl) return;

  const roles = [
    'Computer Science Student',
    'Cloud Computing Enthusiast (AWS & GCP)',
    'Generative AI & LLM Builder',
    'Full-Stack Web Developer',
    'Problem Solver & Systems Thinker'
  ];

  let roleIdx = 0;
  let charIdx = 0;
  let isDeleting = false;
  let typingSpeed = 90;

  function type() {
    const currentRole = roles[roleIdx];

    if (isDeleting) {
      targetEl.textContent = currentRole.substring(0, charIdx - 1);
      charIdx--;
      typingSpeed = 40;
    } else {
      targetEl.textContent = currentRole.substring(0, charIdx + 1);
      charIdx++;
      typingSpeed = 90;
    }

    if (!isDeleting && charIdx === currentRole.length) {
      // Pause at end of text
      typingSpeed = 1800;
      isDeleting = true;
    } else if (isDeleting && charIdx === 0) {
      isDeleting = false;
      roleIdx = (roleIdx + 1) % roles.length;
      typingSpeed = 450;
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

  // Scroll header styling
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    // Scrollspy
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

  // Mobile menu toggle
  if (mobileMenuBtn && navLinksContainer) {
    mobileMenuBtn.addEventListener('click', () => {
      navLinksContainer.classList.toggle('open');
      const icon = mobileMenuBtn.querySelector('svg');
      if (icon) {
        icon.classList.toggle('open');
      }
    });

    // Close on link click
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
          card.style.display = 'flex';
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
  const modalBadgeDesc = document.getElementById('modal-badge-desc');
  const modalBadgeSkills = document.getElementById('modal-badge-skills');

  if (!badgeModal) return;

  const badgeDetailsMap = {
    'compute': {
      title: 'The Basics of Google Cloud Compute',
      desc: 'Demonstrates proficiency in Google Cloud Compute Engine, including virtual machine (VM) creation, persistent disk configuration, network firewall rules, and startup script automation.',
      img: 'assets/badges/compute.svg',
      skills: ['Compute Engine', 'Virtual Machines', 'Cloud VPC', 'Firewall Rules', 'Startup Scripts']
    },
    'iam': {
      title: 'Configure Service Accounts and IAM Roles for Google Cloud',
      desc: 'Validates mastery over cloud security policies, IAM user and service account provisioning, granular custom role definitions, and principle of least privilege auditing.',
      img: 'assets/badges/iam.svg',
      skills: ['Cloud IAM', 'Service Accounts', 'Least Privilege Security', 'IAM Roles & Bindings', 'Audit Logs']
    },
    'data': {
      title: 'Store, Process, and Manage Data on Google Cloud – Console',
      desc: 'Covers practical implementation of structured and unstructured data storage, Google Cloud Storage bucket lifecycles, and BigQuery data exploration via the GCP Console.',
      img: 'assets/badges/data.svg',
      skills: ['Cloud Storage (GCS)', 'BigQuery', 'Cloud SQL', 'Console Management', 'Data Pipelines']
    },
    'ai-studio': {
      title: 'Develop AI-Powered Prototypes in Google AI Studio',
      desc: 'Validates practical skills in rapid prototyping of Generative AI applications using Google AI Studio, multi-turn system prompts, few-shot tuning, and Gemini API integration.',
      img: 'assets/badges/ai-studio.svg',
      skills: ['Google AI Studio', 'Prompt Engineering', 'Gemini 1.5 Pro', 'Few-Shot Learning', 'Python AI SDK']
    },
    'gemini': {
      title: 'Create Your First Gemini Enterprise Application',
      desc: 'Focuses on building production-ready enterprise applications powered by the Gemini multimodal foundation model, API authentication, and robust end-to-end cloud deployment.',
      img: 'assets/badges/gemini.svg',
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
        if (modalBadgeDesc) modalBadgeDesc.textContent = data.desc;
        if (modalBadgeSkills) {
          modalBadgeSkills.innerHTML = data.skills
            .map(s => `<span class="badge-skill-tag" style="background:rgba(66,133,244,0.15); color:#60A5FA; border:1px solid rgba(66,133,244,0.3);">${s}</span>`)
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

      // Simulate instantaneous success + mailto link trigger
      const mailtoUrl = `mailto:mukesh.kumar.dev@example.com?subject=${encodeURIComponent(subject || 'Portfolio Inquiry from ' + name)}&body=${encodeURIComponent('From: ' + name + ' (' + email + ')\n\n' + message)}`;

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
      const email = 'mukesh.kumar.dev@example.com';
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
   9. CARD 3D TILT EFFECT (Subtle Micro-Interaction)
   ========================================================================== */
function initCardTilt() {
  const cards = document.querySelectorAll('.tilt-card');
  if (window.innerWidth < 768) return; // Skip on mobile for battery / performance

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
