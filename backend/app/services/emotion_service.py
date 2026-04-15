"""
AI 情绪分析服务
调用 LLM 对学生反馈文本进行情绪评分和标签分类
"""

import json

from ..config import settings


EMOTION_PROMPT = """你是一位专业的学生心理辅导分析师。请分析以下学生匿名反馈的情绪状态。

**学生反馈内容：**
{content}

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{{
    "score": <1-10的整数>,
    "label": "<情绪标签>"
}}

评分标准：
- 1-2分：极度消极，有自残/自杀倾向或严重心理危机
- 3-4分：较为消极，明显焦虑、抑郁、愤怒或绝望
- 5-6分：中性偏消极，有困扰但可控
- 7-8分：较为积极，属于正常反馈或建议
- 9-10分：积极正面，表达感谢或建设性意见

情绪标签从以下选择：危机预警、抑郁倾向、焦虑不安、愤怒激动、困惑迷茫、一般困扰、中性反馈、积极建议
"""


def _parse_emotion_response(text: str) -> dict:
    """解析 LLM 返回的情绪分析 JSON"""
    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(cleaned)
        score = max(1, min(10, int(data.get("score", 5))))
        label = data.get("label", "中性反馈")
        return {"score": score, "label": label}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"score": 5, "label": "中性反馈"}


async def analyze_emotion(content: str) -> dict:
    """
    分析文本情绪，返回 {"score": int, "label": str}
    score: 1-10（1=极度消极），label: 情绪标签
    """
    from openai import AsyncOpenAI

    client_kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        client_kwargs["base_url"] = settings.OPENAI_BASE_URL

    client = AsyncOpenAI(**client_kwargs)

    # 情绪分析用文本模型即可，不需要视觉模型
    text_model = settings.OPENAI_MODEL
    # 如果配置的是视觉模型，降级到文本模型
    if "VL" in text_model or "vl" in text_model:
        text_model = "Qwen/Qwen2.5-72B-Instruct"

    try:
        response = await client.chat.completions.create(
            model=text_model,
            messages=[
                {"role": "user", "content": EMOTION_PROMPT.format(content=content)},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        return _parse_emotion_response(raw)
    except Exception:
        # LLM 调用失败时返回默认值，不阻断流程
        return {"score": 5, "label": "分析失败"}
