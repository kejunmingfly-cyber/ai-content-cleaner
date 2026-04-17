from pydantic import BaseModel, Field
from typing import Optional

class ProcessResponse(BaseModel):
    task_id: str
    original_text: str
    refined_text: str
    ai_prob_original: float = Field(..., description="原稿 AI 检测概率 (0‑1)")
    ai_prob_refined: float = Field(..., description="重塑后 AI 检测概率 (0‑1)")
    safe: bool
    token_usage: int
    download_url: str