"""
基础还原类
"""

import os
import json
import tempfile
from abc import ABC, abstractmethod

from compression.base_compressor import BaseCompressor
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseRestore(ABC):
    """基础还原类"""
    
    def __init__(self, backup_file, db_path):
        """
        初始化还原实例
        
        Args:
            backup_file: 备份文件路径
            db_path: 还原目标路径
        """
        self.backup_file = backup_file
        self.db_path = db_path
        self.compressor = BaseCompressor()
    
    @abstractmethod
    def restore(self):
        """执行还原操作"""
        pass
    
    def _prepare_restore(self):
        """准备还原环境"""
        # 检查备份文件
        if not os.path.exists(self.backup_file):
            raise FileNotFoundError(f"备份文件不存在: {self.backup_file}")
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"创建临时目录: {self.temp_dir}")
        
    def _cleanup(self):
        """清理临时文件"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"清理临时目录: {self.temp_dir}")
    
    def _extract_backup(self):
        """解压备份文件"""
        logger.info(f"开始解压备份文件: {self.backup_file}")
        
        # 解压到临时目录
        self.compressor.decompress(self.backup_file, self.temp_dir)
        
        logger.info("解压完成")
        
        # 读取备份信息
        info_path = os.path.join(self.temp_dir, 'backup_info.json')
        if not os.path.exists(info_path):
            raise ValueError("备份文件中缺少备份信息")
        
        with open(info_path, 'r', encoding='utf-8') as f:
            backup_info = json.load(f)
        
        logger.info(f"备份信息: {backup_info}")
        return backup_info
    
    def _validate_backup(self, backup_info):
        """验证备份文件"""
        logger.info("验证备份文件...")
        
        # 验证备份类型
        if backup_info.get('backup_type') != self._get_backup_type():
            raise ValueError(f"备份类型不匹配，期望: {self._get_backup_type()}, 实际: {backup_info.get('backup_type')}")
        
        # 验证版本
        version = backup_info.get('version', '0.0.0')
        if version not in ['1.0.0']:
            logger.warning(f"备份版本 {version} 可能与当前版本不兼容")
        
        logger.info("备份文件验证通过")
    
    @abstractmethod
    def _get_backup_type(self):
        """获取备份类型"""
        pass