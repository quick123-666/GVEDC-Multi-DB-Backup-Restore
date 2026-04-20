#!/usr/bin/env python3
"""
增量备份管理模块
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class IncrementalBackupManager:
    """增量备份管理器"""
    
    def __init__(self, metadata_dir: str = "backups/metadata"):
        """
        初始化增量备份管理器
        
        Args:
            metadata_dir: 元数据存储目录
        """
        self.metadata_dir = metadata_dir
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def get_backup_metadata_path(self, db_name: str) -> str:
        """
        获取备份元数据文件路径
        
        Args:
            db_name: 数据库名称
        
        Returns:
            元数据文件路径
        """
        return os.path.join(self.metadata_dir, f"{db_name}_backup_metadata.json")
    
    def get_last_backup_metadata(self, db_name: str) -> Optional[Dict]:
        """
        获取上次备份的元数据
        
        Args:
            db_name: 数据库名称
        
        Returns:
            上次备份的元数据，如果不存在则返回None
        """
        metadata_path = self.get_backup_metadata_path(db_name)
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取备份元数据失败: {e}")
            return None
    
    def save_backup_metadata(self, db_name: str, file_metadata: Dict[str, Dict]) -> None:
        """
        保存备份元数据
        
        Args:
            db_name: 数据库名称
            file_metadata: 文件元数据字典
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "files": file_metadata
        }
        
        metadata_path = self.get_backup_metadata_path(db_name)
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存备份元数据失败: {e}")
    
    def get_changed_files(self, db_path: str, db_name: str) -> List[str]:
        """
        获取从上一次备份后发生变化的文件
        
        Args:
            db_path: 数据库路径
            db_name: 数据库名称
        
        Returns:
            发生变化的文件列表
        """
        last_metadata = self.get_last_backup_metadata(db_name)
        current_metadata = self._collect_file_metadata(db_path)
        
        # 如果是第一次备份，返回所有文件
        if not last_metadata:
            return list(current_metadata.keys())
        
        changed_files = []
        last_files = last_metadata.get('files', {})
        
        # 检查新增和修改的文件
        for file_path, current_meta in current_metadata.items():
            if file_path not in last_files:
                changed_files.append(file_path)
            else:
                last_meta = last_files[file_path]
                if current_meta['hash'] != last_meta['hash']:
                    changed_files.append(file_path)
        
        # 检查删除的文件（可选）
        # for file_path in last_files:
        #     if file_path not in current_metadata:
        #         print(f"文件已删除: {file_path}")
        
        return changed_files
    
    def _collect_file_metadata(self, db_path: str) -> Dict[str, Dict]:
        """
        收集文件元数据
        
        Args:
            db_path: 数据库路径
        
        Returns:
            文件元数据字典
        """
        metadata = {}
        
        for root, dirs, files in os.walk(db_path):
            # 排除一些不需要备份的目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for file in files:
                # 排除临时文件和日志文件
                if file.endswith(('.tmp', '.log')):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, db_path)
                
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    file_size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    
                    metadata[relative_path] = {
                        'hash': file_hash,
                        'size': file_size,
                        'mtime': mtime
                    }
                except Exception as e:
                    print(f"收集文件元数据失败 {file_path}: {e}")
        
        return metadata
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件哈希值
        """
        hash_obj = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"计算文件哈希失败 {file_path}: {e}")
            return ''
    
    def clean_metadata(self, db_name: str) -> None:
        """
        清理备份元数据
        
        Args:
            db_name: 数据库名称
        """
        metadata_path = self.get_backup_metadata_path(db_name)
        if os.path.exists(metadata_path):
            try:
                os.remove(metadata_path)
                print(f"已清理 {db_name} 的备份元数据")
            except Exception as e:
                print(f"清理备份元数据失败: {e}")
