# -*- coding: utf-8 -*-
"""
DSE/高考数学提分潜力诊断工具 v2.0
陈老师专属 - AI驱动的数学诊断系统
UI设计：专业、简洁、高对比度
"""

import streamlit as st
import google.generativeai as genai
from zhipuai import ZhipuAI
from PIL import Image, ImageEnhance
import fitz  # PyMuPDF
import io
import re
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 设置matplotlib支持中文
mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
mpl.rcParams['axes.unicode_minus'] = False

# ==================== 核心配置 ====================
# API密钥
GEMINI_API_KEY = "AIzaSyBcvLsNA4ZeLbxHjcWmx_Fy1OcXYS5z9J0"
GLM_API_KEY = "445b29b7119946d49c65361161dae089.tdSIhpAFssxWAoEO"

# 微信号
WECHAT_ID = "xiaobo20230512"

# 模型选择（质量优先）
PRIMARY_MODEL = "gemini-2.5-pro"  # 主模型：最新专业版
FALLBACK_MODEL = "glm-4-plus"     # 备用：GLM最强版

# ==================== UI 配置 ====================
st.set_page_config(
    page_title="陈老师数学诊断",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 顶尖UI设计 - 专业简洁风格
st.markdown("""
<style>
    /* ========== 全局样式 ========== */
    .stApp {
        background: #0a0e27;
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ========== 主标题样式 - 清晰可见 ========== */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    .main-subtitle {
        font-size: 1rem;
        color: #8892b0;
        text-align: center;
        margin-bottom: 30px;
    }

    /* ========== 卡片样式 ========== */
    .feature-card {
        background: linear-gradient(135deg, #1e2130 0%, #161925 100%);
        border: 1px solid #2d3548;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .feature-card h3 {
        color: #ffffff;
        font-size: 1.2rem;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .feature-card p {
        color: #8892b0;
        font-size: 0.9rem;
        margin: 0;
    }

    /* ========== 模式选择按钮 ========== */
    .mode-selector {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
    }

    .mode-btn {
        flex: 1;
        padding: 20px;
        background: #1e2130;
        border: 2px solid #2d3548;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }

    .mode-btn:hover {
        border-color: #4a9eff;
        background: #1a2540;
    }

    .mode-btn.active {
        border-color: #4a9eff;
        background: linear-gradient(135deg, #1a2540 0%, #0d1b2a 100%);
    }

    /* ========== 输入框样式 - 高对比度 ========== */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: #1e2130 !important;
        border: 2px solid #2d3548 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 12px !important;
    }

    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #4a9eff !important;
        box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1) !important;
    }

    /* ========== 多选框样式 ========== */
    .stMultiSelect > div > div > div {
        background: #1e2130 !important;
        border: 2px solid #2d3548 !important;
        border-radius: 8px !important;
    }

    /* ========== 下拉框样式 ========== */
    .stSelectbox > div > div > div {
        background: #1e2130 !important;
        border: 2px solid #2d3548 !important;
        border-radius: 8px !important;
    }

    /* ========== 主要按钮样式 ========== */
    .stButton > button {
        background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 14px 40px;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(74, 158, 255, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 158, 255, 0.4);
    }

    /* ========== 下载按钮样式 ========== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00c853 0%, #00a844 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-size: 1rem;
        font-weight: 600;
    }

    /* ========== 侧边栏样式 ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161925 100%);
        border-right: 1px solid #2d3548;
    }

    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stSidebar"] .css-1d391kg {
        color: #8892b0 !important;
    }

    /* ========== 报告展示区 ========== */
    .report-container {
        background: #1e2130;
        border: 1px solid #2d3548;
        border-radius: 12px;
        padding: 24px;
        line-height: 1.8;
    }

    .report-container h1 {
        color: #4a9eff !important;
        font-size: 1.5rem !important;
        margin-bottom: 15px;
    }

    .report-container h2 {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .report-container h3 {
        color: #8892b0 !important;
        font-size: 1rem !important;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    .report-container p, .report-container li {
        color: #c9d1e0 !important;
    }

    /* ========== 微信引流卡片 ========== */
    .wechat-card {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.15) 0%, rgba(0, 200, 83, 0.15) 100%);
        border: 2px solid #4a9eff;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-top: 30px;
    }

    .wechat-card h3 {
        color: #ffffff;
        font-size: 1.3rem;
        margin-bottom: 10px;
    }

    .wechat-card .wechat-id {
        font-size: 1.5rem;
        font-weight: 700;
        color: #4a9eff;
        background: rgba(74, 158, 255, 0.1);
        padding: 10px 20px;
        border-radius: 8px;
        display: inline-block;
        margin: 15px 0;
    }

    /* ========== 上传区样式 ========== */
    [data-testid='stFileUploader'] {
        background: #1e2130 !important;
        border: 2px dashed #4a9eff !important;
        border-radius: 12px !important;
        padding: 30px !important;
    }

    [data-testid='stFileUploader'] label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ========== 状态提示 ========== */
    .stAlert {
        background: #1e2130 !important;
        border: 1px solid #2d3548 !important;
        border-radius: 10px !important;
    }

    [data-testid="stAlert"] p {
        color: #c9d1e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== AI 调用函数（双模型支持） ====================
def call_ai_gemini(prompt, images=None):
    """使用Gemini API"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(PRIMARY_MODEL)

        if images:
            response = model.generate_content([prompt] + images)
        else:
            response = model.generate_content(prompt)

        return response.text, "gemini"
    except Exception as e:
        return None, f"gemini_error: {str(e)}"

def call_ai_glm(prompt):
    """使用GLM API作为备用"""
    try:
        client = ZhipuAI(api_key=GLM_API_KEY)
        response = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.7
        )
        return response.choices[0].message.content, "glm"
    except Exception as e:
        return None, f"glm_error: {str(e)}"

def call_ai_with_fallback(prompt, images=None):
    """智能调用AI，自动切换备用模型"""
    # 首先尝试Gemini
    result, source = call_ai_gemini(prompt, images)
    if result:
        return result, source

    # Gemini失败，尝试GLM
    if images:
        # GLM不支持图片，返回简化提示
        return None, "图像输入需要Gemini，当前服务繁忙"

    result, source = call_ai_glm(prompt)
    if result:
        return result, source

    return None, "所有AI服务暂时不可用，请稍后重试"

# ==================== 辅助函数 ====================
def enhance_image_for_ocr(pil_image):
    """增强图像用于OCR识别"""
    enhancer = ImageEnhance.Contrast(pil_image)
    img = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    return img

def process_pdf_bytes(file_bytes, start_page, end_page):
    """处理PDF文件，提取图像"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_pages = len(doc)
    start = max(0, start_page - 1)
    end = min(total_pages, end_page)

    images = []
    enhanced_images = []

    for i in range(start, end):
        try:
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=200)
            img_data = pix.tobytes("png")
            original = Image.open(io.BytesIO(img_data))

            if original.width > 2000:
                ratio = 2000 / original.width
                new_size = (2000, int(original.height * ratio))
                original = original.resize(new_size, Image.Resampling.LANCZOS)

            images.append(original)
            enhanced_images.append(enhance_image_for_ocr(original))
            del pix, img_data
        except Exception as e:
            st.error(f"页码 {i+1} 处理错误: {e}")

    doc.close()
    return images, enhanced_images

def create_radar_chart_image(scores):
    """创建雷达图（支持中文标签）"""
    labels = list(scores.keys())
    values = list(scores.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # 创建图表
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    # 尝试设置中文字体
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        pass

    # 设置背景色
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    ax.grid(color='#2d3548', linestyle='-', linewidth=1.0)
    ax.spines['polar'].set_visible(False)

    # 绘制数据
    ax.plot(angles, values, color='#4a9eff', linewidth=2.5, linestyle='-', zorder=10)
    ax.fill(angles, values, color='#4a9eff', alpha=0.2)
    ax.scatter(angles, values, color='#4a9eff', s=80, edgecolors='white', linewidth=2, zorder=11)
    ax.set_ylim(0, 100)

    # 设置标签
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='#ffffff', weight='bold', fontsize=13)
    ax.tick_params(pad=35)

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=300, facecolor='#1e2130', transparent=False)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

def set_cell_margins(cell, **kwargs):
    """设置单元格边距"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin in ['top', 'left', 'bottom', 'right']:
        if margin in kwargs:
            elm = OxmlElement(f'w:{margin}')
            elm.set(qn('w:w'), str(kwargs[margin]))
            tcMar.append(elm)
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for border in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        if border in kwargs:
            elm = OxmlElement(f'w:{border}')
            for key, value in kwargs[border].items():
                elm.set(qn(f'w:{key}'), str(value))
            tcBorders.append(elm)
    tcPr.append(tcBorders)

def set_run_font(run, chinese_font='宋体', english_font='Times New Roman', size=10.5, bold=False, color=None):
    """设置运行字体 - 中英文分别设置"""
    run.font.name = english_font
    run.font.size = Pt(size)
    run.font.bold = bold

    # 设置中文字体
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), chinese_font)
    rFonts.set(qn('w:ascii'), english_font)
    rFonts.set(qn('w:hAnsi'), english_font)
    rPr.append(rFonts)

    if color:
        color_elem = OxmlElement('w:color')
        color_elem.set(qn('w:val'), color)
        rPr.append(color_elem)

def create_word_docx_simple(report_text, student_name, radar_img_stream=None):
    """创建Word文档 - 麦肯锡咨询报告风格"""
    doc = Document()

    # ==================== 页面设置 ====================
    section = doc.sections[0]
    section.page_height = Cm(29.7)  # A4高度
    section.page_width = Cm(21)     # A4宽度
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)

    # ==================== 设置默认样式 ====================
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(10.5)

    # 设置中文字体
    rPr = style._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '宋体')
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    rPr.append(rFonts)

    # 设置行间距1.5倍
    pPr = style._element.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:line'), '360')  # 1.5倍行距 = 240 * 1.5 = 360
    spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)

    # ==================== 封面/标题页 ====================
    # 主标题
    title = doc.add_heading(level=1)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_run = title.add_run(f"{student_name} 数学诊断报告")
    set_run_font(title_run, chinese_font='黑体', english_font='Arial', size=18, bold=True)
    title_format = title._element.get_or_add_pPr()
    title_spacing = OxmlElement('w:spacing')
    title_spacing.set(qn('w:before'), '240')
    title_spacing.set(qn('w:after'), '120')
    title_format.append(title_spacing)

    # 添加雷达图
    if radar_img_stream:
        try:
            radar_img_stream.seek(0)
            pic_para = doc.add_paragraph()
            pic_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            pic_para.add_run().add_picture(radar_img_stream, width=Inches(4.5))
        except:
            pass

    # ==================== 分隔线 ====================
    doc.add_paragraph('_' * 80)

    # ==================== 解析报告内容 ====================
    lines = report_text.split('\n')
    in_list = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith("```") or line.startswith("---"):
            continue

        # 一级标题
        if line.startswith('# '):
            in_list = False
            text = line.replace('# ', '').replace('数学诊断报告（预览版）', '').replace('数学诊断报告', '').strip()
            if text:
                h1 = doc.add_heading(level=1)
                run = h1.add_run(text)
                set_run_font(run, chinese_font='黑体', english_font='Arial', size=16, bold=True)

                # 标题后间距
                pPr = h1._element.get_or_add_pPr()
                spacing = OxmlElement('w:spacing')
                spacing.set(qn('w:before'), '180')
                spacing.set(qn('w:after'), '120')
                pPr.append(spacing)

        # 二级标题
        elif line.startswith('## '):
            in_list = False
            text = line.replace('## ', '')
            h2 = doc.add_heading(level=2)
            run = h2.add_run(text)
            set_run_font(run, chinese_font='黑体', english_font='Arial', size=14, bold=True)

            # 标题间距
            pPr = h2._element.get_or_add_pPr()
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '120')
            spacing.set(qn('w:after'), '96')
            pPr.append(spacing)

        # 三级标题
        elif line.startswith('### '):
            in_list = False
            text = line.replace('### ', '')
            h3 = doc.add_heading(level=3)
            run = h3.add_run(text)
            set_run_font(run, chinese_font='黑体', size=12, bold=True)

            pPr = h3._element.get_or_add_pPr()
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '96')
            spacing.set(qn('w:after'), '72')
            pPr.append(spacing)

        # 列表项
        elif line.startswith(('- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            # 提取列表标记
            text = line
            marker = ''
            if line.startswith('- '):
                marker = '•'
                text = line[2:]
            elif line.startswith('* '):
                marker = '•'
                text = line[2:]
            elif line.startswith('• '):
                marker = '•'
                text = line[2:]
            elif len(line) > 3 and line[2] == '.' and line[0].isdigit():
                marker = line[:3]
                text = line[3:]

            if not in_list:
                p = doc.add_paragraph(style='List Bullet')
                in_list = True
            else:
                p = doc.add_paragraph(style='List Bullet')

            # 清除默认内容
            p.clear()
            # 添加列表标记
            run = p.add_run(marker + ' ')
            set_run_font(run, size=10.5, bold=True)
            # 添加列表内容
            run = p.add_run(text)
            set_run_font(run, size=10.5)

        # 普通段落
        else:
            in_list = False
            p = doc.add_paragraph()
            run = p.add_run(line)
            set_run_font(run, size=10.5)

            # 段落间距
            pPr = p._element.get_or_add_pPr()
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:after'), '96')  # 段后6磅
            pPr.append(spacing)

    # ==================== 页脚 ====================
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = f"陈老师数学诊断 | 微信：{WECHAT_ID} | 报告生成时间：{time.strftime('%Y-%m-%d')}"
    footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    for run in footer_para.runs:
        set_run_font(run, size=9)

    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io

def create_word_docx_simple(report_text, student_name, radar_img_stream=None):
    """创建Word文档"""
    doc = Document()

    title = doc.add_heading(level=1)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = title.add_run(f"{student_name} 数学诊断报告")
    run.font.size = Pt(18)
    run.bold = True

    if radar_img_stream:
        try:
            radar_img_stream.seek(0)
            doc.add_picture(radar_img_stream, width=Inches(4.5))
        except:
            pass

    lines = report_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith("```"):
            continue

        if line.startswith('# '):
            p = doc.add_heading(level=1)
            run = p.add_run(line.replace('# ', ''))
            run.font.size = Pt(18)
            run.bold = True
        elif line.startswith('## '):
            p = doc.add_heading(level=2)
            run = p.add_run(line.replace('## ', ''))
            run.font.size = Pt(15)
            run.bold = True
        elif line.startswith('### '):
            p = doc.add_heading(level=3)
            run = p.add_run(line.replace('### ', ''))
            run.font.size = Pt(12)
            run.bold = True
        else:
            p = doc.add_paragraph()
            p.add_run(line)

    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io

# ==================== Prompt 模板 ====================
def get_quick_diagnosis_prompt(student_info):
    """快速诊断Prompt"""
    return f"""你是陈老师，一位有11年经验的DSE/高考数学专家。

【学生信息】
{json.dumps(student_info, ensure_ascii=False, indent=2)}

【任务】
请生成一份简明的数学诊断报告（预览版），包含：

1. **当前水平评估**（1-2句话，客观具体）
2. **主要问题识别**（3个要点，针对错题类型）
3. **提分建议**（3条具体可执行的建议）
4. **能力雷达图评分**（JSON格式，6个维度各0-100分，根据错题情况合理分布）

【输出格式】
# {student_info.get('name', '同学')} 数学诊断报告（预览版）

## 一、当前水平评估
[具体评估内容，结合成绩和错题分析]

## 二、主要问题识别
1. [针对第一个错题类型的问题分析]
2. [针对第二个错题类型的问题分析]
3. [针对第三个错题类型的问题分析]

## 三、提分建议
1. [第一条具体建议，包含方法和时间]
2. [第二条具体建议]
3. [第三条具体建议]

## 四、获取完整报告
这是预览版（30%内容）。完整版包含：
- 详细知识漏洞分析
- 个性化学习计划（分阶段）
- 专属练习题库
- 提分时间预测

添加陈老师微信免费领取完整报告：{WECHAT_ID}

---JSON_START---
{{"代数运算": 65, "几何直观": 60, "逻辑推理": 70, "数据分析": 55, "数学建模": 50, "创新意识": 60}}
"""

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: #ffffff; margin: 0;'>诊断设置</h2>
        <p style='color: #8892b0; margin: 5px 0 0 0;'>Configuration</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    exam_type = st.selectbox(
        "考试类型",
        ("DSE - 必修数学", "DSE - 延伸M1", "DSE - 延伸M2", "高考 - 数学"),
        label_visibility="visible"
    )

    student_name = st.text_input("学生姓名", value="同学", placeholder="请输入姓名")

    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(74, 158, 255, 0.1); border: 1px solid #4a9eff; border-radius: 10px; padding: 15px;'>
        <h4 style='color: #ffffff; margin: 0 0 10px 0;'>关于陈老师</h4>
        <p style='color: #8892b0; margin: 5px 0;'>11年数学教学经验</p>
        <p style='color: #8892b0; margin: 5px 0;'>3年DSE国际教育经验</p>
        <p style='color: #8892b0; margin: 5px 0 15px 0;'>专业：DSE延伸数学</p>
        <p style='color: #ffffff; margin: 0;'>微信：<strong>{WECHAT_ID}</strong></p>
    </div>
    """.format(WECHAT_ID=WECHAT_ID), unsafe_allow_html=True)

# ==================== 主内容区 ====================
# 标题区域
st.markdown("""
<div class='main-title'>DSE/高考数学提分潜力诊断</div>
<div class='main-subtitle'>AI驱动的智能诊断 · 精准识别薄弱环节 · 科学规划提分路径</div>
""", unsafe_allow_html=True)

# 模式选择（使用radio避免页面频繁刷新）
mode = st.radio(
    "选择诊断模式",
    ["快速诊断", "深度诊断"],
    horizontal=True,
    label_visibility="collapsed"
)

# 初始化session state
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'quick'

# 只在模式真正改变时更新状态
current_mode = 'quick' if mode == "快速诊断" else 'deep'
if st.session_state['mode'] != current_mode:
    st.session_state['mode'] = current_mode

# ==================== 快速诊断模式 ====================
if mode == "快速诊断":
    st.markdown("""
    <div class='feature-card'>
        <h3>快速诊断</h3>
        <p>填写基本信息，AI系统将快速分析学生的数学学习状况，识别薄弱环节，给出针对性建议</p>
    </div>
    """, unsafe_allow_html=True)

    # 输入区域
    col1, col2 = st.columns(2)
    with col1:
        recent_score = st.number_input("最近一次数学成绩", min_value=0, max_value=160, value=80, step=1)
    with col2:
        total_score = st.number_input("试卷满分", min_value=60, max_value=160, value=150, step=1)

    col1, col2 = st.columns(2)
    with col1:
        wrong_topics = st.multiselect(
            "常错题型（可多选）",
            ["函数与导数", "三角函数", "数列", "解析几何", "概率统计", "立体几何", "延伸数学-微积分", "延伸数学-代数"],
            default=[]
        )
    with col2:
        learning_goal = st.selectbox(
            "学习目标",
            ["夯实基础", "提升成绩", "冲刺高分", "DSE延伸数学入门"]
        )

    # 开始诊断按钮
    if st.button("开始AI诊断", type="primary", use_container_width=True):
        if not wrong_topics:
            st.error("请至少选择一个错题类型，以便AI进行精准分析")
        else:
            student_info = {
                "name": student_name,
                "score": recent_score,
                "total": total_score,
                "wrong_topics": wrong_topics,
                "goal": learning_goal,
                "exam_type": exam_type
            }

            with st.status("AI正在分析中...", expanded=True) as status:
                st.write("分析成绩数据...")
                time.sleep(0.3)
                st.write("识别薄弱环节...")
                time.sleep(0.3)
                st.write("生成诊断报告...")

                prompt = get_quick_diagnosis_prompt(student_info)
                result, source = call_ai_with_fallback(prompt)

                if result:
                    # 提取JSON部分
                    if "---JSON_START---" in result:
                        parts = result.split("---JSON_START---")
                        body = parts[0].strip()
                        json_str = parts[1].strip().replace("```json", "").replace("```", "").strip()
                    else:
                        body = result
                        json_str = '{"代数运算": 60, "几何直观": 60, "逻辑推理": 60, "数据分析": 60, "数学建模": 60, "创新意识": 60}'

                    # 解析雷达图数据
                    try:
                        radar_data = json.loads(json_str)
                    except:
                        radar_data = {"代数运算": 60, "几何直观": 60, "逻辑推理": 60, "数据分析": 60, "数学建模": 60, "创新意识": 60}

                    st.session_state['report_text'] = body
                    st.session_state['radar_img'] = create_radar_chart_image(radar_data)
                    st.session_state['student_name'] = student_name

                    st.toast(f"诊断完成！使用模型：{source}", icon="✅")
                    status.update(label="诊断完成！", state="complete")
                    st.rerun()
                else:
                    st.error(f"诊断失败：{source}")

    # 显示报告
    if 'report_text' in st.session_state:
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("<h3 style='color: #ffffff; margin-bottom: 15px;'>诊断报告</h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-container'>{st.session_state['report_text']}</div>", unsafe_allow_html=True)

        with col2:
            if 'radar_img' in st.session_state:
                st.image(st.session_state['radar_img'], use_container_width=True)

            # 下载按钮
            docx_file = create_word_docx_simple(
                st.session_state['report_text'],
                st.session_state.get('student_name', '同学'),
                st.session_state.get('radar_img')
            )
            st.download_button(
                "📥 下载报告",
                data=docx_file,
                file_name=f"{st.session_state.get('student_name', '同学')}_诊断报告.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        # 微信引流
        st.markdown(f"""
        <div class='wechat-card'>
            <h3>获取完整深度报告</h3>
            <p style='color: #8892b0; margin-bottom: 15px;'>完整版包含详细知识漏洞分析、个性化学习计划、专属练习题库</p>
            <div class='wechat-id'>微信：{WECHAT_ID}</div>
            <p style='color: #8892b0; margin-top: 10px;'>备注【提分】免费领取完整报告</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== 深度诊断模式 ====================
elif mode == "深度诊断":
    st.markdown("""
    <div class='feature-card'>
        <h3>深度诊断</h3>
        <p>上传试卷图片或PDF，AI将逐题分析，生成详细的学习诊断报告</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "上传试卷图片或PDF",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="支持PDF、PNG、JPG格式，建议上传清晰图片"
    )

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()

        if uploaded_file.type == "application/pdf":
            doc_temp = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc_temp)
            doc_temp.close()

            st.info(f"检测到PDF文件，共 {total_pages} 页")

            page_range = st.slider("选择要分析的页面", 1, total_pages, (1, min(3, total_pages)))

            if st.button("开始深度分析", type="primary", use_container_width=True):
                with st.status("AI分析中...", expanded=True) as status:
                    st.write("处理图像...")
                    images, enhanced = process_pdf_bytes(file_bytes, page_range[0], page_range[1])

                    st.write("AI逐题分析...")
                    prompt = f"""你是陈老师，一位有11年经验的DSE/高考数学专家。

请分析这些试卷图片，生成完整的诊断报告。

【学生信息】
- 姓名：{student_name}
- 考试类型：{exam_type}
- 页码范围：{page_range[0]}-{page_range[1]}

【任务】
1. 识别试卷中的题目和作答情况
2. 分析错误原因
3. 给出针对性的学习建议

【输出格式】
使用Markdown格式，包含：
1. 总体评价
2. 逐题分析
3. 薄弱环节诊断
4. 复习建议
"""

                    result, source = call_ai_with_fallback(prompt, enhanced)

                    if result:
                        st.session_state['report_text'] = result
                        st.session_state['student_name'] = student_name

                        st.toast(f"分析完成！使用模型：{source}", icon="✅")
                        status.update(label="分析完成！", state="complete")
                        st.rerun()
                    else:
                        st.error(f"分析失败：{source}")
        else:
            st.info("检测到图片文件")
            st.image(uploaded_file, caption="上传的试卷", use_container_width=True)

            if st.button("开始分析", type="primary", use_container_width=True):
                with st.status("AI分析中..."):
                    image = Image.open(io.BytesIO(file_bytes))
                    enhanced = enhance_image_for_ocr(image)

                    prompt = f"""你是陈老师，一位有11年经验的DSE/高考数学专家。

请分析这张试卷图片，生成诊断报告。

【学生信息】
- 姓名：{student_name}
- 考试类型：{exam_type}

【任务】
分析试卷内容，给出诊断和学习建议。
"""

                    result, source = call_ai_with_fallback(prompt, [enhanced])

                    if result:
                        st.session_state['report_text'] = result
                        st.session_state['student_name'] = student_name
                        st.rerun()
                    else:
                        st.error(f"分析失败：{source}")

    # 显示深度报告
    if 'report_text' in st.session_state:
        st.markdown("<h3 style='color: #ffffff; margin-bottom: 15px;'>深度分析报告</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='report-container'>{st.session_state['report_text']}</div>", unsafe_allow_html=True)

        docx_file = create_word_docx_simple(
            st.session_state['report_text'],
            st.session_state.get('student_name', '同学')
        )

        st.download_button(
            "📥 下载完整报告",
            data=docx_file,
            file_name=f"{st.session_state.get('student_name', '同学')}_深度诊断报告.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

# ==================== 底部信息 ====================
st.markdown("""
<div style='text-align: center; color: #8892b0; font-size: 0.85rem; margin-top: 50px; padding: 20px; border-top: 1px solid #2d3548;'>
    <p>DSE/高考数学诊断工具 v2.0 | 陈老师开发</p>
    <p>AI模型：Gemini 2.5 Pro + GLM-4 Plus 双引擎</p>
</div>
""", unsafe_allow_html=True)
