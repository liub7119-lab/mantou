"""
LLM 服务：调用大模型从证书图片中提取结构化信息
支持 OpenAI (GPT-4o) 和 Google Gemini 两种 Provider
按成果类别使用不同的提取 Prompt
"""

import base64
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from ..config import settings
from ..schemas import (
    CompetitionExtract,
    PaperExtract,
    PatentExtract,
    ResearchProjectExtract,
)

# ──────────────────────────────────────────────
# 按类别区分的 Prompt
# ──────────────────────────────────────────────
PROMPTS = {
    "科研项目": """你是一个专业的科研项目信息提取助手。请仔细分析这张图片，提取以下信息：

1. **立项编号** (project_number)
2. **项目层级** (project_level)：国家级、省级、市厅级、校级
3. **参与科研项目名称** (project_name)
4. **学生排名** (student_rank)
5. **立项年度** (project_year)
6. **项目来源** (project_source)
7. **项目负责人** (project_leader)
8. **工号** (leader_id)
9. **辅导员姓名** (counselor_name)

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{
    "project_number": "...",
    "project_level": "...",
    "project_name": "...",
    "student_rank": "...",
    "project_year": "...",
    "project_source": "...",
    "project_leader": "...",
    "leader_id": "...",
    "counselor_name": "..."
}

如果某个字段无法从图片中识别，请填写空字符串 ""。""",

    "专利软著": """你是一个专业的专利/软件著作权信息提取助手。请仔细分析这张图片，提取以下信息：

1. **名称** (name)：专利或软著的名称
2. **类别** (patent_type)：如 实用新型专利、发明专利、外观设计专利、软著
3. **授权号** (authorization_number)
4. **获批时间** (approval_date)：格式尽量统一为 YYYY.MM.DD
5. **发明人排名** (inventor_rank)
6. **辅导员姓名** (counselor_name)

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{
    "name": "...",
    "patent_type": "...",
    "authorization_number": "...",
    "approval_date": "...",
    "inventor_rank": "...",
    "counselor_name": "..."
}

如果某个字段无法从图片中识别，请填写空字符串 ""。""",

    "学术论文": """你是一个专业的学术论文信息提取助手。请仔细分析这张图片，提取以下信息：

1. **论文名称** (paper_name)
2. **发表期刊名称** (journal_name)
3. **作者排名** (author_rank)
4. **发表时间** (publish_date)：格式尽量统一为 YYYY.MM
5. **收录情况** (indexing)：如 CSSCI、SCI、EI、CPCI、普刊 等
6. **论文链接** (paper_link)
7. **辅导员姓名** (counselor_name)

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{
    "paper_name": "...",
    "journal_name": "...",
    "author_rank": "...",
    "publish_date": "...",
    "indexing": "...",
    "paper_link": "...",
    "counselor_name": "..."
}

如果某个字段无法从图片中识别，请填写空字符串 ""。""",

    "学科竞赛": """你是一个专业的学科竞赛获奖信息提取助手。请仔细分析这张获奖证书图片，提取以下信息：

1. **赛事名称** (competition_name)：完整的赛事全称
2. **赛道** (track)
3. **赛事主办方** (organizer)
4. **项目名称** (project_name)
5. **奖项名称** (award_name)：如 一等奖、金奖、省级银奖 等
6. **项目负责人** (team_leader)
7. **联系电话** (phone)
8. **指导老师** (advisor)：全部指导老师姓名
9. **学生成员** (team_members)：全部成员姓名
10. **获奖时间** (award_date)：格式尽量统一为 YYYY.MM.DD
11. **备注** (remark)

请严格按照以下 JSON 格式返回，不要包含任何其他文字：
{
    "competition_name": "...",
    "track": "...",
    "organizer": "...",
    "project_name": "...",
    "award_name": "...",
    "team_leader": "...",
    "phone": "...",
    "advisor": "...",
    "team_members": "...",
    "award_date": "...",
    "remark": "..."
}

如果某个字段无法从图片中识别，请填写空字符串 ""。""",
}

EXTRACT_MODELS = {
    "科研项目": ResearchProjectExtract,
    "专利软著": PatentExtract,
    "学术论文": PaperExtract,
    "学科竞赛": CompetitionExtract,
}


def _read_image_as_base64(image_path: Path) -> tuple[str, str]:
    img = Image.open(image_path)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


def _parse_llm_response(text: str, category: str):
    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    model_cls = EXTRACT_MODELS[category]
    try:
        data = json.loads(cleaned)
        return model_cls(**data)
    except (json.JSONDecodeError, ValueError):
        return model_cls()


async def _extract_via_openai(image_path: Path, category: str):
    from openai import AsyncOpenAI

    client_kwargs = {"api_key": settings.OPENAI_API_KEY}
    if settings.OPENAI_BASE_URL:
        client_kwargs["base_url"] = settings.OPENAI_BASE_URL

    client = AsyncOpenAI(**client_kwargs)
    b64, mime_type = _read_image_as_base64(image_path)
    prompt = PROMPTS[category]

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=500,
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    return _parse_llm_response(raw, category), raw


async def _extract_via_gemini(image_path: Path, category: str):
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    img = Image.open(image_path)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    image_data = buf.getvalue()

    prompt = PROMPTS[category]
    response = await model.generate_content_async(
        [
            prompt,
            {"mime_type": "image/jpeg", "data": image_data},
        ],
        generation_config={"temperature": 0.1, "max_output_tokens": 500},
    )

    raw = response.text
    return _parse_llm_response(raw, category), raw


async def extract_certificate_info(image_path: Path, category: str):
    """
    统一入口：根据配置选择 LLM Provider，根据 category 使用对应 Prompt
    返回: (提取结果 Pydantic Model, 原始响应文本)
    """
    if category not in PROMPTS:
        raise ValueError(f"不支持的成果类别: {category}")

    if settings.LLM_PROVIDER == "gemini":
        return await _extract_via_gemini(image_path, category)
    else:
        return await _extract_via_openai(image_path, category)


async def call_llm_with_image(b64: str, mime_type: str, prompt: str) -> str:
    """通用图片+文字调用 LLM，返回原始文本"""
    if settings.LLM_PROVIDER == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        image_data = base64.b64decode(b64)
        response = await model.generate_content_async(
            [prompt, {"mime_type": mime_type, "data": image_data}],
            generation_config={"temperature": 0.1, "max_output_tokens": 2000},
        )
        return response.text
    else:
        from openai import AsyncOpenAI

        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
        client = AsyncOpenAI(**client_kwargs)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                ],
            }],
            max_tokens=2000,
            temperature=0.1,
        )
        return response.choices[0].message.content
