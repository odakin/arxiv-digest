# arxiv-digest Session

> 📌 SESSION.md = 案件ごとの現在地 + 正本への link (進んだら置き換える、 日付を見出しにした節・commit hash・messageId を置かない = 層1 claude-config/CONVENTIONS.md#session-no-durable-record)。 日付つきの節は SESSION-archive.md へ verbatim MOVE 済 (2026-09-28)。

## 現在の状態
**安定運用中**: Mode B（ローカル scheduled task）で平日朝に自動配信

## 要対応（学校 Mac で pull 後）

- [x] **`arxiv-digest` の backend prompt を SKILL.md と同期する**（2026-04-02 完了: `update_scheduled_task` で prompt を再設定）

## 残タスク

### 継続タスク

- [ ] Bluesky / Slack チャンネル追加
- [ ] ogawa の正しい INSPIRE BAI を確認・登録 (2026-04-14 に homonym 由来の誤 BAI を除去。実 subscriber に BAI があれば `tools/setup_inspire.py` を再実行、無ければ `inspire_id: null` のまま継続)
  - ⚠️ **2026-07-01 追記 (inspire-monthly 実行時の landmine)**: `skill/inspire-monthly/SKILL.md` Step 2 が ogawa に `N.Ogawa.4` を指定するが、これは複数の同名著者が混在した INSPIRE クラスタで、大半が subscriber の登録興味 (config.yaml: quant-ph/hep-th/gr-qc) と無関係な実験系分野の論文。`setup_inspire N.Ogawa.4 --profile ogawa` を走らせると `inspire_arxiv_categories` が実験系で汚染され digest の scoring を歪める。**当月次実行 (2026-07-01) では ogawa をスキップ**、BAI は 2026-04-14 以降の cleared 状態を維持 (ogawa は現在 inspire_profile.txt を持たず interest_profile.txt + config のみで正常運用)。**要対応: SKILL.md Step 2 の ogawa 行を削除するか、clean な BAI を確定するまで無効化する** (SKILL.md 編集後は `update_scheduled_task` で prompt 同期が必要)。

### 完了 (詳細は DESIGN.md / git log)

- **2026-05-28** (整備 sweep): claude-config CONVENTIONS 準拠の repo hygiene 整備 — (1) `LICENSE` 追加 (MIT、 README の claim と GitHub `licenseInfo: null` の drift 解消)、 (2) `.github/workflows/semgrep.yml` 追加 (security-automation baseline、 odakin-prefs/scripts/templates/ から copy)、 (3) `digest.yml` workflow に `EMAIL_*` secret 6 件追加 (email channel の GitHub Actions 経路完成)、 (4) `docs/setup-guide.md` に「Email Channel Setup」 section + Step 4 secrets table 拡張、 (5) `README.md` を CONVENTIONS §README流儀 準拠で trim + `README.ja.md` 新規分離 (英日混在 single-file → 言語別 file、 245→ ~70 行)、 (6) `DESIGN.md` に 2 entries 追加 (Email channel 採用根拠 + 4 案 vs 検討 / Personal profiles layer-3 移設の 4 案 vs 検討)、 (7) local `.git/hooks/pre-commit.bak` 除去。 4 軸 sweep clean
- **2026-05-28** (`90ebd13`): maintainer の personal profile 4 件 (`odakin` / `takeda` / `ogawa` / `onda`) を public template から layer 3 (`odakin-prefs/arxiv-digest-profiles/`) に移設、 public 側は gitignored relative symlink で参照。 PR #3 (山岡さん) を契機に、 「template 利用者が pull すると 4 profile を `fetch_all` / `post_all` が iteration → 山岡さんの env で channel init が全部 raise + 無関係 categories で API budget 浪費」 を発覚 → 修復。 fresh-clone 検証で `list_active_profiles()` が空配列 (= 早期 return) になることを確認。 maintainer 側 runtime は symlink 経由で全 profile 認識継続。 ペア commit: `odakin-prefs@9e818d2` (profile dirs + layer-3 rationale README)
- **2026-05-28** (`3bae379`): email delivery channel 追加 (PR #3、 tyamaoka24 さんから、 SMTP/STARTTLS、 HTML + plain-text multipart、 score-badge 色分け)。 maintainer 側 polish (= `c8d56e2`) で (1) Subject の RFC 2047 encoding (= Outlook/Thunderbird での mojibake 防止)、 (2) `EMAIL_TO` の comma-separated multi-recipient 対応 (`email.utils.getaddresses` で display name 内 comma も正しく parse)、 (3) docstring の precedence 修正 (config > env > default)。 8 件 parsing test + Subject RFC 2047 round-trip 検証済。 4 軸 sweep clean
- 2026-04-14: onda プロファイル追加 + Discord mention ID の layer 3 委譲 (設計は DESIGN.md「Discord mention ID を collaborator layer に委譲」セクション)
- 2026-04-14: homonym 由来の誤 INSPIRE データ除去 (ogawa)
- 2026-04-08: archive/ 自動 commit + push 実装 (設計は DESIGN.md)
- 2026-03-31: ogawa プロファイル追加、arxiv_categories 二層構造、scheduled task 統合

## 過去の修正 (詳細は git log)

- **2026-03-31** (`65e7ffe`): ogawa プロファイル追加 + `arxiv_categories` 二層構造 (`inspire_arxiv_categories` 自動 + `arxiv_categories` 手動 union) + `setup_inspire` の対話改善 (BAI 確認、`lookup_author`)。
- **2026-03-30** (`685d2f0`, `819ec81`): Mode B 統合パイプライン (`fetch_all` → スコアリング → `post_all`)、Discord `mention_target` バグ修正、`SKILL-takeda.md` 削除。
- **2026-03-24**: takeda プロファイル追加 (修論:波束形式量子干渉)、マルチプロファイル state ファイル分離、SKILL.md → リポ symlink 化 + バックエンド sync ルール明文化。
