# Test report

## v0.6.0 ローカルソース候補 — 2026-09-05

対象は `nanj-thread` の文体・レス形式、明示指定の境界、既存モードとの合成、元資料の保持である。
基点はv0.5.0、commit `f8416cc34fcbadfc59d9388eb9207d439b9c2770`。変更前は11単体テストとpackage validatorが成功し、作業ツリーはcleanだった。

### 必須確認と結果

- R1 — 入口から新規参照へ到達し、なんJ風の明示指定だけで適用することを確認。通常編集、GitHub等のスレッド、annotation、口調だけの変換を区別する。
- R2 — package validatorは0 warnings、単体テストは12件成功、Skill Creatorのquick validatorも成功。新しい参照の欠落とstyle_profileの不正な値・型を拒否する。
- R3 — スキルと関連referencesを渡した独立生成者の3依頼を、親エージェントが実際の出力で確認した。7レスへの変換、3行を保つ口調だけの変換、annotationだけの返答の各最終出力で、指定形式と保真を確認した。
- R4 — 相対Markdownリンク44件、パッケージ対象31ファイルのチェックサム、Git差分検査を確認した。Codex/Geminiの導入済みSKILL.mdとチェックサム台帳のハッシュは基点から変えていない。

回帰仕様は `HJ-052`〜`HJ-059` の8件を追加して全59件となった。59件のモデル生成を実行したという意味ではない。

### 独立生成で見つかった問題と限定した再確認

独立生成は `terra_worker` 1名で実施した。期待出力、evals、tests、README、設計・検証記録は渡さず、SKILL.mdと参照文書、ユーザー依頼と生の材料を渡した。出力の意味は親エージェントが確認した。

7レスの変換を求めたAでは、最初の出力のタイトルに「らしい」が加わり、資料で確定した結果が伝聞調になった。タイトルにも元の確度を保つ規則を具体化し、Aだけを再試行した。
次の出力では、原資料にない差分110msが加わった。計算自体は正しかったが、計算を求められていない数字の追加は今回の保真契約に合わないため、スレッド化だけでは差分・割合・倍率を計算して追加しない規則を具体化した。
Aの最後の出力では、7レスと有効な先行レスへのアンカーを確認し、測定者、同一環境、200件、p95の420ms/310ms、メモリ未測定、本番未確認、コマンドと引用の逐語保持を確認した。新しい計算値はなかった。

Bの「口調だけ・番号なし・3行」は、2026年10月の公開予定、オフライン未確認、最大15分かかる可能性を保持した。
Cの「問題点だけ」は、主体、試験と本番、平均と全件、保証の違いを指摘し、完成スレを生成しなかった。B/Cは再生成していない。

これらはR3の不適合に基づく限定した追加確認であり、全モードや全モデルへの検証拡張は行っていない。初回Aと修正後Aは同じ生成者による試行であり、最後のAを新しい被験者による初見試行とは扱わない。

### 停止状態と限界

R1〜R4を満たし、ソース・利用例が存在するため、ローカル候補としてのSTOP_CONDITIONはmet。
文体の好み、濃いめ指定の生成品質、全回帰仕様のモデル実行、複数モデル比較は未評価。
GitHubへのpush、PR作成、導入済みCodex/Geminiへの配置、ZIP配布、fresh runtime discoveryは実施していない。現行の導入済みスキルはv0.5.0のままである。

任意証拠として追加の大規模評価や配布確認は収集していない。以下はv0.5.0の過去記録であり、今回の候補の導入・実行証拠として流用しない。

---

# v0.5.0の過去記録

Build date: 2026-08-31

## Scope

この報告は、Humanizer JA Editor v0.5.0で追加した次の目的プロファイルと、その配布・導入経路を対象にする。

- `guided-tutorial`：読者が手順を進め、観察可能な完了点へ到達するためのガイド付きチュートリアル
- `troubleshooting`：症状、観察、仮説、原因確度、対応、再検証を分けるトラブルシューティング
- `comparison-selection`：比較条件、必須条件、証拠、未知、ライフサイクルを分ける比較・選定

文章生成の全ケースでの意味品質、初見利用者による操作評価、ChatGPTデスクトップ画面での視覚表示、Geminiによる実生成、プラグイン化、外部公開は、この報告だけでは保証しない。

## Baseline and preservation

変更前のCodex配置はv0.4.1、Gemini配置はv0.4.0だった。

復元用として、次のアーカイブを候補ツリーの外へ保存した。

- Codex v0.4.1配布ZIP：`5f352305503401274e487a05759cab1181d438f6854caaf05577724870c049f3`
- Gemini v0.4.0配置アーカイブ：`10bee0f7429d4b1bffc73ce8badda85b23f4b46a58e5f32fc2fe5bfd5b04f7db`
- 既存のv0.4.0配布ZIP：`08c8a69b599e8a906128de16d13c92592ad7f4a050c773875593f0135a07430d`

候補はlive配置を直接編集せず、同名の独立ツリーで構築した。

## Design research

3つのプロファイルについて、2026-08-31時点で21件の公開資料を直接確認した。資料は、公式ドキュメント、政府・公的機関の指針、技術組織の一次的な解説を中心に選んだ。

公開資料から借りたのは、情報を並べる順序、停止点、証拠の分け方、役割境界である。各サイト固有の製品事実、数値、判定、口調、医療・政府調達・宇宙などの領域固有要件は、一般プロファイルへ持ち込んでいない。確認先と採用境界は `NOTICE.md` と各プロファイル参照に記録した。

## Candidate changes

v0.5.0では、既存の処理モード、場面プロファイル、初心者向け説明方針、作者プロファイルを置き換えず、依頼の目的に応じて重ねる目的プロファイルを追加した。

- `SKILL.md` に目的プロファイルの選択規則、非適用条件、合成順序を追加
- `references/guided-tutorial-profile.md` を追加
- `references/troubleshooting-profile.md` を追加
- `references/comparison-selection-profile.md` を追加
- `references/software-exposition.md` と `references/output-modes.md` に合成境界を追加
- `README.md`、`DESIGN.md`、`CHANGELOG.md`、`NOTICE.md` をv0.5.0へ更新
- `HJ-040`〜`HJ-051`を追加し、評価仕様を51件へ拡張
- `purpose_profile` の型、許可値、3プロファイルの網羅を独自検証器へ追加
- 不正値と網羅不足を拒否する単体テストを追加

`agents/openai.yaml` の表示名、短い説明、既定プロンプトはv0.4.1から変更していない。

## Candidate validation

候補ルートで次を実行した。

```bash
python3 scripts/validate_package.py .
python3 -m unittest discover -s tests -v
python3 /home/umise/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

最初の検証では、候補ディレクトリの仮名とfrontmatterの`name`が一致しないことだけを検出した。候補ディレクトリを`humanizer-ja-editor`へ改め、同じ検証を再実行した。

再実行の結果は次のとおりだった。

- 独自パッケージ検証：`0 warning(s)`
- 単体テスト：11件成功
- Skill Creator quick validator：`Skill is valid!`
- 評価仕様：51件、IDは`HJ-001`から`HJ-051`まで一意かつ連番
- `SKILL.md`本文：306行、7,546文字。独自検証器の警告基準内

## Independent forward evaluation

期待出力と評価仕様を見せていない独立評価者へ、候補の`SKILL.md`と実行時に参照する文書だけを渡し、次の3依頼を評価した。

1. 外部公開と費用発生の可能性がある本番公開チュートリアル。承認、rollback、利用者向け確認、実行記録が不足
2. 設定は保存済みだが`MainPID=0`で、利用者画面から機能を使えない診断専用の依頼
3. 実行環境、入力件数、測定方法、単位が異なる性能資料と、不完全な移行資料による比較

3件とも、適切な目的プロファイルを選択し、次の禁止境界を守った。

- 公開依頼では、不足する承認とrollbackを創作せず、外部公開コマンドの前に停止した
- 診断依頼では、設定保存、設定読込、プロセス状態、利用者向け動作を別の証拠段階として扱った
- 比較依頼では、条件の異なるベンチマークを順位へ変換せず、候補Bの不明を劣位または失敗と扱わなかった
- いずれも、与えられていない実行結果、原因、権限、費用、移行成功を補完しなかった

独立評価は読み取り専用で行い、外部操作、公開、設定変更、購入、ファイル編集を実行していない。

## Package integrity

`CHECKSUMS.sha256`自身、配布ZIP、旧版バックアップ、Pythonキャッシュを対象外として、30ファイルのチェックサムを生成した。全30項目が一致した。

配布ZIPは、チェックサムファイルを含む31ファイルで構成した。ZIP内には、別のZIP、`__pycache__`、`.pyc`を含めていない。`unzip -t`はエラーなしだった。

配布ZIPを新しい一時ディレクトリの`humanizer-ja-editor`へ展開し、次を再実行した。

- `sha256sum -c CHECKSUMS.sha256`：30項目成功
- 独自パッケージ検証：`0 warning(s)`
- 単体テスト：11件成功
- Skill Creator quick validator：`Skill is valid!`

配布ZIPのSHA-256は、自己参照を避けるためZIP内の報告書には埋め込まず、配布物と一緒に外側で報告する。

## Installed-state and fresh-runtime validation

検証済み候補を、次の配置へ非削除型で反映した。

- Codex：`/home/umise/.codex/skills/humanizer-ja-editor`
- Gemini：`/home/umise/.gemini/config/skills/humanizer-ja-editor`

候補のマニフェスト対象ファイルは、Codex配置、Gemini配置の両方と一致した。両配置で、独自パッケージ検証0 warning、11件の単体テスト、Skill Creator quick validatorを実行し、すべて成功した。

Codex配置には、次の復元用ZIPを保持した。

- v0.4.0：`08c8a69b599e8a906128de16d13c92592ad7f4a050c773875593f0135a07430d`
- v0.4.1：`5f352305503401274e487a05759cab1181d438f6854caaf05577724870c049f3`

Codex CLI 0.149.0のapp-serverを`--stdio --strict-config`で新規起動し、`initialize`の応答後に`skills/list`を`forceReload=true`で実行した。結果は次のとおりだった。

```text
initialize: ok
errors: []
matchCount: 1
validMatchCount: 1
path: /home/umise/.codex/skills/humanizer-ja-editor/SKILL.md
scope: user
enabled: true
displayName: Humanizer JA Editor
```

取得したdescriptionには、ガイド付きチュートリアル、トラブルシューティング、比較・選定の3用途が含まれていた。この結果はfresh Codex runtimeからの発見を示すが、Gemini上の実生成やChatGPTデスクトップ画面の描画を示すものではない。

## Remaining limits

- 51件は回帰評価の仕様であり、すべてのケースを複数モデルで生成・採点した結果ではない。
- 独立forward evaluationは、3プロファイルにつき1件ずつの代表ケースである。
- ChatGPTデスクトップ画面の視覚表示と、初見利用者による操作テストは実施していない。
- Gemini上の実生成は検証していない。
- プラグイン化、外部リポジトリへの書き込み、公開ディレクトリへの提出は実施していない。
