#!/usr/bin/env python3
"""
gitリポジトリの構造とファイル内容をLLMに理解しやすい形式で出力するモジュール
repo-to-textライブラリを使用して、リポジトリの内容をLLMが理解しやすい形式に変換します。
変換された内容はファイルに保存され、ユーザーが必要に応じてLLMへのプロンプトに含めることができます。
"""

__all__ = ['RepoProcessor']

import os
import logging
from typing import Optional, List
from repo_to_text.core.core import save_repo_to_text

class RepoProcessor:
    """
    gitリポジトリを処理し、構造とファイル内容を単一のテキストファイルに変換するクラス
    """
    
    def __init__(self, debug: bool = False):
        """
        RepoProcessorの初期化
        
        Args:
            debug: デバッグモードを有効にするかどうか
        """
        self.debug = debug
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def process_repository(self, 
                          repo_path: str, 
                          output_dir: Optional[str] = None,
                          output_file: Optional[str] = None,
                          ignore_patterns: Optional[List[str]] = None,
                          to_stdout: bool = False) -> str:
        """
        リポジトリを処理し、構造とファイル内容を単一のテキストファイルに変換
        
        Args:
            repo_path: 処理するリポジトリのパス
            output_dir: 出力ファイルを保存するディレクトリ
            output_file: 出力ファイルの名前（指定しない場合は自動生成）
            ignore_patterns: 無視するファイルやディレクトリのパターンのリスト
            to_stdout: 標準出力に結果を出力するかどうか
            
        Returns:
            str: 生成されたファイルのパス、またはto_stdout=Trueの場合は生成されたコンテンツ
        """
        self.logger.info(f"リポジトリを処理しています: {repo_path}")
        
        # repo_pathが存在するか確認
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"指定されたパスが存在しません: {repo_path}")
        
        # repo-to-textのsave_repo_to_text関数を呼び出し
        try:
            # If output_file is specified, use it directly
            if output_file and not to_stdout:
                result = save_repo_to_text(
                    path=repo_path,
                    output_path=output_file,
                    to_stdout=to_stdout,
                    cli_ignore_patterns=ignore_patterns
                )
            else:
                # Use original behavior with output_dir
                result = save_repo_to_text(
                    path=repo_path,
                    output_dir=output_dir,
                    to_stdout=to_stdout,
                    cli_ignore_patterns=ignore_patterns
                )
            
            if to_stdout:
                self.logger.info("リポジトリの処理が完了し、コンテンツを返します")
            else:
                self.logger.info(f"リポジトリの処理が完了し、結果を保存しました: {result}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"リポジトリの処理中にエラーが発生しました: {str(e)}")
            raise
    
    def get_repository_content(self, repo_path: str, 
                              ignore_patterns: Optional[List[str]] = None,
                              output_file: Optional[str] = None) -> str:
        """
        リポジトリの内容を文字列として取得
        
        Args:
            repo_path: 処理するリポジトリのパス
            ignore_patterns: 無視するファイルやディレクトリのパターンのリスト
            output_file: 出力ファイルの名前（指定した場合はファイルに保存も行う）
            
        Returns:
            str: リポジトリの内容を表す文字列
        """
        # 文字列として取得するためにto_stdout=Trueで処理
        content = self.process_repository(
            repo_path=repo_path,
            ignore_patterns=ignore_patterns,
            to_stdout=True
        )
        
        # output_fileが指定されている場合は、ファイルにも保存
        if output_file:
            self.logger.info(f"リポジトリの内容を {output_file} に保存しています")
            # ディレクトリパスが存在する場合のみ作成
            dir_path = os.path.dirname(output_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"リポジトリの内容を {output_file} に保存しました")
            
        return content
