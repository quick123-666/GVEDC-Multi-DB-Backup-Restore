"""
ChromaDB还原实现
"""

import os
import shutil
import concurrent.futures

from restore.base_restore import BaseRestore
from utils.logger import get_logger

logger = get_logger(__name__)

class ChromaDBRestore(BaseRestore):
    """ChromaDB还原类"""
    
    def __init__(self, backup_file, db_path):
        """
        初始化ChromaDB还原实例
        
        Args:
            backup_file: 备份文件路径
            db_path: 还原目标路径
        """
        super().__init__(backup_file, db_path)
    
    def restore(self):
        """执行ChromaDB还原"""
        try:
            # 准备还原
            self._prepare_restore()
            
            # 解压备份文件
            backup_info = self._extract_backup()
            
            # 验证备份
            self._validate_backup(backup_info)
            
            # 清理目标目录
            if os.path.exists(self.db_path):
                logger.warning(f"目标目录已存在，将被覆盖: {self.db_path}")
                shutil.rmtree(self.db_path)
            
            # 创建目标目录
            os.makedirs(self.db_path, exist_ok=True)
            
            # 复制文件到目标目录
            self._copy_files()
            
            logger.info(f"ChromaDB还原成功: {self.db_path}")
            
        except Exception as e:
            logger.error(f"ChromaDB还原失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self._cleanup()
    
    def _get_backup_type(self):
        """获取备份类型"""
        return 'chromadb'
    
    def _copy_files(self):
        """复制文件到目标目录"""
        # 收集临时目录中的所有文件（除了backup_info.json）
        files_to_copy = []
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file == 'backup_info.json':
                    continue
                file_path = os.path.join(root, file)
                files_to_copy.append(file_path)
        
        logger.info(f"开始复制 {len(files_to_copy)} 个文件到目标目录")
        
        # 并行复制
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for file_path in files_to_copy:
                relative_path = os.path.relpath(file_path, self.temp_dir)
                dest_path = os.path.join(self.db_path, relative_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                futures.append(executor.submit(self._copy_file, file_path, dest_path))
            
            # 等待所有复制完成
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"文件复制失败: {str(e)}")
                    raise
        
        logger.info("文件复制完成")
    
    def _copy_file(self, src, dst):
        """复制单个文件"""
        try:
            shutil.copy2(src, dst)
            logger.debug(f"复制文件: {src} -> {dst}")
        except Exception as e:
            logger.error(f"复制文件失败: {src} -> {dst}: {str(e)}")
            raise