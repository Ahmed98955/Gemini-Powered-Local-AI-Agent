import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem, Flowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch

# --- Utility for inline bold ---
def parse_inline_bold(text):
    # Replace **bold** with <b>bold</b> for reportlab xml
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

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
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(A4[0] / 2.0, 30, f"Page {page_num}")

# --- Main formatting function ---
def format_cv_to_pdf(text, filename="outputs/enhanced_cv.pdf"):
    os.makedirs("outputs", exist_ok=True)

    # --- Document setup ---
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
        title="CV"
    )

    # --- Styles ---
    styles = getSampleStyleSheet()
    main_title = ParagraphStyle(
        name="MainTitle",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        alignment=TA_CENTER,
        spaceAfter=8,
        textColor="#000000"
    )
    header = ParagraphStyle(
        name="Header",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor="#000000"
    )
    section_heading = ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=6,
        textColor="#000000",
        alignment=TA_LEFT
    )
    normal = ParagraphStyle(
        name="Normal",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=0
    )
    bullet = ParagraphStyle(
        name="Bullet",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        leftIndent=15,
        bulletIndent=0,
        bulletFontName="Helvetica",
        bulletFontSize=10,
        textColor="#000000",
        alignment=TA_LEFT
    )
    project_title = ParagraphStyle(
        name="ProjectTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=2,
        textColor="#000000",
        alignment=TA_LEFT
    )
    edu_sub = ParagraphStyle(
        name="EduSub",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        spaceAfter=2,
        alignment=TA_LEFT,
        textColor="#000000"
    )

    # ✅ THIS IS THE CRUCIAL PART!
    bullet_list_style = ListStyle(
        name='BulletList',
        leftIndent=20,
        bulletIndent=10,
        bulletFontName='Helvetica',
        bulletFontSize=10
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
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            content.append(Spacer(1, 0.1 * inch))
            i += 1
            continue

        if i == 0 and re.match(r"^\*\*.+\*\*$", line):
            name = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            content.append(Paragraph(name, main_title))
            i += 1
            continue

        if i == 1 and line:
            content.append(Paragraph(parse_inline_bold(line), header))
            i += 1
            continue

        sec_match = section_reg.match(line)
        if sec_match and sec_match.group(1).strip().lower() in section_names:
            # 🟢 هنا التغيير الهام
            if buffer_bullets:
                content.append(ListFlowable(buffer_bullets, bulletType='bullet', style=bullet_list_style))
                buffer_bullets = []
            if not first_section:
                content.append(Spacer(1, 0.20 * inch))
                content.append(HR())
                content.append(Spacer(1, 0.10 * inch))
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
                buffer_bullets.append(ListItem(Paragraph(bullet_text, bullet)))
            else:
                if buffer_bullets:
                    content.append(ListFlowable(buffer_bullets, bulletType='bullet', style=bullet_list_style))
                    buffer_bullets = []
                content.append(Paragraph(parse_inline_bold(line), normal))
            i += 1
            continue

        if current_section == 'projects':
            proj_title_match = re.match(r"^\*\*(.+?)\*\*\s*:?\s*(.*)", line)
            if proj_title_match:
                proj_title = proj_title_match.group(1).strip()
                proj_desc = proj_title_match.group(2).strip()
                content.append(Paragraph(proj_title, project_title))
                if proj_desc:
                    content.append(Paragraph(parse_inline_bold(proj_desc), normal))
            elif line.startswith("* ") or line.startswith("- "):
                bullet_text = parse_inline_bold(line[2:].strip())
                content.append(Paragraph(f"• {bullet_text}", bullet))
            else:
                content.append(Paragraph(parse_inline_bold(line), normal))
            i += 1
            continue

        if current_section == 'education':
            deg_match = re.match(r"^\*\*(.+?)\*\*\s*(.+)?", line)
            if deg_match:
                degree = deg_match.group(1).strip()
                rest = deg_match.group(2).strip() if deg_match.group(2) else ""
                content.append(Paragraph(degree, project_title))
                if rest:
                    content.append(Paragraph(parse_inline_bold(rest), edu_sub))
            else:
                content.append(Paragraph(parse_inline_bold(line), edu_sub))
            i += 1
            continue

        if current_section == 'experience':
            if line.startswith("* ") or line.startswith("- "):
                bullet_text = parse_inline_bold(line[2:].strip())
                buffer_bullets.append(ListItem(Paragraph(bullet_text, bullet)))
            else:
                if buffer_bullets:
                    content.append(ListFlowable(buffer_bullets, bulletType='bullet', style=bullet_list_style))
                    buffer_bullets = []
                content.append(Paragraph(parse_inline_bold(line), normal))
            i += 1
            continue

        if current_section == 'summary':
            content.append(Paragraph(parse_inline_bold(line), normal))
            i += 1
            continue

        if line.startswith("* ") or line.startswith("- "):
            bullet_text = parse_inline_bold(line[2:].strip())
            buffer_bullets.append(ListItem(Paragraph(bullet_text, bullet)))
            i += 1
            continue

        if buffer_bullets:
            content.append(ListFlowable(buffer_bullets, bulletType='bullet', style=bullet_list_style))
            buffer_bullets = []
        content.append(Paragraph(parse_inline_bold(line), normal))
        i += 1

    if buffer_bullets:
        content.append(ListFlowable(buffer_bullets, bulletType='bullet', style=bullet_list_style))

    doc.build(content, onLaterPages=add_page_number, onFirstPage=add_page_number)

    print(f"✅ Enhanced CV formatted and saved as: {filename}")