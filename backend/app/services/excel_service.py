"""
Excel 导出服务
使用 openpyxl 生成格式化的 Excel 文件（含证书原件图片）
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XlImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from ..config import settings


# 图片在单元格中的目标尺寸（像素）
IMG_WIDTH_PX = 120
IMG_HEIGHT_PX = 90
# 对应的行高（磅）和列宽（字符宽度）
IMG_ROW_HEIGHT = 72
IMG_COL_WIDTH = 18


def generate_achievement_excel(data: list[dict]) -> str:
    """
    生成成果汇总 Excel 文件（含证书原件图片嵌入）
    data 中每条记录需包含 _image_path 字段（服务器上的相对路径）
    返回临时文件路径
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "科研与比赛成果汇总"

    # ---- 表头定义（固定顺序） ----
    headers = [
        "学号", "上报人", "班级", "学院",
        "比赛/项目名称", "获奖人（AI识别）", "获奖等级", "获奖日期",
        "成果分类", "状态", "提交时间", "证书原件",
    ]

    # ---- 样式 ----
    header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    data_font = Font(name="微软雅黑", size=10)
    data_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # ---- 写表头 ----
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # ---- 列宽 ----
    column_widths = {
        "学号": 15, "上报人": 10, "班级": 18, "学院": 22,
        "比赛/项目名称": 35, "获奖人（AI识别）": 20, "获奖等级": 12,
        "获奖日期": 14, "成果分类": 12, "状态": 10, "提交时间": 18,
        "证书原件": IMG_COL_WIDTH,
    }
    for col, header in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(col)].width = column_widths.get(header, 15)

    # ---- 数据行 ----
    image_col_idx = headers.index("证书原件") + 1  # 1-based

    for row_idx, record in enumerate(data, 2):
        # 写文本列
        for col_idx, header in enumerate(headers, 1):
            if header == "证书原件":
                continue  # 图片单独处理
            cell = ws.cell(row=row_idx, column=col_idx, value=record.get(header, ""))
            cell.font = data_font
            cell.alignment = data_alignment
            cell.border = thin_border

        # 写证书原件边框
        img_cell = ws.cell(row=row_idx, column=image_col_idx)
        img_cell.border = thin_border
        img_cell.alignment = data_alignment

        # 设置行高以容纳图片
        ws.row_dimensions[row_idx].height = IMG_ROW_HEIGHT

        # 嵌入图片
        image_rel_path = record.get("_image_path", "")
        if image_rel_path:
            # /uploads/xxx.png → 实际文件路径
            filename = image_rel_path.lstrip("/").replace("uploads/", "", 1)
            abs_path = Path(settings.UPLOAD_DIR) / filename
            if abs_path.exists():
                try:
                    img = XlImage(str(abs_path))
                    img.width = IMG_WIDTH_PX
                    img.height = IMG_HEIGHT_PX
                    cell_ref = f"{get_column_letter(image_col_idx)}{row_idx}"
                    ws.add_image(img, cell_ref)
                except Exception:
                    # 图片插入失败时写文字兜底
                    img_cell.value = "（图片加载失败）"
            else:
                img_cell.value = "（文件不存在）"

    # ---- 保存到临时文件 ----
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    tmp.close()

    return tmp.name
