#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PoliSide × PoliDash × PoliStep SEO/AEO Static Article Publisher
Generates static HTML with Triple JSON-LD (Article, FAQPage, BreadcrumbList + SoftwareApplication mentions),
updates articles.json, sitemap.xml, llms.txt, and topic_queue.json.
"""

import json
import os
import re
import sys
from datetime import datetime

BASE_DIR = "/Users/takanoyousuke/poliside-net"
POSTS_DIR = os.path.join(BASE_DIR, "insight", "posts")
ARTICLES_JSON_PATH = os.path.join(BASE_DIR, "insight", "data", "articles.json")
TOPIC_QUEUE_PATH = os.path.join(BASE_DIR, "insight", "data", "topic_queue.json")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
LLMS_TXT_PATH = os.path.join(BASE_DIR, "llms.txt")


def format_jp_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except Exception:
        return date_str[:10]


def build_product_spotlight_html(primary_product):
    if primary_product == "PoliStep":
        return """
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%); border: 2px solid #0EA5E9; box-shadow: 0 10px 28px rgba(14, 165, 233, 0.08);">
          <div style="display:inline-block; background:#0EA5E9; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">立候補準備・進行支援アプリ</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">やるべきことが一目でわかる「PoliStep（ポリステップ）」</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            「何からどの順番で準備すればいいか分からない」という新人候補者のために開発された、ステップバイステップの政治活動進行支援アプリです。立候補決意から告示日までの全タスクを迷わず管理できます。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="https://polistep.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#0EA5E9; color:#fff; padding:12px 24px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.95rem;">
              <i class="fas fa-shoe-prints"></i> PoliStep 公式サイトを見る
            </a>
            <a href="https://polidash.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem;">
              <i class="fas fa-chart-line" style="color:#F97316;"></i> 陣営管理なら PoliDash
            </a>
          </div>
        </div>
        """
    elif primary_product == "PoliDash":
        return """
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #FFF7ED 0%, #FFFBEB 100%); border: 2px solid #F97316; box-shadow: 0 10px 28px rgba(249, 115, 22, 0.08);">
          <div style="display:inline-block; background:#F97316; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">選挙陣営向け高機能ダッシュボード</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">陣営タスクとボランティアを一元化する「PoliDash（ポリダッシュ）」</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            バラバラになりがちなExcelファイルやLINE連絡を卒業し、選挙陣営のタスク進捗・ボランティアシフト・重要共有事項をひとつの画面に集約。少人数陣営でもプロ並みのオペレーションを実現します。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="https://polidash.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#F97316; color:#fff; padding:12px 24px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.95rem;">
              <i class="fas fa-chart-line"></i> PoliDash 公式サイトを見る
            </a>
            <a href="https://polistep.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 20px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.9rem;">
              <i class="fas fa-shoe-prints" style="color:#0EA5E9;"></i> 準備手順なら PoliStep
            </a>
          </div>
        </div>
        """
    else:
        return """
        <div class="ecosystem-spotlight" style="margin: 48px 0; padding: 32px; border-radius: 20px; background: linear-gradient(135deg, #F8FAFC 0%, #FFF7ED 100%); border: 2px solid #F97316; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);">
          <div style="display:inline-block; background:#0F172A; color:#fff; font-size:0.78rem; font-weight:800; padding:4px 12px; border-radius:999px; margin-bottom:12px;">PoliSide エコシステム</div>
          <h3 style="margin-top:0; margin-bottom:12px; font-size:1.35rem; color:#0F172A;">HP作成・伴走相談からツール活用までトータルサポート</h3>
          <p style="margin-bottom:20px; color:#334155; font-size:0.98rem; line-height:1.75;">
            PoliSide（候補者HP作成＆月1回のオンライン伴走サポート）に加え、準備ステップ管理アプリ「PoliStep」、選挙陣営ダッシュボード「PoliDash」であなたの挑戦を全方位から支えます。
          </p>
          <div style="display:flex; flex-wrap:wrap; gap:12px;">
            <a href="https://poliside.net/#pricing" style="display:inline-flex; align-items:center; gap:8px; background:#F97316; color:#fff; padding:12px 22px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.92rem;">
              <i class="fas fa-handshake-angle"></i> PoliSideの伴走支援・料金を見る
            </a>
            <a href="https://polidash.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 18px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.88rem;">
              <i class="fas fa-chart-line" style="color:#F97316;"></i> PoliDash
            </a>
            <a href="https://polistep.jp" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:8px; background:#fff; color:#0F172A; border:1px solid #CBD5E1; padding:12px 18px; border-radius:999px; font-weight:700; text-decoration:none; font-size:0.88rem;">
              <i class="fas fa-shoe-prints" style="color:#0EA5E9;"></i> PoliStep
            </a>
          </div>
        </div>
        """


def generate_static_html(article_data):
    slug = article_data["slug"]
    title = article_data["title"]
    category = article_data.get("category", "選挙")
    lead = article_data["lead"]
    tldr = article_data.get("tldr", lead)
    content_html = article_data["content_html"]
    faqs = article_data.get("faqs", [])
    keywords = ", ".join(article_data.get("target_keywords", ["地方選挙", "若手候補者", "PoliSide", "PoliDash", "PoliStep"]))
    published_at = article_data.get("published_at", datetime.now().strftime("%Y-%m-%dT09:00:00+09:00"))
    date_jp = format_jp_date(published_at)
    primary_product = article_data.get("primary_product", "PoliSide")
    thumb_path = article_data.get("thumbnail", "/images/insight/political_mindset.jpg")
    if thumb_path.startswith("/"):
        rel_thumb = "../.." + thumb_path
        abs_thumb = "https://poliside.net" + thumb_path
    else:
        rel_thumb = thumb_path
        abs_thumb = "https://poliside.net/ogp.jpg"

    page_url = f"https://poliside.net/insight/posts/{slug}.html"

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
                "description": "選挙陣営向けの高機能ダッシュボード。ボランティア管理や日々のタスク進行を一元化"
            },
            {
                "@type": "SoftwareApplication",
                "name": "PoliStep（ポリステップ）",
                "url": "https://polistep.jp",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "description": "政治活動のステップバイステップ進行支援アプリ。立候補準備でやるべきことが明確になるロードマップツール"
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
            {"@type": "ListItem", "position": 2, "name": "政治活動ノウハウ記事", "item": "https://poliside.net/insight/index.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url}
        ]
    }

    spotlight_html = build_product_spotlight_html(primary_product)

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
  <link rel="stylesheet" href="../../css/style.css">
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
        <a href="https://lin.ee/en5smI7" onclick="if(typeof gtag==='function'){{gtag('event', 'add_line', {{ 'event_category': 'conversion' }});}}" target="_blank" rel="noopener" class="nav__link nav__link--cta">
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
      <img src="{rel_thumb}" alt="{title}" style="width:100%; max-height:420px; object-fit:cover; border-radius:16px; margin-bottom:36px; box-shadow:0 8px 24px rgba(15,23,42,0.06);">

      <!-- AEO Direct Answer / TL;DR Box -->
      <div class="tldr-box">
        <div class="tldr-box__label"><i class="fas fa-lightbulb"></i> この記事の結論・要点（30秒でわかる要約）</div>
        <p style="margin-bottom:0; color:#0F172A; font-weight:500; line-height:1.75;">{tldr}</p>
      </div>

      {content_html}

      {spotlight_html}

      {faq_section_html}
    </article>

    <!-- 記事読了後のCTA導線 -->
    <div class="article-cta-banner" style="max-width:760px; margin:48px auto; padding:36px 28px; background:#0F172A; color:#fff; border-radius:24px; text-align:center;">
      <h3 style="color:#fff; font-size:1.4rem; margin-bottom:12px;">まずは、ひとりで抱えないことから。</h3>
      <p style="color:#CBD5E1; font-size:0.98rem; line-height:1.8; margin-bottom:24px;">
        PoliSideは、若手候補者・若手議員の「隣に立つ」伴走型サポートです。<br>
        選挙準備のステップ整理（<a href="https://polistep.jp" target="_blank" rel="noopener" style="color:#38BDF8; text-decoration:underline;">PoliStep</a>）・陣営タスク管理（<a href="https://polidash.jp" target="_blank" rel="noopener" style="color:#FB923C; text-decoration:underline;">PoliDash</a>）・HP作成まで、初回60分無料でご相談いただけます。
      </p>
      <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:14px;">
        <a href="https://lin.ee/en5smI7" onclick="if(typeof gtag==='function'){{gtag('event', 'add_line', {{ 'event_category': 'conversion' }});}}" target="_blank" rel="noopener" class="cta-btn">
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
          <a href="https://polidash.jp" target="_blank" rel="noopener" class="footer__link">PoliDash（陣営管理）</a>
          <a href="https://polistep.jp" target="_blank" rel="noopener" class="footer__link">PoliStep（準備支援）</a>
          <a href="https://lin.ee/en5smI7" target="_blank" rel="noopener" class="footer__link">LINE相談</a>
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

  <script src="../../js/main.js"></script>
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
    articles = [a for a in articles if a.get("slug") != slug]
    entry = {
        "id": article_data.get("id", slug),
        "title": article_data["title"],
        "slug": slug,
        "category": article_data.get("category", "選挙"),
        "lead": article_data["lead"],
        "published_at": article_data.get("published_at", datetime.now().strftime("%Y-%m-%dT09:00:00+09:00")),
        "thumbnail": article_data.get("thumbnail", "/images/insight/political_mindset.jpg"),
        "static_url": f"/insight/posts/{slug}.html",
        "primary_product": article_data.get("primary_product", "PoliSide"),
        "published": True
    }
    articles.insert(0, entry)
    with open(ARTICLES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def update_sitemap(slug, published_at):
    if not os.path.exists(SITEMAP_PATH):
        return
    with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
        xml = f.read()

    loc = f"https://poliside.net/insight/posts/{slug}.html"
    date_str = published_at[:10]
    if loc in xml:
        return

    new_entry = f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    xml = xml.replace("</urlset>", new_entry)
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(xml)


def update_llms_txt(article_data):
    if not os.path.exists(LLMS_TXT_PATH):
        return
    with open(LLMS_TXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    slug = article_data["slug"]
    title = article_data["title"]
    lead = article_data["lead"]
    url = f"https://poliside.net/insight/posts/{slug}.html"
    line = f"- [{title}]({url}): {lead}"

    if url in content:
        return

    marker = "<!-- ARTICLES_START -->"
    if marker in content:
        content = content.replace(marker, f"{marker}\n{line}")
        with open(LLMS_TXT_PATH, "w", encoding="utf-8") as f:
            f.write(content)


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
        print("Usage: python3 publish_article.py <article_json_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        article_data = json.load(f)

    if "published_at" not in article_data or not article_data["published_at"]:
        article_data["published_at"] = datetime.now().strftime("%Y-%m-%dT09:00:00+09:00")

    html_file = generate_static_html(article_data)
    update_articles_json(article_data)
    update_sitemap(article_data["slug"], article_data["published_at"])
    update_llms_txt(article_data)
    mark_topic_published(article_data["slug"], article_data["published_at"])
    print(f"Published static article successfully: {html_file}")


if __name__ == "__main__":
    main()
