# 🍂 晚秋记账

一款运行在 Windows 上的个人记账桌面应用，界面简洁、操作直观，支持记录人民币收支并管理分类。

> **数据完全本地化** — 所有记账数据保存在你的电脑上，不上传任何服务器。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-32%20passed-brightgreen.svg)](test_main.py)

---

## ✨ 功能

- **记一笔** — 输入金额、选择支出/收入、分类、日期，一键提交
- **账单列表** — 按时间倒序展示所有记录，支持按月份筛选、编辑和删除
- **月度统计** — 支出/收入/结余汇总卡片 + 饼图展示各分类占比
- **分类管理** — 12 个预设分类 + 支持自定义新增、编辑、删除分类
- **🎮 贪吃蛇** — 工作累了？来一局贪吃蛇小游戏放松一下（侧边栏底部进入）

---

## 🖥 界面预览

```
┌──────────┐  ┌─────────────────────────────┐
│  🍂 晚秋  │  │  记一笔                       │
│  记账    │  │                             │
│          │  │  金额  [______________]      │
│  记一笔   │  │  类型  [支出 ▾]  分类  [餐饮 ▾] │
│  账单列表 │  │  日期  [2024-07-04 ▾]        │
│  月度统计 │  │  备注  [______________]      │
│  分类管理 │  │                             │
│          │  │  [  ➕ 提交记录  ]            │
│  当月支出 │  └─────────────────────────────┘
│  ¥ 0.00  │
└──────────┘
```

---

## 🛠 技术栈

| 组件 | 用途 | 说明 |
|------|------|------|
| Python 3 | 编程语言 | 语法简单，Windows 安装便捷 |
| PyQt6 | 桌面界面框架 | 提供窗口、按钮、表格等控件 |
| SQLite | 本地数据库 | Python 内置，无需额外安装 |
| Matplotlib | 图表绘制 | 月度统计页的饼图 |

---

## 🚀 快速开始

### 环境要求

- Windows 系统
- Python 3.8 或更高版本

### 安装依赖

```bash
pip install PyQt6 matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 注：`-i` 参数指定使用清华镜像源，国内下载更快。如果不需要可以去掉。

### 启动应用

```bash
python main.py
```

---

## 🤖 Claude Code 用户

如果你使用 [Claude Code](https://claude.ai/code)，本项目内置了多个快捷命令，让你无需手动敲命令行：

### 项目技能（仅本项目可用）

| 命令 | 功能 | 说明 |
|------|------|------|
| `/start` | 一键启动 | 自动检查依赖 → 安装 → 启动应用 |
| `/rebuild-app` | 重新打包 | 用 PyInstaller 将应用打包成独立 `.exe` 文件 |
| `/unit-test` | 单元测试 | 分析代码 → 编写测试 → 运行 → 生成报告 |
| `/comments-check` | 注释检查 | 检查代码注释覆盖率、注释是否与代码一致、是否通俗易懂 |
| `/security-audit` | 安全审计 | 检查 SQL 注入、硬编码密钥、危险函数等安全隐患 |

### 全局技能（所有项目可用）

| 命令 | 功能 | 说明 |
|------|------|------|
| `/git-save` | Git 存档 | 一键暂存 → 提交 → 推送到 GitHub |

### 子代理

| 名称 | 功能 | 说明 |
|------|------|------|
| `tester` | 测试工程师 | 自动分析代码并补充单元测试，运行后自动写入测试通行证 |
| `quality-engineer` | 质量工程师 | 从安全、注释、规范、错误处理、性能五个维度审计代码质量 |
| `gitcommit-agent` | 提交门禁 | 调度 tester + quality-engineer，两项通过后颁发通行证 |

---

## 🚧 Git 提交门禁

本项目配置了 Git 提交门禁系统，确保每次提交的代码都通过了**单元测试**和**代码质量检查**。

### 工作流程

```
改代码 → /gitcommit → ✅ 通行证 → /git-save → 提交成功
```

1. **`/gitcommit`** — 自动运行 tester（单元测试）和 quality-engineer（质量检查），两项通过后颁发"通行证"
2. **`/git-save`** — 提交时，pre-commit hook 检查通行证，有则放行，没有则拦截
3. **自动清理** — 提交成功后，post-commit hook 自动删除旧通行证，下次提交必须重新检查

### 通行证标准

| 检查项 | 通过标准 |
|--------|---------|
| 单元测试 | 全部用例通过（当前 32 个） |
| 代码质量 | 总分 ≥ 70/100（B 级及以上） |

> 💡 如果直接执行 `git commit` 或 `/git-save` 而没有事先运行 `/gitcommit`，提交会被拦截并提示先获取通行证。

---

## 📦 打包为独立 EXE

无需安装 Python 也能运行，适合分享给朋友或在其他电脑上使用：

```bash
# 安装打包工具（只需一次）
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

# 打包
pyinstaller --onefile --windowed --name "晚秋记账" main.py
```

打包完成后，在 `dist/` 目录下找到 `晚秋记账.exe`（约 67MB），双击即可运行。

> 💡 Claude Code 用户直接输入 `/rebuild-app` 即可自动完成打包。

---

## 🧪 单元测试

本项目包含 32 个单元测试用例，覆盖数据库初始化和所有增删改查操作：

```bash
# 安装测试工具（只需一次）
pip install pytest -i https://pypi.tuna.tsinghua.edu.cn/simple

# 运行测试
python -m pytest test_main.py -v
```

测试覆盖范围：

| 模块 | 测试数 | 内容 |
|------|--------|------|
| 数据库初始化 | 5 | 目录创建、文件生成、表结构、预设分类、重复初始化保护 |
| 分类管理 | 8 | 增删改查 + 预设分类保护（不可删除/修改预设分类） |
| 账单记录 | 10 | 支出/收入添加、金额校验、月份筛选、日期排序、编辑、删除 |
| 月度统计 | 5 | 空月份、支出合计、收入合计、分类占比排序、月份隔离 |
| 边界情况 | 2 | 大额金额（近1亿）、特殊字符分类名 |
| 颜色常量 | 2 | 必需字段完整、hex 格式合法 |

> 💡 Claude Code 用户直接输入 `/unit-test` 即可自动运行并查看报告。

---

## 📁 项目结构

```
晚秋记账/
├── main.py                        # 主程序（界面 + 数据库 + 贪吃蛇游戏）
├── test_main.py                   # 单元测试（32 个测试用例）
├── CLAUDE.md                      # 项目开发说明
├── README.md                      # 本文件
├── .gitignore                     # Git 忽略规则
├── .git/hooks/
│   ├── pre-commit                 # 提交前门禁：检查通行证
│   └── post-commit                # 提交后清理：销毁旧通行证
├── .claude/
│   ├── agents/
│   │   ├── tester.md              # 测试子代理
│   │   ├── quality-engineer.md    # 代码质量子代理
│   │   └── gitcommit-agent.md     # 提交门禁子代理
│   ├── skills/
│   │   ├── start/SKILL.md         # /start 一键启动
│   │   ├── rebuild-app/SKILL.md   # /rebuild-app 重新打包
│   │   ├── unit-test/SKILL.md     # /unit-test 单元测试
│   │   ├── comments-check/SKILL.md # /comments-check 注释检查
│   │   └── security-audit/SKILL.md # /security-audit 安全审计
│   └── checkpoints/               # 通行证存放目录
└── dist/
    └── 晚秋记账.exe                # 打包后的独立可执行文件
```

---

## 💾 数据存储

所有记账数据保存在本地 SQLite 数据库中：

```
C:\Users\你的用户名\AppData\Roaming\晚秋记账\data.db
```

- 数据完全本地化，不会上传到任何服务器
- 卸载应用不会自动删除数据，如需清除请手动删除上述目录

---

## 📝 预设分类

> 共 12 个，不可删除或修改（保护核心分类不被误操作），可新增自定义分类

| 餐饮 | 交通 | 住房 | 服饰 | 医疗 | 通讯 |
|------|------|------|------|------|------|
| 🍽️ | 🚗 | 🏠 | 👗 | 💊 | 📱 |

| 娱乐 | 学习 | 人情 | 工作 | 收入 | 其他 |
|------|------|------|------|------|------|
| 🎮 | 📚 | 🎁 | 💼 | 💰 | 📌 |

---

## 📄 许可证

MIT License
