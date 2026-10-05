# TODO — arxiv-digest

未完了の作業の台帳 (maintainer 用)。 済んだ項目は消す (経緯は git log、 設計は DESIGN.md)。 SESSION.md は現在地とこの file への link だけを持つ。

## 要対応

定期実行 (`skill/SKILL.md` のステップ0) がダイジェストの前に読む節。 配信の前に確かめる項目だけを置く。

- [ ] 二重実行インシデント = 二重実行の停止 / 将来課題: post 時の message ID 捕捉 → [SESSION-archive.md](SESSION-archive.md#double-execution-incident) の「要対応」 の節 (本文と経緯は archive の節のまま)

## 継続タスク

定期実行は読まない。

- [ ] Bluesky / Slack チャンネル追加
- [ ] INSPIRE BAIが未設定の登録者は、本人の論文・所属・共著者を照合してから登録する。確認できるまでは `inspire_bai: null` と手書きの `interest_profile.txt` で運用する。更新処理は各profileの現在の設定値を読み、過去の固定コマンドからIDを復元しない。

- [ ] 一括 MOVE で SESSION-archive.md へ行った未完了の項目 (本文と経緯は archive の節のまま):
  - onda 追加に付随 = 他マシン (学校 Mac 等) で `.env` 生成 / 新 subscriber への事前告知 / README.md / SKILL.md に `.env` の `DISCORD_MENTION_*` 項目を明示 → [節](SESSION-archive.md#from-残タスク-2026-04-14-の-onda-追加に付随)
  - redact の副作用 = 共同研究者の stub 登録 / orphan 監視 / local backup branch 削除 → [節](SESSION-archive.md#from-残タスク-派生-2026-04-14-redact-の副作用)
