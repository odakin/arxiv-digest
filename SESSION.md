# arxiv-digest Session

## 現在の状態
**作業中**: 設計修正完了 → コミット待ち

### タスク進捗
- [x] リポ作成（public: odakin/arxiv-digest）
- [x] CLAUDE.md 初版作成
- [x] 設計レビュー（6つの矛盾を発見）
- [x] CLAUDE.md 修正版作成（全矛盾を解消） ← **完了**
- [ ] コミット＆push
- [ ] physics-research から汎用コード移植
- [ ] config.yaml 作成
- [ ] Channel 基底クラス + Mastodon アダプタ実装
- [ ] scorer.py（Anthropic API スコアリング）実装
- [ ] main.py（エントリポイント）実装
- [ ] GitHub Actions ワークフロー作成
- [ ] stdout チャンネル（テスト用）
- [ ] README.md（日英バイリンガル）
- [ ] セットアップガイド（docs/setup-guide.md）
- [ ] Bluesky / Discord / Slack チャンネル追加

## 次のステップ
1. 修正した CLAUDE.md をコミット＆push
2. physics-research の `fetch_arxiv.py` を移植（ほぼそのまま）
3. `src/config.py` を新規作成（config.yaml 読み込み）
4. Channel 基底クラスと Mastodon アダプタを実装

## 直近の決定事項
- 2026-03-16: プロジェクト開始
- 2026-03-16: **Pro Max OAuth は GitHub Actions で使用不可**と判明。MVP を API 直接呼び出し（モード A）に変更
- 2026-03-16: Pro Max で無料にできるのはローカル実行（モード B）のみ。ただし API 費用は月 $0.05〜0.30 と極めて安い
- 2026-03-16: config.yaml はコミット対象に変更（機密情報を含まないため）
- 2026-03-16: state/ は廃止（Actions は使い捨てランナー）
- 2026-03-16: interest_profile.txt を正本としてコミット。papers.yaml は中間生成物で gitignore
- 2026-03-16: execution.mode, schedule セクションを config から削除（二重管理の排除）
- 2026-03-16: 配信チャンネルはプラグイン方式。フォーマットはスコアリング時に長めに生成し、各チャンネルがトリム

## 設計レビューで発見・修正した問題
1. config.yaml が .gitignore なのに Actions で読めない → コミット対象に変更
2. state/ が Actions で永続しない → 廃止（cron が頻度制御）
3. papers.yaml も gitignore でプロファイル生成不可 → interest_profile.txt を正本に
4. Pro Max OAuth は Actions で使えない → API 直接呼び出しに一本化
5. チャンネルごとのフォーマット適応が未設計 → スコアリングは長め生成、チャンネルがトリム
6. execution.mode が config と workflow で二重管理 → config から削除

## 作業ログ
### 2026-03-16
- リポ作成: odakin/arxiv-digest (public)
- CLAUDE.md 初版作成 → 設計レビューで6つの矛盾を発見
- claude-code-action の認証方式を調査 → Pro Max OAuth は Actions 不可と判明
- CLAUDE.md 修正版を作成（全6問題を解消、設計を根本から見直し）
