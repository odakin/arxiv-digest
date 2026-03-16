# arxiv-digest

arXiv 新着論文の AI スコアリング＋自動配信システム。研究者が自分の興味に合った論文を毎朝受け取れる。

## 概要

physics-research リポの arXiv ダイジェスト機能を汎用化・オープンソース化したもの。
GitHub Template Repository として公開し、誰でも「Use this template」→ 設定 → 動作開始できることを目指す。

**開発者（odakin）自身もこのリポで日常運用する**。physics-research の arxiv_digest は移行済み。

## リポジトリ情報

- パス: `~/Claude/arxiv-digest/`
- ブランチ: `main`
- リモート: `odakin/arxiv-digest` (public, GitHub)
- 元プロジェクト: `odakin/physics-research` (private) の `papers/arxiv_digest/`

## 設計方針

### 1. 実行モード（2つ、どちらも一級市民）

| モード | 対象ユーザー | スコアリング方法 | API 費用 | 必要環境 |
|--------|-------------|----------------|---------|---------|
| **A: GitHub Actions + API** | 全ユーザー | Python から Anthropic API 直接呼び出し | 〜$0.01/日（Sonnet）〜$0.002/日（Haiku） | GitHub + API キー |
| **B: ローカル Claude Code** | Pro Max 契約者 | Claude Code scheduled task（OAuth 認証） | **無料** | 常時起動 Mac/PC |

**どちらのモードも正式サポート**。開発者自身がモード B で日常運用する。

#### 「Pro Max なら無料」の正確な意味

- **Pro Max の OAuth トークンは公式ツール（claude.ai, Claude Code CLI）専用**。GitHub Actions 内での使用は不可
- したがって GitHub Actions では必ず `ANTHROPIC_API_KEY` が必要（Pro Max とは別の従量課金）
- **Pro Max で無料にできるのはモード B（ローカル実行）のみ**
- ただしモード A の API 費用は極めて安い（月 $0.05〜0.30 程度）

### 2. アーキテクチャ

#### 共通パイプライン（モード A・B 共通）

```
fetch_arxiv.py → today_papers.json → [スコアリング] → publish.py → チャンネル配信
```

Python が担う部分（fetch + publish）は両モード共通。スコアリング部分だけが異なる：

- **モード A**: `scorer.py` が Anthropic API を直接呼び出し
- **モード B**: Claude Code scheduled task が自分でスコアリング（Python は fetch + publish のみ）

#### モード A: GitHub Actions

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (cron: 平日 UTC で設定)               │
│                                                     │
│  python3 -m src.main                                 │
│    1. fetch_arxiv.py → 論文リスト取得                 │
│    2. scorer.py → Anthropic API でスコアリング        │
│    3. publish.py → チャンネルに配信                   │
│                                                     │
│  ※ 全ステップが Python 内で完結                       │
└─────────────────────────────────────────────────────┘
```

#### モード B: ローカル Claude Code

```
┌─────────────────────────────────────────────────────┐
│  Claude Code scheduled task (cron: 平日 10:30 JST)   │
│                                                     │
│  1. python3 -m src.fetch → today_papers.json 出力     │
│  2. Claude 自身が JSON を読みスコアリング             │
│     （API 不使用、Pro Max OAuth で無料）               │
│  3. python3 -m src.post → スコア結果をチャンネル配信   │
│                                                     │
│  ※ スコアリングは Claude が直接行う（最も高品質）      │
└─────────────────────────────────────────────────────┘
```

**モード B の利点**: Claude Code CLI のフルコンテキストでスコアリングするため、API 直接呼び出しより高品質な推薦文・要約が生成できる。

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

### 4. 研究興味プロファイル（2ファイル構成 × マルチプロファイル）

スコアリングに使うプロファイルを**手書き**と**自動生成**の2ファイルに分離。月次 INSPIRE 更新で手書き内容が消える問題を根本解決。

#### マルチプロファイル

全ユーザー（odakin 含む）のプロファイルを `profiles/<name>/` に格納。ルート直下にはテンプレートのみ置く。

```
profiles/
├── odakin/
│   ├── config.yaml              # odakin 固有の設定オーバーライド
│   ├── interest_profile.txt     # 手書きプロファイル
│   └── inspire_profile.txt      # INSPIRE 自動生成
└── ogawa/
    └── inspire_profile.txt      # テスト用
```

`--profile <name>` フラグで指定。省略時はルート直下のファイルを使用（テンプレートユーザー向け後方互換）。

#### ファイルの役割

| ファイル | 役割 | 更新者 | コミット |
|---------|------|--------|---------|
| `profiles/<name>/interest_profile.txt` | 手書きの主観的優先事項（正本） | 人間のみ | **Yes** |
| `profiles/<name>/inspire_profile.txt` | INSPIRE 自動生成の客観データ | `setup_inspire.py` | **Yes** |
| `profiles/<name>/config.yaml` | プロファイル固有の設定オーバーライド | 人間 | **Yes** |
| `papers.yaml` | INSPIRE からの生データ（中間ファイル） | `fetch_inspire.py` | No (.gitignore) |

**設計判断**: スコアラー（`scorer.py` / SKILL.md）は両ファイルを読んで合成する。`interest_profile.txt` だけでも動作する（INSPIRE にいないユーザー向け）。`inspire_profile.txt` だけでも動作する（手書き不要なユーザー向け）。

#### セットアップ

- **INSPIRE 自動生成**（HEP 系研究者向け）
  1. `python3 -m tools.setup_inspire K.Y.Oda.1 --profile odakin` → `profiles/odakin/inspire_profile.txt` を生成
  2. `templates/interest_profile.txt` を参考に `profiles/odakin/interest_profile.txt` を手書き
  3. 両ファイルをコミット

- **手動テンプレートのみ**（INSPIRE にいない研究者向け）
  1. `templates/interest_profile.txt` をコピーして `profiles/<name>/interest_profile.txt` を作成
  2. コミット（`inspire_profile.txt` は不要）

#### 月次 INSPIRE 更新

`python3 -m tools.setup_inspire K.Y.Oda.1 --profile odakin` は `profiles/odakin/inspire_profile.txt` のみ上書き。`interest_profile.txt` は一切触らない。

#### 設定のマージ

`load_config(profile_name)` はルートの `config.yaml`（テンプレートデフォルト）を読んだ後、`profiles/<name>/config.yaml` をディープマージする。プロファイル側で指定したキーだけが上書きされる。

#### 実例（odakin のプロファイル）

**profiles/odakin/config.yaml**（オーバーライド）:
```yaml
language: ja
arxiv_categories: [hep-ph, hep-th, gr-qc, astro-ph.CO, quant-ph]
channels:
  mastodon:
    enabled: true
    instance: "https://social.vivaldi.net"
    bot_account: "odakinarxiv"
    mention_target: "@odakin@social.vivaldi.net"
style:
  tone: casual
  emoji_level: heavy
scoring_instructions: |
  - 「先生」は絶対に使わない
```

**profiles/odakin/interest_profile.txt**（手書き）: 波束形式、Einstein-Cartan、Higgs inflation 等の優先事項

**profiles/odakin/inspire_profile.txt**（自動生成）: INSPIRE から導出した統計データ（カテゴリ重み、共同研究者頻度、最近の論文タイトル等）

**運用方針**: odakin の全プロファイル・設定は常に public リポにコミットし、公開し続ける。

### 5. スコアリング設定

#### スコアリングプロンプト（モード A・B 共通の指示）

以下は `src/scorer.py` が API に送るプロンプトの骨格であり、モード B の SKILL.md にも同等の内容を書く：

```
あなたは arXiv 論文のスコアラーです。

## 研究興味プロファイル
{interest_profile.txt の内容}

## スコアリング基準
- 100点満点。閾値 {scoring_threshold} 以上の論文を配信
- 研究興味との直接的な重なり → 高スコア
- 共同研究者の論文 → 高スコア
- 関連手法・結果 → 中スコア
- 分野の一般的な発展 → 低スコア

## 出力形式
各論文について以下を {language} で生成（文字数制限なし、配信時にチャンネル側でトリム）:
- score: 0-100
- reason: 推薦文（この論文がなぜ面白いか、{style.tone} トーン、絵文字は {style.emoji_level} に従う）
- summary: 要約（技術的内容の簡潔な説明、絵文字は {style.emoji_level} に従う）

## 追加指示
{scoring_instructions}
```

#### 文体設定（config.yaml の style セクション）

ユーザーがトーン・絵文字の度合いを選べる：

```yaml
style:
  tone: casual       # casual（フランク）/ formal（学術的）/ neutral（中立）
  emoji_level: heavy  # none / light / moderate / heavy
```

#### odakin 専用の追加指示（実例）

```yaml
# config.yaml
style:
  tone: casual
  emoji_level: heavy
scoring_instructions: |
  - 「先生」は絶対に使わない
```

### 6. 設定ファイル構成

#### ルート config.yaml（テンプレートデフォルト）

`config.yaml` は**コミット対象**。ルート直下のものはテンプレートデフォルト（英語、チャンネル無効、ニュートラルスタイル）。各ユーザーは `profiles/<name>/config.yaml` で上書きする。機密情報（トークン類）は含めず、GitHub Secrets または環境変数で管理する。

#### プロファイル固有の設定（オーバーライド）

`profiles/<name>/config.yaml` にはそのユーザー固有の設定のみを記述。ルートの config.yaml にディープマージされる。

odakin の例: `profiles/odakin/config.yaml`
```yaml
language: ja
arxiv_categories: [hep-ph, hep-th, gr-qc, astro-ph.CO, quant-ph]
channels:
  mastodon:
    enabled: true
    instance: "https://social.vivaldi.net"
    bot_account: "odakinarxiv"
    mention_target: "@odakin@social.vivaldi.net"
style:
  tone: casual
  emoji_level: heavy
scoring_instructions: |
  - 「先生」は絶対に使わない
```

### 7. セットアップフロー

プログラミング経験のない研究者でも使えることを目標にする。

#### モード A（GitHub Actions）

```
1. GitHub アカウント作成（持っていない場合）
2. 「Use this template」→「Create a new repository」
   - Public / Private を選べる（スコアリング設定を非公開にしたければ Private）
3. config.yaml を編集（GitHub の Web UI で直接可能）
   - arXiv カテゴリを選ぶ
   - 配信先を設定（Mastodon / Bluesky / Discord 等）
4. interest_profile.txt を自分のプロファイルで上書き
   - INSPIRE にいる人: セットアップスクリプトで自動生成（ローカル実行）
   - いない人: テンプレートを参考に記入（GitHub の Web UI で可能）
5. GitHub Secrets を設定
   - ANTHROPIC_API_KEY（必須）
   - 配信先のトークン類（Mastodon / Bluesky / Discord 等）
6. GitHub Actions を有効化
7. Actions タブから手動実行でテスト → 翌朝からダイジェストが届く！
```

**プライバシー**: Template から作るリポは fork と違い、Private にできる。研究興味やスコアリング設定を非公開にしたいユーザーは Private リポを選べばよい。odakin のリポ（本体）は常に Public。

**注意**: テンプレートユーザー（個人リポ）はルート直下の config.yaml / interest_profile.txt を直接編集する（`--profile` は不要）。`profiles/` ディレクトリと `--profile` フラグは、1つのリポで複数ユーザーを配信する場合にのみ使用。

#### モード B（ローカル Claude Code）

```
1. リポを clone
2. config.yaml を編集
3. interest_profile.txt を作成
4. 環境変数にトークン類を設定（~/.zshrc 等）
5. Claude Code の scheduled task を作成（SKILL.md をコピー）
6. 動作確認 → 毎朝自動実行
```

スクリーンショット付きステップバイステップガイドを `docs/setup-guide.md` に用意する。

### 8. リポ構成（目標）

```
arxiv-digest/
├── CLAUDE.md                   # このファイル（開発指示書）
├── SESSION.md                  # 作業ログ
├── README.md                   # ユーザー向け説明（日英バイリンガル）
├── LICENSE                     # MIT
├── .gitignore
├── config.yaml                 # テンプレートデフォルト設定（英語、チャンネル無効）
├── interest_profile.txt        # テンプレート（ルート直下は後方互換用）
├── requirements.txt            # pyyaml, anthropic
│
├── profiles/
│   ├── odakin/                 # odakin のプロファイル（常に公開）
│   │   ├── config.yaml         # odakin 固有の設定オーバーライド
│   │   ├── interest_profile.txt
│   │   └── inspire_profile.txt
│   └── ogawa/                  # テスト用プロファイル
│       └── inspire_profile.txt
│
├── src/
│   ├── __init__.py
│   ├── config.py               # config.yaml 読み込み
│   ├── fetch_arxiv.py          # arXiv RSS 取得（stdlib のみ）
│   ├── scorer.py               # Anthropic API でスコアリング（モード A 用）
│   ├── publish.py              # チャンネル振り分け
│   ├── main.py                 # モード A エントリポイント（fetch → score → publish）
│   ├── fetch.py                # モード B 用: fetch のみ → JSON 出力
│   ├── post.py                 # モード B 用: スコア結果を受け取り publish
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
│   ├── __init__.py
│   ├── setup_inspire.py        # INSPIRE → inspire_profile.txt 生成
│   └── fetch_inspire.py        # INSPIRE API クライアント
│
├── skill/
│   └── SKILL.md                # モード B 用: Claude Code scheduled task 定義（実例）
│
├── .github/
│   └── workflows/
│       └── digest.yml          # モード A 用: 日次ダイジェスト
│
├── docs/
│   └── setup-guide.md          # スクリーンショット付きガイド
│
└── templates/
    └── interest_profile.txt    # 手動プロファイルのテンプレート
```

**モード B 用のファイル分離**:
- `src/fetch.py`: arXiv 取得 → `state/today_papers.json` 出力。Claude Code task の Step 1 で呼ばれる
- `src/post.py`: `state/scored_papers.json` を読み、publish.py 経由で配信。Claude Code task の Step 3 で呼ばれる
- `skill/SKILL.md`: Claude Code scheduled task の定義ファイル。ユーザーが `~/.claude/scheduled-tasks/` にコピーして使う
- `state/`: ローカル実行時の中間ファイル置き場（.gitignore 対象）

### 9. GitHub Actions ワークフロー設計（モード A）

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
        run: python3 -m src.main --profile odakin
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          MASTODON_ACCESS_TOKEN: ${{ secrets.MASTODON_ACCESS_TOKEN }}
          BLUESKY_APP_PASSWORD: ${{ secrets.BLUESKY_APP_PASSWORD }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 10. Claude Code Scheduled Task 設計（モード B）

`skill/SKILL.md` にテンプレートを置く。ユーザーがコピーして `~/.claude/scheduled-tasks/arxiv-digest/SKILL.md` に配置。

```markdown
---
name: arxiv-digest
description: 平日朝に arXiv 新着論文をスコアリングし配信
---

## 手順

1. `cd ~/Claude/arxiv-digest && python3 -m src.fetch --profile <name>` を実行し、arXiv RSS から新着論文を取得
2. `state/today_papers.json` を読み込む
3. プロファイルと設定を読む:
   - `profiles/<name>/interest_profile.txt`（手書きの研究優先事項）
   - `profiles/<name>/inspire_profile.txt`（INSPIRE 自動生成、存在する場合）
   - `profiles/<name>/config.yaml` の `scoring_instructions` および `style`（tone, emoji_level）
4. 各論文をスコアリング（100点満点、閾値は config.yaml の scoring_threshold）:
   - 研究興味との直接的な重なり → 高スコア
   - 共同研究者の論文 → 高スコア
   - 関連手法・結果 → 中スコア
   - 分野の一般的な発展 → 低スコア
5. 閾値以上の論文について、config.yaml の language で推薦文と要約を生成:
   - 推薦文: この論文がなぜ面白いか（文字数制限なし、config.yaml の style.tone に従う）
   - 要約: 技術的内容の簡潔な説明
   - 絵文字の量は config.yaml の style.emoji_level に従う（none/light/moderate/heavy）
6. スコア結果を `state/scored_papers.json` に JSON で書き出す（各論文に score, reason, summary を付与）
7. `python3 -m src.post --profile <name>` を実行し、scored_papers.json を読んでチャンネルに配信

## 注意
- profiles/<name>/config.yaml + ルート config.yaml のマージ設定に従って配信
- 環境変数（MASTODON_ACCESS_TOKEN 等）が設定されていること
- 土日は arXiv 更新なし（fetch が自動スキップ）
```

**odakin の実際の SKILL.md** はこれをベースに、スコアリング基準を直接記述する（現在の physics-research の SKILL.md と同等）。

### 11. 国際化

- 推薦文・要約の言語は `config.yaml` の `language` で切り替え
- UI（README、セットアップガイド）は日英バイリンガル
- スコアリングプロンプトは言語設定に応じて切り替え

### 12. 将来の拡張（検討中）

- **他の LLM 対応**: OpenAI, Gemini 等（scorer のプラグイン化）
- **X (Twitter) 対応**: API 費用が高いため優先度低
- **Web UI**: GitHub Pages で結果閲覧（JSON → 静的 HTML）
- **複数ユーザー集約**: 同じ分野の研究者がダイジェストを共有する仕組み
- **自論文検出 → プロファイル自動更新**: arXiv に自分の新論文が出たらプロファイル再生成
- **無料枠**: API 不使用のキーワードマッチングモード（精度は落ちるが費用ゼロ）

### 13. 開発上の注意

- **外部依存は最小限**: `pyyaml` と `anthropic` SDK のみ。RSS 取得は `urllib`、XML は `xml.etree`
- **Python 3.9+**: f-string, type hints を活用
- **テスト**: `pytest` でユニットテスト。API 呼び出しはモック
- **CI**: PR に対して lint + test を実行
- コード・コメントは英語、ドキュメントは日英バイリンガル

## 実行環境

- 言語: Python 3.9+
- 依存: `pyyaml`, `anthropic`（モード A のみ）
- 実行: GitHub Actions（モード A）/ ローカル Claude Code（モード B）

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
