# Morpheus 配置指南

**配置日期**: 2026-03-16  
**项目位置**: `D:\openclaw\.openclaw\Morpheus`

---

## ✅ 已完成配置

### 1. 项目克隆 ✅
```bash
git clone https://github.com/Pangzte-Sri/Morpheus.git
```
位置：`D:\openclaw\.openclaw\Morpheus`

### 2. 后端配置 ✅
文件：`backend/.env`

**配置内容**:
```ini
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_CONTEXT_WINDOW_TOKENS=131072
DEEPSEEK_MAX_TOKENS=8192

EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSION=1024
```

---

## ⚠️ 需要您完成的配置

### 1. 配置 DeepSeek API Key

**获取 API Key**:
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API 管理页面
4. 创建 API Key

**填入配置**:
编辑 `backend/.env` 文件，将：
```ini
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```
改为：
```ini
DEEPSEEK_API_KEY=sk-你的真实 APIKey
```

---

### 2. 安装后端依赖

**方式 1: 使用 pip（推荐）**
```powershell
cd D:\openclaw\.openclaw\Morpheus\backend
pip install -r requirements.txt
```

**方式 2: 使用 Poetry**
```powershell
cd D:\openclaw\.openclaw\Morpheus\backend
poetry install
```

---

### 3. 安装前端依赖

```powershell
cd D:\openclaw\.openclaw\Morpheus\frontend
npm install
```

---

## 🚀 启动服务

### 方式 1: 手动启动（推荐新手）

**终端 1 - 启动后端**:
```powershell
cd D:\openclaw\.openclaw\Morpheus\backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload --workers 2
```

**终端 2 - 启动前端**:
```powershell
cd D:\openclaw\.openclaw\Morpheus\frontend
npm run dev
```

### 方式 2: 使用启动脚本

**创建启动脚本** `start.bat`:
```batch
@echo off
echo 🚀 启动 Morpheus...

echo 📦 启动后端...
start powershell -Command "cd backend && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 2"

timeout /t 5 /nobreak >nul

echo 🎨 启动前端...
start powershell -Command "cd frontend && npm run dev"

echo ✅ 启动完成！
echo.
echo 📱 前端地址：http://localhost:3000
echo 🔧 后端地址：http://127.0.0.1:8000
echo 📚 API 文档：http://127.0.0.1:8000/docs
```

---

## 📋 验证安装

### 1. 检查后端健康
访问：http://127.0.0.1:8000/api/health

应返回：
```json
{
  "status": "healthy",
  "llm_ready": true,
  "database_ready": true
}
```

### 2. 检查 LLM 状态
访问：http://127.0.0.1:8000/api/runtime/llm

应返回：
```json
{
  "remote_effective": true,
  "remote_ready": true,
  "provider": "deepseek"
}
```

### 3. 访问前端
打开浏览器访问：http://localhost:3000

应看到项目列表页面。

---

## 🎯 快速开始

### 1. 创建第一个项目

在前端界面：
1. 点击"创建项目"
2. 填写：
   - **项目名称**: 末世修仙录
   - **类型**: 玄幻
   - **风格**: 热血升级
   - **目标字数**: 200 万
   - **世界观**: （简要描述）

### 2. 创建章节

1. 进入项目详情
2. 点击"创建章节"
3. 输入章节标题或让 AI 生成
4. 点击"生成章节计划"

### 3. 生成章节正文

1. 审查章节计划
2. 点击"生成草稿"
3. 实时观看 AI 创作过程
4. 审查和润色
5. 定稿

---

## 🔧 常见问题

### Q1: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```powershell
cd backend
pip install -r requirements.txt
```

### Q2: 前端启动失败

**错误**: `npm: command not found`

**解决**:
1. 安装 Node.js: https://nodejs.org/
2. 重启终端
3. 重新运行 `npm install`

### Q3: LLM 一直是降级模式

**检查**:
1. 访问 http://127.0.0.1:8000/api/runtime/llm
2. 确认 `remote_ready: true`
3. 如为 false，检查：
   - `.env` 中 API Key 是否正确
   - API Key 是否有余额
   - 网络连接是否正常

### Q4: 向量检索报错

**解决**:
```powershell
# 删除向量数据库重建
cd D:\openclaw\.openclaw\Morpheus
Remove-Item -Recurse -Force data\vectors\*
# 重启后端
```

---

## 📊 项目结构

```
Morpheus/
├── backend/              # FastAPI 后端
│   ├── api/             # API 路由
│   ├── agents/          # 4 个 Agent（Director/Setter/Stylist/Arbiter）
│   ├── memory/          # 三层记忆系统
│   ├── core/            # 核心工具（LLM 客户端等）
│   └── .env             # 配置文件 ✅
├── frontend/            # React 前端
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   ├── components/  # UI 组件
│   │   └── stores/      # Zustand 状态管理
│   └── package.json
├── data/                # 运行时数据（自动生成）
│   ├── projects/        # 项目数据
│   ├── vectors/         # 向量数据库
│   └── logs/            # 日志文件
└── docs/                # 文档
```

---

## 🎁 核心功能

### 1. 三层记忆系统
- **L1 Identity**: 项目核心设定（世界观、主角、风格）
- **L2 Entities**: 人物、地点、物品等实体
- **L3 Events**: 关键事件与情节发展

### 2. 四个 Agent
- **Director**: 章节规划和初稿生成
- **Setter**: 审查场景设定和世界观一致性
- **Stylist**: 优化文笔和叙事节奏
- **Arbiter**: 最终定稿和质量把关

### 3. 实时流式生成
- SSE 推送生成进度
- 前端实时显示创作过程
- 支持整书批量生成

### 4. 可视化界面
- 项目管理
- 创作控制台
- 知识图谱
- 决策轨迹回放
- 质量看板

---

## 📝 下一步

1. ✅ **获取 DeepSeek API Key**
2. ✅ **安装后端依赖**
3. ✅ **安装前端依赖**
4. ✅ **启动服务测试**
5. ⏳ **创建第一个项目**
6. ⏳ **生成第一个章节**

---

**配置者**: 爱丽丝 (Alice)  
**配置时间**: 2026-03-16 06:30  
**状态**: ⚠️ 等待 API Key 配置
