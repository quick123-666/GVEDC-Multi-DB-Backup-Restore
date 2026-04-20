"""
备份验证器
"""

import os
import json
import zipfile

from utils.logger import get_logger

logger = get_logger(__name__)

class Validator:
    """备份验证器"""
    
    def verify(self, backup_file):
        """
        验证备份文件
        
        Args:
            backup_file: 备份文件路径
        
        Returns:
            bool: 验证是否通过
        """
        try:
            logger.info(f"开始验证备份文件: {backup_file}")
            
            # 检查文件是否存在
            if not os.path.exists(backup_file):
                logger.error("备份文件不存在")
                return False
            
            # 检查文件是否为有效的zip文件
            if not self._is_valid_zip(backup_file):
                logger.error("备份文件不是有效的zip文件")
                return False
            
            # 检查备份信息
            if not self._verify_backup_info(backup_file):
                logger.error("备份信息验证失败")
                return False
            
            # 检查文件完整性
            if not self._verify_file_integrity(backup_file):
                logger.error("文件完整性验证失败")
                return False
            
            logger.info("备份文件验证通过")
            return True
            
        except Exception as e:
            logger.error(f"验证失败: {str(e)}")
            return False
    
    def _is_valid_zip(self, file_path):
        """检查文件是否为有效的zip文件"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zipf:
                return True
        except zipfile.BadZipFile:
            return False
    
    def _verify_backup_info(self, backup_file):
        """验证备份信息"""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # 检查是否包含backup_info.json
                if 'backup_info.json' not in zipf.namelist():
                    logger.error("备份文件中缺少backup_info.json")
                    return False
                
                # 读取备份信息
                with zipf.open('backup_info.json') as f:
                    backup_info = json.load(f)
                
                # 验证必要字段
                required_fields = ['backup_type', 'timestamp', 'version']
                for field in required_fields:
                    if field not in backup_info:
                        logger.error(f"备份信息缺少字段: {field}")
                        return False
                
                # 验证备份类型
                valid_types = ['chromadb', 'sqlite']
                if backup_info.get('backup_type') not in valid_types:
                    logger.error(f"无效的备份类型: {backup_info.get('backup_type')}")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"验证备份信息失败: {str(e)}")
            return False
    
    def _verify_file_integrity(self, backup_file):
        """验证文件完整性"""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # 测试所有文件
                zipf.testzip()
                return True
        except zipfile.BadZipFile:
            return False
        except Exception as e:
            logger.error(f"验证文件完整性失败: {str(e)}")
            return False