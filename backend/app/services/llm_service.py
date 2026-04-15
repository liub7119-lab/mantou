"""
LLM 服务：调用大模型从证书图片中提取结构化信息
支持 OpenAI (GPT-4o) 和 Google Gemini 两种 Provider
"""

import base64
import json
from pathlib import Path

from ..config import settings
from ..schemas import LLMExtractResult

# 提取证书信息的 Prompt
EXTRACT_PROMPT = """你是一个专业的证书信息提取助手。请仔细分析这张获奖证书图片，提取以下信息：

1. **比赛/项目名称** (competition_name)：完整的比赛或项目名称
2. **获奖人姓名** (winner_name)：获奖者的姓名
3. **获奖等级** (award_level)：如一等奖、二等奖、金奖、银奖、最佳奖等
4. **获奖日期** (award_date)：证书上标注的日期，格式尽量统一为 YYYY-MM-DD

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{
    "competition_name": "...",
    "winner_name": "...",
    "award_level": "...",
    "award_date": "..."
}

如果某个字段无法从图片中识别，请填写空字符串 ""。
"""


def _read_image_as_base64(image_path: Path) -> tuple[str, str]:
    """读取图片并转为 base64"""
    suffix = image_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(suffix, "image/jpeg")

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return b64, mime_type


def _parse_llm_response(text: str) -> LLMExtractResult:
    """解析 LLM 返回的 JSON 文本"""
    # 尝试提取 JSON 块（兼容 markdown 代码块包裹）
    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
        return LLMExtractResult(**data)
    except (json.JSONDecodeError, ValueError):
        # 解析失败，返回空结果
        return LLMExtractResult()


async def _extract_via_openai(image_path: Path) -> tuple[LLMExtractResult, str]:
    """使用 OpenAI GPT-4o 提取"""
    from openai import AsyncOpenAI

    client_kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        client_kwargs["base_url"] = settings.OPENAI_BASE_URL

    client = AsyncOpenAI(**client_kwargs)
    b64, mime_type = _read_image_as_base64(image_path)

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACT_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64}",
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    return _parse_llm_response(raw), raw


async def _extract_via_gemini(image_path: Path) -> tuple[LLMExtractResult, str]:
    """使用 Google Gemini 提取"""
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    with open(image_path, "rb") as f:
        image_data = f.read()

    suffix = image_path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

    response = await model.generate_content_async(
        [
            EXTRACT_PROMPT,
            {"mime_type": mime_map.get(suffix, "image/jpeg"), "data": image_data},
        ],
        generation_config={"temperature": 0.1, "max_output_tokens": 500},
    )

    raw = response.text
    return _parse_llm_response(raw), raw


async def extract_certificate_info(image_path: Path) -> tuple[LLMExtractResult, str]:
    """
    统一入口：根据配置选择 LLM Provider 提取证书信息
    返回: (提取结果, 原始响应文本)
    """
    if settings.LLM_PROVIDER == "gemini":
        return await _extract_via_gemini(image_path)
    else:
        return await _extract_via_openai(image_path)
