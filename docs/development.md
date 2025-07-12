# 開発環境・セットアップ

## 開発環境

### 権限設定
- `.claude/settings.local.json`で基本的なbashコマンドの実行が許可されています

### 開発要件
- SDWUIプラグイン開発の知識
- Ollama API仕様の理解
- JavaScript/Python（SDWUIの実装言語に依存）
- HTTP通信の実装

### セットアップ手順
1. SDWUIの拡張機能ディレクトリに配置
2. Ollama APIエンドポイントの設定（デフォルト: http://localhost:11434）
3. プロンプト拡張ルールの設定

### 前提条件
- Ollamaがローカル環境で起動済みであること
- Ollama APIエンドポイント（http://localhost:11434）にアクセス可能であること

## セキュリティ要件

### 機密情報の管理
- **APIキー・認証情報**: 絶対にソースコードに直接記述しない
- **環境変数の使用**: `.env`ファイルで設定、`.env.example`をテンプレートとして提供
- **設定ファイル**: ローカル設定ファイルは`.gitignore`で除外済み
- **ログ出力**: APIキーやトークンをログに出力しない

### 開発時の注意事項
- APIキーや認証情報は環境変数またはローカル設定ファイルで管理
- 本番環境では適切な権限設定でファイルアクセスを制限
- コードレビュー時は機密情報の漏洩をチェック
- デバッグ情報にAPIキーが含まれないよう注意

### ファイル管理
- `.env`: 実際の設定値（Git管理対象外）
- `.env.example`: 設定テンプレート（Git管理対象）
- `secrets/`, `credentials/`: 認証情報ディレクトリ（Git管理対象外）

## デプロイメント

### SDWUIインストール手順
1. **プラグインディレクトリに配置**
   ```bash
   cd /path/to/stable-diffusion-webui/extensions
   git clone https://github.com/user/generate-prompt-ollama-plugin.git
   ```

2. **依存関係インストール**
   ```bash
   cd generate-prompt-ollama-plugin
   pip install -r requirements.txt
   ```

3. **設定ファイル作成**
   ```bash
   cp .env.example .env
   # .envファイルでOllama API設定を編集
   ```

4. **SDWUI再起動**
   ```bash
   # SDWUI を再起動してプラグインを有効化
   ```

### 配布パッケージング
```bash
# リリース用パッケージ作成
python scripts/build_package.py
# 生成物: dist/ollama-plugin-v1.0.0.zip
```

### 更新プロセス
1. GitHub Releases でバージョンタグ作成
2. パッケージファイルのアップロード  
3. ユーザー向け更新通知
4. SDWUI拡張機能マネージャーでの自動更新対応