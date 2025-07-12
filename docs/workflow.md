# 開発ワークフロー

## Git Worktree並行開発

### 並行開発環境のセットアップ
```bash
# worktreeディレクトリの作成
mkdir -p ../worktrees

# 各機能ブランチの作成とworktree設定
git checkout -b feature/core-implementation
git push -u origin feature/core-implementation
git checkout -b feature/ui-integration  
git push -u origin feature/ui-integration
git checkout master

# worktreeの作成
git worktree add ../worktrees/core-implementation feature/core-implementation
git worktree add ../worktrees/ui-integration feature/ui-integration
```

### 各worktreeでの作業方法
```bash
# コア機能開発
cd ../worktrees/core-implementation
claude-code

# UI統合開発
cd ../worktrees/ui-integration  
claude-code
```

### ブランチ戦略
- **master**: 安定版メインブランチ
- **feature/core-implementation**: Ollama API通信コア機能
- **feature/ui-integration**: SDWUI統合とUI実装
- **hotfix/***: 緊急修正用ブランチ

### マージプロセス
1. 各worktreeで機能開発・テスト完了
2. GitHub Issue連携でPR作成
3. PR レビュー（Claude Code活用）
4. masterブランチへマージ
5. worktree cleanup

## 開発コマンド
```bash
# テスト実行
npm test                    # JavaScript テスト
pytest                     # Python テスト
pytest tests/integration/  # 統合テスト

# コード品質
npm run lint               # JavaScript リント
black src/                 # Python フォーマット
flake8 src/               # Python リント

# 開発サーバー
python scripts/dev_server.py  # 開発用テストサーバー
```

## テスト戦略
- **単体テスト**: 各モジュール（ollama/, ui/, utils/）の独立テスト
- **統合テスト**: Ollama API通信、SDWUI統合の end-to-end テスト
- **UI テスト**: SDWUI設定画面、フック機能のテスト
- **CI/CD**: Git push時の自動テスト実行

### ブランチでのテスト
```bash
# 各worktreeでのテスト実行例
cd ../worktrees/core-implementation
pytest tests/test_ollama/    # コア機能テスト

cd ../worktrees/ui-integration  
pytest tests/test_ui/        # UI統合テスト
```