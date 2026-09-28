# arxiv-digest Session

> 📌 SESSION.md = 案件ごとの現在地 + 正本への link (進んだら置き換える、 日付を見出しにした節・commit hash・messageId を置かない = 層1 claude-config/CONVENTIONS.md#session-no-durable-record)。 日付つきの節は SESSION-archive.md へ verbatim MOVE 済 (2026-09-28)。

## 現在の状態
**安定運用中**: Mode B（ローカル scheduled task）で平日朝に自動配信

## 残タスク

### 継続タスク

- [ ] Bluesky / Slack チャンネル追加
- [ ] ogawa の正しい INSPIRE BAI を確認・登録 (2026-04-14 に homonym 由来の誤 BAI を除去。実 subscriber に BAI があれば `tools/setup_inspire.py` を再実行、無ければ `inspire_id: null` のまま継続)
  - ⚠️ **2026-07-01 追記 (inspire-monthly 実行時の landmine)**: `skill/inspire-monthly/SKILL.md` Step 2 が ogawa に `N.Ogawa.4` を指定するが、これは複数の同名著者が混在した INSPIRE クラスタで、大半が subscriber の登録興味 (config.yaml: quant-ph/hep-th/gr-qc) と無関係な実験系分野の論文。`setup_inspire N.Ogawa.4 --profile ogawa` を走らせると `inspire_arxiv_categories` が実験系で汚染され digest の scoring を歪める。**当月次実行 (2026-07-01) では ogawa をスキップ**、BAI は 2026-04-14 以降の cleared 状態を維持 (ogawa は現在 inspire_profile.txt を持たず interest_profile.txt + config のみで正常運用)。**要対応: SKILL.md Step 2 の ogawa 行を削除するか、clean な BAI を確定するまで無効化する** (SKILL.md 編集後は `update_scheduled_task` で prompt 同期が必要)。

### 完了・過去の修正

記録 (旧「要対応（学校 Mac で pull 後）」「完了」「過去の修正」 の節) = [SESSION-archive.md](SESSION-archive.md)。 設計は DESIGN.md、 変更は git log。
