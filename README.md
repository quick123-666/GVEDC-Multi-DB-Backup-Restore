# GVEDC-Multi-DB-Backup-Restore

## 1. 项目概述

GVEDC-Multi-DB-Backup-Restore 是一个企业级多数据库备份和还原解决方案，专为 ChromaDB、SQLite 等数据库设计，提供无损高压缩备份和智能增量备份功能。

### 1.1 核心价值

- **数据安全**：确保数据完整性，无数据丢失
- **存储优化**：高压缩率，节省存储空间
- **效率提升**：增量备份，只备份变化数据
- **可靠性**：自动备份验证，确保备份有效性
- **灵活性**：支持多数据库，跨平台兼容
- **智能决策**：基于文件变化自动判断备份范围

## 2. 技术架构

### 2.1 系统架构

| 模块 | 职责 | 文件位置 |
|------|------|----------|
| 备份模块 | 执行数据库备份 | `src/backup/` |
| 还原模块 | 执行数据库还原 | `src/restore/` |
| 压缩模块 | 处理文件压缩 | `src/compression/` |
| 验证模块 | 验证备份文件 | `src/validation/` |
| 增量备份 | 管理增量备份元数据 | `src/backup/incremental_backup.py` |
| 配置模块 | 管理配置文件 | `src/utils/config.py` |
| 日志模块 | 记录系统日志 | `src/utils/logger.py` |

### 2.2 数据流

1. **备份流程**：数据库 → 文件收集 → 增量检测 → 压缩 → 备份文件 → 元数据更新
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

### 3.3 配置说明

**备份配置示例**：
```yaml
global:
  compression_level: 9
  parallel: true
  verify: true

databases:
  - name: chromadb_main
    type: chromadb
    path: /path/to/chromadb
    output: /path/to/backup/chromadb_main_$(date).chroma
    incremental: true
```

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

### 4.4 增量备份

**自动增量备份**：
- 首次执行完整备份
- 后续备份只备份变化的文件
- 基于文件哈希值检测变化
- 自动更新备份元数据

## 5. 部署与集成

### 5.1 定时备份

**Windows 计划任务**：
1. 打开「任务计划程序」
2. 创建新任务，设置触发时间（如每天中午11点）
3. 操作设置为运行备份脚本

**示例脚本**：
```batch
@echo off
cd /d "C:\path\to\GVEDC-Multi-DB-Backup-Restore"
python main.py backup --config config/backup_config.yml
```

### 5.2 集成方案

- **CI/CD 集成**：在构建流程中添加备份步骤
- **监控系统**：与监控工具集成，监控备份状态
- **告警机制**：配置备份失败告警

## 6. 监控与维护

### 6.1 日志管理

- 日志文件存储在 `logs/` 目录
- 按日期分类，方便查看历史操作
- 包含详细的备份过程和错误信息

### 6.2 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 备份失败 | 数据库路径错误 | 检查数据库路径是否正确 |
| 还原失败 | 备份文件损坏 | 验证备份文件完整性 |
| 压缩错误 | 磁盘空间不足 | 确保目标磁盘有足够空间 |
| 增量备份失败 | 元数据文件损坏 | 删除元数据文件，重新执行完整备份 |

### 6.3 维护建议

- 定期检查备份文件完整性
- 定期清理过期备份文件
- 确保备份存储位置的安全性
- 测试还原流程，确保数据可恢复性

## 7. 贡献指南

### 7.1 开发环境

1. **克隆项目**
2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```
3. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 7.2 代码规范

- 遵循 PEP 8 编码规范
- 提交前运行代码检查
- 编写清晰的代码注释

### 7.3 提交流程

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送分支
5. 创建 Pull Request

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.1.1 | 2026-04-20 | 实现增量备份功能，优化备份效率 |
| 1.1.0 | 2026-04-20 | 修复路径错误，添加.gitignore文件 |
| 1.0.0 | 2026-04-20 | 初始版本，实现基本备份和还原功能 |

## 9. 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 10. 联系方式

- **项目地址**：https://github.com/quick123-666/GVEDC-Multi-DB-Backup-Restore
- **问题反馈**：https://github.com/quick123-666/GVEDC-Multi-DB-Backup-Restore/issues

---

**© 2026 GVEDC-Multi-DB-Backup-Restore. All rights reserved.**