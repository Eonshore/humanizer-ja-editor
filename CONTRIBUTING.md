# 改善への参加

文章例、不具合報告、ドキュメント修正、編集規則や補助スクリプトの改善を受け付けています。

## 問題を報告する

Issueには、再現に必要な範囲で次の情報を添えてください。

- スキルのバージョンまたはコミット
- 使用したクライアントとモデル
- 依頼文と、個人情報・秘密情報を除いた入力
- 期待した結果と実際の結果
- 失われた条件や追加された因果など、気になった箇所

公開できない原稿は、同じ問題が起きる短い架空の例へ置き換えてください。

## 変更を提案する

`SKILL.md`は共通の方針と参照先を選ぶ入口です。場面に固有の詳しい規則は`references/`へ置き、関係する評価ケースと文書を更新してください。

意味、数字、主体、条件、確度、引用、識別子を保つことを優先します。「自然に見える」という理由だけで、新しい事実や語り手の体験を加えないでください。適用範囲を広げるときは、似ていても適用しない依頼も検討します。

既存の`HJ-*`評価IDを再利用しないでください。統合の境界を扱うケースは`HJI-*`へ追加できます。評価仕様を追加したことと、そのケースをモデルで実行したことは分けて報告します。

## 検証する

Python 3.10以上で、リポジトリのルートから実行します。Pythonの外部パッケージは不要です。

```bash
python3 scripts/validate_package.py .
python3 -m unittest discover -s tests -v
git diff --check
```

パッケージ検証はファイル構成と参照を、単体テストは補助スクリプトを確認します。文章規則を変更した場合は、関連する入力で出力も確認し、使ったモデル、成功・失敗、未検証の範囲をPull Requestに記載してください。

## チェックサムを更新する

配布ファイルを編集したら、内容を確定した後で`CHECKSUMS.sha256`を更新します。新しい配布ファイルは先に個別のパスを指定して`git add`してください。次のスクリプトは、Gitが追跡するファイルだけを対象にします。

```bash
python3 - <<'PY'
import hashlib
import subprocess
from pathlib import Path

paths = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
excluded = {"CHECKSUMS.sha256", ".gitignore"}
files = sorted(
    name for name in paths
    if name and name not in excluded and not name.startswith(".github/")
)
Path("CHECKSUMS.sha256").write_text(
    "".join(
        f"{hashlib.sha256(Path(name).read_bytes()).hexdigest()}  {name}\n"
        for name in files
    ),
    encoding="utf-8",
)
PY
sha256sum -c CHECKSUMS.sha256
```

macOSなどで`sha256sum`がない場合は、`shasum -a 256 -c CHECKSUMS.sha256`を使えます。

`.codex/`などの作業記録、原稿、秘密情報、バックアップ、ZIP、キャッシュはコミットに含めないでください。追加した配布ファイルとチェックサムを確認してから、変更したパスを指定してステージします。

GitHub Actionsでもパッケージ検証、単体テスト、チェックサム、追跡ファイルの範囲を確認します。自動テストの成功は、任意の文章で意味が保持される保証ではありません。

## ライセンスと参照資料

提案するコードと文書は、このプロジェクトの[MIT License](LICENSE)で配布できるものにしてください。第三者の文章や図、非公開資料をそのまま追加せず、参考にした資料の帰属が必要な場合は[NOTICE.md](NOTICE.md)へ記載してください。
