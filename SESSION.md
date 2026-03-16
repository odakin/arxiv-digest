# arxiv-digest Session

## 現在の状態
**作業中**: 設計完了 → 最終精査＆push

### タスク進捗
- [x] リポ作成（public: odakin/arxiv-digest、Template 設定済み）
- [x] CLAUDE.md 設計指示書（3回の改訂を経て確定）
- [x] 最終精査（整合性・無矛盾性・効率性） ← **完了**
- [ ] physics-research から汎用コード移植
- [ ] config.yaml 作成（odakin の実設定）
- [ ] interest_profile.txt 作成（odakin の実プロファイル）
- [ ] Channel 基底クラス + Mastodon アダプタ実装
- [ ] scorer.py（Anthropic API スコアリング）実装
- [ ] main.py（モード A エントリポイント）実装
- [ ] fetch.py + post.py（モード B 用）実装
- [ ] skill/SKILL.md 作成
- [ ] GitHub Actions ワークフロー作成
- [ ] stdout チャンネル（テスト用）
- [ ] README.md（日英バイリンガル）
- [ ] セットアップガイド（docs/setup-guide.md）
- [ ] physics-research から arxiv_digest を削除・移行
- [ ] Bluesky / Discord / Slack チャンネル追加

## 次のステップ
1. physics-research の `fetch_arxiv.py` を移植
2. `src/config.py` を新規作成（config.yaml 読み込み）
3. Channel 基底クラスと Mastodon アダプタを実装

## 直近の決定事項
- 2026-03-16: プロジェクト開始
- 2026-03-16: Pro Max OAuth は GitHub Actions で使用不可と判明
- 2026-03-16: モード A（Actions + API）とモード B（ローカル Claude Code）の両方を一級市民として実装
- 2026-03-16: odakin 自身がこのリポで日常運用する（physics-research の arxiv_digest はこちらに統合・移行）
- 2026-03-16: odakin のスコアリング設定・プロファイルは常に public で公開し続ける
- 2026-03-16: 他ユーザーは GitHub Template から Private リポを作成可能（スコアリング設定を非公開にできる）
- 2026-03-16: config.yaml, interest_profile.txt はコミット対象。papers.yaml, state/ は .gitignore
- 2026-03-16: モード B のデータ受け渡し: fetch → state/today_papers.json → Claude スコアリング → state/scored_papers.json → post

## 設計変遷
1. 初版: Pro Max で Actions 無料前提 → 6つの矛盾発見
2. 第2版: API 直接呼び出しに一本化、ローカルは「将来」扱い
3. 第3版: ローカル Claude Code を一級市民に格上げ。開発者自身が使うことで持続的メンテを保証
4. 第4版: Template 方式で他ユーザーのプライバシー確保。最終精査で残存する不整合を修正

## 作業ログ
### 2026-03-16
- リポ作成: odakin/arxiv-digest (public, Template)
- CLAUDE.md: 初版 → 6矛盾修正 → モード B 格上げ → Template 方式 → 最終精査
