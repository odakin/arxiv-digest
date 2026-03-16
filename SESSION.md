# arxiv-digest Session

## 現在の状態
**作業中**: コア実装完了 → コミット待ち

### タスク進捗
- [x] リポ作成（public: odakin/arxiv-digest、Template 設定済み）
- [x] CLAUDE.md 設計指示書
- [x] src/config.py（config.yaml 読み込み）
- [x] src/fetch_arxiv.py（arXiv RSS 取得、動作確認済み）
- [x] src/channels/base.py（Channel 基底クラス）
- [x] src/channels/mastodon.py（Mastodon アダプタ）
- [x] src/channels/stdout.py（テスト用、動作確認済み）
- [x] src/publish.py（チャンネル振り分け）
- [x] src/scorer.py（Anthropic API スコアリング、style 対応）
- [x] src/main.py（モード A エントリポイント）
- [x] src/fetch.py（モード B ステップ1、動作確認済み）
- [x] src/post.py（モード B ステップ3）
- [x] config.yaml（odakin の実設定）
- [x] interest_profile.txt（odakin の実プロファイル）
- [x] skill/SKILL.md（モード B scheduled task テンプレート）
- [x] .github/workflows/digest.yml（モード A ワークフロー）
- [x] templates/interest_profile.txt（手動プロファイルテンプレート）
- [x] tools/fetch_inspire.py + setup_inspire.py
- [x] requirements.txt
- [x] style 設定（tone, emoji_level）追加
- [ ] README.md（日英バイリンガル）
- [ ] セットアップガイド（docs/setup-guide.md）
- [ ] physics-research から arxiv_digest を削除・移行
- [ ] Bluesky / Discord / Slack チャンネル追加

## 次のステップ
1. コミット＆push
2. README.md 作成
3. physics-research の移行（arxiv_digest 削除、SKILL.md パス変更）

## 直近の決定事項
- 2026-03-16: style セクション追加（tone: casual/formal/neutral, emoji_level: none/light/moderate/heavy）
- 2026-03-16: ユーザーが言語・絵文字・フランクさを自由に選べるように

## 作業ログ
### 2026-03-16
- リポ作成 → 設計 → 実装
- コア全モジュール実装完了（config, fetch, scorer, publish, channels, main, fetch, post）
- 動作確認: config 読み込み、arXiv fetch（133件取得）、stdout チャンネル出力、Mode B fetch → JSON 出力
