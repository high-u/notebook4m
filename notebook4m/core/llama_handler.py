#!/usr/bin/env python3
"""
llama-cpp-pythonを使用してローカルLLMを処理するモジュール
"""

__all__ = ['LlamaHandler']

import platform
import os
from llama_cpp import Llama

class LlamaHandler:
    def __init__(self):
        self.llm = None
        
    def load_model(self, model_path, n_ctx=2048, n_gpu_layers=0, gpu_type="auto", 
                  chat_format=None, temperature=0.7, verbose=True):
        """モデルを読み込む"""
        # GPUタイプの自動検出
        if gpu_type == "auto":
            if platform.system() == "Darwin" and platform.processor() == "arm":
                gpu_type = "metal"
            elif os.environ.get("CUDA_VISIBLE_DEVICES") is not None or os.path.exists("/usr/local/cuda"):
                gpu_type = "cuda"
            else:
                gpu_type = "none"
        
        # n_gpu_layersの設定
        if n_gpu_layers != 0 and gpu_type == "none":
            print("Warning: n_gpu_layers is set but GPU acceleration is disabled. Setting n_gpu_layers to 0.")
            n_gpu_layers = 0
        
        # モデルパラメータの設定
        print(f"Loading model from {model_path}...")
        print(f"GPU acceleration: {gpu_type.upper() if gpu_type != 'none' else 'Disabled'} (n_gpu_layers={n_gpu_layers})")
        
        model_params = {
            "model_path": model_path,
            "n_ctx": n_ctx,
            "n_gpu_layers": n_gpu_layers,
            "chat_format": chat_format,
            "verbose": verbose
        }
        
        # GPUタイプに応じたパラメータ追加
        if gpu_type == "metal":
            model_params["use_mlock"] = True
            model_params["use_metal"] = True
        elif gpu_type == "cuda":
            model_params["use_mlock"] = True
        
        # モデルの読み込み
        self.llm = Llama(**model_params)
        print("Model loaded successfully!")
        return self.llm
    
    def generate_response(self, messages, max_tokens=512, temperature=0.7, stream=True):
        """レスポンスを生成する"""
        if self.llm is None:
            raise ValueError("Model not loaded. Call load_model first.")
        
        if stream:
            return self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
        else:
            return self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
    
    def cleanup(self):
        """リソースを解放する"""
        if self.llm is not None:
            del self.llm
            self.llm = None
