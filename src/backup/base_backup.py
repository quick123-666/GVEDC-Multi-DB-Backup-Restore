"""
基础备份类
"""

import os
import json
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime

from compression.base_compressor import BaseCompressor
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseBackup(ABC):
    """基础备份类"""
    
    def __init__(self, db_path, output_path, compression_level=9):
        """
        初始化备份实例
        
        Args:
            db_path: 数据库路径
            output_path: 备份文件输出路径
            compression_level: 压缩级别 (1-9)
        """
        self.db_path = db_path
        self.output_path = output_path
        self.compression_level = compression_level
        self.compressor = BaseCompressor(level=compression_level)
        
    @abstractmethod
    def backup(self):
        """执行备份操作"""
        pass
    
    def _prepare_backup(self):
        """准备备份环境"""
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"创建临时目录: {self.temp_dir}")
        
    def _cleanup(self):
        """清理临时文件"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"清理临时目录: {self.temp_dir}")
    
    def _create_backup_info(self, backup_type, file_count, total_size):
        """创建备份信息文件"""
        backup_info = {
            'backup_type': backup_type,
            'timestamp': datetime.now().isoformat(),
            'database_path': self.db_path,
            'file_count': file_count,
            'total_size': total_size,
            'compression_level': self.compression_level,
            'version': '1.0.0'
        }
        
        info_path = os.path.join(self.temp_dir, 'backup_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        return info_path
    
    def _compress_backup(self, files, output_file):
        """压缩备份文件"""
        logger.info(f"开始压缩备份文件，压缩级别: {self.compression_level}")
        
        # 创建压缩文件
        compressed_size = self.compressor.compress(files, output_file)
        
        logger.info(f"压缩完成，压缩文件大小: {compressed_size / 1024 / 1024:.2f} MB")
        return compressed_size
    
    def _get_file_size(self, path):
        """获取文件或目录大小"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total_size = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            return total_size
        return 0