"""
SQLite备份实现
"""

import os
import shutil
import sqlite3

from backup.base_backup import BaseBackup
from utils.logger import get_logger

logger = get_logger(__name__)

class SQLiteBackup(BaseBackup):
    """SQLite备份类"""
    
    def __init__(self, db_path, output_path, compression_level=9):
        """
        初始化SQLite备份实例
        
        Args:
            db_path: SQLite数据库文件路径
            output_path: 备份文件输出路径
            compression_level: 压缩级别 (1-9)
        """
        super().__init__(db_path, output_path, compression_level)
    
    def backup(self):
        """执行SQLite备份"""
        try:
            # 准备备份
            self._prepare_backup()
            
            # 检查数据库文件
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"SQLite数据库文件不存在: {self.db_path}")
            
            if not self._is_sqlite_db(self.db_path):
                raise ValueError(f"文件不是有效的SQLite数据库: {self.db_path}")
            
            # 执行SQLite在线备份
            backup_db_path = os.path.join(self.temp_dir, os.path.basename(self.db_path))
            self._sqlite_backup(self.db_path, backup_db_path)
            
            # 创建备份信息
            file_count = 1
            total_size = os.path.getsize(self.db_path)
            self._create_backup_info('sqlite', file_count, total_size)
            
            # 收集临时目录中的所有文件
            temp_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    temp_files.append(file_path)
            
            # 压缩备份
            self._compress_backup(temp_files, self.output_path)
            
            logger.info(f"SQLite备份成功: {self.output_path}")
            
        except Exception as e:
            logger.error(f"SQLite备份失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self._cleanup()
    
    def _is_sqlite_db(self, file_path):
        """检查文件是否为有效的SQLite数据库"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            return header == b'SQLite format 3\x00'
        except:
            return False
    
    def _sqlite_backup(self, src_db, dest_db):
        """执行SQLite在线备份
        
        使用SQLite的在线备份API，确保备份过程中数据库可以正常使用
        """
        logger.info(f"开始SQLite在线备份: {src_db} -> {dest_db}")
        
        # 连接源数据库
        src_conn = sqlite3.connect(src_db)
        
        # 连接目标数据库
        dest_conn = sqlite3.connect(dest_db)
        
        try:
            # 开始备份
            src_conn.backup(dest_conn)
            logger.info("SQLite备份完成")
        finally:
            # 关闭连接
            src_conn.close()
            dest_conn.close()