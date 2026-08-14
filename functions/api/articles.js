export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const limit = url.searchParams.get('limit') || '100';

  let microCmsUrl = `https://poliside.microcms.io/api/v1/poliside?limit=${limit}`;

  const response = await fetch(microCmsUrl, {
    headers: {
      'X-MICROCMS-API-KEY': 'NvwN8T5qbZ69fxMRR8zF2rDbrh0D2C0uPuoe'
    }
  });

  const data = await response.json();
  
  if (!data.contents) {
    return new Response(JSON.stringify({ data: [] }), { status: 200, headers: { 'Content-Type': 'application/json' } });
  }

  // Format the data to match what main.js expects
  const formattedData = {
    data: data.contents.map(item => ({
      id: item.id,
      title: item.title || '無題',
      slug: item.slug || item.id,
      category: item.category || 'その他',
      lead: item.lead || '',
      content: item.content || '',
      published_at: item.publishedAt,
      thumbnail: item.thumbnail ? item.thumbnail.url : null,
      published: true
    }))
  };

  return new Response(JSON.stringify(formattedData), {
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
      'Cache-Control': 's-maxage=60, stale-while-revalidate=300'
    }
  });
}
