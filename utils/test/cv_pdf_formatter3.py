import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Register Arial and Arial Bold fonts from Windows Fonts ---
arial_path = r"C:\Windows\Fonts\Arial.ttf"
arial_bold_path = r"C:\Windows\Fonts\arialbd.ttf"

pdfmetrics.registerFont(TTFont("Arial", arial_path))
pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold_path))

# --- Utility for inline bold ---
def parse_inline_bold(text):
    # Replace **bold** with <b>bold</b> for reportlab xml
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\\1</b>", text)

# --- Utility to check and add hyperlinks ---
def parse_hyperlinks(text):
    url_regex = r"(https?://[^\s,]+)"
    mail_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    text = re.sub(url_regex, r'<a href="\\1" color="blue">\\1</a>', text)
    text = re.sub(mail_regex, r'<a href="mailto:\\1" color="blue">\\1</a>', text)
    return text

# --- Custom Horizontal Line Flowable ---
class HR(Flowable):
    def __init__(self, width=None, thickness=0.7, color=(0, 0, 0), space_before=6, space_after=6):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.space_after = space_after

    def wrap(self, availWidth, availHeight):
        self.width = self.width or availWidth
        return (self.width, self.thickness + self.space_before + self.space_after)

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColorRGB(*self.color)
        self.canv.setLineWidth(self.thickness)
        y = self.space_after / 2
        self.canv.line(0, y, self.width, y)
        self.canv.restoreState()

# --- Footer (page numbers) ---
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Arial", 9)
    canvas.drawCentredString(A4[0] / 2.0, 30, f"Page {page_num}")

# --- Main formatting function ---
def format_cv_to_pdf(text, filename="outputs/enhanced_cv.pdf"):
    os.makedirs("outputs", exist_ok=True)

    # --- Document setup ---
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="CV"
    )

    # --- Styles ---
    main_title = ParagraphStyle(
        name="MainTitle",
        fontName="Arial-Bold",
        fontSize=20,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor="#000000"
    )
    job_title = ParagraphStyle(
        name="JobTitle",
        fontName="Arial-Bold",
        fontSize=15,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor="#000000"
    )
    header_info = ParagraphStyle(
        name="HeaderInfo",
        fontName="Arial",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor="#000000"
    )
    section_heading = ParagraphStyle(
        name="SectionHeading",
        fontName="Arial-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=16,
        spaceAfter=8,
        textColor="#000000",
        alignment=TA_LEFT
    )
    normal = ParagraphStyle(
        name="Normal",
        fontName="Arial",
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=0
    )
    dash_bullet = ParagraphStyle(
        name="DashBullet",
        fontName="Arial",
        fontSize=12,
        leading=16,
        leftIndent=14,
        bulletIndent=0,
        bulletFontName="Arial",
        bulletFontSize=12,
        textColor="#000000",
        alignment=TA_LEFT
    )
    project_title = ParagraphStyle(
        name="ProjectTitle",
        fontName="Arial-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=2,
        textColor="#000000",
        alignment=TA_LEFT
    )
    edu_sub = ParagraphStyle(
        name="EduSub",
        fontName="Arial",
        fontSize=11,
        leading=13,
        spaceAfter=2,
        alignment=TA_LEFT,
        textColor="#000000"
    )

    bullet_list_style = ListStyle(
        name='DashBulletList',
        leftIndent=22,
        bulletIndent=12,
        bulletFontName='Arial',
        bulletFontSize=12
    )

    # --- Section names for detection ---
    section_names = [
        'summary', 'skills', 'experience', 'education', 'certifications', 'projects', 'awards'
    ]
    section_reg = re.compile(r"^\s*\*\*(.+?)\*\*\s*$", re.IGNORECASE)
    current_section = None
    content = []
    buffer_bullets = []
    first_section = True

    lines = text.splitlines()
    i = 0
    # --- Header block: each line alone (اسم، وظيفة، إيميل، لينكدإن، Github) ---
    while i < len(lines):
        line = lines[i].strip()
        if not line or i > 6:
            break
        if i == 0 and re.match(r"^\*\*.+\*\*$", line):
            name = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            content.append(Paragraph(name, main_title))
        elif i == 1 and line:
            content.append(Paragraph(parse_inline_bold(line), job_title))
        else:
            if line:
                content.append(Paragraph(parse_hyperlinks(line), header_info))
        i += 1
    content.append(Spacer(1, 0.2 * inch))

    # --- Main Content parsing ---
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            content.append(Spacer(1, 0.1 * inch))
            i += 1
            continue

        sec_match = section_reg.match(line)
        if sec_match and sec_match.group(1).strip().lower() in section_names:
            if buffer_bullets:
                content.append(ListFlowable(buffer_bullets, bulletType='bullet', start='–', style=bullet_list_style))
                buffer_bullets = []
            if not first_section:
                content.append(Spacer(1, 0.23 * inch))
                content.append(HR())
                content.append(Spacer(1, 0.12 * inch))
            first_section = False
            section_title = sec_match.group(1).strip()
            content.append(Paragraph(section_title, section_heading))
            current_section = section_title.lower()
            content.append(Spacer(1, 0.08 * inch))
            i += 1
            continue

        if current_section in ['skills', 'certifications', 'awards']:
            if line.startswith("* ") or line.startswith("- "):
                bullet_text = parse_inline_bold(line[2:].strip())
                bullet_text = parse_hyperlinks(bullet_text)
                buffer_bullets.append(ListItem(Paragraph(bullet_text, dash_bullet), bulletText='–'))
            else:
                if buffer_bullets:
                    content.append(ListFlowable(buffer_bullets, bulletType='bullet', start='–', style=bullet_list_style))
                    buffer_bullets = []
                content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), normal))
            i += 1
            continue

        if current_section == 'projects':
            proj_title_match = re.match(r"^\*\*(.+?)\*\*\s*:?\s*(.*)", line)
            if proj_title_match:
                proj_title = proj_title_match.group(1).strip()
                proj_desc = proj_title_match.group(2).strip()
                content.append(Paragraph(proj_title, project_title))
                if proj_desc:
                    content.append(Paragraph(parse_hyperlinks(parse_inline_bold(proj_desc)), normal))
            elif line.startswith("* ") or line.startswith("- "):
                bullet_text = parse_inline_bold(line[2:].strip())
                bullet_text = parse_hyperlinks(bullet_text)
                content.append(Paragraph(f"– {bullet_text}", dash_bullet))
            else:
                content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), normal))
            i += 1
            continue

        if current_section == 'education':
            deg_match = re.match(r"^\*\*(.+?)\*\*\s*(.+)?", line)
            if deg_match:
                degree = deg_match.group(1).strip()
                rest = deg_match.group(2).strip() if deg_match.group(2) else ""
                content.append(Paragraph(degree, project_title))
                if rest:
                    content.append(Paragraph(parse_hyperlinks(parse_inline_bold(rest)), edu_sub))
            else:
                content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), edu_sub))
            i += 1
            continue

        if current_section == 'experience':
            if line.startswith("* ") or line.startswith("- "):
                bullet_text = parse_inline_bold(line[2:].strip())
                bullet_text = parse_hyperlinks(bullet_text)
                buffer_bullets.append(ListItem(Paragraph(bullet_text, dash_bullet), bulletText='–'))
            else:
                if buffer_bullets:
                    content.append(ListFlowable(buffer_bullets, bulletType='bullet', start='–', style=bullet_list_style))
                    buffer_bullets = []
                content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), normal))
            i += 1
            continue

        if current_section == 'summary':
            content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), normal))
            i += 1
            continue

        if line.startswith("* ") or line.startswith("- "):
            bullet_text = parse_inline_bold(line[2:].strip())
            bullet_text = parse_hyperlinks(bullet_text)
            buffer_bullets.append(ListItem(Paragraph(bullet_text, dash_bullet), bulletText='–'))
            i += 1
            continue

        if buffer_bullets:
            content.append(ListFlowable(buffer_bullets, bulletType='bullet', start='–', style=bullet_list_style))
            buffer_bullets = []
        content.append(Paragraph(parse_hyperlinks(parse_inline_bold(line)), normal))
        i += 1

    if buffer_bullets:
        content.append(ListFlowable(buffer_bullets, bulletType='bullet', start='–', style=bullet_list_style))

    doc.build(content, onLaterPages=add_page_number, onFirstPage=add_page_number)

    print(f"✅ Enhanced CV formatted and saved as: {filename}")