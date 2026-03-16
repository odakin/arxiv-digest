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

### 1. 実行モード

| モード | 対象ユーザー | スコアリング方法 | API 費用 | 必要環境 |
|--------|-------------|----------------|---------|---------|
| **A: GitHub Actions + API** | 全ユーザー（MVP） | Python から Anthropic API 直接呼び出し | 〜$0.01/日（Sonnet）〜$0.002/日（Haiku） | GitHub + API キー |
| **B: ローカル Claude Code** | Pro Max 契約者 | Claude Code scheduled task（OAuth 認証） | **無料** | 常時起動 Mac/PC |

#### 「Pro Max なら無料」の正確な意味

- **Pro Max の OAuth トークンは公式ツール（claude.ai, Claude Code CLI）専用**。GitHub Actions 内での使用は不可
- したがって GitHub Actions では必ず `ANTHROPIC_API_KEY` が必要（Pro Max とは別の従量課金）
- **Pro Max で無料にできるのはモード B（ローカル実行）のみ**
- ただしモード A の API 費用は極めて安い（月 $0.05〜0.30 程度）

**フェーズ1（MVP）**: モード A を実装。GitHub Actions + API で誰でも使える。
**フェーズ2**: モード B のドキュメント整備（physics-research の方式を参考に）。

### 2. GitHub Actions アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (cron: 平日 UTC で設定)               │
│                                                     │
│  Step 1: Python (fetch_arxiv.py)                    │
│    arXiv RSS → papers リスト                         │
│    ※ stdlib のみ、外部 API 不要                       │
│                                                     │
│  Step 2: Python (scorer_api.py)                     │
│    papers + interest_profile.txt → Anthropic API    │
│    → スコア＋推薦文＋要約を生成                       │
│                                                     │
│  Step 3: Python (publish.py)                        │
│    config.yaml に応じて有効チャンネルに配信            │
└─────────────────────────────────────────────────────┘
```

**ポイント**: Actions ランナーは使い捨て。state ファイルは使わない（cron が頻度を制御）。

### 3. 配信チャンネル（プラグイン方式）

チャンネルはアダプタパターンで実装し、追加が容易な構成にする。

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
        """ヘッダーと論文リストを配信する。

        各 paper dict は以下のキーを持つ:
          score, title, authors, categories, url,
          reason (推薦文・長め), summary (要約・長め)
        チャンネル側で自身の文字制限に応じてトリムする。
        """
        raise NotImplementedError

    @property
    def char_limit(self) -> int | None:
        """1投稿あたりの文字制限。None なら無制限。"""
        return None
```

**フォーマット戦略**: スコアリング段階では文字数を気にせず、推薦文・要約を十分な長さで生成する。各チャンネルのアダプタが `char_limit` に応じてトリムまたは分割する。これにより、Discord なら詳しい解説、Mastodon なら簡潔な紹介、と同じスコアリング結果から最適な出力を生成できる。

### 4. 研究興味プロファイル

ユーザーの研究興味を Claude に伝えるためのテキストファイル。

#### 生成方法（セットアップ時に1回）

- **パス A: INSPIRE 自動生成**（HEP 系研究者向け）
  1. `python -m src.setup --inspire K.Y.Oda.1` を実行
  2. INSPIRE API → papers.yaml → interest_profile.txt を自動生成
  3. 生成されたプロファイルを確認・微調整してコミット

- **パス B: 手動テンプレート**（INSPIRE にいない研究者向け）
  1. `templates/interest_profile.txt` をコピー
  2. 研究キーワード・分野・共同研究者を記入
  3. コミット

#### ファイルの役割

| ファイル | コミット対象 | 役割 |
|---------|------------|------|
| `interest_profile.txt` | **Yes** | スコアリングに使う確定プロファイル（正本） |
| `papers.yaml` | No (.gitignore) | INSPIRE からの生のデータ（プロファイル生成の中間ファイル） |

**設計判断**: `interest_profile.txt` を正本とし、コミットする。`papers.yaml` はセットアップ時の中間生成物であり、日次実行には不要。INSPIRE の月次更新でプロファイルを再生成したい場合はローカルで実行してコミットする。

### 5. 設定ファイル構成

`config.yaml` は**コミット対象**。fork ごとに自分の設定を持つ。機密情報（トークン類）は含めず、GitHub Secrets で管理する。

```yaml
# config.yaml（ユーザーが編集する設定ファイル）

# --- 基本設定 ---
language: ja                    # 推薦文・要約の言語 (ja / en)
scoring_threshold: 75           # この点数以上の論文を配信 (0-100)
scoring_model: claude-sonnet-4-6  # スコアリングに使うモデル

# --- arXiv カテゴリ ---
arxiv_categories:
  - hep-ph
  - hep-th
  - gr-qc

# --- 配信チャンネル ---
channels:
  mastodon:
    enabled: true
    instance: "https://social.vivaldi.net"
    mention_target: "@yourname@social.vivaldi.net"
    # access_token は GitHub Secrets (MASTODON_ACCESS_TOKEN) で設定

  bluesky:
    enabled: false
    handle: "researcher.bsky.social"
    # app_password は GitHub Secrets (BLUESKY_APP_PASSWORD) で設定

  discord:
    enabled: false
    # webhook_url は GitHub Secrets (DISCORD_WEBHOOK_URL) で設定

  slack:
    enabled: false
    # webhook_url は GitHub Secrets (SLACK_WEBHOOK_URL) で設定

  stdout:
    enabled: false              # デバッグ用

# --- スコアリング追加指示（任意） ---
# interest_profile.txt に加えて、追加の指示がある場合に記入。
# 例: 「量子コンピュータ関連は低めにスコアリングして」等。空欄でもOK。
scoring_instructions: ""
```

**設計判断**:
- `execution.mode` は削除。実行環境（Actions vs ローカル）はワークフロー/スクリプト側で決まるので、config に書くのは二重管理になる
- `schedule` セクションも削除。cron は `.github/workflows/digest.yml` に直接書く（single source of truth）
- `profile` セクションも削除。`interest_profile.txt` を直接コミットする方式に統一したので、config でモード切り替えする必要がない

### 6. セットアップフロー

プログラミング経験のない研究者でも使えることを目標にする。

```
1. GitHub アカウント作成（持っていない場合）
2. このリポを Fork
3. config.yaml を編集（GitHub の Web UI で直接可能）
   - arXiv カテゴリを選ぶ
   - 配信先を設定（Mastodon / Bluesky / Discord 等）
4. interest_profile.txt を作成
   - INSPIRE にいる人: セットアップスクリプトで自動生成（ローカル実行）
   - いない人: テンプレートを埋める（GitHub の Web UI で可能）
5. GitHub Secrets を設定
   - ANTHROPIC_API_KEY（必須）
   - 配信先のトークン類（Mastodon / Bluesky / Discord 等）
6. GitHub Actions を有効化（Fork では手動で有効化が必要）
7. Actions タブから手動実行でテスト → 翌朝からダイジェストが届く！
```

スクリーンショット付きステップバイステップガイドを `docs/setup-guide.md` に用意する。

### 7. リポ構成（目標）

```
arxiv-digest/
├── CLAUDE.md                   # このファイル（開発指示書）
├── SESSION.md                  # 作業ログ
├── README.md                   # ユーザー向け説明（日英バイリンガル）
├── LICENSE                     # MIT
├── .gitignore
├── config.yaml                 # ユーザー設定（コミット対象）
├── interest_profile.txt        # 研究興味プロファイル（コミット対象）
├── requirements.txt            # pyyaml, anthropic
│
├── src/
│   ├── __init__.py
│   ├── config.py               # config.yaml 読み込み
│   ├── fetch_arxiv.py          # arXiv RSS 取得（stdlib のみ）
│   ├── scorer.py               # Anthropic API でスコアリング
│   ├── publish.py              # チャンネル振り分け
│   ├── main.py                 # エントリポイント（fetch → score → publish）
│   └── channels/
│       ├── __init__.py
│       ├── base.py             # Channel 基底クラス
│       ├── mastodon.py         # Mastodon 投稿
│       ├── bluesky.py          # Bluesky 投稿（フェーズ2）
│       ├── discord.py          # Discord Webhook（フェーズ2）
│       ├── slack.py            # Slack Webhook（フェーズ2）
│       └── stdout.py           # stdout 出力（テスト用）
│
├── tools/
│   ├── setup_inspire.py        # INSPIRE → interest_profile.txt 生成
│   └── fetch_inspire.py        # INSPIRE API クライアント
│
├── .github/
│   └── workflows/
│       └── digest.yml          # 日次ダイジェスト
│
├── docs/
│   └── setup-guide.md          # スクリーンショット付きガイド
│
└── templates/
    └── interest_profile.txt    # 手動プロファイルのテンプレート
```

**旧設計からの変更点**:
- `state/` ディレクトリ削除（Actions では不要）
- `setup.py` → `tools/setup_inspire.py`（役割を明確化）
- `scorer_api.py` → `scorer.py`（API が唯一のスコアリング方法なので `_api` 接尾辞不要）
- `fetch_inspire.py` を `tools/` に移動（日次実行ではなくセットアップ時のみ使用）
- `config.example.yaml` 廃止（`config.yaml` を直接コミット）
- `monthly-update.yml` 削除（INSPIRE 更新はローカルのセットアップツール扱い）
- `main.py` 追加（fetch → score → publish を1コマンドで実行）

### 8. physics-research からの移植方針

| 元ファイル | 移植先 | 変更点 |
|-----------|--------|--------|
| `arxiv_digest/fetch_arxiv.py` | `src/fetch_arxiv.py` | ほぼそのまま。config.py からカテゴリ取得に変更 |
| `arxiv_digest/config.py` | `src/config.py` | ハードコード → `config.yaml` 読み込み |
| `arxiv_digest/profile.py` | `tools/setup_inspire.py` | Oda 固有ロジック（`"Oda" not in a`）→ 汎用化 |
| `arxiv_digest/mastodon.py` | `src/channels/mastodon.py` | Channel 基底クラスに準拠。インスタンス URL を config から取得 |
| `arxiv_digest/run_digest.py` | `src/main.py` | state 管理を削除。fetch → score → publish の直列実行 |
| `fetch_inspire.py` | `tools/fetch_inspire.py` | BAI を引数で受け取る |
| SKILL.md (scheduled task) | `.github/workflows/digest.yml` + `src/scorer.py` | スコアリングロジックを Python に実装 |

### 9. GitHub Actions ワークフロー設計

```yaml
# .github/workflows/digest.yml
name: arXiv Daily Digest
on:
  schedule:
    - cron: '30 1 * * 1-5'  # UTC = JST 10:30, 平日のみ
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

      - name: Run digest
        run: python -m src.main
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
          BLUESKY_APP_PASSWORD: ${{ secrets.BLUESKY_APP_PASSWORD }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**設計判断**: ワークフローは1つ。モード切り替え不要（API 直接呼び出し一本）。

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
- **無料枠**: API 不使用のキーワードマッチングモード（精度は落ちるが費用ゼロ）
- **モード B（ローカル Claude Code）のドキュメント**: Pro Max ユーザー向けに、ローカル scheduled task での運用方法をガイド化

### 12. 開発上の注意

- **外部依存は最小限**: `pyyaml` と `anthropic` SDK のみ。RSS 取得は `urllib`、XML は `xml.etree`
- **Python 3.10+**: f-string, type hints を活用
- **テスト**: `pytest` でユニットテスト。API 呼び出しはモック
- **CI**: PR に対して lint + test を実行
- コード・コメントは英語、ドキュメントは日英バイリンガル

## 実行環境

- 言語: Python 3.10+
- 依存: `pyyaml`, `anthropic`
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
