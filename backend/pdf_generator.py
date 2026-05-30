from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

# ── Color Palette ─────────────────────────────────────────────
DARK_BG = HexColor('#0f1117')
CARD_BG = HexColor('#1a1d2e')
BLUE = HexColor('#2563eb')
LIGHT_BLUE = HexColor('#60a5fa')
GREEN = HexColor('#34d399')
YELLOW = HexColor('#fbbf24')
RED = HexColor('#f87171')
TEXT_PRIMARY = HexColor('#e2e8f0')
TEXT_SECONDARY = HexColor('#94a3b8')
BORDER = HexColor('#2d3748')


def get_risk_color(score):
    if score >= 61:
        return RED
    elif score >= 31:
        return YELLOW
    return GREEN


def get_risk_label(score):
    if score >= 61:
        return "HIGH RISK"
    elif score >= 31:
        return "MEDIUM RISK"
    return "LOW RISK"


def generate_vendor_pdf(report_data: dict) -> bytes:
    """
    Generates a professional PDF risk report for a vendor.
    Returns the PDF as bytes so it can be sent via API.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    # ── Styles ─────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=TEXT_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        textColor=TEXT_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=LIGHT_BLUE,
        spaceBefore=16,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=TEXT_PRIMARY,
        spaceAfter=6,
        leading=16
    )

    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=TEXT_SECONDARY,
        spaceAfter=4
    )

    # ── Extract Data ───────────────────────────────────────────
    vendor_name = report_data.get('vendor_name', 'Unknown')
    risk_score = report_data.get('risk_score', 0)
    risk_level = report_data.get('risk_level', 'UNKNOWN')
    summary = report_data.get('summary', '')
    key_findings = report_data.get('key_findings', [])
    risk_categories = report_data.get('risk_categories', {})
    recommended_actions = report_data.get('recommended_actions', [])
    confidence = report_data.get('confidence_level', 'MEDIUM')
    signals_found = report_data.get('signals_found', 0)
    scan_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    risk_color = get_risk_color(risk_score)
    risk_label = get_risk_label(risk_score)

    # ── Build PDF Content ──────────────────────────────────────
    content = []

    # Header background table
    header_data = [[
        Paragraph("🛡 VENDORGUARD AI", title_style),
    ]]
    header_table = Table(header_data, colWidths=[515])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    content.append(header_table)
    content.append(Spacer(1, 4))

    # Subtitle
    content.append(Paragraph("VENDOR RISK INTELLIGENCE REPORT", subtitle_style))
    content.append(Paragraph(f"Generated on {scan_date}", small_style))
    content.append(Spacer(1, 16))

    # ── Vendor + Score Banner ──────────────────────────────────
    score_data = [[
        Paragraph(f"<b>{vendor_name}</b>", ParagraphStyle(
            'VN', parent=styles['Normal'],
            fontSize=20, fontName='Helvetica-Bold',
            textColor=TEXT_PRIMARY
        )),
        Paragraph(
            f"<b>{risk_score}</b>",
            ParagraphStyle(
                'Score', parent=styles['Normal'],
                fontSize=36, fontName='Helvetica-Bold',
                textColor=risk_color, alignment=TA_CENTER
            )
        ),
    ]]
    score_table = Table(score_data, colWidths=[320, 195])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, BORDER),
    ]))
    content.append(score_table)

    # Risk level badge row
    badge_data = [[
        Paragraph(
            f"Risk Level: <b>{risk_label}</b>  |  "
            f"Confidence: <b>{confidence}</b>  |  "
            f"Signals Collected: <b>{signals_found}</b>",
            ParagraphStyle(
                'Badge', parent=styles['Normal'],
                fontSize=10, fontName='Helvetica',
                textColor=risk_color, alignment=TA_CENTER
            )
        )
    ]]
    badge_table = Table(badge_data, colWidths=[515])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 2, risk_color),
    ]))
    content.append(badge_table)
    content.append(Spacer(1, 16))

    # ── Summary ────────────────────────────────────────────────
    content.append(Paragraph("EXECUTIVE SUMMARY", section_title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 8))
    content.append(Paragraph(summary, body_style))
    content.append(Spacer(1, 12))

    # ── Key Findings ───────────────────────────────────────────
    content.append(Paragraph(
        f"KEY FINDINGS ({len(key_findings)})",
        section_title_style
    ))
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 8))

    for finding in key_findings:
        finding_data = [[
            Paragraph(f"• {finding}", body_style)
        ]]
        finding_table = Table(finding_data, colWidths=[515])
        finding_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ('LINEAFTER', (0, 0), (0, -1), 3, risk_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(finding_table)
        content.append(Spacer(1, 6))

    content.append(Spacer(1, 12))

    # ── Risk Categories ────────────────────────────────────────
    content.append(Paragraph("RISK BREAKDOWN BY CATEGORY", section_title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 8))

    cat_items = list(risk_categories.items())
    # Build 2x2 grid
    rows = []
    for i in range(0, len(cat_items), 2):
        row = []
        for j in range(2):
            if i + j < len(cat_items):
                k, v = cat_items[i + j]
                label = k.replace('_risk', '').replace('_', ' ').upper()
                color = get_risk_color(v)
                cell = Paragraph(
                    f"<b>{label}</b><br/>"
                    f"<font size=22 color='#{color.hexval()}'><b>{v}/100</b></font>",
                    ParagraphStyle(
                        'Cat', parent=styles['Normal'],
                        fontSize=10, textColor=TEXT_SECONDARY,
                        alignment=TA_CENTER, leading=28
                    )
                )
                row.append(cell)
            else:
                row.append(Paragraph("", body_style))
        rows.append(row)

    if rows:
        cat_table = Table(rows, colWidths=[252, 252], rowHeights=70)
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(cat_table)

    content.append(Spacer(1, 16))

    # ── Recommended Actions ────────────────────────────────────
    content.append(Paragraph("RECOMMENDED ACTIONS", section_title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 8))

    for i, action in enumerate(recommended_actions, 1):
        action_data = [[
            Paragraph(f"<b>{i}</b>", ParagraphStyle(
                'Num', parent=styles['Normal'],
                fontSize=14, fontName='Helvetica-Bold',
                textColor=BLUE, alignment=TA_CENTER
            )),
            Paragraph(f"→ {action}", body_style)
        ]]
        action_table = Table(action_data, colWidths=[40, 475])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBEFORE', (0, 0), (0, -1), 3, BLUE),
        ]))
        content.append(action_table)
        content.append(Spacer(1, 6))

    content.append(Spacer(1, 20))

    # ── Footer ─────────────────────────────────────────────────
    content.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    content.append(Spacer(1, 8))
    content.append(Paragraph(
        "This report was generated automatically by VendorGuard AI. "
        "Data is collected from public web sources using Bright Data infrastructure. "
        "This report is for informational purposes and should be reviewed by a qualified risk professional.",
        ParagraphStyle(
            'Footer', parent=styles['Normal'],
            fontSize=8, textColor=TEXT_SECONDARY,
            alignment=TA_CENTER, leading=14
        )
    ))

    # ── Build PDF ──────────────────────────────────────────────
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()