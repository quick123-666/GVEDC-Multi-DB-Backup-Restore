# GVEDC-Multi-DB-Backup-Restore

## 1. 项目概述

GVEDC-Multi-DB-Backup-Restore 是一个企业级多数据库备份和还原解决方案，专为 ChromaDB、SQLite 等数据库设计，提供无损高压缩备份功能。

### 1.1 核心价值

- **数据安全**：确保数据完整性，无数据丢失
- **存储优化**：高压缩率，节省存储空间
- **效率提升**：增量备份，只备份变化数据
- **可靠性**：自动备份验证，确保备份有效性
- **灵活性**：支持多数据库，跨平台兼容

## 2. 技术架构

### 2.1 系统架构

| 模块 | 职责 | 文件位置 |
|------|------|----------|
| 备份模块 | 执行数据库备份 | `src/backup/` |
| 还原模块 | 执行数据库还原 | `src/restore/` |
| 压缩模块 | 处理文件压缩 | `src/compression/` |
| 验证模块 | 验证备份文件 | `src/validation/` |
| 配置模块 | 管理配置文件 | `src/utils/config.py` |
| 日志模块 | 记录系统日志 | `src/utils/logger.py` |

### 2.2 数据流

1. **备份流程**：数据库 → 文件收集 → 压缩 → 备份文件
2. **还原流程**：备份文件 → 解压 → 验证 → 数据库还原

## 3. 安装与配置

### 3.1 系统要求

- Python 3.8+
- 足够的磁盘空间用于备份存储
- 网络连接（用于依赖安装）

### 3.2 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/quick123-666/GVEDC-Multi-DB-Backup-Restore.git
   cd GVEDC-Multi-DB-Backup-Restore
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置文件**
   - 编辑 `config/backup_config.yml` 设置备份参数
   - 编辑 `config/restore_config.yml` 设置还原参数

## 4. 使用指南

### 4.1 备份操作

**命令格式**：
```bash
python main.py backup [选项]
```

**示例**：
- 备份 ChromaDB：
  ```bash
  python main.py backup --db-type chromadb --db-path /path/to/chroma --output backup.chroma
  ```

- 使用配置文件：
  ```bash
  python main.py backup --config config/backup_config.yml
  ```

### 4.2 还原操作

**命令格式**：
```bash
python main.py restore [选项]
```

**示例**：
- 还原 ChromaDB：
  ```bash
  python main.py restore --db-type chromadb --backup-file backup.chroma --db-path /path/to/chroma
  ```

- 使用配置文件：
  ```bash
  python main.py restore --config config/restore_config.yml
  ```

### 4.3 验证操作

**命令格式**：
```bash
python main.py verify --backup-file <备份文件>
```

## 5. 监控与维护

### 5.1 日志管理

- 日志文件存储在 `logs/` 目录
- 按日期分类，方便查看历史操作

### 5.2 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 备份失败 | 数据库路径错误 | 检查数据库路径是否正确 |
| 还原失败 | 备份文件损坏 | 验证备份文件完整性 |
| 压缩错误 | 磁盘空间不足 | 确保目标磁盘有足够空间 |

## 6. 版本信息

- **版本**：1.1.0
- **发布日期**：2026-04-20
- **状态**：正式发布

## 7. 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。