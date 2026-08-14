/* ======================================
   POLISIDE — Main JavaScript v10
   Clean · Warm · Textured · Ultra-Smooth
   800vh sticky scroll — slow storytelling
   ====================================== */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initScrollAnimations();
  initNavScrollEffect();
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
   Insight Page Helpers
   =========================================== */
async function fetchMicroCMS() {
  const response = await fetch('https://poliside.microcms.io/api/v1/poliside?limit=100', {
    headers: { 'X-MICROCMS-API-KEY': 'NvwN8T5qbZ69fxMRR8zF2rDbrh0D2C0uPuoe' }
  });
  const result = await response.json();
  const fallbackImages = {
    'mindset-for-beginners': '../images/insight/political_mindset.jpg',
    'sns-basic-rules': '../images/insight/sns_rules.jpg',
    'how-to-build-kouenkai': '../images/insight/community_connection.jpg'
  };
  return (result.contents || []).map(item => {
    const slug = item.slug || item.id;
    let thumbUrl = item.thumbnail ? item.thumbnail.url : null;
    if (!thumbUrl && fallbackImages[slug]) thumbUrl = fallbackImages[slug];
    return {
      id: item.id,
      title: item.title || '無題',
      slug: slug,
      category: (isinstance_array(item.category) ? item.category[0] : item.category) || 'その他',
      lead: item.lead || '',
      content: item.content || '',
      published_at: item.publishedAt,
      thumbnail: thumbUrl,
      published: true
    };
  });
}
function isinstance_array(val) { return Array.isArray(val); }

async function loadArticles(category = 'all') {
  try {
    let articles = await fetchMicroCMS();
    if (category !== 'all') articles = articles.filter(a => a.category === category);
    return articles;
  } catch (err) { console.error('Error loading articles:', err); return []; }
}

async function loadArticleBySlug(slug) {
  try {
    const articles = await fetchMicroCMS();
    return articles.find(a => a.slug === slug) || null;
  } catch (err) { console.error('Error loading article:', err); return null; }
}

async function loadRelatedArticles(currentId, relatedIds) {
  try {
    const articles = await fetchMicroCMS();
    if (relatedIds && relatedIds.length > 0) return articles.filter(a => relatedIds.includes(a.id) && a.id !== currentId);
    return articles.filter(a => a.id !== currentId).sort((a, b) => new Date(b.published_at) - new Date(a.published_at)).slice(0, 3);
  } catch (err) { console.error('Error loading related articles:', err); return []; }
}

}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
}

function renderArticleCard(article) {
  const icons = { '選挙': '🗳️', '議会': '🏛️', '発信': '📢', '考え方': '💡', '政策': '📋' };
  const icon = icons[article.category] || '📄';
  const imgHtml = article.thumbnail ? `<img src="${article.thumbnail}" alt="${article.title}" style="width:100%;height:100%;object-fit:cover;">` : `<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:3rem;">${icon}</div>`;
  return `
    <a href="/insight/article.html?slug=${article.slug}" class="insight-card animate-on-scroll">
      <div class="insight-card__img" style="padding:0; overflow:hidden; background: var(--color-bg-alt);">${imgHtml}</div>
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

// FAQ Accordion
document.addEventListener('DOMContentLoaded', () => {
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      item.classList.toggle('active');
    });
  });
});
