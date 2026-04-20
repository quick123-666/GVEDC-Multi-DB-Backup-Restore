#!/usr/bin/env python3
"""
多数据库备份和还原系统主入口
"""

import argparse
import yaml
import os
import sys
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from backup.chromadb_backup import ChromaDBBackup
from backup.sqlite_backup import SQLiteBackup
from restore.chromadb_restore import ChromaDBRestore
from restore.sqlite_restore import SQLiteRestore
from validation.validator import Validator
from compression.base_compressor import BaseCompressor
from utils.config import load_config
from utils.logger import get_logger

logger = get_logger(__name__)

def backup(args):
    """执行备份操作"""
    if args.config:
        # 使用配置文件
        config = load_config(args.config)
        global_config = config.get('global', {})
        databases = config.get('databases', [])
        
        for db_config in databases:
            db_name = db_config.get('name')
            db_type = db_config.get('type')
            db_path = db_config.get('path')
            output = db_config.get('output')
            
            # 处理日期占位符
            if '$(date)' in output:
                output = output.replace('$(date)', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output), exist_ok=True)
            
            logger.info(f"开始备份数据库: {db_name} ({db_type})")
            
            try:
                if db_type == 'chromadb':
                    backup_instance = ChromaDBBackup(
                        db_path=db_path,
                        output_path=output,
                        compression_level=global_config.get('compression_level', 9),
                        parallel=global_config.get('parallel', True)
                    )
                    backup_instance.backup()
                elif db_type == 'sqlite':
                    backup_instance = SQLiteBackup(
                        db_path=db_path,
                        output_path=output,
                        compression_level=global_config.get('compression_level', 9)
                    )
                    backup_instance.backup()
                else:
                    logger.error(f"不支持的数据库类型: {db_type}")
                    continue
                
                if global_config.get('verify', True):
                    validator = Validator()
                    if validator.verify(output):
                        logger.info(f"备份验证成功: {output}")
                    else:
                        logger.warning(f"备份验证失败: {output}")
                        
                logger.info(f"备份完成: {output}")
            except Exception as e:
                logger.error(f"备份失败: {str(e)}")
    else:
        # 单个数据库备份
        # 确保输出目录存在
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        if args.db_type == 'chromadb':
            backup_instance = ChromaDBBackup(
                db_path=args.db_path,
                output_path=args.output,
                compression_level=9,
                parallel=True
            )
            backup_instance.backup()
        elif args.db_type == 'sqlite':
            backup_instance = SQLiteBackup(
                db_path=args.db_path,
                output_path=args.output,
                compression_level=9
            )
            backup_instance.backup()
        else:
            logger.error(f"不支持的数据库类型: {args.db_type}")
            return
        
        # 验证备份
        validator = Validator()
        if validator.verify(args.output):
            logger.info(f"备份验证成功: {args.output}")
        else:
            logger.warning(f"备份验证失败: {args.output}")

def restore(args):
    """执行还原操作"""
    if args.config:
        # 使用配置文件
        config = load_config(args.config)
        databases = config.get('databases', [])
        
        for db_config in databases:
            db_name = db_config.get('name')
            db_type = db_config.get('type')
            backup_file = db_config.get('backup_file')
            db_path = db_config.get('path')
            
            logger.info(f"开始还原数据库: {db_name} ({db_type})")
            
            try:
                if db_type == 'chromadb':
                    restore_instance = ChromaDBRestore(
                        backup_file=backup_file,
                        db_path=db_path
                    )
                    restore_instance.restore()
                elif db_type == 'sqlite':
                    restore_instance = SQLiteRestore(
                        backup_file=backup_file,
                        db_path=db_path
                    )
                    restore_instance.restore()
                else:
                    logger.error(f"不支持的数据库类型: {db_type}")
                    continue
                
                logger.info(f"还原完成: {db_path}")
            except Exception as e:
                logger.error(f"还原失败: {str(e)}")
    else:
        # 单个数据库还原
        if args.db_type == 'chromadb':
            restore_instance = ChromaDBRestore(
                backup_file=args.backup_file,
                db_path=args.db_path
            )
            restore_instance.restore()
        elif args.db_type == 'sqlite':
            restore_instance = SQLiteRestore(
                backup_file=args.backup_file,
                db_path=args.db_path
            )
            restore_instance.restore()
        else:
            logger.error(f"不支持的数据库类型: {args.db_type}")
            return

def verify(args):
    """验证备份文件"""
    validator = Validator()
    if validator.verify(args.backup_file):
        logger.info(f"备份验证成功: {args.backup_file}")
    else:
        logger.error(f"备份验证失败: {args.backup_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='多数据库备份和还原系统')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='执行备份操作')
    backup_parser.add_argument('--config', type=str, help='备份配置文件路径')
    backup_parser.add_argument('--db-type', type=str, choices=['chromadb', 'sqlite'], help='数据库类型')
    backup_parser.add_argument('--db-path', type=str, help='数据库路径')
    backup_parser.add_argument('--output', type=str, help='备份文件输出路径')
    backup_parser.add_argument('--incremental', type=str, help='增量备份的基础备份文件')
    
    # 还原命令
    restore_parser = subparsers.add_parser('restore', help='执行还原操作')
    restore_parser.add_argument('--config', type=str, help='还原配置文件路径')
    restore_parser.add_argument('--db-type', type=str, choices=['chromadb', 'sqlite'], help='数据库类型')
    restore_parser.add_argument('--backup-file', type=str, help='备份文件路径')
    restore_parser.add_argument('--db-path', type=str, help='还原目标路径')
    
    # 验证命令
    verify_parser = subparsers.add_parser('verify', help='验证备份文件')
    verify_parser.add_argument('--backup-file', type=str, required=True, help='备份文件路径')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup(args)
    elif args.command == 'restore':
        restore(args)
    elif args.command == 'verify':
        verify(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()