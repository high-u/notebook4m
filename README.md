# notebook4m

ローカルのGGUF形式のLLMモデルを使用して対話するためのシンプルなPythonパッケージ。
Apple Silicon (Metal) とNVIDIA GPU (CUDA) の両方に対応しています。

## 機能

- ローカルのGGUF形式のLLMモデルを読み込み、対話
- チャット形式でのやり取り（Chat Completionモード）
- レスポンスのリアルタイムストリーミング表示
- Gitリポジトリの内容をLLMのコンテキストとして使用
- Apple Silicon (Metal) とNVIDIA GPU (CUDA) の両方に対応

## インストール

必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

開発モードでインストールする場合：

```bash
pip install -e .
```

## 使用方法

### 基本的な使い方

```bash
python -m notebook4m --model /path/to/your/model.gguf
```

または、インストール後：

```bash
notebook4m --model /path/to/your/model.gguf
```

### GPUアクセラレーション

Apple Silicon (M1/M2/M3) の場合：

```bash
notebook4m --model /path/to/your/model.gguf --gpu_type metal --n_gpu_layers -1
```

NVIDIA GPU の場合：

```bash
notebook4m --model /path/to/your/model.gguf --gpu_type cuda --n_gpu_layers -1
```

### コンテキストウィンドウサイズの調整

```bash
notebook4m --model /path/to/your/model.gguf --n_ctx 4096
```

### Gitリポジトリの内容をコンテキストとして使用

```bash
notebook4m --model /path/to/your/model.gguf --repo-path /path/to/your/repository
```

特定のファイルやディレクトリを無視する場合：

```bash
notebook4m --model /path/to/your/model.gguf --repo-path /path/to/your/repository --repo-ignore "*.log" "node_modules/"
```

## コマンドラインオプション

- `--model`: GGUF形式のモデルファイルへのパス（必須）
- `--n_ctx`: コンテキストウィンドウサイズ（デフォルト: 32768）
- `--n_gpu_layers`: GPUにオフロードするレイヤー数（-1: すべてのレイヤー）
- `--gpu_type`: GPUアクセラレーションの種類（none, metal, cuda, auto）
- `--temperature`: サンプリング温度（デフォルト: 0.7）
- `--max_tokens`: 生成する最大トークン数（デフォルト: 512）
- `--chat_format`: 使用するチャット形式（例: 'llama-2', 'chatml', 'gemma'）
- `--repo-path`: LLMに送信するGitリポジトリのパス
- `--repo-ignore`: リポジトリ処理時に無視するパターン（例: '*.log' 'node_modules/'）

## 終了方法

対話中にCtrl+Cを押すと、プログラムが正常に終了します。

## プロジェクト構造

```
notebook4m/
├── notebook4m/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llama_handler.py
│   │   └── repo_processor.py
│   └── utils/
│       └── __init__.py
├── data/
│   └── context.txt
├── tests/
│   └── __init__.py
├── setup.py
├── requirements.txt
└── README.md
```

## 依存パッケージ

- llama-cpp-python: ローカルLLMモデルの読み込みと実行
- prompt_toolkit: 入力履歴機能付きのプロンプト
- repo-to-text: Gitリポジトリの内容をテキスト形式に変換
