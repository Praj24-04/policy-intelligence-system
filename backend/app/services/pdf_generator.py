from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

# Color Palette Definitions
COLOR_BLACK = colors.HexColor('#0a0a0a')
COLOR_DARK  = colors.HexColor('#1f2937')
COLOR_MID   = colors.HexColor('#6b7280')
COLOR_LIGHT = colors.HexColor('#9ca3af')
COLOR_RULE  = colors.HexColor('#e8e8e8')
COLOR_ACCENT= colors.HexColor('#5c9e2e')
COLOR_BG    = colors.HexColor('#fafafa')

def generate_policy_pdf(policy_data: dict) -> bytes:
    """
    Generates a professional government-style A4 PDF of the generated policy framework.
    Returns binary bytes for direct attachment/inline downloads.
    """
    country = policy_data.get("country", "Global")
    sector = policy_data.get("sector", "Cybersecurity")
    document = policy_data.get("document", {})
    
    title = document.get("title", f"{country} {sector} Policy Framework")
    short_title = document.get("short_title", f"{sector} Framework")
    
    buffer = BytesIO()
    
    # Doc Template Configuration
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2.5*cm,
        title=title,
        author="PolicyIQ Intelligence Platform",
        subject=f"{sector} Policy Framework for {country}"
    )

    # Styles Setup
    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=COLOR_BLACK,
            spaceAfter=12,
            leading=30,
            alignment=TA_LEFT
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            fontName="Helvetica",
            fontSize=13,
            textColor=COLOR_MID,
            spaceAfter=6,
            leading=18,
            alignment=TA_LEFT
        ),
        "SectionNumber": ParagraphStyle(
            "SectionNumber",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=COLOR_ACCENT,
            spaceAfter=2,
            leading=11,
            alignment=TA_LEFT
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=COLOR_BLACK,
            spaceAfter=8,
            spaceBefore=16,
            leading=18,
            alignment=TA_LEFT
        ),
        "SubsectionTitle": ParagraphStyle(
            "SubsectionTitle",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=COLOR_DARK,
            spaceAfter=4,
            spaceBefore=10,
            leading=14,
            alignment=TA_LEFT
        ),
        "BodyText": ParagraphStyle(
            "BodyText",
            fontName="Helvetica",
            fontSize=10,
            textColor=COLOR_DARK,
            spaceAfter=8,
            leading=16,
            alignment=TA_JUSTIFY
        ),
        "ExecutiveSummary": ParagraphStyle(
            "ExecutiveSummary",
            fontName="Helvetica",
            fontSize=10,
            textColor=COLOR_DARK,
            spaceAfter=6,
            leading=16,
            alignment=TA_JUSTIFY
        ),
        "BulletItem": ParagraphStyle(
            "BulletItem",
            fontName="Helvetica",
            fontSize=10,
            textColor=COLOR_DARK,
            spaceAfter=4,
            leading=15,
            leftIndent=16
        ),
        "SmallMono": ParagraphStyle(
            "SmallMono",
            fontName="Courier",
            fontSize=8,
            textColor=COLOR_MID,
            spaceAfter=2,
            leading=10
        ),
        "Reference": ParagraphStyle(
            "Reference",
            fontName="Helvetica",
            fontSize=9,
            textColor=COLOR_MID,
            spaceAfter=4,
            leading=13,
            leftIndent=16
        )
    }

    story = []

    # ----------------- PAGE 1: COVER PAGE -----------------
    # Top thick accent line
    story.append(HRFlowable(width="100%", thickness=4, color=COLOR_ACCENT, spaceAfter=24))
    
    # Classification badge Table
    badge_data = [[Paragraph("OFFICIAL POLICY FRAMEWORK", styles["SmallMono"])]]
    badge_table = Table(badge_data, colWidths=[6.5*cm])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("POLICYIQ INTELLIGENCE PLATFORM", styles["SmallMono"]))
    story.append(Paragraph(f"{country.upper()}  ·  {sector.upper()}", styles["SmallMono"]))
    story.append(Spacer(1, 12))
    
    # Title & Subtitle
    story.append(Paragraph(title, styles["CoverTitle"]))
    story.append(Paragraph(f"A comprehensive {sector.lower()} legislative framework draft tailored specifically to the domestic regulatory standards of {country}.", styles["CoverSubtitle"]))
    
    story.append(Spacer(1, 24))
    
    # Metadata Table
    now_str = datetime.now().strftime("%B %d, %Y")
    meta_rows = [
        ["Document Type", "National Policy Framework Blueprint"],
        ["Jurisdiction", country],
        ["Sector Focus", sector],
        ["Generated", now_str],
        ["Version", "Draft 1.0.0"],
        ["Classification", "For Official Adaptation"],
        ["Platform Source", "PolicyIQ Pipeline ML-v2"]
    ]
    
    meta_table_data = []
    for r in meta_rows:
        label = Paragraph(r[0].upper(), styles["SmallMono"])
        val = Paragraph(r[1], styles["BodyText"])
        meta_table_data.append([label, val])
        
    meta_table = Table(meta_table_data, colWidths=[4.2*cm, 11.8*cm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, COLOR_BG])
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_RULE, spaceAfter=8))
    
    footer_text = "Generated by the PolicyIQ Intelligence Platform. This model draft serves as an analytical reference. Jurisdictions must consult legal counsel before enacting formal provisions."
    story.append(Paragraph(footer_text, styles["SmallMono"]))
    
    story.append(PageBreak())

    # ----------------- PAGE 2: TABLE OF CONTENTS & SUMMARIES -----------------
    story.append(Paragraph("TABLE OF CONTENTS", styles["SectionNumber"]))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=14))
    
    # TOC Entries
    toc_data = []
    sections = document.get("sections", [])
    for sec in sections:
        toc_title = Paragraph(f"Section {sec.get('number')} — {sec.get('title')}", styles["BodyText"])
        toc_page = Paragraph("—", styles["SmallMono"])
        toc_data.append([toc_title, toc_page])
        
    toc_table = Table(toc_data, colWidths=[14.5*cm, 1.5*cm])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 20))
    
    # Executive Summary Card
    exec_summary_text = document.get("executive_summary", "")
    exec_rows = [
        [Paragraph("EXECUTIVE SUMMARY OVERVIEW", styles["SmallMono"])],
        [Paragraph(exec_summary_text, styles["ExecutiveSummary"])]
    ]
    exec_table = Table(exec_rows, colWidths=[16*cm])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 16),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('LINEBELOW', (0,0), (0,0), 0.5, COLOR_RULE),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 20))
    
    # Gap Analysis Summary (if gaps exist)
    gaps = document.get("gap_analysis_addressed", [])
    if gaps:
        story.append(Paragraph("REGULATORY GAPS REMEDIATED IN THIS DRAFT", styles["SectionNumber"]))
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))
        
        gap_rows = []
        for gap in gaps:
            bullet = Paragraph("●", styles["SectionNumber"])
            gap_desc = Paragraph(f"<b>Gap:</b> {gap.get('gap')}", styles["BodyText"])
            gap_res = Paragraph(f"<b>Remediation:</b> {gap.get('how_addressed')}", styles["BodyText"])
            gap_rows.append([bullet, gap_desc, gap_res])
            
        gap_table = Table(gap_rows, colWidths=[0.5*cm, 7.5*cm, 8.0*cm])
        gap_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE)
        ]))
        story.append(gap_table)
        
    story.append(PageBreak())

    # ----------------- PAGE 3+: PREAMBLE & SECTIONS -----------------
    story.append(Paragraph("LEGISLATIVE PREAMBLE", styles["SectionNumber"]))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=10))
    
    preamble_text = document.get("preamble", "")
    story.append(Paragraph(preamble_text, styles["BodyText"]))
    story.append(Spacer(1, 16))
    
    for sec in sections:
        # Keep section headers together
        sec_header = KeepTogether([
            Paragraph(f"SECTION {sec.get('number')}", styles["SectionNumber"]),
            HRFlowable(width="100%", thickness=1.25, color=COLOR_ACCENT, spaceAfter=4),
            Paragraph(sec.get("title", ""), styles["SectionTitle"]),
        ])
        story.append(sec_header)
        story.append(Paragraph(sec.get("content", ""), styles["BodyText"]))
        
        subsections = sec.get("subsections", [])
        if subsections:
            for sub in subsections:
                story.append(Paragraph(f"{sub.get('number')} {sub.get('title')}", styles["SubsectionTitle"]))
                story.append(Paragraph(sub.get("content", ""), styles["BodyText"]))
        story.append(Spacer(1, 14))
        
    # ----------------- IMPLEMENTATION TIMELINE -----------------
    timeline = document.get("implementation_timeline", [])
    if timeline:
        story.append(PageBreak())
        story.append(Paragraph("ROADMAP & IMPLEMENTATION TIMELINE", styles["SectionNumber"]))
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_RULE, spaceAfter=12))
        
        for phase in timeline:
            phase_title = phase.get("phase", "Phase")
            duration = phase.get("duration", "")
            actions = phase.get("actions", [])
            
            phase_header = Paragraph(f"<b>{phase_title.upper()} ({duration})</b>", styles["SmallMono"])
            
            phase_rows = [[phase_header]]
            for act in actions:
                phase_rows.append([Paragraph(f"→  {act}", styles["BodyText"])])
                
            phase_table = Table(phase_rows, colWidths=[16*cm])
            phase_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), COLOR_BLACK),
                ('TEXTCOLOR', (0,0), (0,0), colors.white),
                ('PADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (0,0), 6),
                ('TOPPADDING', (0,0), (0,0), 6),
                ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG]),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE)
            ]))
            story.append(phase_table)
            story.append(Spacer(1, 16))
            
    # ----------------- REFERENCES -----------------
    refs = document.get("references", [])
    if refs:
        story.append(PageBreak())
        story.append(Paragraph("REGULATORY REFERENCES & BASIS", styles["SectionNumber"]))
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_RULE, spaceAfter=12))
        
        ref_rows = []
        for idx, ref in enumerate(refs, 1):
            ref_badge = Paragraph(f"[{ref.get('id', idx)}]", styles["SectionNumber"])
            ref_details = Paragraph(f"<b>{ref.get('title')}</b> — {ref.get('country')} ({ref.get('year')})", styles["BodyText"])
            ref_relevance = Paragraph(f"<i>Citation Relevance:</i> {ref.get('relevance')}", styles["Reference"])
            ref_rows.append([ref_badge, ref_details, ref_relevance])
            
        ref_table = Table(ref_rows, colWidths=[1.2*cm, 7.8*cm, 7.0*cm])
        ref_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE)
        ]))
        story.append(ref_table)

    # Header / Footer Page Numbers Callbacks
    def add_page_footer(canvas, doc_obj):
        canvas.saveState()
        
        # We suppress running footer elements on Page 1
        if doc_obj.page > 1:
            canvas.setFont('Courier', 8)
            canvas.setFillColor(COLOR_LIGHT)
            
            # Running Header Top
            canvas.drawString(2.5*cm, 28.2*cm, "POLICYIQ INTEL PROFILE")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 28.2*cm, f"{country.upper()} · {sector.upper()}")
            canvas.setStrokeColor(COLOR_RULE)
            canvas.setLineWidth(0.5)
            canvas.line(2.5*cm, 28.0*cm, doc_obj.pagesize[0] - 2.5*cm, 28.0*cm)
            
            # Running Footer Bottom
            canvas.line(2.5*cm, 2.0*cm, doc_obj.pagesize[0] - 2.5*cm, 2.0*cm)
            canvas.drawString(2.5*cm, 1.6*cm, "PolicyIQ Intelligence Platform")
            canvas.drawCentredString(doc_obj.pagesize[0] / 2.0, 1.6*cm, f"Page {doc_obj.page}")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 1.6*cm, f"{short_title.upper()}")
            
        canvas.restoreState()

    # Build the document flow
    doc.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )
    
    buffer.seek(0)
    pdf_bytes = buffer.read()
    return pdf_bytes
