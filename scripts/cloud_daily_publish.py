#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Daily Publisher for GitHub Actions (Runs in the cloud even when Mac is closed/off).
Picks the next pending topic from insight/data/topic_queue.json, loads its vetted draft from
insight/drafts/<id>.json (or builds a compliant structured article), and invokes publish_article.py.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_JSON_PATH = os.path.join(BASE_DIR, "insight", "data", "articles.json")
TOPIC_QUEUE_PATH = os.path.join(BASE_DIR, "insight", "data", "topic_queue.json")
DRAFTS_DIR = os.path.join(BASE_DIR, "insight", "drafts")
PUBLISH_SCRIPT = os.path.join(BASE_DIR, "scripts", "publish_article.py")


def build_fallback_article(topic, published_at):
    """Fallback structured generator if a future topic in topic_queue.json has no file in insight/drafts/."""
    title = topic["title"]
    category = topic.get("category", "選挙")
    primary_product = topic.get("primary_product", "PoliSide")
    aeo_q = topic.get("aeo_question", f"{title}のポイントは何ですか？")

    lead = f"{title}について、公職選挙法・政治資金規正法を厳格に遵守しながら若手候補者・地方議員が実践できる具体的なステップと、PoliSide・PoliDash・PoliStepの活用法をわかりやすく解説します。適法な政治活動のため選管への政治団体届出を最小限（代表・会計の2名）で済ませ、理念が整ったら即座に駅頭や個別訪問（地域対話）へ動き出す実践論を整理しました。"
    tldr = f"{aeo_q}に対する結論として、適法な政治活動のため選管へ政治団体届出を最小限で済ませ、大掛かりな後援会組織づくりに消耗せず理念が固まり次第すぐに駅頭や地域回り（個別対話・PoliStep）へ動くこと、告示日オペレーションを自動化すること（PoliDash）、公式HPで信頼の受け皿を整えること（PoliSide）が最も効果的です。"
    polidash_note = f"【{category}実践解説】{title[:32]}の要点と陣営オペレーション効率化の手順。"
    polistep_note = f"【{category}実践解説】{title[:32]}と日々のフィールド活動への活かし方。"

    content_html = f"""
<p>{aeo_q}——初めての選挙準備や日々の議員活動において、多くの方がこのテーマで悩まれます。本記事では、公職選挙法・政治資金規正法のルールを厳格に守りながら着実に成果を出すための実践ステップを整理します。</p>
<h2>1. 基本の考え方と優先順位の整理</h2>
<p>限られた時間と人員で最大の成果を出すためには、やるべき作業を「現場での地域対話」「情報発信の基盤づくり」「現場オペレーションの省力化」の3つに分けて進めることが重要です。</p>
<p>特に重要なのは、<strong>適法に政治活動を行うため、都道府県選管への「政治団体の設立届出」は法律上必須である</strong>ということです。ただし、大掛かりな役員会やしがらみのある「昔ながらの後援会組織」を作る必要はありません。代表者と会計責任者の実質2名で迅速に届出を済ませ、自身の理念が整ったら即座に駅頭や個別訪問（日常の政治活動としての対話・意見交換・討議資料配布）を開始することが何よりも大切です。</p>
<table>
  <thead>
    <tr>
      <th>領域</th>
      <th>具体的な取り組み</th>
      <th>活用できるツール・サポート</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>フィールド活動の可視化</strong></td>
      <td>政治団体届出と理念が整ったら即駅頭＆個別対話へ。目標日からの逆算ノルマ設計と地図記録</td>
      <td><strong>PoliStep（ポリステップ）</strong></td>
    </tr>
    <tr>
      <td><strong>ポスター・ルート管理</strong></td>
      <td>掲示板リストの一括ピン登録とAI最適ルート生成・URL共有</td>
      <td><strong>PoliDash（ポリダッシュ）</strong></td>
    </tr>
    <tr>
      <td><strong>公式HP・思考の整理</strong></td>
      <td>有権者に信頼される公式ホームページ構築と月1回の伴走相談</td>
      <td><strong>PoliSide（ポリサイド）</strong></td>
    </tr>
  </tbody>
</table>
<h2>2. 公職選挙法を遵守した安全な実践ステップ</h2>
<ul>
  <li><strong>政治団体の届出と適法な活動</strong>：平時に政策チラシ（討議資料）を発行・配布するには、選管へ届け出た政治団体名義で行う必要があります。</li>
  <li><strong>政治活動と選挙運動の明確な区別</strong>：告示日前の投票依頼（事前運動）や投票依頼目的の戸別訪問、寄附行為などは厳しく制限されています。平時は政策の普及や地域課題のヒアリングに徹しましょう。</li>
  <li><strong>デジタルツールによる業務の標準化</strong>：少人数のチームでも情報共有の抜け漏れが起きないよう、<a href="https://polistep.jp" target="_blank" rel="noopener">PoliStep</a>や<a href="https://polidash.jp" target="_blank" rel="noopener">PoliDash</a>、そして<a href="https://poliside.net" target="_blank" rel="noopener">PoliSide</a>を組み合わせて運用しましょう。</li>
</ul>
"""
    faqs = [
      {
        "q": aeo_q,
        "a": tldr
      },
      {
        "q": "ツールを導入する際、スタッフ全員のアカウント登録は必要ですか？",
        "a": "PoliDashおよびPoliStepは、管理者が発行した専用URLをLINE等で共有するだけで、ボランティアスタッフはログイン不要でマップや進捗共有を利用できます。"
      },
      {
        "q": "具体的な法令上の注意点はどこに確認すればよいですか？",
        "a": "自治体や選挙の種類によって運用や届出要件が異なる場合がありますので、必ず事前に管轄の選挙管理委員会へご確認ください。"
      }
    ]

    return {
        "id": topic["id"],
        "slug": topic["slug"],
        "title": title,
        "category": category,
        "lead": lead,
        "tldr": tldr,
        "polidash_note": polidash_note,
        "polistep_note": polistep_note,
        "primary_product": primary_product,
        "target_keywords": topic.get("target_keywords", ["地方選挙", "PoliSide", "PoliDash", "PoliStep"]),
        "thumbnail": topic.get("thumbnail", "/images/insight/political_mindset.jpg"),
        "published_at": published_at,
        "content_html": content_html,
        "faqs": faqs,
    }


def main():
    now_jst = datetime.now(JST)
    today_str = now_jst.strftime("%Y-%m-%d")
    published_at = f"{today_str}T09:00:00+09:00"

    # 1. Check if today's article is already published (prevents duplicate run on same day)
    if os.path.exists(ARTICLES_JSON_PATH):
        with open(ARTICLES_JSON_PATH, "r", encoding="utf-8") as f:
            articles = json.load(f)
        for art in articles:
            if art.get("published_at", "")[:10] == today_str:
                print(f"[INFO] Article for {today_str} already published ({art.get('slug')}). Nothing to do.")
                return

    # 2. Find first pending topic in topic_queue.json
    if not os.path.exists(TOPIC_QUEUE_PATH):
        print("[ERROR] topic_queue.json not found.")
        sys.exit(1)

    with open(TOPIC_QUEUE_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)

    next_topic = None
    for item in queue:
        if item.get("status") == "pending":
            next_topic = item
            break

    if not next_topic:
        print("[INFO] No pending topics remaining in topic_queue.json.")
        return

    topic_id = next_topic["id"]
    draft_path = os.path.join(DRAFTS_DIR, f"{topic_id}.json")

    if os.path.exists(draft_path):
        print(f"[INFO] Loading pre-vetted draft: {draft_path}")
        with open(draft_path, "r", encoding="utf-8") as f:
            article_data = json.load(f)
        article_data["published_at"] = published_at
    else:
        print(f"[INFO] Building structured article for {topic_id}")
        article_data = build_fallback_article(next_topic, published_at)

    tmp_json = "/tmp/cloud_daily_article.json"
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)

    subprocess.run([sys.executable, PUBLISH_SCRIPT, tmp_json], check=True)
    print(f"[SUCCESS] Published {topic_id} ({article_data['slug']}) for {today_str}")


if __name__ == "__main__":
    main()
