#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PoliSide × PoliDash × PoliStep SEO/AEO Static Article Publisher
Generates static HTML with:
- Triple JSON-LD (Article, FAQPage, BreadcrumbList + SoftwareApplication mentions)
- Cross-domain UTM attribution links for PoliStep / PoliDash
- Mid-article contextual CTA & bottom ecosystem spotlight
- Topic-cluster internal links (Related Articles) across all published posts
- Static HTML sync for index.html, insight/index.html, sitemap.xml, and llms.txt

Supports `--sync-all` to retrofit all existing static posts, homepage cards,
insight index cards, and sitemap lastmod dates cleanly.
"""

import html as html_lib
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "insight", "posts")
ARTICLES_JSON_PATH = os.path.join(BASE_DIR, "insight", "data", "articles.json")
TOPIC_QUEUE_PATH = os.path.join(BASE_DIR, "insight", "data", "topic_queue.json")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
HOME_HTML_PATH = os.path.join(BASE_DIR, "index.html")
INSIGHT_INDEX_PATH = os.path.join(BASE_DIR, "insight", "index.html")
MAIN_JS_VERSION = "20261128"

LLMS_TXT_PATHS = [
    os.path.join(BASE_DIR, "llms.txt"),
    "/Users/takanoyousuke/.gemini/antigravity/scratch/poli-dash/public/llms.txt",
    "/Users/takanoyousuke/.gemini/antigravity/scratch/polistep/public/llms.txt",
]
POLIDASH_FEED_PATH = "/Users/takanoyousuke/.gemini/antigravity/scratch/poli-dash/lib/ecosystem-articles.json"
POLISTEP_FEED_PATH = "/Users/takanoyousuke/.gemini/antigravity/scratch/polistep/src/data/ecosystemArticles.json"
POLISTEP_SITEMAP_PATH = "/Users/takanoyousuke/.gemini/antigravity/scratch/polistep/public/sitemap.xml"


def format_jp_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except Exception:
        return (date_str or "")[:10]


def load_all_articles():
    if not os.path.exists(ARTICLES_JSON_PATH):
        return []
    try:
        with open(ARTICLES_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return sorted(data, key=lambda a: a.get("published_at", ""), reverse=True)
    except Exception:
        pass
    return []


def build_utm_url(base_url, slug, content_loc, medium="article"):
    parsed = urlparse(base_url)
    params = dict(parse_qsl(parsed.query))
    params["utm_source"] = "poliside"
    params["utm_medium"] = medium
    params["utm_campaign"] = slug
    params["utm_content"] = content_loc
    return urlunparse(parsed._replace(query=urlencode(params)))


def add_utm_to_inline_ecosystem_links(content_html, slug):
    """Attach UTM parameters to inline PoliStep / PoliDash links inside article body."""
    def repl(match):
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        if "utm_source=" in url:
            return match.group(0)
        if "polistep.jp" in url:
            new_url = build_utm_url(url, slug, "article_inline_polistep")
        elif "polidash.jp" in url:
            new_url = build_utm_url(url, slug, "article_inline_polidash")
        else:
            return match.group(0)
        return f"{prefix}{new_url}{suffix}"

    return re.sub(
        r'(href=")(https://(?:polistep\.jp|polidash\.jp)[^"]*)(")',
        repl,
        content_html,
    )


def build_mid_article_cta_html(primary_product, slug):
    if primary_product == "PoliStep":
        url = build_utm_url("https://polistep.jp/", slug, "article_mid_polistep")
        return f"""<!-- MID_CTA_START -->
      <aside class="mid-article-cta" style="margin: 36px 0; padding: 22px 24px; border-radius: 16px; background: #F0F9FF; border: 1.5px solid #7DD3FC; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
        <div style="flex: 1 1 320px;">
          <div style="font-size: 0.76rem; font-weight: 800; color: #0284C7; letter-spacing: 0.04em; margin-bottom: 4px;">無料ツールで今すぐ実践</div>
          <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">日々の地域活動・駅頭・対話ログを地図で可視化「PoliStep」</div>
          <p style="margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.6;">2027年統一地方選キャンペーンで全機能0円。スマホ1つで活動記録・目標逆算・SNS日報生成まで完結します。</p>
        </div>
        <a href="{url}" data-cta-location="article_mid_polistep" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#0EA5E9; color:#fff; padding:11px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem; white-space:nowrap;">
          <i class="fas fa-shoe-prints"></i> PoliStepを無料で試す
        </a>
      </aside>
      <!-- MID_CTA_END -->"""
    elif primary_product == "PoliDash":
        url = build_utm_url("https://polidash.jp/", slug, "article_mid_polidash")
        return f"""<!-- MID_CTA_START -->
      <aside class="mid-article-cta" style="margin: 36px 0; padding: 22px 24px; border-radius: 16px; background: #ECFDF5; border: 1.5px solid #6EE7B7; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
        <div style="flex: 1 1 320px;">
          <div style="font-size: 0.76rem; font-weight: 800; color: #059669; letter-spacing: 0.04em; margin-bottom: 4px;">無料ツールで今すぐ実践</div>
          <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">公営掲示板マッピング＆AI最適ルート生成「PoliDash」</div>
          <p style="margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.6;">住所リストを貼るだけで地図化＆スタッフへLINE共有。告示日当日のポスター貼りを最速で完了できます。</p>
        </div>
        <a href="{url}" data-cta-location="article_mid_polidash" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#10B981; color:#fff; padding:11px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem; white-space:nowrap;">
          <i class="fas fa-map-location-dot"></i> PoliDashを無料で試す
        </a>
      </aside>
      <!-- MID_CTA_END -->"""
    else:
        return """<!-- MID_CTA_START -->
      <aside class="mid-article-cta" style="margin: 36px 0; padding: 22px 24px; border-radius: 16px; background: #FFF7ED; border: 1.5px solid #FDBA74; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
        <div style="flex: 1 1 320px;">
          <div style="font-size: 0.76rem; font-weight: 800; color: #EA580C; letter-spacing: 0.04em; margin-bottom: 4px;">初回60分無料・秘密厳守</div>
          <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">選挙準備・候補者HP・発信戦略をひとりで抱えていませんか？</div>
          <p style="margin: 0; font-size: 0.88rem; color: #334155; line-height: 1.6;">PoliSideでは立候補経験者が壁打ち相手として伴走します。まずはLINEからお気軽にご相談ください。</p>
        </div>
        <a href="https://lin.ee/en5smI7" data-cta-location="article_mid_line" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#06C755; color:#fff; padding:11px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem; white-space:nowrap;">
          <i class="fab fa-line"></i> LINEで無料相談する
        </a>
      </aside>
      <!-- MID_CTA_END -->"""


def inject_mid_article_cta(content_html, primary_product, slug):
    mid_cta = build_mid_article_cta_html(primary_product, slug)
    if "<!-- MID_CTA_START -->" in content_html:
        return re.sub(
            r"<!-- MID_CTA_START -->.*?<!-- MID_CTA_END -->",
            mid_cta,
            content_html,
            flags=re.DOTALL,
        )
    h2_matches = list(re.finditer(r"<h2\b", content_html))
    if len(h2_matches) >= 2:
        pos = h2_matches[1].start()
        return content_html[:pos] + "\n" + mid_cta + "\n\n" + content_html[pos:]
    return content_html


def build_product_spotlight_html(primary_product, slug):
    polistep_primary = build_utm_url("https://polistep.jp/", slug, "article_spotlight_polistep")
    polidash_primary = build_utm_url("https://polidash.jp/", slug, "article_spotlight_polidash")
    if primary_product == "PoliStep":
        return f"""
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%); border: 2px solid #0EA5E9; box-shadow: 0 10px 28px rgba(14, 165, 233, 0.08);">
          <div style="display:inline-block; background:#0EA5E9; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">政治活動DX・フィールド活動可視化アプリ</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">孤独なドブ板を可視化で変える「PoliStep（ポリステップ）」</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            日々の地域訪問・対話記録・ポスター貼付・街頭演説・ビラ配りをスマホ地図上でワンタップ記録。目標日からの1日あたりのノルマ自動逆算や、SNS・LINEグループへの日報画像自動生成まで、政治活動の進捗管理とチーム共有を完全無料でサポートします。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="{polistep_primary}" data-cta-location="article_spotlight_polistep" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#0EA5E9; color:#fff; padding:12px 24px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.95rem;">
              <i class="fas fa-shoe-prints"></i> PoliStep 公式サイトを見る（無料）
            </a>
            <a href="{polidash_primary}" data-cta-location="article_spotlight_polidash_sub" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem;">
              <i class="fas fa-map-location-dot" style="color:#10B981;"></i> ポスター貼付管理なら PoliDash
            </a>
          </div>
        </div>
        """
    elif primary_product == "PoliDash":
        return f"""
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #ECFDF5 0%, #F8FAFC 100%); border: 2px solid #10B981; box-shadow: 0 10px 28px rgba(16, 185, 129, 0.08);">
          <div style="display:inline-block; background:#10B981; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">選挙ポスター貼付管理アプリ</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">ポスター割り振りと進捗をスマホで一元管理「PoliDash（ポリダッシュ）」</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            掲示場所の住所リストをコピペするだけで地図上にピンを一括自動配置。AIがスタッフ人数や移動手段に合わせて最適な巡回ルートを自動生成し、ログイン不要の専用URLをLINEで送るだけでリアルタイムに進捗を同期できます。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="{polidash_primary}" data-cta-location="article_spotlight_polidash" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#10B981; color:#fff; padding:12px 24px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.95rem;">
              <i class="fas fa-map-location-dot"></i> PoliDash 公式サイトを見る（無料）
            </a>
            <a href="{polistep_primary}" data-cta-location="article_spotlight_polistep_sub" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem;">
              <i class="fas fa-shoe-prints" style="color:#0EA5E9;"></i> 日々の地域活動記録なら PoliStep
            </a>
          </div>
        </div>
        """
    else:
        return f"""
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #F8FAFC 0%, #FFF7ED 100%); border: 2px solid #F97316; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);">
          <div style="display:inline-block; background:#0F172A; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">PoliSide エコシステム</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">HP作成・伴走相談から政治活動DXツールまでトータルサポート</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            PoliSide（候補者HP作成＆月1回のオンライン伴走サポート）に加え、日々の地域活動を地図とグラフで可視化する「PoliStep」、選挙ポスター貼付管理アプリ「PoliDash」であなたの挑戦を全方位から支えます。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="https://poliside.net/#pricing" data-cta-location="article_spotlight_poliside" style="display:inline-flex; align-items:center; gap:8px; background:#F97316; color:#fff; padding:12px 22px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.92rem;">
              <i class="fas fa-handshake-angle"></i> PoliSideの伴走支援・料金を見る
            </a>
            <a href="{polidash_primary}" data-cta-location="article_spotlight_polidash_sub" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 18px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.88rem;">
              <i class="fas fa-map-location-dot" style="color:#10B981;"></i> PoliDash（ポスター管理）
            </a>
            <a href="{polistep_primary}" data-cta-location="article_spotlight_polistep_sub" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 18px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.88rem;">
              <i class="fas fa-shoe-prints" style="color:#0EA5E9;"></i> PoliStep（活動記録DX）
            </a>
          </div>
        </div>
        """


def select_related_articles(current_slug, current_category, current_product, all_articles, limit=3):
    scored = []
    for idx, art in enumerate(all_articles):
        if art.get("slug") == current_slug:
            continue
        score = 0
        if art.get("primary_product") == current_product:
            score += 3
        if art.get("category") == current_category:
            score += 2
        # Slight recency bonus
        score += max(0, (30 - idx) * 0.02)
        scored.append((score, art))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]


def build_related_articles_html(current_slug, current_category, current_product, all_articles):
    related = select_related_articles(current_slug, current_category, current_product, all_articles, limit=3)
    if not related:
        return "<!-- RELATED_ARTICLES_START --><!-- RELATED_ARTICLES_END -->"

    cards = []
    for art in related:
        r_slug = art["slug"]
        r_title = html_lib.escape(art["title"])
        r_cat = html_lib.escape(art.get("category", "選挙"))
        r_date = format_jp_date(art.get("published_at", ""))
        r_lead = html_lib.escape((art.get("lead") or "")[:72] + "…")
        cards.append(f"""
          <a href="/insight/posts/{r_slug}" class="related-card" data-cta-location="related_article" style="display:block; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:20px; text-decoration:none; transition:border-color 0.2s, transform 0.2s; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; font-size:0.78rem;">
              <span style="background:rgba(249,115,22,0.12); color:#EA580C; font-weight:700; padding:2px 10px; border-radius:999px;">{r_cat}</span>
              <span style="color:#64748B;">{r_date}</span>
            </div>
            <div style="font-size:1rem; font-weight:800; color:#0F172A; line-height:1.5; margin-bottom:6px;">{r_title}</div>
            <p style="margin:0; font-size:0.86rem; color:#475569; line-height:1.6;">{r_lead}</p>
          </a>""")

    return f"""<!-- RELATED_ARTICLES_START -->
    <section class="related-articles" aria-label="あわせて読みたい関連記事" style="max-width:760px; margin:48px auto 0; padding:0 20px;">
      <h2 style="font-size:1.35rem; font-weight:800; color:#0F172A; margin-bottom:18px; display:flex; align-items:center; gap:10px;">
        <i class="fas fa-book-open" style="color:#F97316;"></i>
        <span>あわせて読みたい実践ガイド</span>
      </h2>
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px;">
        {''.join(cards)}
      </div>
    </section>
    <!-- RELATED_ARTICLES_END -->"""


def generate_static_html(article_data, all_articles=None):
    slug = article_data["slug"]
    title = article_data["title"]
    category = article_data.get("category", "選挙")
    lead = article_data["lead"]
    tldr = article_data.get("tldr", lead)
    primary_product = article_data.get("primary_product", "PoliSide")
    content_html = add_utm_to_inline_ecosystem_links(article_data["content_html"], slug)
    content_html = inject_mid_article_cta(content_html, primary_product, slug)
    faqs = article_data.get("faqs", [])
    keywords = ", ".join(article_data.get("target_keywords", ["地方選挙", "若手候補者", "PoliSide", "PoliDash", "PoliStep"]))
    published_at = article_data.get("published_at", datetime.now().strftime("%Y-%m-%dT09:00:00+09:00"))
    date_jp = format_jp_date(published_at)
    thumb_path = article_data.get("thumbnail", "/images/insight/political_mindset.jpg")
    if thumb_path.startswith("/"):
        rel_thumb = "../.." + thumb_path
        abs_thumb = "https://poliside.net" + thumb_path
    else:
        rel_thumb = thumb_path
        abs_thumb = "https://poliside.net/ogp.jpg"

    page_url = f"https://poliside.net/insight/posts/{slug}"
    polistep_bottom = build_utm_url("https://polistep.jp/", slug, "article_bottom_polistep")
    polidash_bottom = build_utm_url("https://polidash.jp/", slug, "article_bottom_polidash")
    polistep_footer = build_utm_url("https://polistep.jp/", slug, "article_footer_polistep")
    polidash_footer = build_utm_url("https://polidash.jp/", slug, "article_footer_polidash")

    # Build FAQ HTML & JSON-LD
    faq_html_items = []
    faq_json_items = []
    for f in faqs:
        q = f["q"]
        a = f["a"]
        faq_html_items.append(f"""
          <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:24px; margin-bottom:16px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
            <h3 style="margin-top:0; margin-bottom:10px; font-size:1.1rem; color:#0F172A; display:flex; align-items:flex-start; gap:10px;">
              <span style="background:#F97316; color:#fff; border-radius:6px; padding:2px 8px; font-size:0.85rem; font-weight:800; flex-shrink:0;">Q</span>
              <span>{q}</span>
            </h3>
            <p style="margin-bottom:0; color:#334155; font-size:0.98rem; line-height:1.75; padding-left:34px;">{a}</p>
          </div>
        """)
        faq_json_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })

    faq_section_html = ""
    if faq_html_items:
        faq_section_html = f"""
        <section style="margin-top: 56px; padding-top: 32px; border-top: 1px solid #E2E8F0;">
          <h2 style="font-size:1.5rem; color:#0F172A; margin-bottom:24px;">よくある質問（FAQ）</h2>
          {''.join(faq_html_items)}
        </section>
        """

    article_json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": lead,
        "image": [abs_thumb],
        "datePublished": published_at,
        "dateModified": published_at,
        "author": {
            "@type": "Organization",
            "name": "PoliSide（ポリサイド）編集部",
            "url": "https://poliside.net"
        },
        "publisher": {
            "@type": "Organization",
            "name": "PoliSide",
            "url": "https://poliside.net",
            "logo": {
                "@type": "ImageObject",
                "url": "https://poliside.net/ogp.jpg"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": page_url
        },
        "mentions": [
            {
                "@type": "Service",
                "name": "PoliSide（ポリサイド）",
                "url": "https://poliside.net",
                "description": "若手候補者・若手議員の隣に立つ伴走型サポート＆候補者ホームページ構築サービス"
            },
            {
                "@type": "SoftwareApplication",
                "name": "PoliDash（ポリダッシュ）",
                "url": "https://polidash.jp",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": "選挙ポスター貼付管理アプリ。住所一括登録・AI最適ルート自動生成・専用URLでのスタッフ共有・リアルタイム進捗管理"
            },
            {
                "@type": "SoftwareApplication",
                "name": "PoliStep（ポリステップ）",
                "url": "https://polistep.jp",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": "日々の政治活動（地域訪問・対話記録・ポスター貼付・街頭演説・ビラ配り等）をスマホ地図上で可視化・逆算管理・日報画像生成できる政治活動DXアプリ"
            }
        ]
    }

    faq_json_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_json_items
    }

    breadcrumb_json_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "TOP", "item": "https://poliside.net/"},
            {"@type": "ListItem", "position": 2, "name": "政治活動ノウハウ記事", "item": "https://poliside.net/insight/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url}
        ]
    }

    spotlight_html = build_product_spotlight_html(primary_product, slug)
    related_html = build_related_articles_html(
        slug, category, primary_product, all_articles if all_articles is not None else load_all_articles()
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-QVR4P6J8D5"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-QVR4P6J8D5');
  </script>
  <title>{title} | PoliSide 政治活動ノウハウ記事</title>
  <meta name="description" content="{lead}">
  <meta name="keywords" content="{keywords}">
  <meta name="author" content="PoliSide">
  <link rel="canonical" href="{page_url}">

  <!-- OGP -->
  <meta property="og:title" content="{title} | PoliSide">
  <meta property="og:description" content="{lead}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{page_url}">
  <meta property="og:image" content="{abs_thumb}">
  <meta property="og:site_name" content="PoliSide">
  <meta property="og:locale" content="ja_JP">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{lead}">
  <meta name="twitter:image" content="{abs_thumb}">

  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <meta name="theme-color" content="#F97316">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+JP:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" integrity="sha384-iw3OoTErCYJJB9mCa8LNS2hbsQ7M3C0EpIsO/H5+EGAkPGc6rk+V8i04oW/K5xq0" crossorigin="anonymous">
  <link rel="stylesheet" href="../../css/style.css?v=20261113">
  <style>
    .article-header {{ padding: 110px 0 48px; text-align: center; background: var(--color-bg-alt); border-bottom: 1px solid var(--color-border); }}
    .article-meta {{ font-size: 0.9rem; color: var(--color-text-muted); margin-bottom: 16px; }}
    .article-meta .cat-badge {{ display: inline-block; padding: 4px 14px; border-radius: 999px; background: rgba(249,115,22,0.12); color: var(--color-accent); font-weight: 700; margin-right: 12px; }}
    .article-title {{ font-size: clamp(1.5rem, 3.2vw, 2.1rem); font-weight: 800; color: var(--color-primary); line-height: 1.45; max-width: 820px; margin: 0 auto; }}
    .article-content {{ max-width: 760px; margin: 48px auto; padding: 0 20px; font-size: 1.04rem; line-height: 1.85; color: var(--color-text); }}
    .article-content h2 {{ margin-top: 52px; margin-bottom: 20px; font-size: 1.48rem; color: var(--color-primary); border-bottom: 2px solid var(--color-accent); padding-bottom: 10px; }}
    .article-content h3 {{ margin-top: 32px; margin-bottom: 14px; font-size: 1.22rem; color: var(--color-primary); }}
    .article-content p {{ margin-bottom: 22px; }}
    .article-content ul, .article-content ol {{ margin: 0 0 24px 22px; }}
    .article-content ul {{ list-style: disc; }}
    .article-content ol {{ list-style: decimal; }}
    .article-content li {{ margin-bottom: 10px; line-height: 1.75; }}
    .article-content table {{ width: 100%; border-collapse: collapse; margin: 28px 0; font-size: 0.95rem; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(15,23,42,0.04); }}
    .article-content th, .article-content td {{ border: 1px solid #E2E8F0; padding: 14px 16px; text-align: left; vertical-align: top; }}
    .article-content th {{ background: #F1F5F9; color: #0F172A; font-weight: 700; }}
    .tldr-box {{ background: #FFF7ED; border-left: 4px solid #F97316; border-radius: 12px; padding: 24px 28px; margin-bottom: 36px; }}
    .tldr-box__label {{ font-size: 0.85rem; font-weight: 800; color: #EA580C; letter-spacing: 0.06em; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }}
    .btn-back {{ display: inline-block; margin-top: 32px; color: var(--color-accent); font-weight: 700; text-decoration: none; }}
    .related-card:hover {{ border-color: #F97316 !important; transform: translateY(-2px); }}
  </style>
</head>
<body>

  <!-- Navigation -->
  <nav class="nav" role="navigation" aria-label="メインナビゲーション">
    <div class="nav__inner">
      <a href="../../index.html" class="nav__logo" style="display:flex; align-items:center; gap:10px;">
        <img src="../../favicon.svg" alt="PoliSide Icon" style="width:26px; height:26px; border-radius:6px; box-shadow: 0 2px 6px rgba(249,115,22,0.3);">
        PoliSide
      </a>
      <div class="nav__links" id="mobile-menu">
        <a href="../../index.html" class="nav__link">TOP</a>
        <a href="../index.html" class="nav__link">政治活動ノウハウ記事</a>
        <a href="../../index.html#lineup" class="nav__link">サービス</a>
        <a href="../../index.html#pricing" class="nav__link">料金</a>
        <a href="https://lin.ee/en5smI7" data-cta-location="article_nav_line" target="_blank" rel="noopener" class="nav__link nav__link--cta">
          <i class="fab fa-line"></i> LINE相談
        </a>
      </div>
      <button class="nav__hamburger" aria-label="メニュー" aria-expanded="false" aria-controls="mobile-menu" type="button" style="background:none;border:none;cursor:pointer;">
        <span></span><span></span><span></span>
      </button>
    </div>
    <div class="nav__overlay"></div>
  </nav>

  <main>
    <header class="article-header">
      <div class="container--narrow">
        <div class="article-meta">
          <span class="cat-badge">{category}</span>
          <time datetime="{published_at[:10]}">{date_jp}</time>
        </div>
        <h1 class="article-title">{title}</h1>
      </div>
    </header>

    <article class="article-content">
      <img src="{rel_thumb}" alt="{title}" style="width:100%; aspect-ratio:16/9; height:auto; object-fit:cover; border-radius:16px; margin-bottom:36px; box-shadow:0 8px 24px rgba(15,23,42,0.06);">

      <!-- AEO Direct Answer / TL;DR Box -->
      <div class="tldr-box">
        <div class="tldr-box__label"><i class="fas fa-lightbulb"></i> この記事の結論・要点（30秒でわかる要約）</div>
        <p style="margin-bottom:0; color:#0F172A; font-weight:500; line-height:1.75;">{tldr}</p>
      </div>

      {content_html}

      {spotlight_html}

      {faq_section_html}

      <!-- 公職選挙法・法令遵守に関する注意事項 -->
      <div style="margin-top: 40px; padding: 18px 22px; background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 12px; font-size: 0.86rem; color: #475569; line-height: 1.7;">
        <strong style="color: #0F172A;"><i class="fas fa-scale-balanced" style="color: #64748B; margin-right: 6px;"></i>法令遵守（公職選挙法等）に関するご注意</strong><br>
        本記事は一般的な政治活動・選挙準備の情報提供を目的としており、特定の法的判断や選挙運動を誘導するものではありません。告示日前の投票依頼（事前運動）や戸別訪問、寄附行為等は公職選挙法により厳しく制限されています。選挙の種類や自治体によって運用・届出要件が異なる場合がありますので、実際の活動や制作物の仕様については必ず事前に管轄の選挙管理委員会へご確認ください。
      </div>
    </article>

    {related_html}

    <!-- 記事読了後のCTA導線 -->
    <div class="article-cta-banner" style="max-width:760px; margin:48px auto; padding:36px 28px; background:#0F172A; color:#fff; border-radius:24px; text-align:center;">
      <h3 style="color:#fff; font-size:1.4rem; margin-bottom:12px;">まずは、ひとりで抱えないことから。</h3>
      <p style="color:#CBD5E1; font-size:0.98rem; line-height:1.8; margin-bottom:24px;">
        PoliSideは、若手候補者・若手議員の「隣に立つ」伴走型サポートです。<br>
        日々の政治活動の地図記録・可視化（<a href="{polistep_bottom}" data-cta-location="article_bottom_polistep" target="_blank" rel="noopener" style="color:#38BDF8; text-decoration:underline;">PoliStep</a>）・選挙ポスター貼付管理（<a href="{polidash_bottom}" data-cta-location="article_bottom_polidash" target="_blank" rel="noopener" style="color:#34D399; text-decoration:underline;">PoliDash</a>）・HP作成まで、初回60分無料でご相談いただけます。
      </p>
      <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:14px;">
        <a href="https://lin.ee/en5smI7" data-cta-location="article_bottom_line" target="_blank" rel="noopener" class="cta-btn">
          <i class="fab fa-line" style="font-size:1.3rem;"></i>
          <span>無料相談を予約する（LINE）</span>
        </a>
        <a href="../../index.html" style="display:inline-flex; align-items:center; gap:8px; padding:14px 26px; border-radius:999px; background:rgba(255,255,255,0.1); color:#fff; text-decoration:none; font-weight:700; font-size:0.95rem;">
          <i class="fas fa-home"></i> PoliSide トップページへ
        </a>
      </div>
    </div>

    <div style="text-align:center; padding-bottom: 64px;">
      <a href="../index.html" class="btn-back"><i class="fas fa-arrow-left"></i> 政治活動ノウハウ記事一覧へ戻る</a>
    </div>
  </main>

  <footer class="footer">
    <div class="footer__inner">
      <div class="footer__top">
        <span class="footer__logo">PoliSide</span>
        <div class="footer__links">
          <a href="../../index.html" class="footer__link">TOP</a>
          <a href="../index.html" class="footer__link">政治活動ノウハウ記事</a>
          <a href="{polidash_footer}" data-cta-location="article_footer_polidash" target="_blank" rel="noopener" class="footer__link">PoliDash（ポスター管理）</a>
          <a href="{polistep_footer}" data-cta-location="article_footer_polistep" target="_blank" rel="noopener" class="footer__link">PoliStep（活動記録DX）</a>
          <a href="https://lin.ee/en5smI7" data-cta-location="article_footer_line" target="_blank" rel="noopener" class="footer__link">LINE相談</a>
        </div>
      </div>
      <div class="footer__legal">
        <a href="../../terms.html">利用規約</a>
        <a href="../../privacy.html">プライバシーポリシー</a>
        <a href="../../law.html">特定商取引法に基づく表記</a>
      </div>
      <div class="footer__bottom">
        <p class="footer__copy">&copy; 2026 PoliSide. All rights reserved.</p>
      </div>
    </div>
  </footer>

  <script src="../../js/main.js?v={MAIN_JS_VERSION}"></script>
  <script type="application/ld+json">
{json.dumps(article_json_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(faq_json_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(breadcrumb_json_ld, ensure_ascii=False, indent=2)}
  </script>
</body>
</html>
"""
    os.makedirs(POSTS_DIR, exist_ok=True)
    out_file = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    return out_file


def update_articles_json(article_data):
    articles = []
    if os.path.exists(ARTICLES_JSON_PATH):
        try:
            with open(ARTICLES_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    articles = data
        except Exception:
            articles = []

    slug = article_data["slug"]
    category = article_data.get("category", "選挙")
    polidash_note = article_data.get(
        "polidash_note",
        f"【{category}ノウハウ】選挙準備・ポスター貼付計画や陣営オペレーションの効率化に役立つ実践解説。"
    )
    polistep_note = article_data.get(
        "polistep_note",
        f"【{category}ノウハウ】日々の地域活動・目標逆算計画や公職選挙法を踏まえた実践ステップを解説。"
    )
    articles = [a for a in articles if a.get("slug") != slug]
    entry = {
        "id": article_data.get("id", slug),
        "title": article_data["title"],
        "slug": slug,
        "category": category,
        "lead": article_data["lead"],
        "polidash_note": polidash_note,
        "polistep_note": polistep_note,
        "published_at": article_data.get("published_at", datetime.now().strftime("%Y-%m-%dT09:00:00+09:00")),
        "thumbnail": article_data.get("thumbnail", "/images/insight/political_mindset.jpg"),
        "static_url": f"/insight/posts/{slug}",
        "primary_product": article_data.get("primary_product", "PoliSide"),
        "published": True
    }
    articles.insert(0, entry)
    articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
    with open(ARTICLES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    return articles


def update_sitemap(slug, published_at, all_articles=None):
    """Rebuild or update sitemap.xml with clean Cloudflare Pages URLs (no .html redirects, no noindex pages)."""
    date_str = (published_at or datetime.now().strftime("%Y-%m-%d"))[:10]
    if all_articles is None:
        all_articles = load_all_articles()

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        '    <loc>https://poliside.net/</loc>',
        f'    <lastmod>{date_str}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        '    <loc>https://poliside.net/about</loc>',
        '    <lastmod>2026-08-13</lastmod>',
        '    <changefreq>monthly</changefreq>',
        '    <priority>0.8</priority>',
        '  </url>',
        '  <url>',
        '    <loc>https://poliside.net/insight/</loc>',
        f'    <lastmod>{date_str}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>',
    ]
    for art in sorted(all_articles, key=lambda a: a.get("published_at", "")):
        a_slug = art.get("slug")
        if not a_slug:
            continue
        a_date = (art.get("published_at") or date_str)[:10]
        lines.extend([
            '  <url>',
            f'    <loc>https://poliside.net/insight/posts/{a_slug}</loc>',
            f'    <lastmod>{a_date}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>',
        ])
    lines.append('</urlset>')
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def update_llms_txt(article_data):
    slug = article_data["slug"]
    title = article_data["title"]
    lead = article_data["lead"]
    url = f"https://poliside.net/insight/posts/{slug}"
    line = f"- [{title}]({url}): {lead}"
    marker = "<!-- ARTICLES_START -->"

    for llms_path in LLMS_TXT_PATHS:
        if not os.path.exists(llms_path):
            continue
        with open(llms_path, "r", encoding="utf-8") as f:
            content = f.read()
        if url in content:
            continue
        if marker in content:
            content = content.replace(marker, f"{marker}\n{line}")
            with open(llms_path, "w", encoding="utf-8") as f:
                f.write(content)


def build_static_article_card(art, relative_prefix="", delay_class=""):
    slug = art["slug"]
    title = html_lib.escape(art["title"])
    category = html_lib.escape(art.get("category", "選挙"))
    lead_raw = art.get("lead", "")
    lead = html_lib.escape(lead_raw[:80] + ("..." if len(lead_raw) > 80 else ""))
    date_jp = format_jp_date(art.get("published_at", ""))
    thumb = (art.get("thumbnail") or "/images/insight/political_mindset.jpg").lstrip("/")
    img_src = f"{relative_prefix}{thumb}"
    href = f"/insight/posts/{slug}"
    cls = f"insight-card animate-on-scroll{(' ' + delay_class) if delay_class else ''}"
    return f"""          <a href="{href}" class="{cls}" data-category="{category}">
            <div class="insight-card__img" style="padding:0; overflow:hidden; background: var(--color-bg-alt);">
              <img src="{img_src}" alt="{title}" loading="lazy" width="1280" height="720" style="width:100%;height:100%;object-fit:cover;display:block;">
            </div>
            <div class="insight-card__body">
              <span class="insight-card__category">{category}</span>
              <h3 class="insight-card__title">{title}</h3>
              <p class="insight-card__lead">{lead}</p>
              <span class="insight-card__date">{date_jp}</span>
            </div>
          </a>"""


def update_home_and_insight_index(all_articles):
    """Sync latest 3 cards in index.html and all static cards in insight/index.html."""
    if not all_articles:
        return

    # 1. Homepage (latest 3 articles)
    if os.path.exists(HOME_HTML_PATH):
        with open(HOME_HTML_PATH, "r", encoding="utf-8") as f:
            home_html = f.read()
        delays = ["", "delay-1", "delay-2"]
        home_cards = "\n".join(
            build_static_article_card(art, relative_prefix="", delay_class=delays[i])
            for i, art in enumerate(all_articles[:3])
        )
        new_home_block = f"<!-- LATEST_INSIGHTS_START -->\n{home_cards}\n          <!-- LATEST_INSIGHTS_END -->"
        if "<!-- LATEST_INSIGHTS_START -->" in home_html:
            home_html = re.sub(
                r"<!-- LATEST_INSIGHTS_START -->.*?<!-- LATEST_INSIGHTS_END -->",
                new_home_block,
                home_html,
                flags=re.DOTALL,
            )
            with open(HOME_HTML_PATH, "w", encoding="utf-8") as f:
                f.write(home_html)

    # 2. Insight index (all published articles statically embedded for SEO crawlers)
    if os.path.exists(INSIGHT_INDEX_PATH):
        with open(INSIGHT_INDEX_PATH, "r", encoding="utf-8") as f:
            idx_html = f.read()
        all_cards = "\n".join(
            build_static_article_card(art, relative_prefix="../", delay_class="visible")
            for art in all_articles
        )
        new_idx_block = f"<!-- STATIC_ARTICLES_START -->\n{all_cards}\n        <!-- STATIC_ARTICLES_END -->"
        if "<!-- STATIC_ARTICLES_START -->" in idx_html:
            idx_html = re.sub(
                r"<!-- STATIC_ARTICLES_START -->.*?<!-- STATIC_ARTICLES_END -->",
                new_idx_block,
                idx_html,
                flags=re.DOTALL,
            )
            with open(INSIGHT_INDEX_PATH, "w", encoding="utf-8") as f:
                f.write(idx_html)


def refresh_existing_posts_seo(all_articles):
    """Retrofit/refresh all existing static post HTMLs with UTMs, mid-CTA, related articles, and main.js version."""
    art_map = {a["slug"]: a for a in all_articles}
    updated = 0

    for slug, art in art_map.items():
        path = os.path.join(POSTS_DIR, f"{slug}.html")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            page = f.read()

        category = art.get("category", "選挙")
        primary_product = art.get("primary_product", "PoliSide")

        # 1. Replace inline onclick add_line with unified data-cta-location (avoid double-fire & capture location)
        page = re.sub(
            r'<a href="https://lin\.ee/en5smI7" onclick="[^"]*" target="_blank" rel="noopener" class="nav__link nav__link--cta">',
            '<a href="https://lin.ee/en5smI7" data-cta-location="article_nav_line" target="_blank" rel="noopener" class="nav__link nav__link--cta">',
            page,
        )
        page = re.sub(
            r'<a href="https://lin\.ee/en5smI7" onclick="[^"]*" target="_blank" rel="noopener" class="cta-btn">',
            '<a href="https://lin.ee/en5smI7" data-cta-location="article_bottom_line" target="_blank" rel="noopener" class="cta-btn">',
            page,
        )
        page = page.replace(
            '<a href="https://lin.ee/en5smI7" target="_blank" rel="noopener" class="footer__link">LINE相談</a>',
            '<a href="https://lin.ee/en5smI7" data-cta-location="article_footer_line" target="_blank" rel="noopener" class="footer__link">LINE相談</a>',
        )

        # 2. Add UTMs to PoliStep / PoliDash links across sections
        def add_utm_generic(m):
            prefix, url, suffix = m.group(1), m.group(2), m.group(3)
            if "utm_source=" in url:
                return m.group(0)
            target = "polistep" if "polistep.jp" in url else "polidash"
            new_url = build_utm_url(url, slug, f"article_{target}")
            return f"{prefix}{new_url}{suffix}"

        page = re.sub(
            r'(href=")(https://(?:polistep\.jp|polidash\.jp)[^"]*)(")',
            add_utm_generic,
            page,
        )

        # 3. Inject or refresh Mid-Article CTA inside <article class="article-content">
        mid_cta = build_mid_article_cta_html(primary_product, slug)
        if "<!-- MID_CTA_START -->" in page:
            page = re.sub(
                r"<!-- MID_CTA_START -->.*?<!-- MID_CTA_END -->",
                mid_cta,
                page,
                flags=re.DOTALL,
            )
        else:
            art_match = re.search(r'(<article class="article-content">)(.*?)(</article>)', page, flags=re.DOTALL)
            if art_match:
                body = art_match.group(2)
                h2s = list(re.finditer(r"<h2\b", body))
                if len(h2s) >= 2:
                    pos = h2s[1].start()
                    new_body = body[:pos] + "\n" + mid_cta + "\n\n" + body[pos:]
                    page = page[:art_match.start(2)] + new_body + page[art_match.end(2):]

        # 4. Inject or refresh Related Articles section right before <!-- 記事読了後のCTA導線 -->
        related_html = build_related_articles_html(slug, category, primary_product, all_articles)
        if "<!-- RELATED_ARTICLES_START -->" in page:
            page = re.sub(
                r"<!-- RELATED_ARTICLES_START -->.*?<!-- RELATED_ARTICLES_END -->",
                related_html,
                page,
                flags=re.DOTALL,
            )
        elif "<!-- 記事読了後のCTA導線 -->" in page:
            page = page.replace(
                "<!-- 記事読了後のCTA導線 -->",
                related_html + "\n\n    <!-- 記事読了後のCTA導線 -->",
                1,
            )

        # 5. Normalize Clean URLs (remove .html from canonical, og:url, JSON-LD, nav/footer links)
        clean_url = f"https://poliside.net/insight/posts/{slug}"
        page = page.replace(f"https://poliside.net/insight/posts/{slug}.html", clean_url)
        page = page.replace("https://poliside.net/insight/index.html", "https://poliside.net/insight/")
        page = page.replace('href="../../index.html"', 'href="/"')
        page = page.replace('href="../../index.html#', 'href="/#')
        page = page.replace('href="../index.html"', 'href="/insight/"')
        page = page.replace('href="../../terms.html"', 'href="/terms"')
        page = page.replace('href="../../privacy.html"', 'href="/privacy"')
        page = page.replace('href="../../law.html"', 'href="/law"')

        # 6. Sync <title>, meta description, OGP/Twitter tags from articles.json
        t_esc = html_lib.escape(art["title"], quote=True)
        d_esc = html_lib.escape(art["lead"], quote=True)
        page = re.sub(r"<title>.*?</title>", f"<title>{t_esc} | PoliSide</title>", page, count=1, flags=re.DOTALL)
        page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d_esc}">', page, count=1)
        page = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t_esc} | PoliSide">', page, count=1)
        page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d_esc}">', page, count=1)
        page = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{t_esc}">', page, count=1)
        page = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{d_esc}">', page, count=1)

        # 7. Add hover CSS for related-card if absent & bump main.js cache query
        if ".related-card:hover" not in page and "</style>" in page:
            page = page.replace(
                "</style>",
                "    .related-card:hover { border-color: #F97316 !important; transform: translateY(-2px); }\n  </style>",
                1,
            )
        page = re.sub(
            r'<script src="\.\./\.\./js/main\.js(?:\?v=[^"]*)?"></script>',
            f'<script src="../../js/main.js?v={MAIN_JS_VERSION}"></script>',
            page,
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        updated += 1

    return updated


def update_sister_site_feeds(article_data):
    """
    PoliDash / PoliStep のトップページ表示用JSONフィードを更新する。
    コピーコンテンツ判定（重複ペナルティ）を完全に回避するため、
    記事本文やmeta description(lead)の丸写しは行わず、
    各プロダクトの読者視点に合わせた短文紹介（1行ダイジェスト）のみを格納する。
    """
    slug = article_data["slug"]
    title = article_data["title"]
    category = article_data.get("category", "選挙")
    published_at = article_data.get("published_at", datetime.now().strftime("%Y-%m-%dT09:00:00+09:00"))
    date_jp = format_jp_date(published_at)
    url = f"https://poliside.net/insight/posts/{slug}"
    primary_product = article_data.get("primary_product", "PoliSide")

    polidash_note = article_data.get(
        "polidash_note",
        f"【{category}ノウハウ】選挙準備・ポスター貼付計画や陣営オペレーションの効率化に役立つ実践解説。"
    )
    polistep_note = article_data.get(
        "polistep_note",
        f"【{category}ノウハウ】日々の地域活動・目標逆算計画や公職選挙法を踏まえた実践ステップを解説。"
    )

    for feed_path, note_text in [
        (POLIDASH_FEED_PATH, polidash_note),
        (POLISTEP_FEED_PATH, polistep_note),
    ]:
        if not os.path.exists(os.path.dirname(feed_path)):
            continue
        items = []
        if os.path.exists(feed_path):
            try:
                with open(feed_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        items = loaded
            except Exception:
                items = []

        items = [x for x in items if x.get("slug") != slug]
        items.insert(0, {
            "slug": slug,
            "title": title,
            "category": category,
            "published_at": published_at[:10],
            "date_jp": date_jp,
            "url": url,
            "primary_product": primary_product,
            "digest": note_text
        })
        items = items[:6]
        with open(feed_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    if os.path.exists(POLISTEP_SITEMAP_PATH):
        with open(POLISTEP_SITEMAP_PATH, "r", encoding="utf-8") as f:
            sxml = f.read()
        sxml = re.sub(
            r"(<loc>https://polistep\.jp/</loc>\s*<lastmod>)[0-9\-]+(</lastmod>)",
            rf"\g<1>{published_at[:10]}\g<2>",
            sxml
        )
        with open(POLISTEP_SITEMAP_PATH, "w", encoding="utf-8") as f:
            f.write(sxml)


def mark_topic_published(slug, published_at):
    if not os.path.exists(TOPIC_QUEUE_PATH):
        return
    with open(TOPIC_QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)

    for item in queue:
        if item.get("slug") == slug:
            item["status"] = "published"
            item["published_at"] = published_at

    with open(TOPIC_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_article.py <article_json_path> | --sync-all")
        sys.exit(1)

    if sys.argv[1] == "--sync-all":
        all_articles = load_all_articles()
        updated = refresh_existing_posts_seo(all_articles)
        update_home_and_insight_index(all_articles)
        if all_articles:
            update_sitemap(None, all_articles[0].get("published_at", datetime.now().strftime("%Y-%m-%d")))
        print(f"Synced SEO/UTM/internal links across {updated} posts, homepage, insight index, and sitemap.")
        return

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        article_data = json.load(f)

    if "published_at" not in article_data or not article_data["published_at"]:
        article_data["published_at"] = datetime.now().strftime("%Y-%m-%dT09:00:00+09:00")

    all_articles = update_articles_json(article_data)
    html_file = generate_static_html(article_data, all_articles=all_articles)
    refresh_existing_posts_seo(all_articles)
    update_home_and_insight_index(all_articles)
    update_sitemap(article_data["slug"], article_data["published_at"])
    update_llms_txt(article_data)
    update_sister_site_feeds(article_data)
    mark_topic_published(article_data["slug"], article_data["published_at"])
    print(f"Published static article successfully: {html_file}")


if __name__ == "__main__":
    main()
