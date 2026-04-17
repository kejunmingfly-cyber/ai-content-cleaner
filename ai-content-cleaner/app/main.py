import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .models import ProcessResponse
from .utils import check_ai_prob, refine_text, safe_check
from .db import insert_task, hashids

app = FastAPI(title="AI 内容净化原型")

# -------------- 静态页面（根路径）--------------
app.mount("/", StaticFiles(directory="../static", html=True), name="static")

# -------------- CORS（跨域）--------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请锁定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------- 处理入口 -----------------
@app.post("/api/v1/process", response_model=ProcessResponse)
async def process(file: UploadFile = File(...)):
    # 只接受纯文本
    if file.content_type not in ("text/plain", "text/markdown"):
        raise HTTPException(status_code=400, detail="仅支持 txt / md 文件")

    raw = await file.read()
    original = raw.decode("utf-8")

    # 1️⃣ 检测原稿是否像 AI
    prob_orig = check_ai_prob(original)

    # 2️⃣ 若检测率高 (>5%) 执行重塑，否则直接返回原稿
    if prob_orig > 0.05:
        refined, token_usage = refine_text(original)
        prob_refined = check_ai_prob(refined)
    else:
        refined = original
        token_usage = 0
        prob_refined = prob_orig

    # 3️⃣ 内容安全（可选）
    safe = safe_check(refined)

    # 4️⃣ 持久化记录并生成短链接
    task_id = insert_task(
        original, refined, prob_orig, prob_refined, safe, token_usage
    )
    short = hashids.encode(task_id)
    download_url = f"/download/{short}"

    return ProcessResponse(
        task_id=str(task_id),
        original_text=original,
        refined_text=refined,
        ai_prob_original=prob_orig,
        ai_prob_refined=prob_refined,
        safe=safe,
        token_usage=token_usage,
        download_url=download_url,
    )


# -------------- 下载 endpoint -----------------
@app.get("/download/{short}")
def download(short: str):
    # 解析短链得到 task_id
    try:
        task_id = hashids.decode(short)[0]
    except Exception:
        raise HTTPException(status_code=404, detail="短链不存在")

    # 查询 SQLite
    import sqlite3
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT refined FROM tasks WHERE id=?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="记录未找到")

    refined = row[0]
    # 把稿件写入临时文件供下载
    tmp_path = f"/tmp/refined_{task_id}.md"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(refined)

    return FileResponse(tmp_path, filename="refined.md", media_type="text/markdown")