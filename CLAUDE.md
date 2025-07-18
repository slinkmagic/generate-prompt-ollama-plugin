# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [技術仕様](#技術仕様)
- [アーキテクチャ](#アーキテクチャ)
- [開発ワークフロー](#開発ワークフロー)
- [開発環境](#開発環境)
- [ドキュメント構造](#ドキュメント構造)

---

## プロジェクト概要

Stable Diffusion WebUI（SDWUI）用のプラグインで、Generateボタン押下時にOllama APIを使用してプロンプトを自動拡張する機能を提供します。

### 🎯 主要機能

- **プロンプト自動拡張**: Generateボタン押下時に、現在のプロンプトをOllama APIに送信し、不足している情報を自動補完
- **バッチ処理対応**: Batch Countごとに個別にOllama APIと通信し、各バッチで異なるプロンプト拡張を実行
- **多様な画像生成**: 1回のGenerateで様々なパターンの画像を生成できるよう、プロンプトをバリエーション豊かに拡張
- **SDWUIとの統合**: 既存のワークフローを変更せずに使用可能

### 🔄 データフロー

```
ユーザー入力 → SDWUIフロントエンド → [プラグイン割り込み] → Batch Count分だけループ → Ollama API通信 → プロンプト拡張 → SDWUI生成処理
```

---

## 技術仕様

### 🏗️ 基本仕様

| 項目 | 仕様 |
|-----|-----|
| **対象プラットフォーム** | Stable Diffusion WebUI (txt2imgのみ対応) |
| **外部API** | Ollama API (openhermes モデル) |
| **プラグイン形式** | SDWUIエクステンション |
| **通信方式** | one-shot API通信、逐次バッチ処理 |
| **プロンプト拡張** | 元プロンプト + カンマ + 拡張プロンプト (150token以内) |

### ⚙️ 詳細要件仕様

#### Ollama API
- **サーバー**: localhost:11434
- **モデル**: openhermes
- **タイムアウト**: 30秒
- **リトライ**: 5回失敗で中断

#### プロンプト拡張
- **拡張対象**: シーン・背景、色調・ムード、構図・カメラアングル、ライティング・照明、テーマ・コンセプト
- **拡張除外**: アーティスト名、技術・手法、スタイル情報
- **テンプレート**: 英語で指示、50token以内、応答フォーマット自由
- **バリエーション**: ランダム要素追加、再現性不要

#### システム統合
- **エラーハンドリング**: API通信失敗時はUI通知、元プロンプトで続行
- **UI/UX**: プログレスバー・ステータステキスト表示、プレビューなし
- **設定管理**: settings.json（extensionsフォルダ内）、URL・数値validation、自動生成
- **ログ出力**: console.log、タイムスタンプ付きJSON形式、API通信・プロンプト変換詳細
- **技術統合**: extensionsフォルダ配置、実装方式自由、gradio要素からバッチカウント取得
- **パフォーマンス**: メモリ1GB以下、CPU50%以下、info・errorログ出力

---

## アーキテクチャ

### 🔧 コア機能

1. **フックシステム**: SDWUIのGenerate処理にフックして、プロンプト送信前に割り込み処理を実行
2. **Ollama通信モジュール**: Ollama APIとの通信を管理し、プロンプト拡張リクエストを処理
3. **プロンプト処理エンジン**: 元のプロンプトと拡張されたプロンプトを適切に統合

### 📦 バッチ処理の詳細

- SDWUIのBatch Count設定に応じて、指定された回数分Ollama APIと通信
- 各バッチで異なるプロンプト拡張を行うことで、バリエーション豊かな画像生成を実現
- バッチごとに独立したプロンプト処理により、同一設定でも多様性のある結果を取得

### 🚀 段階的開発

1. **基本プラグイン構造の実装** → [開発手順](docs/setup-guide.md)参照
2. **Ollama API通信機能の実装** → [技術仕様](docs/technical-specs.md)参照
3. **プロンプト拡張ロジックの実装**
4. **SDWUIとの統合テスト**
5. **ユーザー設定機能の追加**

---

## 開発ワークフロー

### 📋 GitHub Issue/PR ワークフロー

#### Issue作成戦略
すべてのタスクは以下の手順で管理すること：

1. **Phase開始前にIssue作成**: 各Phaseの最初に必要なIssueをすべて作成
2. **タスク単位でIssue化**: 機能実装、バグ修正、設定変更等をIssue単位で管理
3. **随時Issue追加**: 作業中に発見した追加タスクは即座にIssue化
4. **Issue → ブランチ → PR → マージ**: 必ずこの流れでタスクを処理

#### Issue作成ルール
- **Phase系Issue**: "Phase X: [Phase名] - [概要説明]"
- **機能系Issue**: "[機能名] の実装"
- **修正系Issue**: "[問題] の修正"
- **設定系Issue**: "[設定項目] の更新"

#### PR作成とマージ
- Issue作成後、専用ブランチで作業開始
- 作業完了後、PR作成してマージ
- PR Titleは対応Issueと関連付け
- マージ後はIssueをクローズ

### 📝 Git Commit戦略

#### 長期タスクでの作業単位
長いタスクの場合は、以下の作業まとまり単位で必ずcommitを実行すること：

1. **Phase完了時**: 各開発Phase（Phase 1, 2, 3など）の完了時
2. **モジュール実装完了時**: 独立したモジュール・機能の実装完了時
3. **テスト追加時**: 新しいテストファイルやテストケース追加時
4. **設定ファイル更新時**: requirements.txt、設定ファイル等の更新時
5. **エラー修正時**: 重要なバグ修正やビルドエラー解決時

#### Commit メッセージ規則
- **Phase系**: "Implement Phase X: [具体的な内容]"
- **機能系**: "Add [機能名]: [詳細]"
- **修正系**: "Fix [問題]: [解決内容]"
- **設定系**: "Update [設定項目]: [変更内容]"

#### 自動化指示での注意点
長期タスクを指示する際は以下を明記：
- "各PhaseでIssue作成してからPR作成すること"
- "各作業まとまりでcommitを実行すること"
- "エラー発生時は修正後にcommitすること"
- "Phase完了時は必ずPRマージすること"

---

## 開発環境

### 🧪 テスト実行
```bash
pytest                     # Python テスト
pytest tests/integration/  # 統合テスト
```

### 🔍 コード品質
```bash
black src/                 # Python フォーマット
flake8 src/               # Python リント
```

### 🔧 開発サーバー
```bash
python scripts/dev_server.py  # 開発用テストサーバー
```

### ⚡ クイックスタート
```bash
# 1. プロジェクト構造作成
docs/setup-guide.md の Phase 1 を実行

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. 開発環境セットアップ
python scripts/setup_hooks.py
```

---

## ドキュメント構造

詳細な技術仕様と開発ガイドは以下のファイルに分割されています：

| ドキュメント | 内容 |
|-------------|------|
| **[要件Q&A](docs/qa.md)** | 設計前の詳細要件確認と回答 |
| **[開発環境・セットアップ](docs/development.md)** | 開発環境、セキュリティ要件、セットアップ手順 |
| **[プロジェクト構造](docs/project-structure.md)** | ディレクトリ構成、モジュール役割、ファイル構成 |
| **[開発ワークフロー](docs/workflow.md)** | Git Worktree、テスト戦略、CI/CD、コード品質管理 |
| **[技術仕様](docs/technical-specs.md)** | Ollama API仕様、プロンプト拡張ルール、SDWUI統合 |
| **[開発手順](docs/setup-guide.md)** | Phase 1-3の詳細な実装手順とコマンド |