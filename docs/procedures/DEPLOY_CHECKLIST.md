# デプロイチェックリスト（Ubuntu + Apache2）

Intelligent Modeling Laboratory (IML) website の本番反映前チェック手順です。

1. Hugo 出力を再ビルド

```bash
cd /Users/Daily/Development/Xomics/site
hugo --destination ../public --cleanDestinationDir
```

2. 生成ファイルを確認

```bash
ls -la /Users/Daily/Development/Xomics/public
```

`/Users/Daily/Development/Xomics/public/index.html` が存在することを確認します。

3. ローカル品質チェック

```bash
python /Users/Daily/Development/Xomics/scripts/validate_content.py
python /Users/Daily/Development/Xomics/scripts/check_markdown_validity.py --root /Users/Daily/Development/Xomics
python /Users/Daily/Development/Xomics/scripts/check_internal_links.py --public-dir /Users/Daily/Development/Xomics/public
find /Users/Daily/Development/Xomics/site/static/images -type f -size +500k
```

最後の `find` が空結果であることを確認します。

4. GitHub へ反映

```bash
git add .
git commit -m "..."
git push
```

### GitHub Actions 用 SSH 鍵の注意

- GitHub Actions 用の deploy 鍵は、通常のログイン鍵と分けて専用鍵にする。
- GitHub Actions 用の秘密鍵は、**パスフレーズなし** で作成する。
- `Permission denied (publickey)` が出た場合は、まず以下を確認する。
  - `DEPLOY_SSH_KEY` が正しい秘密鍵か
  - `DEPLOY_HOST` / `DEPLOY_USER` / `DEPLOY_PORT` がローカル成功時と一致しているか
  - サーバ側 `deploy` ユーザの `~/.ssh/authorized_keys` に対応する公開鍵が登録されているか
  - `~/.ssh` と `authorized_keys` の権限が適切か

GitHub Actions 用の鍵作成例:

```bash
cd /Users/Daily/Development/Xomics
mkdir -p .deploy-keys
ssh-keygen -t ed25519 -N "" -f .deploy-keys/github_actions_deploy_nopass -C "github-actions-deploy"
```

公開鍵をサーバの `deploy` ユーザへ登録する例:

```bash
cat /Users/Daily/Development/Xomics/.deploy-keys/github_actions_deploy_nopass.pub | \
ssh -p 10022 deploy@mercury.cc.kyushu-u.ac.jp 'umask 077; mkdir -p ~/.ssh; cat > ~/.ssh/authorized_keys'
```

ローカル疎通確認:

```bash
ssh -i /Users/Daily/Development/Xomics/.deploy-keys/github_actions_deploy_nopass \
  -p 10022 deploy@mercury.cc.kyushu-u.ac.jp
```

GitHub secret 登録例:

```bash
gh secret set DEPLOY_SSH_KEY < /Users/Daily/Development/Xomics/.deploy-keys/github_actions_deploy_nopass
printf '%s' 'mercury.cc.kyushu-u.ac.jp' | gh secret set DEPLOY_HOST
printf '%s' 'deploy' | gh secret set DEPLOY_USER
printf '%s' '10022' | gh secret set DEPLOY_PORT
```

5. CI 結果を確認

- `site_checks.yml` が成功していること
- （必要時）`update_publications.yml` / `site_audit.yml` が成功していること

6. Ubuntu 側デプロイ（GitHub Actions 経由）

- `develop` なら staging へ
- `main` なら production へ
- `public/` が `rsync/scp` で `/var/www/...` に配備されること

7. Apache 設定を確認（サーバ側）

```bash
sudo apache2ctl configtest
```

`Syntax OK` を確認後、必要なら reload。

```bash
sudo systemctl reload apache2
```

8. HTTP 応答を確認

```bash
curl -I http://mercury.cc.kyushu-u.ac.jp
```

`HTTP/1.1 200 OK` を確認します。

9. ブラウザ表示を確認

- production: `http://mercury.cc.kyushu-u.ac.jp`
- staging: `http://staging.mercury.cc.kyushu-u.ac.jp`（運用時）

確認項目:
- ページ表示崩れなし
- 主要ナビゲーション到達可
- 画像/CSS読み込み正常
- 最新更新内容が反映

10. 障害時ロールバック

- GitHub の直近正常コミットへ戻す
- 再デプロイ
- Apache 応答を再確認
