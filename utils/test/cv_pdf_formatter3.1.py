# utils/cv_pdf_formatter.py

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch


def format_cv_to_pdf(text, filename="outputs/enhanced_cv.pdf"):
    os.makedirs("outputs", exist_ok=True)

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        name="Normal",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )

    heading = ParagraphStyle(
        name="Heading",
        fontName="Helvetica-Bold",
        fontSize=13,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.HexColor("#003366"),
        alignment=TA_LEFT
    )

    bullet = ParagraphStyle(
        name="Bullet",
        parent=normal,
        bulletFontName="Helvetica",
        bulletIndent=0,
        leftIndent=15,
    )

    content = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            content.append(Spacer(1, 0.15 * inch))
            continue

        # Heading if line is surrounded by ** and short
        if re.match(r"^\*\*(.+)\*\*$", line) and len(line) < 80:
            title = re.sub(r"\*\*(.+)\*\*", r"\1", line)
            content.append(Paragraph(title, heading))
        elif line.startswith("* ") or line.startswith("- "):
            bullet_text = line[2:].strip()
            content.append(Paragraph(f"• {bullet_text}", bullet))
        else:
            # Remove inline **bold** text (optional: you can enhance this to support inline bold)
            line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            content.append(Paragraph(line, normal))

    doc.build(content)
    print(f"✅ Enhanced CV formatted and saved as: {filename}")