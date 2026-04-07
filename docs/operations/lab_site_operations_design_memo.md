# 研究室HP

------

## 1. 全体構成

全体は次の3層に分けると分かりやすいです。

```text
[GitHub]
  - ソースコードの正本
  - Markdown, theme, layouts, scripts, CI設定

      ↑ push / pull
      ↓ CI checks
      ↓ deploy trigger (checks success only)

[自分のPC]
  - 開発
  - Hugo ローカル確認
  - 変更作成
  - PR / merge

      ↓ build artifact or rsync/scp

[Ubuntu + Apache2]
  - 本番公開
  - Hugo生成済み public/ を配信
```

役割はこうです。

- **GitHub**: 唯一の正本
- **自分のPC**: 開発・確認環境
- **Ubuntu + Apache2**: 本番配信環境

------

## 2. GitHub の構成

GitHub には、**サイトを再現するのに必要なものを全部置く**のが原則です。

推奨構成:

```text
lab-website/
├─ site/
│  ├─ config.toml or hugo.toml
│  ├─ content/
│  ├─ layouts/
│  ├─ static/
│  ├─ assets/
│  └─ themes/   (または theme は submodule / module)
├─ scripts/
│  ├─ deploy_staging.sh
│  ├─ deploy_production.sh
│  ├─ bibtex_to_markdown.py
│  └─ scholar_fetch.py
├─ apache/
│  └─ sites-available/
├─ .github/
│  └─ workflows/
├─ docs/        (運用メモ)
├─ audits/      (LLM監査プロンプト)
└─ README.md
```

GitHub を正本にするなら、**Ubuntu サーバ側で直接編集しない**のが重要です。
`public/` はローカルまたは GitHub Actions で生成する build artifact とし、Git 管理しません。

------

## 3. 自分のPCの構成

PC は **開発専用**です。  
ここでは Hugo のソースを編集し、ローカルで確認します。

推奨構成:

```text
~/work/lab-website/
```

開発時の基本操作（推奨）:

```bash
git clone <repo>
cd lab-website
make build
make up
make ps
```

確認URL:

`http://127.0.0.1`

補助的に Hugo 開発サーバを使う場合:

```bash
cd lab-website/site
hugo server
```

`http://localhost:1313`

PC 側でやること:

- Markdown 更新
- レイアウト修正
- CSS 修正
- 画像追加
- publication 自動生成スクリプト実行
- `make build` / `make up` で公開相当の見た目確認
- 必要に応じて `hugo server` で執筆中プレビュー確認

------

## 4. Ubuntu + Apache2 の構成

Ubuntu 側は **配信専用**に寄せるのが安全です。  
**生成済みの静的ファイルだけを Apache が配信**します。

推奨ディレクトリ:

```text
/var/www/
  ├─ html/            ← production
  └─ mercury-staging/ ← staging（任意）
```

VirtualHost 例:

```apache
<VirtualHost *:80>
    ServerName mercury.cc.kyushu-u.ac.jp
    DocumentRoot /var/www/html

    <Directory /var/www/html>
        Options FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

------

## 5. staging と production

運用安定のため、**分離**を推奨します。

```text
staging.mercury.cc.kyushu-u.ac.jp -> /var/www/mercury-staging
mercury.cc.kyushu-u.ac.jp         -> /var/www/html
```

ブランチ対応:

```text
main      -> production
develop   -> staging
feature/* -> 個別作業
```

------

## 6. デプロイ運用

静的サイトのため、デプロイは単純です。

```text
GitHub Actions -> site checks -> Hugo build -> rsync/scp -> Ubuntu (/var/www/...)
```

方針:

- `develop` push: `site checks` 成功後に staging デプロイ
- `main` push: `site checks` 成功後に production デプロイ

------

## 7. publication 更新との関係

publication 自動更新は、いきなり本番に出さず `develop` 経由にします。

```text
Scholar / BibTeX 更新
  ↓
スクリプトで Markdown 化
  ↓
develop へ commit
  ↓
staging 確認
  ↓
main へ反映
```

------

## 8. Apache2 側の運用ポリシー

- `/var/www/html` は配信専用
- サーバ上で直接編集しない
- 変更は必ず GitHub 経由
- `sites-available` で管理
- `a2ensite` で有効化
- 反映前に `apache2ctl configtest`、その後 `systemctl reload apache2`

------

## 9. 具体的な更新フロー

### 通常更新

1. PC で編集
2. `make build && make up && make ps` で確認
3. feature ブランチで commit
4. GitHub に push
5. PR
6. `develop` にマージ
7. staging 確認
8. `main` にマージ
9. production 更新

### 緊急修正

1. `hotfix/*` 作成
2. 修正
3. `main` に PR
4. production 反映
5. `develop` へ戻しマージ

------

## 10. バックアップと復旧

GitHub が事実上のバックアップです。加えて以下を定期バックアップします。

- Apache 設定
- `/var/www/html` と staging 配下
- 証明書設定
- デプロイスクリプト

復旧手順:

```text
Ubuntu再構築
-> Apache設定復元
-> GitHubから再デプロイ
```

------

## 11. セキュリティ

- 静的サイトのみ公開
- サーバ直接編集禁止
- DB/PHP 等の動的処理を導入しない

------

## 12. 最終目標

研究室サイトを **研究成果公開プラットフォーム** として安定運用する。

- 長期運用可能
- 更新容易
- 研究成果の可視化
- 安全な公開
