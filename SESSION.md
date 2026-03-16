# arxiv-digest Session

## 現在の状態
**作業中**: 設計第3版完了 → コミット待ち

### タスク進捗
- [x] リポ作成（public: odakin/arxiv-digest）
- [x] CLAUDE.md 初版作成
- [x] 設計レビュー（6つの矛盾を発見・修正）
- [x] 設計第3版: モード B（ローカル Claude Code）を一級市民に格上げ ← **完了**
- [ ] コミット＆push
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
1. 修正した CLAUDE.md をコミット＆push
2. physics-research の `fetch_arxiv.py` を移植
3. `src/config.py` を新規作成（config.yaml 読み込み）
4. Channel 基底クラスと Mastodon アダプタを実装

## 直近の決定事項
- 2026-03-16: プロジェクト開始
- 2026-03-16: Pro Max OAuth は GitHub Actions で使用不可と判明
- 2026-03-16: **モード A（Actions + API）とモード B（ローカル Claude Code）の両方を一級市民として実装**
- 2026-03-16: **odakin 自身がこのリポで日常運用する**。physics-research の arxiv_digest はこちらに統合・移行
- 2026-03-16: odakin のスコアリング設定・プロファイルは公開のまま維持（実例として他ユーザーの参考にもなる）
- 2026-03-16: config.yaml はコミット対象（機密情報なし）
- 2026-03-16: interest_profile.txt を正本としてコミット
- 2026-03-16: スコアリングは長めに生成、各チャンネルがトリム

## 設計変遷
1. 初版: Pro Max で Actions 無料前提 → 6つの矛盾発見
2. 第2版: API 直接呼び出しに一本化、ローカルは「将来」扱い
3. 第3版: **ローカル Claude Code を一級市民に格上げ**。開発者自身が使うことで持続的メンテを保証

## 作業ログ
### 2026-03-16
- リポ作成: odakin/arxiv-digest (public)
- CLAUDE.md 初版 → 設計レビュー → 第2版 → 第3版
- 設計の根本方針を確立: 自分が使い続けるオープンソースプロジェクト
