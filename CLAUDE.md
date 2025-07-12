# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Stable Diffusion WebUI（SDWUI）用のプラグインで、Generateボタン押下時にOllama APIを使用してプロンプトを自動拡張する機能を提供します。

### 主要機能
- **プロンプト自動拡張**: Generateボタン押下時に、現在のプロンプトをOllama APIに送信し、不足している情報を自動補完
- **バッチ処理対応**: Batch Countごとに個別にOllama APIと通信し、各バッチで異なるプロンプト拡張を実行
- **多様な画像生成**: 1回のGenerateで様々なパターンの画像を生成できるよう、プロンプトをバリエーション豊かに拡張
- **SDWUIとの統合**: 既存のワークフローを変更せずに使用可能

### 技術仕様
- **対象プラットフォーム**: Stable Diffusion WebUI (txt2imgのみ対応)
- **外部API**: Ollama API (openhermes モデル)
- **プラグイン形式**: SDWUIエクステンション
- **通信方式**: one-shot API通信、逐次バッチ処理
- **プロンプト拡張**: 元プロンプト + カンマ + 拡張プロンプト (150token以内)

### 要件仕様（qa.md回答反映）
- **Ollamaサーバー**: localhost:11434、openhermes モデル、30秒タイムアウト
- **プロンプト拡張対象**: シーン・背景、色調・ムード、構図・カメラアングル、ライティング・照明、テーマ・コンセプト
- **プロンプト拡張除外**: アーティスト名、技術・手法、スタイル情報
- **プロンプトテンプレート**: 英語で指示、50token以内、応答フォーマット自由
- **バリエーション**: ランダム要素追加、再現性不要
- **エラーハンドリング**: API通信5回失敗で中断、UI通知、元プロンプトで続行
- **UI/UX**: プログレスバー・ステータステキスト表示、プレビューなし
- **設定管理**: settings.json（extensionsフォルダ内）、URL・数値validation、自動生成
- **ログ出力**: console.log、タイムスタンプ付きJSON形式、API通信・プロンプト変換詳細
- **技術統合**: extensionsフォルダ配置、実装方式自由、gradio要素からバッチカウント取得
- **パフォーマンス**: メモリ1GB以下、CPU50%以下、info・errorログ出力

## アーキテクチャ

### コア機能
1. **フックシステム**: SDWUIのGenerate処理にフックして、プロンプト送信前に割り込み処理を実行
2. **Ollama通信モジュール**: Ollama APIとの通信を管理し、プロンプト拡張リクエストを処理
3. **プロンプト処理エンジン**: 元のプロンプトと拡張されたプロンプトを適切に統合

### データフロー
```
ユーザー入力 → SDWUIフロントエンド → [プラグイン割り込み] → Batch Count分だけループ → Ollama API通信 → プロンプト拡張 → SDWUI生成処理
```

### バッチ処理の詳細
- SDWUIのBatch Count設定に応じて、指定された回数分Ollama APIと通信
- 各バッチで異なるプロンプト拡張を行うことで、バリエーション豊かな画像生成を実現
- バッチごとに独立したプロンプト処理により、同一設定でも多様性のある結果を取得

## ドキュメント構造

詳細な技術仕様と開発ガイドは以下のファイルに分割されています：

- **[要件Q&A](docs/qa.md)**: 設計前の詳細要件確認と回答
- **[開発環境・セットアップ](docs/development.md)**: 開発環境、セキュリティ要件、セットアップ手順
- **[プロジェクト構造](docs/project-structure.md)**: ディレクトリ構成、モジュール役割、ファイル構成
- **[開発ワークフロー](docs/workflow.md)**: Git Worktree、テスト戦略、CI/CD、コード品質管理
- **[技術仕様](docs/technical-specs.md)**: Ollama API仕様、プロンプト拡張ルール、SDWUI統合
- **[開発手順](docs/setup-guide.md)**: Phase 1-3の詳細な実装手順とコマンド

## 開発コマンド

### テスト実行
```bash
pytest                     # Python テスト
pytest tests/integration/  # 統合テスト
```

### コード品質
```bash
black src/                 # Python フォーマット
flake8 src/               # Python リント
```

### 開発サーバー
```bash
python scripts/dev_server.py  # 開発用テストサーバー
```

## 実装方針

### 段階的開発
1. **基本プラグイン構造の実装** → [開発手順](docs/setup-guide.md)参照
2. **Ollama API通信機能の実装** → [技術仕様](docs/technical-specs.md)参照
3. **プロンプト拡張ロジックの実装**
4. **SDWUIとの統合テスト**
5. **ユーザー設定機能の追加**

## Git Commit戦略

### 長期タスクでの作業単位
長いタスクの場合は、以下の作業まとまり単位で必ずcommitを実行すること：

1. **Phase完了時**: 各開発Phase（Phase 1, 2, 3など）の完了時
2. **モジュール実装完了時**: 独立したモジュール・機能の実装完了時
3. **テスト追加時**: 新しいテストファイルやテストケース追加時
4. **設定ファイル更新時**: requirements.txt、設定ファイル等の更新時
5. **エラー修正時**: 重要なバグ修正やビルドエラー解決時

### Commit メッセージ規則
- **Phase系**: "Implement Phase X: [具体的な内容]"
- **機能系**: "Add [機能名]: [詳細]"
- **修正系**: "Fix [問題]: [解決内容]"
- **設定系**: "Update [設定項目]: [変更内容]"

### 自動化指示での注意点
長期タスクを指示する際は以下を明記：
- "各作業まとまりでcommitを実行すること"
- "エラー発生時は修正後にcommitすること"
- "Phase完了時は必ずcommitすること"

## クイックスタート

```bash
# 1. プロジェクト構造作成
docs/setup-guide.md の Phase 1 を実行

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. 開発環境セットアップ
python scripts/setup_hooks.py
```