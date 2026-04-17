# AI 内容净化（检测 → 人类化）

演示站点：https://<your‑render‑service>.onrender.com

前端页面（GitHub Pages）: https://<your‑username>.github.io/ai-content-cleaner/

### 项目简介
1️⃣ 用 OpenAI **moderation** 检测稿件是否像 AI 生成。
2️⃣ 若检测率 > 5% 调用 **GPT‑4o**（或 Gemini‑3.1）进行“人类化”改写：加入口语、情感、地方梗、个人小故事等。
3️⃣ 再次走 **腾讯内容安全**（可选）过滤敏感词。
4️⃣ 前端展示原稿、检测分数、改写稿以及下载链接。

### 部署方式
- **GitHub Actions** 自动把代码打包成 Docker 镜像并推到 **GitHub Container Registry (GHCR)**。
- **Render** 拉取 GHCR 镜像，免费运行 24/7 Web Service。
- （可选）前端单独托管到 **GitHub Pages**，访问更快。

### 本地调试（可选）
```bash
cp .env.example .env        # 填入你的 OpenAI / 腾讯密钥
docker compose up -d
# 浏览器打开 http://localhost:8000