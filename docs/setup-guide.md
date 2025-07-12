# 開発手順

## Phase 1: プロジェクト構造の作成
```bash
# 全ディレクトリ構造を作成
mkdir -p src/ollama src/ui src/utils scripts tests/test_ollama tests/test_ui tests/test_integration config/prompts docs

# 各ディレクトリに基本ファイルを作成
touch src/ollama/__init__.py src/ollama/client.py src/ollama/config.py src/ollama/prompt_engine.py
touch src/ui/__init__.py src/ui/extension.py src/ui/settings.py src/ui/hooks.py
touch src/utils/__init__.py src/utils/logger.py src/utils/security.py
touch scripts/install.py scripts/setup_config.py scripts/dev_server.py scripts/build_package.py
touch tests/__init__.py tests/test_ollama/__init__.py tests/test_ui/__init__.py tests/test_integration/__init__.py
touch config/default_config.json docs/api.md docs/installation.md
touch README.md setup.py __init__.py
```

## Phase 2: 核となる設定ファイルの作成
```bash
# Python依存関係設定
cat > requirements.txt << 'EOF'
requests>=2.28.0
pydantic>=1.10.0
python-dotenv>=1.0.0
gradio>=3.0.0
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
pre-commit>=3.0.0
EOF

# JavaScript依存関係設定（もしJS部分が必要な場合）
cat > package.json << 'EOF'
{
  "name": "generate-prompt-ollama-plugin",
  "version": "1.0.0",
  "description": "Stable Diffusion WebUI plugin for automatic prompt enhancement via Ollama API",
  "dependencies": {
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "@types/node": "^20.0.0"
  },
  "scripts": {
    "test": "jest",
    "lint": "eslint src/",
    "dev": "node scripts/dev_server.js"
  }
}
EOF

# 環境変数テンプレート
cat > .env.example << 'EOF'
# Ollama API設定
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30

# プラグイン設定
PLUGIN_ENABLED=true
PROMPT_ENHANCEMENT_ENABLED=true
BATCH_PROCESSING_ENABLED=true
MAX_CONCURRENT_REQUESTS=3

# ログ設定
LOG_LEVEL=INFO
LOG_FILE=logs/ollama_plugin.log

# セキュリティ設定
SECURE_MODE=true
API_KEY_ENCRYPTION=true
EOF

# Python setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="generate-prompt-ollama-plugin",
    version="1.0.0",
    description="Stable Diffusion WebUI plugin for automatic prompt enhancement via Ollama API",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "python-dotenv>=1.0.0",
        "gradio>=3.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
EOF

# .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 環境設定
.env
.env.local
.env.production
secrets/
credentials/

# IDE
.vscode/
.idea/
*.swp
*.swo

# ログ
logs/
*.log

# テスト
.coverage
.pytest_cache/
.tox/
htmlcov/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 一時ファイル
.tmp/
.cache/
EOF
```

## Phase 3: 基本的なCI/CD設定
```bash
# GitHub Actionsディレクトリ作成
mkdir -p .github/workflows

# CI/CDワークフロー設定
cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ master, feature/* ]
  pull_request:
    branches: [ master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: |
        black --check src/
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --coverage-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan-results.sarif'

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Build package
      run: |
        python setup.py sdist bdist_wheel
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist-packages
        path: dist/
EOF

# pre-commit設定
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
      - id: check-docstring-first
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127, --extend-ignore=E203,W503]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json
EOF

# pre-commitフック インストールスクリプト
cat > scripts/setup_hooks.py << 'EOF'
#!/usr/bin/env python3
"""Pre-commit hooks setup script"""

import subprocess
import sys

def install_pre_commit():
    """Install and setup pre-commit hooks"""
    try:
        # Install pre-commit
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pre-commit'], check=True)
        
        # Install the git hook scripts
        subprocess.run(['pre-commit', 'install'], check=True)
        
        # Run hooks on all files (optional)
        print("Installing pre-commit hooks...")
        subprocess.run(['pre-commit', 'run', '--all-files'], check=False)
        
        print("✅ Pre-commit hooks installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing pre-commit hooks: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_pre_commit()
EOF

chmod +x scripts/setup_hooks.py
```

## セットアップ実行手順

### 1. 基本構造作成
```bash
# Phase 1のコマンドを実行
bash -c "$(cat docs/setup-guide.md | grep -A 10 'Phase 1:' | tail -n +2)"
```

### 2. 設定ファイル作成
```bash
# Phase 2のコマンドを実行
bash -c "$(cat docs/setup-guide.md | grep -A 100 'Phase 2:' | head -n 50)"
```

### 3. CI/CD設定
```bash
# Phase 3のコマンドを実行
bash -c "$(cat docs/setup-guide.md | grep -A 200 'Phase 3:' | head -n 100)"
```