export async function onRequest(context) {
  const request = context.request;
  const url = new URL(request.url);

  // If not requesting the article HTML page, just pass through
  if (!url.pathname.includes('/insight/article.html')) {
    return context.next();
  }

  // Get the slug from query parameters
  const slug = url.searchParams.get('slug');
  if (!slug) {
    return context.next();
  }

  // Fetch the actual static HTML page
  const response = await context.next();

  // Fetch article data from MicroCMS
  try {
    const apiRes = await fetch(`https://poliside.microcms.io/api/v1/poliside?filters=slug[equals]${slug}&limit=1`, {
      headers: {
        'X-MICROCMS-API-KEY': 'NvwN8T5qbZ69fxMRR8zF2rDbrh0D2C0uPuoe'
      }
    });
    const apiData = await apiRes.json();
    
    if (apiData.contents && apiData.contents.length > 0) {
      const article = apiData.contents[0];
      const title = `${article.title} | PoliSide 政治活動ノウハウ`;
      const description = article.lead || 'PoliSideの政治活動ノウハウ記事です。';
      
      const fallbackImages = {
        'mindset-for-beginners': 'https://poliside.net/images/insight/political_mindset.jpg',
        'sns-basic-rules': 'https://poliside.net/images/insight/sns_rules.jpg',
        'how-to-build-kouenkai': 'https://poliside.net/images/insight/community_connection.jpg'
      };

      let imageUrl = article.thumbnail ? article.thumbnail.url : null;
      if (!imageUrl && fallbackImages[slug]) {
        imageUrl = fallbackImages[slug];
      }
      if (!imageUrl) {
        imageUrl = 'https://poliside.net/ogp.jpg';
      }

      const pageUrl = `https://poliside.net/insight/article.html?slug=${slug}`;

      // Rewrite HTML tags dynamically using Cloudflare HTMLRewriter
      return new HTMLRewriter()
        .on('title', {
          element(el) { el.setInnerContent(title); }
        })
        .on('meta[name="description"]', {
          element(el) { el.setAttribute('content', description); }
        })
        .on('meta[property="og:title"]', {
          element(el) { el.setAttribute('content', title); }
        })
        .on('meta[property="og:description"]', {
          element(el) { el.setAttribute('content', description); }
        })
        .on('meta[property="og:image"]', {
          element(el) { el.setAttribute('content', imageUrl); }
        })
        .on('meta[property="og:url"]', {
          element(el) { el.setAttribute('content', pageUrl); }
        })
        .on('meta[name="twitter:title"]', {
          element(el) { el.setAttribute('content', title); }
        })
        .on('meta[name="twitter:description"]', {
          element(el) { el.setAttribute('content', description); }
        })
        .on('meta[name="twitter:image"]', {
          element(el) { el.setAttribute('content', imageUrl); }
        })
        .transform(response);
    }
  } catch (err) {
    // If API fails, just return original response without modification
    console.error("HTMLRewriter Error:", err);
  }

  return response;
}
