"""
SQLite还原实现
"""

import os
import shutil
import sqlite3

from restore.base_restore import BaseRestore
from utils.logger import get_logger

logger = get_logger(__name__)

class SQLiteRestore(BaseRestore):
    """SQLite还原类"""
    
    def __init__(self, backup_file, db_path):
        """
        初始化SQLite还原实例
        
        Args:
            backup_file: 备份文件路径
            db_path: 还原目标路径
        """
        super().__init__(backup_file, db_path)
    
    def restore(self):
        """执行SQLite还原"""
        try:
            # 准备还原
            self._prepare_restore()
            
            # 解压备份文件
            backup_info = self._extract_backup()
            
            # 验证备份
            self._validate_backup(backup_info)
            
            # 查找备份的SQLite文件
            sqlite_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    if file.endswith('.db') or file == 'chroma.sqlite3':
                        sqlite_files.append(os.path.join(root, file))
            
            if not sqlite_files:
                raise ValueError("备份文件中没有找到SQLite数据库文件")
            
            # 选择第一个SQLite文件
            backup_db_path = sqlite_files[0]
            logger.info(f"找到SQLite备份文件: {backup_db_path}")
            
            # 清理目标文件
            if os.path.exists(self.db_path):
                logger.warning(f"目标文件已存在，将被覆盖: {self.db_path}")
                os.remove(self.db_path)
            
            # 执行SQLite在线还原
            self._sqlite_restore(backup_db_path, self.db_path)
            
            logger.info(f"SQLite还原成功: {self.db_path}")
            
        except Exception as e:
            logger.error(f"SQLite还原失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self._cleanup()
    
    def _get_backup_type(self):
        """获取备份类型"""
        return 'sqlite'
    
    def _sqlite_restore(self, src_db, dest_db):
        """执行SQLite在线还原
        
        使用SQLite的在线备份API，确保还原过程的安全性
        """
        logger.info(f"开始SQLite在线还原: {src_db} -> {dest_db}")
        
        # 连接源数据库
        src_conn = sqlite3.connect(src_db)
        
        # 连接目标数据库
        dest_conn = sqlite3.connect(dest_db)
        
        try:
            # 开始还原
            src_conn.backup(dest_conn)
            logger.info("SQLite还原完成")
        finally:
            # 关闭连接
            src_conn.close()
            dest_conn.close()