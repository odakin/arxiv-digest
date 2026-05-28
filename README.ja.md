# arxiv-digest

[English version](README.md)

研究者向け arXiv 新着論文の AI 日刊ダイジェスト。 毎朝、 あなたの研究興味に合った論文を Mastodon / Discord / メール 等の任意チャンネルに配信します。

## なぜこれが必要か

活発な分野の arXiv RSS は日に 50–200 件の新着が並びます。 全タイトルに目を通すのは時間の無駄、 関連のあるものを見落とすのは機会損失。 arxiv-digest は新着論文をあなたの手書き研究興味プロファイルに対して Claude でスコアリングし、 高スコアのものだけを推薦理由付きで配信します。 2 つの実行モードが同じ fetch / score / publish パイプラインを共有し、 スコアリング step のみが異なります:

| モード | スコアリング | コスト | 必要環境 |
|--------|------------|--------|---------|
| **A: GitHub Actions** | Anthropic API | ~$0.01/日 (Sonnet) | GitHub + API キー |
| **B: ローカル Claude Code** | Claude Code scheduled task | **無料** (Pro Max) | 常時起動 Mac/PC |

## どんな出力か

配信例 (一部):

```
📚 arXiv新着ダイジェスト
本日の新着 87 件中 4 件をお届けします。

⭐ 92/100 | hep-ph, gr-qc
👤 Smith, Jones, Doe, et al.
📄 論文タイトル

理由: あなたの X 路線の直接的な続き — 既存の制約を …
要約: 著者は Y を 2-loop で計算し Z を見出した。

https://arxiv.org/abs/2604.XXXXX
```

同じ論文セットを複数チャンネルに同時 fan-out 可能。

## クイックスタート (モード A)

1. **「Use this template」** → **「Create a new repository」** をクリック
2. `config.yaml` と `profiles/default/interest_profile.txt` を編集
3. 使うチャンネル分の GitHub Secrets を追加 (`ANTHROPIC_API_KEY` + 例えば `MASTODON_ACCESS_TOKEN`)
4. GitHub Actions を有効化 — 平日毎朝自動実行

詳細手順 (HEP 向け INSPIRE 自動プロファイル / チャンネル別設定 / トラブルシューティング) は [docs/setup-guide.md](docs/setup-guide.md) 参照。 Pro Max で無料運用できるモード B も同じガイドに記載。

## 配信チャンネル

| チャンネル | 認証 | 状態 |
|-----------|------|------|
| Mastodon | アクセストークン | 利用可 |
| Discord | Webhook URL | 利用可 |
| メール (SMTP/STARTTLS) | ユーザー名 + App Password | 利用可 |
| stdout | なし | 利用可 (テスト用) |
| Slack | Webhook URL | 計画中 |
| Bluesky | App Password | 計画中 |

チャンネル追加は `src/channels/base.py` の `Channel` を継承 → `src/publish.py` に登録 → 必要なら `config.yaml` を拡張。 既存 (`discord.py` / `mastodon.py` / `email.py`) が pattern reference。

## どこに何があるか

- `config.yaml` — ルートのデフォルト値、 profile 別 override は `profiles/<name>/config.yaml`
- `profiles/default/` — 起点となるプロファイル、 自分のものは copy / rename して作る
- `src/` — fetch / score / publish パイプライン (`src/channels/` = 配信チャンネル)
- `skill/SKILL.md` — モード B 用 Claude Code スコアリング指示書
- `tools/setup_inspire.py` — INSPIRE BAI から HEP プロファイル自動生成
- `docs/setup-guide.md` — 完全 setup walkthrough
- `CLAUDE.md` — メンテナー reference (構造・モード・プロファイル)
- `DESIGN.md` — 設計判断 (モード A vs B の選択理由、 archive owner 分離等)

## ライセンス

MIT — [LICENSE](LICENSE) 参照。
