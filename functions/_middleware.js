// Root Cloudflare Pages middleware:
// Returns HTTP 410 Gone (without GA4) for legacy pre-acquisition English spam slugs
// so Google drops them from the index and GA4 analytics stay completely unpolluted.

const LEGACY_SPAM_EXACT_PREFIXES = [
  "/if-you-",
  "/i-hope-",
  "/doctors-",
  "/why-youll-",
  "/spray-this-",
  "/10-reasons-",
  "/7-day-",
  "/after-you-",
  "/12-all-natural-",
  "/an-invisible-",
  "/dont-destroy-",
  "/eat-garlic-",
  "/german-scientists-",
  "/it-is-considered-",
];

function isLegacyEnglishSpamPath(pathname) {
  const lower = pathname.toLowerCase();
  // Never interfere with known PoliSide sections or static assets
  if (
    lower === "/" ||
    lower.startsWith("/insight") ||
    lower.startsWith("/api") ||
    lower.startsWith("/css") ||
    lower.startsWith("/js") ||
    lower.startsWith("/images") ||
    lower.startsWith("/about") ||
    lower.startsWith("/terms") ||
    lower.startsWith("/privacy") ||
    lower.startsWith("/law")
  ) {
    return false;
  }

  for (const prefix of LEGACY_SPAM_EXACT_PREFIXES) {
    if (lower.startsWith(prefix)) {
      return true;
    }
  }

  // Root-level multi-word English hyphenated slug (4+ segments, e.g. /word-word-word-word/)
  if (/^\/[a-z0-9]+(?:-[a-z0-9]+){3,}\/?$/.test(lower)) {
    return true;
  }

  return false;
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const response = await context.next();

  // Only intervene when no real static asset or route matched (404)
  if (response.status === 404 && isLegacyEnglishSpamPath(url.pathname)) {
    return new Response(
      '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow"><title>410 Gone</title></head><body><h1>410 Gone</h1><p>This legacy page has been permanently removed. Visit <a href="https://poliside.net/">PoliSide</a>.</p></body></html>',
      {
        status: 410,
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "X-Robots-Tag": "noindex, nofollow",
          "Cache-Control": "public, max-age=86400",
        },
      }
    );
  }

  return response;
}
