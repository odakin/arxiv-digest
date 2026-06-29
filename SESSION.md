# arxiv-digest Session

## 現在の状態
**安定運用中**: Mode B（ローカル scheduled task）で平日朝に自動配信

## ⚠️ 要対応 (2026-06-29 二重実行インシデント)

2026-06-29、本番ホストが朝 10:31 にダイジェストを配信・commit（`24c4a1e`）した後、**別マシンの arxiv-digest routine が failover gate 無しのまま再実行**し、同日のダイジェストを**チャンネルへ二重配信**した（odakin Mastodon 3 toots / onda Discord 5 msgs / takeda Discord 2 msgs を重複、ogawa は両 run とも 0 件）。再実行側はローカルの重複 6/29 archive を破棄し canonical（`24c4a1e`）へ ff-pull 同期して git 状態は復旧済み。

- [ ] **二重実行の停止** (auto-wire 配備済、MacBook 次回 Claude session で完了): 直接因 = 旧 `--ensure` semantics は「未 install の routine だけ install」 で **既存 plist は触らない** ゆえ 2026-06-26 layer1-hoist 以前から arxiv-digest を入れてた MacBook 等で gate-less 旧 plist が居座っていた。 修復は 3 層 defense:
  - **層 0 (本番ホスト維持)**: user 方針「iMac canonical のまま配信続行」 (= `routine-host-ledger.py --claim` 切替不要)
  - **層 3 ホットフィックス (odakin-prefs)**: `hooks/session-start-arxiv-gate-hotfix.sh` を SessionStart に配線。 hostname≠iMac-3 + marker `~/.cache/claude-arxiv-gate-hotfix-20260629.done` 不在で `--install-one arxiv-digest` を自動再走 → gate 付き plist 焼直 + surface 通知。 非 canonical マシン (= MacBook 等) は次回 Claude session 開始で 1 回だけ自動 fire。 iMac は silent no-op
  - **層 1 補強 (arxiv-digest)**: `src/archive.py::already_posted_on_origin()` + `src/post_all.py main()` 入口で **origin/main に今日の archive が既に push されてたら post 全 skip** (= 2 段目防御、 gate が万一 stale でも post 前に git レベルで abort、 race window ~tens of seconds、 失敗時 fail-open)
  - 完了条件 = MacBook 次回 session で hotfix fire + marker touch + 翌平日 10:30 cron で gate skip 確認、 その後本 entry を `[x]` + hotfix hook を retire 候補化 (= 全非 canonical マシンに marker が落ちた段階で hook 削除可能)
- [x] **二重投稿の扱い**: **放置確定** (2026-06-29 user 判断「面倒くさいから残そう」)。実測: odakin Mastodon 6/29 = 7 toots in 3 runs (01:19 UTC = 2 toots / 01:38 UTC = 3 + 2 toots、 run B は LLM が Stochastic GW 1 件を追加で拾った)。Discord は webhook post-only で API delete 不可、手動削除も省略。post 時の message ID 捕捉は未実装（下記「将来課題」参照）
- [ ] **将来課題: post 時の message ID 捕捉**: `src/post_all.py` / 各 channel adapter (`mastodon.py` / `discord.py`) は post 時に返却される status ID / message ID を archive に保存していない。保存すれば再発時に自動削除可能。`archive/{date}_{profile}.json` の各 paper entry に `posted_ids: {mastodon: <status_id>, discord: <message_id>}` 等を追記し、Mastodon は `DELETE /api/v1/statuses/<id>`、Discord は **bot 化が必要** (webhook では削除不可、本格採用なら Discord Bot Token 移行)
- [x] **archive 自動 commit のブロック解消** (2026-06-29 完了): matcher の word-boundary 化を claude-config `6aba86d` で land。 `public-precommit-runner.sh` Tier B + `commit-msg-leak-matcher.sh` literal の両方で sensitive-terms.txt を ASCII / 非 ASCII に分割し、 ASCII term は `grep -wFf` (word-boundary)、 非 ASCII (CJK) は `grep -Ff` (substring) で分岐。 ASCII 短 token の英文中 substring FP class を構造的に消す + 日本語 term の substring 検出は維持。 test 63/63 PASS (= 既存 27 + 新 25 + 新 11)。 積み残しの 2026-06-24 / 06-25 archive 8 file は `2792a2f` で catch-up commit + push 済。 詳細 RCA: `~/Claude/odakin-prefs/plans/2026-06-29-archive-leak-wordbound-results.md`

### 配信中プロファイル
| プロファイル | チャンネル | スケジュール |
|------------|-----------|------------|
| odakin | Mastodon (Vivaldi Social) | 平日 10:31 |
| takeda | Discord (#arxiv-digest) | 平日 10:31（同時） |
| ogawa | Discord (#arxiv-digest) | 平日 10:31（同時） |
| onda | Discord (#arxiv-digest) | 平日 10:31（同時、2026-04-14 追加） |

## 要対応（学校 Mac で pull 後）

- [x] **`arxiv-digest` の backend prompt を SKILL.md と同期する**（2026-04-02 完了: `update_scheduled_task` で prompt を再設定）

## 残タスク

### 2026-04-14 の onda 追加に付随

- [ ] **他マシン (学校 Mac 等) で `.env` 生成**: `research-collab` を clone + `git-crypt unlock` 後、`python3 -m tools.sync_mentions` 一発で `DISCORD_MENTION_*` が生成される (helper は 2026-04-14 で実装)。scheduled task がそこで走っている場合、env 未設定だと mention は無言スキップ (fail soft) になるので即時の不具合は出ないが、メンションが消える
- [ ] **新 subscriber への事前告知**: 明日 (2026-04-15) 朝 10:31 ごろから Discord `#arxiv-digest` で mention 付き配信が始まる。一言入れておくべき
- [x] **ogawa エントリの PII 補完** (2026-04-14 完了: name_en / name_ja / affiliation を collaborators.yaml に追加)
- [x] **arxiv-digest/CLAUDE.md の profile 表を更新** (2026-04-14 完了: onda 行追加、stale 表記修正、設計参照を明記)
- [x] **subscriber profile の PII redact (全 3 名)** (2026-04-14 完了: option iii 採用 → takeda/ogawa/onda の interest_profile.txt / SESSION.md / DESIGN.md から実名・所属・named collaborators を削除、詳細は research-collab に集約)
- [ ] **README.md / SKILL.md に `.env` の `DISCORD_MENTION_*` 項目を明示**: 新しいマシンでの setup 時に webhook と並んで用意すべき env var であることを記載

### 継続タスク

- [ ] Bluesky / Slack チャンネル追加
- [ ] ogawa の正しい INSPIRE BAI を確認・登録 (2026-04-14 に homonym 由来の誤 BAI を除去。実 subscriber に BAI があれば `tools/setup_inspire.py` を再実行、無ければ `inspire_id: null` のまま継続)

### 派生 (2026-04-14 redact の副作用)

- [ ] **odakin の主な共同研究者 5 名を `research-collab/collaborators.yaml` に stub 登録**。現状 public profile の「see private registry」が実体を指していない。名前の具体は local backup branch (下記) にのみ残存する pre-redact 版を参照。1 名について漢字表記ゆれが既存 `ogawa` エントリと類似しており別人/同一人物か要確認
- [ ] **orphan 監視**: 2026-04-14 に public repo の history を force-push で rewrite した。残る orphan 状態のノード (詳細 SHA はここに書かない) を GitHub が自然 GC するまでは SHA 直アクセスで旧内容取得可能。1 ヶ月後に origin での 404 化を確認。監視対象 SHA は local backup branch (下記) の `rev-parse HEAD~n` で復元可能
- [ ] **local backup branch 削除**: pre-rewrite history を保持するローカルブランチがある (push 済みでない)。上記 orphan 監視完了後に削除

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
