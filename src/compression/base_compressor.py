"""
基础压缩类
"""

import os
import zipfile
from abc import ABC, abstractmethod

from utils.logger import get_logger

logger = get_logger(__name__)

class BaseCompressor(ABC):
    """基础压缩类"""
    
    def __init__(self, level=9):
        """
        初始化压缩器
        
        Args:
            level: 压缩级别 (1-9)
        """
        self.level = level
    
    def compress(self, files, output_file):
        """
        压缩文件
        
        Args:
            files: 文件列表
            output_file: 输出压缩文件路径
        
        Returns:
            压缩文件大小
        """
        logger.info(f"开始压缩 {len(files)} 个文件")
        
        # 使用zipfile作为默认压缩方式
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=self.level) as zipf:
            for file_path in files:
                # 计算相对路径
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
                logger.debug(f"添加文件到压缩包: {file_path} -> {arcname}")
        
        # 返回压缩文件大小
        compressed_size = os.path.getsize(output_file)
        logger.info(f"压缩完成，压缩文件大小: {compressed_size / 1024 / 1024:.2f} MB")
        return compressed_size
    
    def decompress(self, input_file, output_dir):
        """
        解压文件
        
        Args:
            input_file: 输入压缩文件路径
            output_dir: 输出目录
        """
        logger.info(f"开始解压文件: {input_file}")
        
        # 使用zipfile解压
        with zipfile.ZipFile(input_file, 'r') as zipf:
            zipf.extractall(output_dir)
            logger.debug(f"解压文件到: {output_dir}")
        
        logger.info("解压完成")