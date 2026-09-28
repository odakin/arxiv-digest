# SESSION-archive — arxiv-digest

> 📦 SESSION.md から移した日付つき節 (grep 専用、 verbatim)。 現在地は SESSION.md。

## 2026-09-28 SESSION.md の日付つき節を verbatim MOVE (形の契約 = 案件ごとの現在地、 層1 claude-config/CONVENTIONS.md#session-no-durable-record、 道具 = migrate-session-shape.py)

### (from 残タスク) 2026-04-14 の onda 追加に付随

- [ ] **他マシン (学校 Mac 等) で `.env` 生成**: `research-collab` を clone + `git-crypt unlock` 後、`python3 -m tools.sync_mentions` 一発で `DISCORD_MENTION_*` が生成される (helper は 2026-04-14 で実装)。scheduled task がそこで走っている場合、env 未設定だと mention は無言スキップ (fail soft) になるので即時の不具合は出ないが、メンションが消える
- [ ] **新 subscriber への事前告知**: 明日 (2026-04-15) 朝 10:31 ごろから Discord `#arxiv-digest` で mention 付き配信が始まる。一言入れておくべき
- [x] **ogawa エントリの PII 補完** (2026-04-14 完了: name_en / name_ja / affiliation を collaborators.yaml に追加)
- [x] **arxiv-digest/CLAUDE.md の profile 表を更新** (2026-04-14 完了: onda 行追加、stale 表記修正、設計参照を明記)
- [x] **subscriber profile の PII redact (全 3 名)** (2026-04-14 完了: option iii 採用 → takeda/ogawa/onda の interest_profile.txt / SESSION.md / DESIGN.md から実名・所属・named collaborators を削除、詳細は research-collab に集約)
- [ ] **README.md / SKILL.md に `.env` の `DISCORD_MENTION_*` 項目を明示**: 新しいマシンでの setup 時に webhook と並んで用意すべき env var であることを記載


### (from 残タスク) 派生 (2026-04-14 redact の副作用)

- [ ] **odakin の主な共同研究者 5 名を `research-collab/collaborators.yaml` に stub 登録**。現状 public profile の「see private registry」が実体を指していない。名前の具体は local backup branch (下記) にのみ残存する pre-redact 版を参照。1 名について漢字表記ゆれが既存 `ogawa` エントリと類似しており別人/同一人物か要確認
- [ ] **orphan 監視**: 2026-04-14 に public repo の history を force-push で rewrite した。残る orphan 状態のノード (詳細 SHA はここに書かない) を GitHub が自然 GC するまでは SHA 直アクセスで旧内容取得可能。1 ヶ月後に origin での 404 化を確認。監視対象 SHA は local backup branch (下記) の `rev-parse HEAD~n` で復元可能
- [ ] **local backup branch 削除**: pre-rewrite history を保持するローカルブランチがある (push 済みでない)。上記 orphan 監視完了後に削除

## 2026-09-28 SESSION.md の日付つき節を verbatim MOVE (形の契約 = 案件ごとの現在地、 層1 claude-config/CONVENTIONS.md#session-no-durable-record、 道具 = migrate-session-shape.py)

## 2026-09-15 — 推薦文に人名を書かない + archive commit と公開 gate

- archive は公開 repo に commit される。 推薦文 (reason / summary) に購読者・共同研究者の名前が入っていたので除去し、
  生成の指示 (`skill/SKILL.md` / `src/scorer.py`) に「人名を書かない」 を追加。 判断 = `DESIGN.md` 同日節
- 公開 gate は arXiv の書誌 (著者・題名・要旨) を構造で対象外にした (claude-config
  `conventions/confidential-repo-boundary.md#published-metadata-is-public`)。 以前は共著者の論文や自分の論文が載った日に
  archive の自動 commit が必ず止まる状態だった
- 手元の定期検査が直近 14 日の archive commit を今の gate に通す (claude-config `scripts/replay-public-gate.sh`)


## 2026-09-09 — Mode A (GitHub Actions) を repo レベルで disable

Mode A の cron (`30 1 * * 1-5` UTC = **JST 10:30**) が Mode B のローカル routine と**同時刻**に
組まれたまま生きていた (= 2026-06-29 の二重配信と同じ配線)。 最近二重にならなかったのは
Actions が投稿の手前で落ちていたからで (`BadRequestError: credit balance is too low` = Anthropic
API のクレジット切れ、 09-04/07/08 と 3 連続 failure)、 **偶然による無害化**にすぎなかった
(= API に入金した瞬間に再発する時限爆弾)。

- `gh workflow disable` で **repo レベルで停止** (state = `disabled_manually`)。
  ⚠️ file は消していない — 本 repo は GitHub Template なので、 template 利用者には
  Mode A が必要。 `digest.yml` の header に「Mode A と Mode B を両方 schedule すると
  二重配信になる。 どちらか一方にせよ」 の注記を追加。
- 再開するなら Actions 画面の Enable。 ただし Mode B を止めるのが先。
- 併せて `CLAUDE.md §Mastodon トークン更新手順` を**プライベートウィンドウ方式**に改訂
  (= 旧手順の「ログアウト → 再ログイン」 は、 サイドバーのログアウトが rails-ujs の JS 経由
  DELETE ゆえ Brave のシールドで**無反応**になり実際に詰まった)。 反映は
  `odakin-prefs/scripts/rotate-mastodon-token.sh` が `.env` / Dropbox backup / GitHub Secret /
  旧 token 失効確認まで自動でやる (値は端末にも AI の context にも出さない)。


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
