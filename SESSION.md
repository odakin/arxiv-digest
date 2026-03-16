# arxiv-digest Session

## 現在の状態
**完了**: コア実装 + ドキュメント + physics-research 移行 完了、push 済み

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
- [x] tools/fetch_inspire.py + setup_inspire.py（著者名検索 --search 対応済み）
- [x] requirements.txt
- [x] style 設定（tone, emoji_level）追加
- [x] CLAUDE.md 整合性修正（§2 post, §5 style変数化, §8 tools/__init__.py, §11 SKILL.md style参照, §14 Python 3.9+）
- [x] README.md（日英バイリンガル、英語先・日本語後）
- [x] セットアップガイド（docs/setup-guide.md、日英バイリンガル）
- [x] physics-research から arxiv_digest を削除・移行（scheduled task 更新済み）
- [x] セキュリティ検証（.env を .gitignore に追加）
- [x] python → python3 修正（全11ファイル）
- [x] cross-list カテゴリ対応（inspire_categories fallback + ティア分類）
- [x] E2E テスト（Ogawa プロファイルで fetch→score→Mastodon 投稿成功）
- [x] プロファイル2ファイル分離（interest_profile.txt + inspire_profile.txt）
- [x] 閾値デフォルト 75→80 に変更
- [x] エラー通知（try/except + チャンネル通知 + SKILL.md 報告指示）
- [x] マルチプロファイル対応（profiles/ ディレクトリ + --profile フラグ）
- [x] odakin を profiles/odakin/ に移行（ルート config.yaml をテンプレート化）
- [x] Discord チャンネル追加（Webhook 方式）
- [ ] Bluesky / Slack チャンネル追加

## 次のステップ
1. Bluesky / Slack チャンネル追加（フェーズ2）

## 直近の決定事項
- 2026-03-16: プロファイルのカテゴリをティア分類（Primary >=20%, Secondary 5-20%, Peripheral <5%）
- 2026-03-16: style セクション追加（tone: casual/formal/neutral, emoji_level: none/light/moderate/heavy）
- 2026-03-16: ユーザーが言語・絵文字・フランクさを自由に選べるように
- 2026-03-16: プロファイルを2ファイルに分離（手書き interest_profile.txt + 自動生成 inspire_profile.txt）
- 2026-03-16: デフォルト閾値を80点に変更
- 2026-03-16: エラー通知機能追加（チャンネル経由 + SKILL.md エラー報告指示）
- 2026-03-16: マルチプロファイル対応（profiles/<name>/ + --profile フラグ、後方互換）
- 2026-03-16: odakin を profiles/odakin/ に移行、ルート config.yaml をテンプレートデフォルト化
- 2026-03-16: odakin の固有設定は常に公開（profiles/odakin/ をコミット）
- 2026-03-16: setup_inspire に --search フラグ追加（INSPIRE 著者名検索 → BAI 自動解決）
- 2026-03-16: Discord チャンネル実装（Webhook URL 方式、2000字制限、Markdown 対応）

## 作業ログ
### 2026-03-16
- リポ作成 → 設計 → 実装
- コア全モジュール実装完了（config, fetch, scorer, publish, channels, main, fetch, post）
- 動作確認: config 読み込み、arXiv fetch（133件取得）、stdout チャンネル出力、Mode B fetch → JSON 出力
- CLAUDE.md 整合性修正5件実施、tools/__init__.py 追加
- README.md 作成（英語先・日本語後のバイリンガル構成）
- physics-research 移行完了（arxiv_digest/ 削除、CLAUDE.md/README.md/SESSION.md 更新、scheduled task 2件パス変更）
- docs/setup-guide.md 作成（Mode A/B セットアップ、Mastodon 設定、トラブルシューティング）
- セキュリティ検証 + .env gitignore、python3 修正11ファイル、cross-list カテゴリ対応
- E2E テスト: Ogawa プロファイル自動生成 → arXiv fetch 133件 → スコアリング → Mastodon 投稿成功
- プロファイル2ファイル分離: interest_profile.txt（手書き）+ inspire_profile.txt（自動生成）
  - setup_inspire.py → inspire_profile.txt に出力（interest_profile.txt は不変）
  - config.py get_profile() で両ファイルを合成
  - SKILL.md 3箇所（skill/, arxiv-digest task, inspire-monthly task）を更新
  - CLAUDE.md §4, §8, §10 を更新
- 閾値 75→80 に変更（config.yaml + CLAUDE.md）
- エラー通知: main.py/fetch.py/post.py に try/except、publish.py に notify_error()、channels に post_text()
- マルチプロファイル: config.py に profiles/ 対応、全エントリポイント + setup_inspire.py に --profile フラグ
  - `python3 -m src.main --profile ogawa` で profiles/ogawa/ の設定・プロファイルを使用
  - --profile なしは後方互換（ルート直下のファイルを使用）
  - profiles/ogawa/ にテスト用プロファイルを生成して動作確認
- odakin を profiles/odakin/ に完全移行
  - profiles/odakin/config.yaml に固有設定（言語、カテゴリ、Mastodon、style、scoring_instructions）
  - ルート config.yaml をテンプレートデフォルト化（英語、チャンネル無効、neutral スタイル）
  - .github/workflows/digest.yml に --profile odakin 追加
  - skill/SKILL.md + installed scheduled tasks に --profile odakin 追加
  - CLAUDE.md §4, §6, §8, §9, §10 をプロファイルベースに更新