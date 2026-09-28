# TODO — arxiv-digest

未完了の作業の台帳 (maintainer 用)。 済んだ項目は消す (経緯は git log、 設計は DESIGN.md)。 SESSION.md は現在地とこの file への link だけを持つ。

## 要対応

定期実行 (`skill/SKILL.md` のステップ0) がダイジェストの前に読む節。 配信の前に確かめる項目だけを置く。

- [ ] 二重実行インシデント = 二重実行の停止 / 将来課題: post 時の message ID 捕捉 → [SESSION-archive.md](SESSION-archive.md#double-execution-incident) の「要対応」 の節 (本文と経緯は archive の節のまま)

## 継続タスク

定期実行は読まない。

- [ ] Bluesky / Slack チャンネル追加
- [ ] ogawa の正しい INSPIRE BAI を確認・登録 (2026-04-14 に homonym 由来の誤 BAI を除去。実 subscriber に BAI があれば `tools/setup_inspire.py` を再実行、無ければ `inspire_id: null` のまま継続)
  - ⚠️ **2026-07-01 追記 (inspire-monthly 実行時の landmine)**: `skill/inspire-monthly/SKILL.md` Step 2 が ogawa に `N.Ogawa.4` を指定するが、これは複数の同名著者が混在した INSPIRE クラスタで、大半が subscriber の登録興味 (config.yaml: quant-ph/hep-th/gr-qc) と無関係な実験系分野の論文。`setup_inspire N.Ogawa.4 --profile ogawa` を走らせると `inspire_arxiv_categories` が実験系で汚染され digest の scoring を歪める。**当月次実行 (2026-07-01) では ogawa をスキップ**、BAI は 2026-04-14 以降の cleared 状態を維持 (ogawa は現在 inspire_profile.txt を持たず interest_profile.txt + config のみで正常運用)。**要対応: SKILL.md Step 2 の ogawa 行を削除するか、clean な BAI を確定するまで無効化する** (SKILL.md 編集後は `update_scheduled_task` で prompt 同期が必要)。

- [ ] 一括 MOVE で SESSION-archive.md へ行った未完了の項目 (本文と経緯は archive の節のまま):
  - onda 追加に付随 = 他マシン (学校 Mac 等) で `.env` 生成 / 新 subscriber への事前告知 / README.md / SKILL.md に `.env` の `DISCORD_MENTION_*` 項目を明示 → [節](SESSION-archive.md#from-残タスク-2026-04-14-の-onda-追加に付随)
  - redact の副作用 = 共同研究者の stub 登録 / orphan 監視 / local backup branch 削除 → [節](SESSION-archive.md#from-残タスク-派生-2026-04-14-redact-の副作用)
