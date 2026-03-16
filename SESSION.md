# arxiv-digest Session

## 現在の状態
**作業中**: プロジェクト初期セットアップ — 設計指示書（CLAUDE.md）作成済み

### タスク進捗
- [x] リポ作成（public: odakin/arxiv-digest）
- [x] CLAUDE.md 設計指示書の作成
- [ ] physics-research から汎用コード移植 ← **ここから再開**
- [ ] config.example.yaml 作成
- [ ] Channel 基底クラス + Mastodon アダプタ実装
- [ ] GitHub Actions ワークフロー（モード A: Claude Code）
- [ ] stdout チャンネル（テスト用）
- [ ] README.md（日英バイリンガル）
- [ ] セットアップガイド（docs/setup-guide.md）
- [ ] モード B: Anthropic API スコアリング実装
- [ ] Bluesky / Discord / Slack チャンネル追加

## 次のステップ
1. physics-research の `fetch_arxiv.py` を移植（ほぼそのまま）
2. `config.py` を `config.yaml` 読み込み方式に書き換え
3. Channel 基底クラスと Mastodon アダプタを実装

## 直近の決定事項
- 2026-03-16: プロジェクト開始。Pro Max ユーザー向け（API費用ゼロ）を MVP とする
- 2026-03-16: 配信チャンネルはプラグイン方式。Vivaldi 固定ではなく任意の Mastodon インスタンス対応
- 2026-03-16: 将来的に非 Pro ユーザーも Anthropic API 直接呼び出しで使えるようにする（モード B）
- 2026-03-16: 設定ファイルは config.yaml 1つに集約。機密情報は GitHub Secrets / 環境変数

## 作業ログ
### 2026-03-16
- リポ作成: odakin/arxiv-digest (public)
- CLAUDE.md に設計指示書を作成（実行モード、チャンネル設計、設定構成、移植方針等）
