"""
ChromaDB备份实现
"""

import os
import shutil
import concurrent.futures

from backup.base_backup import BaseBackup
from backup.incremental_backup import IncrementalBackupManager
from utils.logger import get_logger

logger = get_logger(__name__)

class ChromaDBBackup(BaseBackup):
    """ChromaDB备份类"""
    
    def __init__(self, db_path, output_path, compression_level=9, parallel=True, incremental=False, db_name=None):
        """
        初始化ChromaDB备份实例
        
        Args:
            db_path: ChromaDB数据库路径
            output_path: 备份文件输出路径
            compression_level: 压缩级别 (1-9)
            parallel: 是否使用并行处理
            incremental: 是否执行增量备份
            db_name: 数据库名称（用于增量备份元数据）
        """
        super().__init__(db_path, output_path, compression_level)
        self.parallel = parallel
        self.incremental = incremental
        self.db_name = db_name
        self.incremental_manager = IncrementalBackupManager() if incremental and db_name else None
    
    def backup(self):
        """执行ChromaDB备份"""
        try:
            # 准备备份
            self._prepare_backup()
            
            # 检查数据库路径
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"ChromaDB数据库路径不存在: {self.db_path}")
            
            # 收集需要备份的文件
            files_to_backup = self._collect_files()
            
            # 处理增量备份
            if self.incremental and self.incremental_manager:
                # 获取变化的文件
                changed_files = self.incremental_manager.get_changed_files(self.db_path, self.db_name)
                
                if not changed_files:
                    logger.info(f"没有检测到变化的文件，跳过备份: {self.db_name}")
                    return
                
                # 过滤出需要备份的变化文件
                files_to_backup = []
                for root, dirs, files in os.walk(self.db_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.db_path)
                        if relative_path in changed_files:
                            files_to_backup.append(file_path)
                
                logger.info(f"增量备份: 检测到 {len(files_to_backup)} 个变化的文件")
            
            # 复制文件到临时目录
            self._copy_files(files_to_backup)
            
            # 创建备份信息
            file_count = len(files_to_backup)
            total_size = sum(os.path.getsize(f) for f in files_to_backup)
            self._create_backup_info('chromadb', file_count, total_size)
            
            # 收集临时目录中的所有文件
            temp_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    temp_files.append(file_path)
            
            # 压缩备份
            self._compress_backup(temp_files, self.output_path)
            
            # 保存增量备份元数据
            if self.incremental and self.incremental_manager:
                file_metadata = self.incremental_manager._collect_file_metadata(self.db_path)
                self.incremental_manager.save_backup_metadata(self.db_name, file_metadata)
                logger.info(f"已保存增量备份元数据: {self.db_name}")
            
            logger.info(f"ChromaDB备份成功: {self.output_path}")
            
        except Exception as e:
            logger.error(f"ChromaDB备份失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self._cleanup()
    
    def _collect_files(self):
        """收集需要备份的文件"""
        files_to_backup = []
        
        # 收集chroma.sqlite3文件
        sqlite_file = os.path.join(self.db_path, 'chroma.sqlite3')
        if os.path.exists(sqlite_file):
            files_to_backup.append(sqlite_file)
            logger.info(f"添加文件到备份: {sqlite_file}")
        
        # 收集UUID目录中的文件
        for item in os.listdir(self.db_path):
            item_path = os.path.join(self.db_path, item)
            if os.path.isdir(item_path) and len(item) == 36:  # UUID格式
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        files_to_backup.append(file_path)
                        logger.debug(f"添加文件到备份: {file_path}")
        
        # 收集其他可能的配置文件
        for item in os.listdir(self.db_path):
            item_path = os.path.join(self.db_path, item)
            if os.path.isfile(item_path) and item not in ['chroma.sqlite3']:
                files_to_backup.append(item_path)
                logger.info(f"添加文件到备份: {item_path}")
        
        if not files_to_backup:
            raise ValueError(f"ChromaDB数据库路径中没有找到可备份的文件: {self.db_path}")
        
        logger.info(f"共收集到 {len(files_to_backup)} 个文件需要备份")
        return files_to_backup
    
    def _copy_files(self, files):
        """复制文件到临时目录"""
        logger.info(f"开始复制 {len(files)} 个文件到临时目录")
        
        if self.parallel and len(files) > 10:
            # 使用并行复制
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for file_path in files:
                    relative_path = os.path.relpath(file_path, self.db_path)
                    dest_path = os.path.join(self.temp_dir, relative_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    futures.append(executor.submit(self._copy_file, file_path, dest_path))
                
                # 等待所有复制完成
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"文件复制失败: {str(e)}")
                        raise
        else:
            # 串行复制
            for file_path in files:
                relative_path = os.path.relpath(file_path, self.db_path)
                dest_path = os.path.join(self.temp_dir, relative_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                self._copy_file(file_path, dest_path)
        
        logger.info("文件复制完成")
    
    def _copy_file(self, src, dst):
        """复制单个文件"""
        try:
            shutil.copy2(src, dst)
            logger.debug(f"复制文件: {src} -> {dst}")
        except Exception as e:
            logger.error(f"复制文件失败: {src} -> {dst}: {str(e)}")
            raise