# arxiv-digest

arXiv 新着論文の AI スコアリング＋自動配信システム。研究者が自分の興味に合った論文を毎朝受け取れる。

## 概要

physics-research リポの arXiv ダイジェスト機能を汎用化・オープンソース化したもの。
誰でも fork → 設定 → 動作開始できることを目指す。

## リポジトリ情報

- パス: `~/Claude/arxiv-digest/`
- ブランチ: `main`
- リモート: `odakin/arxiv-digest` (public, GitHub)
- 元プロジェクト: `odakin/physics-research` (private) の `papers/arxiv_digest/`

## 設計方針

### 1. 実行モード（3段階）

| モード | 対象ユーザー | スコアリング方法 | API費用 | 必要環境 |
|--------|-------------|----------------|---------|---------|
| **A: Claude Code (Pro Max)** | Claude Pro Max 契約者 | GitHub Actions 上で `claude` CLI 実行（OAuth 認証） | **無料** | GitHub アカウント |
| **B: Anthropic API** | API キー保有者 | GitHub Actions 上で Anthropic API 直接呼び出し | **従量課金**（〜$0.01-0.05/日） | GitHub + API キー |
| **C: ローカル** | 開発者・上級者 | ローカル Claude Code scheduled task | **無料**（Pro Max）/ 従量 | 常時起動 Mac/PC |

**フェーズ1（MVP）**: モード A を実装。これが最もシンプルで、Pro Max ユーザーにとって追加費用ゼロ。
**フェーズ2**: モード B を追加。API キーがあれば Pro Max 不要で使える。
**フェーズ3**: モード C のドキュメント整備（physics-research の方式を参考に）。

### 2. GitHub Actions アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (cron: 平日 UTC で設定)               │
│                                                     │
│  Step 1: Python (fetch_arxiv.py)                    │
│    arXiv RSS → today_papers.json                    │
│    ※ 外部 API 不要、stdlib のみ                       │
│                                                     │
│  Step 2: プロファイル生成 (profile.py)                │
│    papers.yaml or interest_profile.txt → プロファイル │
│                                                     │
│  Step 3A (Pro Max): claude CLI でスコアリング         │
│    OAuth 認証 → Claude がスコア＋推薦文＋要約を生成    │
│  Step 3B (API): Python で Anthropic API 直接呼び出し  │
│    API キー → 同等の出力                              │
│                                                     │
│  Step 4: 配信 (publish.py)                          │
│    設定に応じてチャンネルに投稿                        │
└─────────────────────────────────────────────────────┘
```

### 3. 配信チャンネル（プラグイン方式）

チャンネルはプラグイン（アダプタ）パターンで実装し、追加が容易な構成にする。

| チャンネル | 優先度 | 認証方式 | 文字制限 | 備考 |
|-----------|--------|---------|---------|------|
| **Mastodon** | フェーズ1 | アクセストークン | 500文字 | 任意のインスタンス対応（Vivaldi, mstdn.jp, etc.） |
| **Bluesky** | フェーズ2 | App Password | 300文字 | AT Protocol |
| **Discord** | フェーズ2 | Webhook URL | 2000文字 | サーバー不要、Webhook だけで投稿可 |
| **Slack** | フェーズ2 | Webhook URL | 制限緩い | 研究室・チーム向け |
| **Email** | フェーズ3 | SMTP or SendGrid | 制限なし | ダイジェストまとめメール |
| **stdout / JSON** | フェーズ1 | なし | なし | テスト・デバッグ・他ツール連携 |

#### チャンネルインターフェース

```python
class Channel:
    """配信チャンネルの基底クラス。"""

    def publish(self, header: str, papers: list[dict]) -> None:
        """ヘッダーと論文リストを配信する。"""
        raise NotImplementedError

    @property
    def char_limit(self) -> int | None:
        """1投稿あたりの文字制限。None なら無制限。"""
        return None
```

各チャンネルは `channels/` ディレクトリに1ファイルで実装。設定で有効/無効を切り替え。
複数チャンネル同時配信もサポート（例: Mastodon + Discord）。

### 4. 研究興味プロファイル

ユーザーの研究興味を Claude に伝える方法。2つのパスを用意：

#### パス A: INSPIRE 自動生成（HEP 系研究者向け）
1. `config.yaml` に INSPIRE BAI（例: `K.Y.Oda.1`）を設定
2. `fetch_inspire.py` で全論文取得 → `papers.yaml` 生成
3. `profile.py` で論文データからプロファイル自動生成
4. 月次 cron で自動更新も可能

#### パス B: 手動テンプレート（INSPIRE にいない研究者向け）
1. `interest_profile.txt` のテンプレートに研究キーワードを記入
2. 分野、共同研究者、注目トピック等を自由記述
3. 更新はユーザーが手動で行う

#### パス C: ハイブリッド
- INSPIRE で基盤を自動生成 + 手動で微調整（優先トピック追加など）

### 5. 設定ファイル構成

```yaml
# config.yaml（ユーザーが編集する唯一のファイル）

# --- 基本設定 ---
language: ja                    # 推薦文・要約の言語 (ja / en)
scoring_threshold: 75           # この点数以上の論文を配信 (0-100)

# --- arXiv カテゴリ ---
arxiv_categories:
  - hep-ph
  - hep-th
  - gr-qc

# --- 研究興味プロファイル ---
profile:
  mode: inspire                 # inspire / manual / hybrid
  inspire_bai: "K.Y.Oda.1"     # INSPIRE BAI (mode: inspire/hybrid)
  # manual_file: interest_profile.txt  # (mode: manual/hybrid)

# --- 実行モード ---
execution:
  mode: claude-code             # claude-code / api
  # api_model: claude-sonnet-4-6  # (mode: api のみ)

# --- 配信チャンネル ---
channels:
  mastodon:
    enabled: true
    instance: "https://social.vivaldi.net"
    mention_target: "@odakin@social.vivaldi.net"
    # access_token: GitHub Secrets で設定（MASTODON_ACCESS_TOKEN）

  bluesky:
    enabled: false
    handle: "researcher.bsky.social"
    # app_password: GitHub Secrets で設定（BLUESKY_APP_PASSWORD）

  discord:
    enabled: false
    # webhook_url: GitHub Secrets で設定（DISCORD_WEBHOOK_URL）

  slack:
    enabled: false
    # webhook_url: GitHub Secrets で設定（SLACK_WEBHOOK_URL）

  stdout:
    enabled: false              # デバッグ用

# --- スケジュール（GitHub Actions cron） ---
schedule:
  cron: "30 1 * * 1-5"         # UTC (= JST 10:30, 平日のみ)
  timezone: "Asia/Tokyo"        # 表示用

# --- スコアリング指示（カスタム） ---
scoring_instructions: |
  以下の研究興味に基づいてスコアリングしてください。
  特になし（プロファイルから自動判定）の場合は空欄でOK。
```

#### 機密情報の扱い

- `config.yaml` にはトークン・パスワードを **書かない**
- すべて GitHub Secrets（Actions）または環境変数（ローカル）で管理
- `config.example.yaml` をリポに含め、`config.yaml` は `.gitignore`

### 6. セットアップフロー

プログラミング経験のない研究者でも使えることを目標にする。

```
1. GitHub アカウント作成（持っていない場合）
2. このリポを Fork
3. config.example.yaml → config.yaml にコピー＆編集
   - arXiv カテゴリを選ぶ
   - INSPIRE BAI を入力（or 手動プロファイル作成）
   - 配信先を設定（Mastodon / Bluesky / Discord 等）
4. GitHub Secrets にトークン類を設定
5. GitHub Actions を有効化
6. 翌朝からダイジェストが届く！
```

スクリーンショット付きステップバイステップガイドを `docs/setup-guide.md` に用意する。

### 7. リポ構成（目標）

```
arxiv-digest/
├── CLAUDE.md                   # このファイル（開発指示書）
├── SESSION.md                  # 作業ログ
├── README.md                   # ユーザー向け説明（日英バイリンガル）
├── .gitignore
├── config.example.yaml         # 設定テンプレート
├── requirements.txt            # pyyaml のみ（stdlib 最大活用）
├── setup.py                    # 初回セットアップスクリプト
│
├── src/
│   ├── __init__.py
│   ├── config.py               # config.yaml 読み込み
│   ├── fetch_arxiv.py          # arXiv RSS 取得（stdlib のみ）
│   ├── fetch_inspire.py        # INSPIRE API 取得
│   ├── profile.py              # 研究興味プロファイル生成
│   ├── scorer_api.py           # モード B: Anthropic API 直接スコアリング
│   ├── publish.py              # チャンネル振り分け
│   └── channels/
│       ├── __init__.py
│       ├── base.py             # Channel 基底クラス
│       ├── mastodon.py         # Mastodon 投稿
│       ├── bluesky.py          # Bluesky 投稿
│       ├── discord.py          # Discord Webhook
│       ├── slack.py            # Slack Webhook
│       └── stdout.py           # stdout 出力（テスト用）
│
├── .github/
│   └── workflows/
│       ├── digest.yml          # メイン: 日次ダイジェスト
│       └── monthly-update.yml  # INSPIRE 月次更新（オプション）
│
├── docs/
│   └── setup-guide.md          # スクリーンショット付きガイド
│
├── templates/
│   └── interest_profile.txt    # 手動プロファイルのテンプレート
│
└── state/                      # .gitignore 対象
    ├── today_papers.json
    └── last_run.json
```

### 8. physics-research からの移植方針

| 元ファイル | 移植先 | 変更点 |
|-----------|--------|--------|
| `arxiv_digest/fetch_arxiv.py` | `src/fetch_arxiv.py` | そのまま使える |
| `arxiv_digest/config.py` | `src/config.py` | ハードコード → `config.yaml` 読み込みに変更 |
| `arxiv_digest/profile.py` | `src/profile.py` | Oda 固有ロジック → 汎用化 |
| `arxiv_digest/mastodon.py` | `src/channels/mastodon.py` | Channel 基底クラスに準拠 |
| `arxiv_digest/run_digest.py` | `src/` 内に統合 | GitHub Actions ワークフローが呼び出し |
| `fetch_inspire.py` | `src/fetch_inspire.py` | BAI をハードコード → config から取得 |
| SKILL.md (scheduled task) | `.github/workflows/digest.yml` | Claude Code CLI 呼び出し or API 呼び出し |

### 9. GitHub Actions ワークフロー設計

#### モード A: Claude Code (Pro Max)

```yaml
# .github/workflows/digest.yml
name: arXiv Daily Digest
on:
  schedule:
    - cron: '30 1 * * 1-5'  # UTC = JST 10:30
  workflow_dispatch:          # 手動実行ボタン

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Fetch arXiv papers
        run: python -m src.fetch_arxiv --output state/today_papers.json

      - name: Score and publish (Claude Code)
        uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            state/today_papers.json を読み、config.yaml の設定に基づいて
            論文をスコアリングし、閾値以上の論文を配信チャンネルに投稿してください。
        env:
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
```

#### モード B: Anthropic API

```yaml
      - name: Score and publish (API)
        run: python -m src.scorer_api
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
```

### 10. 国際化

- 推薦文・要約の言語は `config.yaml` の `language` で切り替え
- UI（README、セットアップガイド）は日英バイリンガル
- スコアリングプロンプトは言語設定に応じて切り替え

### 11. 将来の拡張（検討中）

- **他の LLM 対応**: OpenAI, Gemini 等（scorer のプラグイン化）
- **X (Twitter) 対応**: API 費用が高いため優先度低
- **Web UI**: GitHub Pages で結果閲覧（JSON → 静的 HTML）
- **複数ユーザー集約**: 同じ分野の研究者がダイジェストを共有する仕組み
- **自論文検出 → プロファイル自動更新**: arXiv に自分の新論文が出たらプロファイル再生成

### 12. 開発上の注意

- **stdlib 最大活用**: 外部依存は `pyyaml` のみ。HTTP は `urllib`、XML は `xml.etree`
- **Python 3.10+**: f-string, type hints, `match` 文を活用
- **テスト**: `pytest` でユニットテスト。API 呼び出しはモック
- **CI**: PR に対して lint + test を実行
- コード・コメントは英語、ドキュメントは日英バイリンガル

## 実行環境

- 言語: Python 3.10+
- 依存: `pyyaml`（+ `anthropic` SDK はモード B のみ）
- 実行: GitHub Actions（主）/ ローカル（副）

## How to Resume（autocompact 復帰手順）

**autocompact 後・新規セッション開始時、必ずこの手順を実行:**
1. `SESSION.md` を読む → 現在の作業状態と次のステップを把握
2. SESSION.md の「次のステップ」に従って作業を継続
3. 不明点があればユーザーに確認

## 自動更新ルール（必須）

以下を人間に言われなくても自動で行う:
- タスク完了時 → SESSION.md を更新（完了マーク + 成果物記録）
- 重要な判断時 → SESSION.md に決定事項を記録
- ファイル作成/大幅変更時 → SESSION.md に記録
- push 前 → SESSION.md / CLAUDE.md が実態と一致しているか確認（詳細は CONVENTIONS.md §3）
- CLAUDE.md のルールの詳細は `~/Claude/CONVENTIONS.md` 参照
