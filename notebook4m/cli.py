#!/usr/bin/env python3
"""
notebook4m CLI - ローカルLLMとチャットするためのコマンドラインインターフェース
"""

import argparse
import os
import signal
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from notebook4m.core.llama_handler import LlamaHandler
from notebook4m.core.repo_processor import RepoProcessor

# 定数定義
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
CONTEXT_SYSTEM_PROMPT = "You are an assistant that can only answer questions based on the content provided below:"
CONTEXT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "context.txt")

# グローバル変数としてLlamaHandlerを定義
llama_handler = None

# Ctrl+Cシグナルハンドラ
def signal_handler(sig, frame):
    """Ctrl+Cが押された時のシグナルハンドラ"""
    global llama_handler
    print("\n\nプログラムを終了しています...")
    # モデルのリソースを解放
    try:
        if llama_handler is not None:
            llama_handler.cleanup()
    except:
        pass
    print("正常に終了しました。")
    # 例外スタックトレースを表示せずに終了
    os._exit(0)

# シグナルハンドラを登録
signal.signal(signal.SIGINT, signal_handler)

def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="Interact with a local LLM using llama-cpp-python")
    parser.add_argument("--model", type=str, required=True, help="Path to the GGUF model file")
    parser.add_argument("--n_ctx", type=int, default=32768, help="Context window size")
    parser.add_argument("--n_gpu_layers", type=int, default=0, 
                        help="Number of layers to offload to GPU (-1 for all layers)")
    parser.add_argument("--gpu_type", type=str, choices=["none", "metal", "cuda", "auto"], default="auto",
                        help="GPU acceleration type: none, metal (Apple Silicon), cuda (NVIDIA), or auto (detect)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--max_tokens", type=int, default=512, help="Maximum number of tokens to generate")
    parser.add_argument("--chat_format", type=str, default=None, 
                        help="Chat format to use (e.g., 'llama-2', 'chatml', 'gemma')")
    parser.add_argument("--repo-path", type=str, default=None,
                        help="Path to a git repository to process and send to the LLM")
    parser.add_argument("--repo-ignore", type=str, nargs="*", default=None,
                        help="Patterns to ignore when processing repository (e.g., '*.log' 'node_modules/')")
    return parser.parse_args()


def load_model(args):
    """LlamaHandlerを初期化してモデルを読み込む"""
    global llama_handler
    llama_handler = LlamaHandler()
    llama_handler.load_model(
        model_path=args.model,
        n_ctx=args.n_ctx,
        n_gpu_layers=args.n_gpu_layers,
        gpu_type=args.gpu_type,
        chat_format=args.chat_format,
        temperature=args.temperature
    )


def read_context_file(file_path):
    """コンテキストファイルを読み込み、システムメッセージを生成する"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # システムメッセージを生成
        system_message = f"{CONTEXT_SYSTEM_PROMPT}\n\n{content}"
        print(f"{file_path}の内容をシステムメッセージとして読み込みました。")
        return system_message
    except Exception as e:
        print(f"{file_path}の読み込み中にエラーが発生しました: {str(e)}")
        return DEFAULT_SYSTEM_PROMPT


def process_repository(repo_path, ignore_patterns):
    """リポジトリを処理してcontext.txtに保存する"""
    try:
        print(f"\nリポジトリを処理しています: {repo_path}...")
        repo_processor = RepoProcessor(debug=False)
        
        # リポジトリを処理してファイルに保存
        repo_processor.get_repository_content(
            repo_path=repo_path,
            ignore_patterns=ignore_patterns,
            output_file=CONTEXT_FILE
        )
        
        print(f"リポジトリの処理が完了しました。内容は {CONTEXT_FILE} に保存されました。")
        
        # 処理したファイルを読み込む
        return read_context_file(CONTEXT_FILE)
    except Exception as e:
        print(f"リポジトリの処理中にエラーが発生しました: {str(e)}\n")
        return DEFAULT_SYSTEM_PROMPT


def load_existing_context():
    """既存のcontext.txtファイルを読み込む"""
    if os.path.exists(CONTEXT_FILE):
        return read_context_file(CONTEXT_FILE)
    
    return DEFAULT_SYSTEM_PROMPT


def chat_loop(args, messages):
    """チャットループを実行する"""
    # プロンプトセッションの初期化
    history_file = os.path.expanduser("~/.notebook4m_history")
    session = PromptSession(history=FileHistory(history_file))
    
    try:
        while True:
            # ユーザー入力を取得
            user_input = session.prompt("> ").strip()
            
            # 空の入力はスキップ
            if not user_input:
                continue
            
            # ユーザーメッセージを会話履歴に追加
            messages.append({"role": "user", "content": user_input})
            
            print("\n生成中...", end="", flush=True)
            print("\n\n")
            
            # ストリーミングモードで応答を生成
            response_content = process_response(args, messages)
            
            # 最終的な応答をメッセージ履歴に追加
            assistant_message = {"role": "assistant", "content": response_content}
            messages.append(assistant_message)
            print("\n")
    except KeyboardInterrupt:
        # Ctrl+Cが押された場合、シグナルハンドラが処理する
        signal_handler(signal.SIGINT, None)
    finally:
        # プログラム終了時にモデルのリソースを解放
        cleanup_resources()


def process_response(args, messages):
    """LLMからの応答を処理する"""
    response_content = ""
    
    # ストリーミング応答を処理
    for chunk in llama_handler.generate_response(
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        stream=True  # ストリーミングを有効化
    ):
        # チャンクから新しいコンテンツを取得
        if len(chunk["choices"]) > 0:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                content_chunk = delta["content"]
                response_content += content_chunk
                # リアルタイムで出力（改行なし、バッファをフラッシュ）
                print(content_chunk, end="", flush=True)
    
    return response_content


def cleanup_resources():
    """リソースを解放する"""
    global llama_handler
    try:
        if llama_handler is not None:
            llama_handler.cleanup()
            print("\nモデルのリソースを解放しました。")
    except:
        pass


def main():
    """メイン関数"""
    # コマンドライン引数の解析
    args = parse_arguments()
    
    # モデルの読み込み
    load_model(args)
    
    # チャットモードの開始
    print("\n=== Chat Completion ===\n")
    
    # メッセージリストの初期化
    messages = []
    
    # リポジトリの処理またはコンテキストの読み込み
    if args.repo_path:
        # リポジトリが指定されている場合は処理して保存
        system_message = process_repository(args.repo_path, args.repo_ignore)
    else:
        # リポジトリが指定されていない場合は既存のcontext.txtを読み込む
        system_message = load_existing_context()
    
    # システムメッセージを追加
    messages.append({"role": "system", "content": system_message})
    
    # チャットループの実行
    chat_loop(args, messages)


if __name__ == "__main__":
    main()
