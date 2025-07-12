# プロジェクト構造

## ディレクトリ構成
```
generate-prompt-ollama-plugin/
├── src/
│   ├── ollama/              # Ollama API通信モジュール
│   │   ├── client.py        # API接続・通信処理
│   │   ├── config.py        # 設定管理
│   │   └── prompt_engine.py # プロンプト拡張エンジン
│   ├── ui/                  # SDWUI統合UI
│   │   ├── extension.py     # SDWUIエクステンション
│   │   ├── settings.py      # 設定画面
│   │   └── hooks.py         # Generate処理フック
│   └── utils/               # 共通ユーティリティ
│       ├── logger.py        # ログ管理
│       └── security.py      # セキュリティ機能
├── scripts/                 # インストール・設定スクリプト
│   ├── install.py          # SDWUIインストールスクリプト
│   └── setup_config.py     # 初期設定スクリプト
├── tests/                   # テストファイル
│   ├── test_ollama/        # Ollama機能テスト
│   ├── test_ui/            # UI統合テスト
│   └── test_integration/   # 統合テスト
├── config/                  # 設定テンプレート
│   ├── default_config.json # デフォルト設定
│   └── prompts/            # プロンプトテンプレート
└── docs/                   # ドキュメント
    ├── api.md              # API仕様書
    └── installation.md     # インストールガイド
```

## モジュール役割
- **src/ollama/**: Ollama APIとの通信、プロンプト拡張処理
- **src/ui/**: SDWUI統合、ユーザーインターフェース
- **src/utils/**: ログ管理、セキュリティ、共通機能
- **scripts/**: インストール、設定の自動化
- **tests/**: 各モジュールのテスト、統合テスト
- **config/**: 設定ファイル、プロンプトテンプレート

## 依存関係管理
```json
// package.json (JavaScript部分)
{
  "name": "generate-prompt-ollama-plugin",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
```

```python
# requirements.txt (Python部分)
requests>=2.28.0
pydantic>=1.10.0
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
```