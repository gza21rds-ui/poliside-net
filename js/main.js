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
   HERO — Ultra-Smooth Sticky Scroll (800vh)
   
   800vh = 7 full screens of scroll.
   Very slow, cinematic, deliberate.
   
   KEY DESIGN: 
   - Title stays visible for a long time (breathe space)
   - Title fades out SLOWLY
   - Clear gap before gimmick appears
   - Gimmick stays on screen for 50%+ of the scroll
   - Each phase label has long dwell time
   - No text overlap — strict separation
   =========================================== */
function initHeroStickyScroll() {
  const wrapper = document.querySelector('.hero-wrapper');
  const hero = document.querySelector('.hero');
  if (!wrapper || !hero) return;
  
  const personMain = document.getElementById('personMain');
  const personCompanion = document.getElementById('personCompanion');
  const connectionArc = document.getElementById('connectionArc');
  const phaseLabel = document.getElementById('phaseLabel');
  const heroCenter = document.getElementById('heroCenter');
  const gimmick = document.querySelector('.hero__gimmick');
  const scrollIndicator = document.querySelector('.hero__scroll-indicator');
  const blobWarm = document.querySelector('.hero__blob--warm');
  const blobSage = document.querySelector('.hero__blob--sage');
  const blobCream = document.querySelector('.hero__blob--cream');
  const rings = document.querySelectorAll('.hero__ring');
  
  function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  function easeInOutCubic(t) { return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t+2,3)/2; }
  function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }
  function easeInOutQuad(t) { return t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t+2,2)/2; }
  
  let ticking = false;
  
  function update() {
    const rect = wrapper.getBoundingClientRect();
    const scrollRange = wrapper.offsetHeight - window.innerHeight;
    const progress = clamp(-rect.top / scrollRange, 0, 1);
    const mobile = window.innerWidth < 768;
    
    /*
     * 800vh timeline — ultra-slow cinematic storytelling
     * 
     * ┌─────────────────────────────────────────┐
     * │ TITLE PHASE (0.00 – 0.15)               │
     * │  0.00-0.10  Title fully visible, breathe │
     * │  0.10-0.18  Title fades out slowly       │
     * ├─────────────────────────────────────────┤
     * │ GAP (0.16 – 0.20) — empty pause          │
     * ├─────────────────────────────────────────┤
     * │ GIMMICK PHASE 1 (0.18 – 0.42)           │
     * │  0.18-0.24  Gimmick + solo figure in     │
     * │  0.22-0.30  "ひとりで抱え込んでいた" in  │
     * │  0.30-0.38  Label stays visible           │
     * │  0.38-0.42  Label fades out               │
     * ├─────────────────────────────────────────┤
     * │ GIMMICK PHASE 2 (0.36 – 0.62)           │
     * │  0.30-0.48  Main figure slides left       │
     * │  0.36-0.52  Companion slides in           │
     * │  0.44-0.50  "隣に、誰かが来てくれた" in  │
     * │  0.50-0.58  Label stays visible           │
     * │  0.58-0.62  Label fades out               │
     * ├─────────────────────────────────────────┤
     * │ GIMMICK PHASE 3 (0.56 – 0.82)           │
     * │  0.50-0.58  Connection arc appears        │
     * │  0.62-0.68  "もう、ひとりじゃない" in    │
     * │  0.68-0.78  Label stays visible           │
     * │  0.78-0.82  Label fades out               │
     * ├─────────────────────────────────────────┤
     * │ OUTRO (0.82 – 1.00)                      │
     * │  0.85-0.95  Everything fades out gently   │
     * │  0.95-1.00  Clean empty → wave            │
     * └─────────────────────────────────────────┘
     */
    
    // ---- Title text ----
    if (heroCenter) {
      const fadeStart = 0.10;
      const fadeEnd = 0.18;
      const t = easeOutCubic(clamp((progress - fadeStart) / (fadeEnd - fadeStart), 0, 1));
      heroCenter.style.opacity = 1 - t;
      heroCenter.style.transform = `translateY(-${t * 30}px)`;
      heroCenter.style.pointerEvents = t > 0.9 ? 'none' : 'auto';
    }
    
    // ---- Gimmick container ----
    if (gimmick) {
      // Fade in: 0.18 → 0.26 (smooth)
      const gIn = easeOutCubic(clamp((progress - 0.18) / 0.08, 0, 1));
      // Fade out: 0.86 → 0.96 (gentle)
      const gOut = progress > 0.86 ? easeOutCubic(clamp((progress - 0.86) / 0.10, 0, 1)) : 0;
      gimmick.style.opacity = gIn * (1 - gOut);
      gimmick.style.pointerEvents = gIn > 0.1 && gOut < 0.9 ? 'auto' : 'none';
    }
    
    // ---- Main figure: starts center, moves left slowly ----
    if (personMain) {
      const appear = easeOutCubic(clamp((progress - 0.18) / 0.08, 0, 1));
      // Move starts at 0.30, takes until 0.48 — very slow slide
      const moveP = easeOutQuart(clamp((progress - 0.30) / 0.18, 0, 1));
      const moveX = lerp(0, mobile ? -30 : -55, moveP);
      const scale = lerp(0.7, 1.15, easeOutCubic(clamp((progress - 0.18) / 0.12, 0, 1)));
      personMain.style.transform = `translate(calc(-50% + ${moveX}px), -50%) scale(${scale})`;
      personMain.style.opacity = appear;
    }
    
    // ---- Companion: slides in from right, slowly ----
    if (personCompanion) {
      const cp = easeOutQuart(clamp((progress - 0.36) / 0.18, 0, 1));
      const moveX = lerp(mobile ? 110 : 190, mobile ? 30 : 55, cp);
      const opacity = easeOutCubic(clamp((progress - 0.34) / 0.10, 0, 1));
      const scale = lerp(0.5, 1.15, cp);
      personCompanion.style.transform = `translate(calc(-50% + ${moveX}px), -50%) scale(${scale})`;
      personCompanion.style.opacity = opacity;
    }
    
    // ---- Connection arc ----
    if (connectionArc) {
      const ap = easeOutCubic(clamp((progress - 0.50) / 0.08, 0, 1));
      connectionArc.style.opacity = ap;
      connectionArc.style.transform = `translate(-50%, -30%) scale(${lerp(0.3, 1, ap)})`;
    }
    
    // ---- Rings: fade in with gimmick, subtle glow ----
    rings.forEach((ring) => {
      const rIn = easeOutCubic(clamp((progress - 0.18) / 0.10, 0, 1));
      const rOut = progress > 0.86 ? easeOutCubic(clamp((progress - 0.86) / 0.10, 0, 1)) : 0;
      ring.style.opacity = lerp(0, 0.8, rIn) * (1 - rOut);
    });
    
    // ---- Phase labels: 3 stages, smooth crossfade, long dwell ----
    if (phaseLabel) {
      let text = '', opacity = 0;
      
      // Phase 1: 0.22 – 0.42 (20% of scroll = ~1.4 screens!)
      if (progress >= 0.22 && progress < 0.42) {
        text = '右も左も分からず、ひとりで走っていた。';
        if (progress < 0.30)      opacity = easeInOutCubic(clamp((progress - 0.22) / 0.08, 0, 1));
        else if (progress < 0.38) opacity = 1;
        else                      opacity = 1 - easeInOutCubic(clamp((progress - 0.38) / 0.04, 0, 1));
      }
      // Phase 2: 0.44 – 0.62 (18% of scroll)
      else if (progress >= 0.44 && progress < 0.62) {
        text = '隣で一緒に考えてくれる人がいた。';
        if (progress < 0.50)      opacity = easeInOutCubic(clamp((progress - 0.44) / 0.06, 0, 1));
        else if (progress < 0.58) opacity = 1;
        else                      opacity = 1 - easeInOutCubic(clamp((progress - 0.58) / 0.04, 0, 1));
      }
      // Phase 3: 0.62 – 0.84 (22% of scroll — longest, most impactful)
      else if (progress >= 0.62 && progress < 0.84) {
        text = '自分の想いに、集中できるようになった。';
        if (progress < 0.68)      opacity = easeInOutCubic(clamp((progress - 0.62) / 0.06, 0, 1));
        else if (progress < 0.78) opacity = 1;
        else                      opacity = 1 - easeInOutCubic(clamp((progress - 0.78) / 0.06, 0, 1));
      }
      
      phaseLabel.textContent = text;
      phaseLabel.style.opacity = opacity;
    }
    
    // ---- Scroll indicator ----
    if (scrollIndicator) {
      scrollIndicator.style.opacity = 1 - clamp(progress / 0.03, 0, 1);
    }
    
    // ---- Blobs: gentle parallax ----
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

const SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTO0Jmg4lrbprc2UZm0_4gXHPHjkxnHEvEiNIUsLHRbbl3q9IdHTjPjQTdFsZYwq5_c1sRrxCROMR1p/pub?output=csv';

async function fetchArticlesFromCSV() {
  try {
    const res = await fetch(SHEET_CSV_URL);
    if (!res.ok) throw new Error('Network error: ' + res.status);
    const csvText = await res.text();
    
    return new Promise((resolve) => {
      if (typeof Papa === 'undefined') { console.error('PapaParse is not loaded'); resolve([]); return; }
      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
          const articles = results.data.map(row => ({
            ...row,
            published: row.published === 'TRUE' || row.published === 'true'
          }));
          resolve(articles);
        },
        error: function(err) {
          console.error('CSV Parse Error:', err);
          resolve([]);
        }
      });
    });
  } catch (err) {
    console.error('Fetch CSV Error:', err);
    return [];
  }
}

async function loadArticles(category = 'all') {
  try {
    const articles = await fetchArticlesFromCSV();
    let result = articles || [];
    result = result.filter(a => a.published);
    if (category !== 'all') result = result.filter(a => a.category === category);
    return result.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
  } catch (err) { console.error('Error loading articles:', err); return []; }
}

async function loadArticleBySlug(slug) {
  try {
    const articles = await fetchArticlesFromCSV();
    return (articles || []).find(a => a.slug === slug) || null;
  } catch (err) { console.error('Error loading article:', err); return null; }
}

async function loadRelatedArticles(currentId, relatedIds) {
  try {
    const articles = await fetchArticlesFromCSV();
    const allArticles = articles || [];
    let result = allArticles.filter(a => a.id !== currentId && a.published);
    if (relatedIds && relatedIds.length > 0) return result.filter(a => relatedIds.includes(a.id));
    return result.sort((a, b) => new Date(b.published_at) - new Date(a.published_at)).slice(0, 3);
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
    <a href="/insight/article.html?slug=${article.slug}" class="insight-card animate-on-scroll">
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