/* ======================================
   POLISIDE — Main JavaScript v10
   Clean · Warm · Textured · Ultra-Smooth
   800vh sticky scroll — slow storytelling
   ====================================== */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initScrollAnimations();
  initNavScrollEffect();
  
  if (document.querySelector('.hero-wrapper')) {
    initHeroParticles();
    initHeroStickyScroll();
  }
});

/* ===========================================
   Navigation
   =========================================== */
function initNavigation() {
  const hamburger = document.querySelector('.nav__hamburger');
  const navLinks = document.querySelector('.nav__links');
  const overlay = document.querySelector('.nav__overlay');
  
  if (!hamburger) return;
  
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
    if (overlay) overlay.classList.toggle('open');
    document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
  });
  
  if (overlay) {
    overlay.addEventListener('click', () => {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    });
  }
  
  document.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      if (overlay) overlay.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

function initNavScrollEffect() {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

/* ===========================================
   Scroll Animations (IntersectionObserver)
   =========================================== */
function initScrollAnimations() {
  const elements = document.querySelectorAll('.animate-on-scroll:not(.visible)');
  if (!elements.length) return;
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
  
  elements.forEach(el => observer.observe(el));
}

/* ===========================================
   Hero Particles — warm, soft dots
   =========================================== */
function initHeroParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  
  const count = 28;
  const colors = [
    'rgba(199,106,69,0.14)',
    'rgba(199,106,69,0.08)',
    'rgba(107,143,113,0.12)',
    'rgba(107,143,113,0.06)',
    'rgba(216,138,106,0.08)',
    'rgba(139,181,146,0.06)',
  ];
  
  for (let i = 0; i < count; i++) {
    const dot = document.createElement('div');
    const size = 3 + Math.random() * 7;
    dot.style.cssText = `
      width:${size}px;height:${size}px;
      background:${colors[Math.floor(Math.random() * colors.length)]};
      left:${Math.random() * 100}%;top:${Math.random() * 100}%;
      border-radius:50%;position:absolute;
    `;
    container.appendChild(dot);
  }
}

/* ===========================================
   HERO — Sticky Scroll Sequence
   =========================================== */
function initHeroStickyScroll() {
  const wrapper = document.querySelector('.hero-wrapper');
  const hero = document.querySelector('.hero');
  if (!wrapper || !hero) return;
  
  const blobWarm = document.querySelector('.hero__blob--warm');
  const blobSage = document.querySelector('.hero__blob--sage');
  const blobCream = document.querySelector('.hero__blob--cream');
  
  function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  
  let ticking = false;
  
  function update() {
    const rect = wrapper.getBoundingClientRect();
    const scrollRange = wrapper.offsetHeight - window.innerHeight;
    const progress = clamp(-rect.top / scrollRange, 0, 1);
    
    // 0: Title, 1: Phase 1 (Single), 2: Phase 2 (Companion), 3: Phase 3 (Connected), 4: Outro
    let phase = 0;
    if (progress > 0.12 && progress < 0.38) phase = 1;
    else if (progress >= 0.38 && progress < 0.65) phase = 2;
    else if (progress >= 0.65 && progress < 0.88) phase = 3;
    else if (progress >= 0.88) phase = 4;
    
    hero.setAttribute('data-phase', phase);
    
    // Parallax for soft background blobs
    if (blobWarm) {
      blobWarm.style.opacity = lerp(0.5, 1, easeOutCubic(clamp(progress / 0.15, 0, 1)));
      blobWarm.style.transform = `translate(${progress * 25}px, ${progress * -18}px)`;
    }
    if (blobSage) {
      blobSage.style.opacity = lerp(0.3, 0.85, easeOutCubic(clamp(progress / 0.20, 0, 1)));
      blobSage.style.transform = `translate(${progress * -18}px, ${progress * 12}px)`;
    }
    if (blobCream) {
      blobCream.style.opacity = lerp(0.35, 0.7, easeOutCubic(clamp((progress - 0.05) / 0.15, 0, 1)));
      blobCream.style.transform = `translate(${progress * 12}px, ${progress * -8}px)`;
    }
    
    ticking = false;
  }
  
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(update); ticking = true; }
  }, { passive: true });
  
  update();
  window.addEventListener('resize', () => requestAnimationFrame(update), { passive: true });
}

/* ===========================================
   Insight Page Helpers
   =========================================== */
async function loadArticles(category = 'all') {
  try {
    const response = await fetch('tables/insight_articles?limit=100&sort=-published_at');
    const result = await response.json();
    let articles = result.data || [];
    articles = articles.filter(a => a.published);
    if (category !== 'all') articles = articles.filter(a => a.category === category);
    return articles;
  } catch (err) { console.error('Error loading articles:', err); return []; }
}

async function loadArticleBySlug(slug) {
  try {
    const response = await fetch('tables/insight_articles?limit=100');
    const result = await response.json();
    return (result.data || []).find(a => a.slug === slug) || null;
  } catch (err) { console.error('Error loading article:', err); return null; }
}

async function loadRelatedArticles(currentId, relatedIds) {
  try {
    const response = await fetch('tables/insight_articles?limit=100');
    const result = await response.json();
    const articles = result.data || [];
    if (relatedIds && relatedIds.length > 0) return articles.filter(a => relatedIds.includes(a.id) && a.id !== currentId && a.published);
    return articles.filter(a => a.id !== currentId && a.published).sort((a, b) => new Date(b.published_at) - new Date(a.published_at)).slice(0, 3);
  } catch (err) { console.error('Error loading related articles:', err); return []; }
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
}

function renderArticleCard(article) {
  const icons = { '選挙': '🗳️', '議会': '🏛️', '発信': '📢', '考え方': '💡', '政策': '📋' };
  const icon = icons[article.category] || '📄';
  return `
    <a href="insight/article.html?slug=${article.slug}" class="insight-card animate-on-scroll">
      <div class="insight-card__img">${icon}</div>
      <div class="insight-card__body">
        <span class="insight-card__category">${article.category || 'その他'}</span>
        <h3 class="insight-card__title">${article.title}</h3>
        <p class="insight-card__lead">${article.lead ? article.lead.substring(0, 80) + '...' : ''}</p>
        <span class="insight-card__date">${formatDate(article.published_at)}</span>
      </div>
    </a>`;
}

function showToast(message, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 400); }, 3000);
}

/* ===========================================
   GA4 Event Tracking
   =========================================== */
(function initGA4Tracking() {
  if (typeof gtag !== 'function') return;

  document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (!link) return;
    const href = link.getAttribute('href') || '';
    const text = (link.textContent || '').trim().substring(0, 50);

    // CTA clicks (LINE links)
    if (href.includes('lin.ee/') || link.classList.contains('nav__link--cta') || link.classList.contains('cta__btn')) {
      gtag('event', 'cta_click', {
        event_category: 'CTA',
        event_label: text || href,
        link_url: href,
        page_location: window.location.href
      });
    }

    // External link clicks
    if (link.hostname && link.hostname !== window.location.hostname && !href.includes('fonts.google') && !href.includes('cdn.jsdelivr')) {
      gtag('event', 'outbound_click', {
        event_category: 'Outbound',
        event_label: text || href,
        link_url: href,
        page_location: window.location.href
      });
    }

    // Internal navigation
    if (link.hostname === window.location.hostname || href.startsWith('/') || href.startsWith('./') || href.startsWith('../') || (!href.startsWith('http') && href.endsWith('.html'))) {
      gtag('event', 'internal_navigation', {
        event_category: 'Navigation',
        event_label: text || href,
        link_url: href,
        page_location: window.location.href
      });
    }
  });

  // Scroll depth tracking
  let scrollMarkers = [25, 50, 75, 90];
  let firedMarkers = new Set();
  window.addEventListener('scroll', function() {
    const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);
    scrollMarkers.forEach(marker => {
      if (scrollPercent >= marker && !firedMarkers.has(marker)) {
        firedMarkers.add(marker);
        gtag('event', 'scroll_depth', {
          event_category: 'Engagement',
          event_label: marker + '%',
          value: marker,
          page_location: window.location.href
        });
      }
    });
  }, { passive: true });

  // Page visibility (time on page)
  let pageStartTime = Date.now();
  document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden') {
      const timeOnPage = Math.round((Date.now() - pageStartTime) / 1000);
      gtag('event', 'page_engagement_time', {
        event_category: 'Engagement',
        event_label: window.location.pathname,
        value: timeOnPage
      });
    }
  });
})();