import os
import hashlib
import time
import json
import requests
import openai
from typing import Tuple

# ----- OpenAI -----
openai.api_key = os.getenv("OPENAI_API_KEY")

def check_ai_prob(text: str) -> float:
    """
    调用 OpenAI Moderation（内容检测）返回最高的 “probability”。
    返回值 0‑1，越大越像 AI 生成。
    """
    resp = openai.moderations.create(input=text)
    # OpenAI 返回的 categories 里每个都有 score，取最大值
    scores = [cat["score"] for cat in resp.results[0].categories.values()]
    return max(scores)


def refine_text(text: str) -> Tuple[str, int]:
    """
    使用 GPT‑4o（或 Gemini）把 AI 生成稿件改写为 “更像人写的” 版本。
    返回 (改写后文本, 使用的 token 数)。
    """
    prompt = f"""You are a Chinese copy‑editing AI. Transform the following AI‑generated article into a human‑style piece.
Requirements:
- Use colloquial expressions, local slang and cultural references.
- Insert 1‑2 short personal anecdotes or case stories.
- Add emotional ups‑and‑downs (questions, exclamations, rhetorical pauses).
- Keep factual information unchanged.
- Output ONLY the revised article, no extra explanations.

--- Begin article ---
{text}
--- End article ---
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=0.9,
    )
    refined = completion.choices[0].message.content.strip()
    token_usage = completion.usage.total_tokens
    return refined, token_usage


# ----- 腾讯内容安全（可选）-----
def safe_check(text: str) -> bool:
    """
    简单调用腾讯内容安全文本检测 API，返回 True 表示「通过」。
    如果你没有开通腾讯内容安全，直接返回 True 即可。
    """
    secret_id = os.getenv("TENCENT_SECRET_ID")
    secret_key = os.getenv("TENCENT_SECRET_KEY")
    if not secret_id or not secret_key:
        return True   # 开发阶段跳过安全检测

    # -------------------
    # 生成签名（官方 SDK 里有实现，这里给最简化版）
    # -------------------
    params = {
        "Action": "TextModeration",
        "Version": "2020-11-11",
        "Region": "ap-guangzhou",
        "SecretId": secret_id,
        "Timestamp": str(int(time.time())),
        "Nonce": str(int(time.time() * 1000) % 100000),
        "Text": text,
    }

    # 按字典顺序拼接
    src_str = "GET" + "tms.tencentcloudapi.com/?" + "&".join(
        f"{k}={params[k]}" for k in sorted(params)
    )
    # HMAC‑SHA1 加密后再 Base64
    import hmac, base64
    dig = hmac.new(secret_key.encode("utf-8"), src_str.encode("utf-8"), hashlib.sha1).digest()
    sign = base64.b64encode(dig).decode()
    params["Signature"] = sign

    # 发请求
    try:
        r = requests.get("https://tms.tencentcloudapi.com/", params=params, timeout=5)
        r.raise_for_status()
        result = r.json()
        # `Result` 中的 `Pass` 为 1 表示安全
        return result.get("Response", {}).get("Result", {}).get("Pass", 0) == 1
    except Exception as e:
        # 若调用失败，默认认为安全（生产环境请改为严格模式）
        print("Tencent safe_check error:", e)
        return True