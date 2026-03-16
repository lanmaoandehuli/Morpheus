# GLM-4 配置完成

**配置时间**: 2026-03-16 06:31  
**模型**: GLM-4-Plus (智谱 AI)  
**API Key**: `996ab41e9b314fe0887bc58f05f1dd7e.FOVtIEdwFG8a2BUR`

---

## ✅ 配置详情

### 后端配置 (`backend\.env`)

```ini
LLM_PROVIDER=openai
REMOTE_LLM_ENABLED=true

# GLM-4 配置（使用 OpenAI 兼容接口）
DEEPSEEK_API_KEY=996ab41e9b314fe0887bc58f05f1dd7e.FOVtIEdwFG8a2BUR
DEEPSEEK_BASE_URL=https://open.bigmodel.cn/api/paas/v4
DEEPSEEK_MODEL=glm-4-plus
DEEPSEEK_CONTEXT_WINDOW_TOKENS=128000
DEEPSEEK_MAX_TOKENS=8192

# Embedding 配置
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIMENSION=1024
```

---

## 🚀 下一步

### 1. 安装依赖

```powershell
cd D:\openclaw\.openclaw\Morpheus\backend
pip install fastapi uvicorn python-dotenv lancedb openai pydantic httpx

cd ..\frontend
npm install
```

### 2. 启动服务

**方式 1: 双击启动**
- 双击 `start.bat`

**方式 2: 手动启动**
```powershell
# 终端 1 - 后端
cd backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 2

# 终端 2 - 前端
cd ..\frontend
npm run dev
```

### 3. 验证 GLM 连接

启动后访问：
- http://127.0.0.1:8000/api/runtime/llm

应返回：
```json
{
  "remote_effective": true,
  "remote_ready": true,
  "provider": "openai",
  "model": "glm-4-plus"
}
```

---

## 📊 GLM-4-Plus 参数

| 参数 | 值 |
|------|-----|
| **模型** | glm-4-plus |
| **上下文窗口** | 128K tokens |
| **最大输出** | 8192 tokens |
| **API 地址** | https://open.bigmodel.cn/api/paas/v4 |
| **适用场景** | 长篇小说创作、复杂规划 |

---

## 💡 GLM 模型特点

### 优势
- ✅ **中文优化** - 对中文网文理解更好
- ✅ **长上下文** - 128K tokens，适合长篇小说
- ✅ **价格友好** - 比 GPT-4 便宜
- ✅ **稳定可靠** - 国内 API，延迟低

### 适用场景
- 📖 长篇小说创作
- 📝 章节规划
- 🎭 角色设定
- 🌍 世界观构建

---

## ⚠️ 注意事项

### 1. 余额检查
访问 https://open.bigmodel.cn/ 查看账户余额

### 2. 速率限制
GLM-4-Plus 有速率限制，如遇 429 错误：
- 等待几秒后重试
- 或降低 `API_WORKERS=1`

### 3. Token 消耗
长篇小说创作消耗较多 Token，建议：
- 定期查看使用量
- 设置预算提醒

---

## 🎯 快速测试

启动服务后：

1. 访问 http://localhost:3000
2. 创建项目"测试 GLM"
3. 类型：玄幻
4. 创建章节
5. 生成章节计划
6. 观察输出质量

---

## 🔧 如需切换回 DeepSeek

编辑 `backend\.env`：
```ini
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

重启后端即可。

---

**配置者**: 爱丽丝  
**状态**: ✅ 配置完成，等待安装依赖
