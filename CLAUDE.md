# arxiv-digest

arXiv 新着論文の AI スコアリング＋自動配信システム。GitHub Template Repository。

## リポジトリ情報

- パス: `~/Claude/arxiv-digest/`
- ブランチ: `main`
- リモート: `odakin/arxiv-digest` (public)
- 開発者（odakin）自身もこのリポで日常運用

## 実行モード

| モード | スコアリング | コスト |
|--------|------------|--------|
| **A: GitHub Actions** | `src/scorer.py` → Anthropic API | ~$0.01/日 |
| **B: ローカル Claude Code** | scheduled task が直接スコアリング | 無料（Pro Max） |

共通パイプライン: `fetch_arxiv.py → [スコアリング] → publish.py → チャンネル配信`

- モード A: `python3 -m src.main --profile <name>`（全ステップ Python 内で完結）
- モード B: `src.fetch` → Claude がスコアリング → `src.post`（`skill/SKILL.md` 参照）

## プロファイル

全プロファイルは `profiles/<name>/` に格納。`--profile` のデフォルトは `default`。

各プロファイルに置けるファイル:
- `interest_profile.txt` — 手書きの研究優先事項（人間が編集）
- `inspire_profile.txt` — INSPIRE 自動生成（`tools/setup_inspire.py`）
- `config.yaml` — ルート `config.yaml` へのオーバーライド（ディープマージ）

スコアラーは両プロファイルを結合して使う。どちらか片方だけでも動作する。
月次 INSPIRE 更新は `inspire_profile.txt` のみ上書き、`interest_profile.txt` は不変。

## 開発規約

- Python 3.9+、外部依存は `pyyaml` + `anthropic` のみ
- コード・コメント: 英語、ユーザーとのやりとり: 日本語
- チャンネル追加は `src/channels/base.py` の Channel クラスを継承
- トークン類は環境変数で管理（config.yaml に書かない）

## How to Resume（autocompact 復帰手順）

1. `SESSION.md` を読む → 現在の作業状態と次のステップを把握
2. SESSION.md の「次のステップ」に従って作業を継続
3. 不明点があればユーザーに確認

## 自動更新ルール（必須）

- タスク完了時 → SESSION.md を更新
- 重要な判断・ファイル作成/大幅変更時 → SESSION.md に記録
- push 前 → SESSION.md / CLAUDE.md が実態と一致しているか確認（詳細は CONVENTIONS.md §3）
- CLAUDE.md のルールの詳細は `~/Claude/CONVENTIONS.md` 参照
