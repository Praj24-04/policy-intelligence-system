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

def generate_comparison_pdf(comp_data: dict) -> bytes:
    """
    Generates a professional side-by-side coherence and gap comparison report between two policies.
    """
    p1 = comp_data.get("policy_1", comp_data.get("policy1", {}))
    p2 = comp_data.get("policy_2", comp_data.get("policy2", {}))
    p1_title = p1.get("title", "Policy A")
    p2_title = p2.get("title", "Policy B")
    p1_country = p1.get("country", "Jurisdiction A")
    p2_country = p2.get("country", "Jurisdiction B")
    p1_sector = p1.get("sector", "Universal")
    p2_sector = p2.get("sector", "Universal")
    p1_year = p1.get("year", "N/A")
    p2_year = p2.get("year", "N/A")

    metrics = comp_data.get("overall_metrics", {})
    composite = metrics.get("composite_score", 0.0)
    sim_label = metrics.get("similarity_label", "Moderate")

    shared = comp_data.get("shared_tags", [])
    only1 = comp_data.get("only_policy1_tags", [])
    only2 = comp_data.get("only_policy2_tags", [])
    recs = comp_data.get("recs_and_alignment") or comp_data.get("insights") or "No custom alignment advice calculated."

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2.5*cm,
        title=f"Coherence Comparison: {p1_country} vs {p2_country}",
        author="PolicyIQ Intelligence Platform",
        subject="Regulatory Policy Coherence and Gap Alignment Audit"
    )

    styles = {
        "Title": ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=20, textColor=COLOR_BLACK, spaceAfter=12, leading=26),
        "Subtitle": ParagraphStyle("S", fontName="Helvetica", fontSize=11, textColor=COLOR_MID, spaceAfter=8, leading=16),
        "SecNum": ParagraphStyle("SN", fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_ACCENT, spaceAfter=2, leading=11),
        "SecTitle": ParagraphStyle("ST", fontName="Helvetica-Bold", fontSize=13, textColor=COLOR_BLACK, spaceAfter=6, spaceBefore=12, leading=16),
        "Body": ParagraphStyle("B", fontName="Helvetica", fontSize=10, textColor=COLOR_DARK, spaceAfter=8, leading=15),
        "Mono": ParagraphStyle("M", fontName="Courier", fontSize=8, textColor=COLOR_MID, spaceAfter=2, leading=10)
    }

    story = []

    # COVER PAGE
    story.append(HRFlowable(width="100%", thickness=4, color=COLOR_ACCENT, spaceAfter=20))
    story.append(Table([[Paragraph("REGULATORY COMPARISON & COHERENCE REPORT", styles["Mono"])]], colWidths=[9*cm], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ])))
    story.append(Spacer(1, 12))
    story.append(Paragraph("POLICYIQ ALIGNMENT ENGINE", styles["Mono"]))
    story.append(Paragraph(f"COMPARISON AUDIT REPORT", styles["Title"]))
    story.append(Paragraph(f"An automated cross-jurisdiction semantic coherence and regulatory gap audit comparing policies in the {p1_sector} domain.", styles["Subtitle"]))
    story.append(Spacer(1, 16))

    # Meta Comparison Table
    meta_rows = [
        [Paragraph("COMPLETED JURISDICTIONS", styles["Mono"]), Paragraph(f"<b>Policy A:</b> {p1_country} ({p1_year})<br/><b>Policy B:</b> {p2_country} ({p2_year})", styles["Body"])],
        [Paragraph("POLICY A TITLE", styles["Mono"]), Paragraph(p1_title, styles["Body"])],
        [Paragraph("POLICY B TITLE", styles["Mono"]), Paragraph(p2_title, styles["Body"])],
        [Paragraph("COMPOSITE SIMILARITY", styles["Mono"]), Paragraph(f"<b>{int(composite * 100)}%</b> — {sim_label.upper()} ALIGNMENT", styles["Body"])],
        [Paragraph("GENERATED TIMESTAMP", styles["Mono"]), Paragraph(datetime.now().strftime("%B %d, %Y"), styles["Body"])],
    ]
    meta_table = Table(meta_rows, colWidths=[5*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, COLOR_BG])
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 24))

    # Verdict Box
    verdict_text = ""
    if composite > 0.8: verdict_text = "These policies are nearly identical in approach and coverage. Compliance with one substantially satisfies the other."
    elif composite > 0.65: verdict_text = "Strong alignment exists on core principles. Key differences lie in enforcement mechanisms and jurisdictional scope."
    elif composite > 0.5: verdict_text = "Moderate overlap with meaningful divergence. Shared values but distinct implementation approaches reflect different regulatory contexts."
    elif composite > 0.35: verdict_text = "Limited alignment. These policies address related domains but through fundamentally different frameworks and priorities."
    else: verdict_text = "Distinct approaches. These policies represent contrasting regulatory philosophies and are best understood as complementary rather than comparable."

    verdict_rows = [
        [Paragraph("POLICYIQ ALIGNMENT VERDICT", styles["Mono"])],
        [Paragraph(f"<b>Summary:</b> {verdict_text}", styles["Body"])]
    ]
    verdict_table = Table(verdict_rows, colWidths=[16*cm])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ]))
    story.append(verdict_table)
    story.append(PageBreak())

    # PAGE 2: METRICS & SHARED COVERAGE
    story.append(Paragraph("01 OVERALL ALIGNMENT METRICS", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))
    
    metric_rows = [
        [Paragraph("METRIC TYPE", styles["Mono"]), Paragraph("CORRESPONDING ALIGNMENT VALUE", styles["Mono"])],
        [Paragraph("Semantic Intent Similarity", styles["Body"]), Paragraph(f"{int(metrics.get('semantic_similarity_score', composite) * 100)}%", styles["Body"])],
        [Paragraph("Structural Provisions Similarity", styles["Body"]), Paragraph(f"{int(metrics.get('structured_similarity_score', composite) * 100)}%", styles["Body"])],
        [Paragraph("Entity Overlap Weight", styles["Body"]), Paragraph(f"{int(metrics.get('entity_overlap_score', composite) * 100)}%", styles["Body"])],
        [Paragraph("<b>Composite Coherence Score</b>", styles["Body"]), Paragraph(f"<b>{int(composite * 100)}% ({sim_label})</b>", styles["Body"])],
    ]
    metric_table = Table(metric_rows, colWidths=[8*cm, 8*cm])
    metric_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG)
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("02 SHARED REGULATORY COVERAGE", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))
    
    if shared:
        shared_text = ", ".join([s.upper() for s in shared])
        story.append(Paragraph(f"Both regulatory frameworks establish parallel clauses addressing the following domains:<br/><br/><b>{shared_text}</b>", styles["Body"]))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Compliance Synergy: Systems satisfying these overlapping obligations are automatically compliant across both jurisdictions.", styles["Body"]))
    else:
        story.append(Paragraph("No direct shared compliance tags discovered between these frameworks.", styles["Body"]))
        
    story.append(PageBreak())

    # PAGE 3: COVERAGE GAPS & DIVERGENCE
    story.append(Paragraph("03 UNIQUE PROVISIONS & DIVERGENCES", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))

    gap_data = [
        [Paragraph(f"UNIQUE TO JURISDICTION A ({p1_country})", styles["Mono"]), Paragraph(f"UNIQUE TO JURISDICTION B ({p2_country})", styles["Mono"])]
    ]
    
    p1_unique_cells = []
    if only1:
        for t in only1:
            p1_unique_cells.append(f"• {t.capitalize()}")
    else:
        p1_unique_cells.append("No completely unique clauses detected.")
        
    p2_unique_cells = []
    if only2:
        for t in only2:
            p2_unique_cells.append(f"• {t.capitalize()}")
    else:
        p2_unique_cells.append("No completely unique clauses detected.")
        
    gap_data.append([
        Paragraph("<br/>".join(p1_unique_cells), styles["Body"]),
        Paragraph("<br/>".join(p2_unique_cells), styles["Body"])
    ])
    
    gap_table = Table(gap_data, colWidths=[8*cm, 8*cm])
    gap_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG)
    ]))
    story.append(gap_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("04 RECOMMENDED ALIGNMENT ADVICE", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))
    
    if isinstance(recs, list):
        for rec in recs:
            story.append(Paragraph(f"→ {rec}", styles["Body"]))
    else:
        story.append(Paragraph(recs, styles["Body"]))

    def add_page_decor(canvas, doc_obj):
        canvas.saveState()
        if doc_obj.page > 1:
            canvas.setFont('Courier', 8)
            canvas.setFillColor(COLOR_LIGHT)
            canvas.drawString(2.5*cm, 28.2*cm, "POLICYIQ COHERENCE COMPARISON")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 28.2*cm, f"{p1_country.upper()} VS {p2_country.upper()}")
            canvas.setStrokeColor(COLOR_RULE)
            canvas.setLineWidth(0.5)
            canvas.line(2.5*cm, 28.0*cm, doc_obj.pagesize[0] - 2.5*cm, 28.0*cm)
            canvas.line(2.5*cm, 2.0*cm, doc_obj.pagesize[0] - 2.5*cm, 2.0*cm)
            canvas.drawString(2.5*cm, 1.6*cm, "PolicyIQ Alignment Engine")
            canvas.drawCentredString(doc_obj.pagesize[0] / 2.0, 1.6*cm, f"Page {doc_obj.page}")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 1.6*cm, f"{sim_label.upper()} COHERENCE")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_decor, onLaterPages=add_page_decor)
    buffer.seek(0)
    return buffer.read()

def generate_recommendations_pdf(rec_data: dict) -> bytes:
    """
    Generates a professional 5-factor machine learning cross-border adoption recommendation report.
    """
    src_pol = rec_data.get("source_policy", {})
    src_title = src_pol.get("title", "Source Policy")
    src_country = src_pol.get("country", "Origin")
    src_sector = src_pol.get("sector", "Universal")
    src_year = src_pol.get("year", "N/A")

    weights = rec_data.get("weights", {})
    recs = rec_data.get("recommendations", [])

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2.5*cm,
        title=f"Adoption Recommendations: {src_title}",
        author="PolicyIQ Intelligence Platform",
        subject="Policy Cross-Border Adoption Feasibility & Gap Study"
    )

    styles = {
        "Title": ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=20, textColor=COLOR_BLACK, spaceAfter=12, leading=26),
        "Subtitle": ParagraphStyle("S", fontName="Helvetica", fontSize=11, textColor=COLOR_MID, spaceAfter=8, leading=16),
        "SecNum": ParagraphStyle("SN", fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_ACCENT, spaceAfter=2, leading=11),
        "SecTitle": ParagraphStyle("ST", fontName="Helvetica-Bold", fontSize=13, textColor=COLOR_BLACK, spaceAfter=6, spaceBefore=12, leading=16),
        "Body": ParagraphStyle("B", fontName="Helvetica", fontSize=10, textColor=COLOR_DARK, spaceAfter=8, leading=15),
        "Mono": ParagraphStyle("M", fontName="Courier", fontSize=8, textColor=COLOR_MID, spaceAfter=2, leading=10)
    }

    story = []

    # COVER PAGE
    story.append(HRFlowable(width="100%", thickness=4, color=COLOR_ACCENT, spaceAfter=20))
    story.append(Table([[Paragraph("POLICY ADOPTION FEASIBILITY STUDY", styles["Mono"])]], colWidths=[7.5*cm], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ])))
    story.append(Spacer(1, 12))
    story.append(Paragraph("POLICYIQ DECISION INTELLIGENCE", styles["Mono"]))
    story.append(Paragraph(f"ADOPTION FEASIBILITY BRIEF", styles["Title"]))
    story.append(Paragraph(f"A 5-factor machine learning evaluation identifying global jurisdictions with the highest priority gaps and compatibility readiness to adopt the target framework.", styles["Subtitle"]))
    story.append(Spacer(1, 16))

    # Meta Info Table
    meta_rows = [
        [Paragraph("SOURCE FRAMEWORK", styles["Mono"]), Paragraph(f"<b>{src_title}</b>", styles["Body"])],
        [Paragraph("ORIGIN JURISDICTION", styles["Mono"]), Paragraph(f"{src_country} ({src_year})", styles["Body"])],
        [Paragraph("SECTOR DOMAIN", styles["Mono"]), Paragraph(src_sector, styles["Body"])],
        [Paragraph("FACTOR WEIGHTS APPLIED", styles["Mono"]), Paragraph(f"Gap Severity: {int(weights.get('sector_gap', 0.35)*100)}% | Infrastructure: {int(weights.get('regulatory_maturity', 0.25)*100)}%<br/>Intent Match: {int(weights.get('semantic_need', 0.20)*100)}% | Geopolitical Peer: {int(weights.get('regional_pressure', 0.12)*100)}%<br/>Developmental: {int(weights.get('economic_tier', 0.08)*100)}%", styles["Body"])],
        [Paragraph("ANALYSIS TIMESTAMP", styles["Mono"]), Paragraph(datetime.now().strftime("%B %d, %Y"), styles["Body"])],
    ]
    meta_table = Table(meta_rows, colWidths=[5*cm, 11*cm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, COLOR_BG])
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 24))

    # Overview text
    story.append(Paragraph("<b>Evaluation Posture:</b> This analytical feasibility study maps domestic regulatory deficits across other sovereign entities, assessing where the source guidelines address urgent legal omissions while fitting the target country's active technological and economic ecosystem.", styles["Body"]))
    story.append(PageBreak())

    # PAGE 2: TOP RECOMMENDED JURISDICTIONS
    story.append(Paragraph("01 TOP JURISDICTION ADOPTION PRIORITIES", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=8))
    
    rec_headers = [
        [Paragraph("RANK", styles["Mono"]), Paragraph("COUNTRY/JURISDICTION", styles["Mono"]), Paragraph("NEED SCORE", styles["Mono"]), Paragraph("ACTIVE GAP STATE", styles["Mono"]), Paragraph("MATURITY", styles["Mono"])]
    ]
    for idx, r in enumerate(recs, 1):
        score_num = r.get("need_score", r.get("overall_score", r.get("score", 0)))
        score_val = f"{int(score_num * 100)}%"
        
        has_sector = r.get("already_has_sector", False)
        gap_state = "Framework Enhancement" if has_sector else "GAP DETECTED (High Need)"
        
        maturity = r.get("regulatory_maturity", r.get("maturity_level", "Developing")).upper()
        
        rec_headers.append([
            Paragraph(f"#{idx}", styles["Body"]),
            Paragraph(f"<b>{r.get('country')}</b>", styles["Body"]),
            Paragraph(score_val, styles["Body"]),
            Paragraph(gap_state, styles["Body"]),
            Paragraph(maturity, styles["Body"])
        ])
        
    rec_table = Table(rec_headers, colWidths=[1.5*cm, 5.0*cm, 2.5*cm, 4.5*cm, 2.5*cm])
    rec_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_RULE),
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG)
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 16))

    # PAGE 3+: JURISDICTION ANALYSIS SHEETS
    story.append(PageBreak())
    story.append(Paragraph("02 TARGET FEASIBILITY PROFILES & DETAILS", styles["SecNum"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=12))

    for idx, r in enumerate(recs[:4], 1):
        country_name = r.get("country")
        score_num = r.get("need_score", r.get("overall_score", r.get("score", 0)))
        overall_score = f"{int(score_num * 100)}%"
        
        story.append(KeepTogether([
            Paragraph(f"#{idx} PROFILE: {country_name.upper()}  (Need Index: {overall_score})", styles["SecTitle"]),
            HRFlowable(width="100%", thickness=0.75, color=COLOR_ACCENT, spaceAfter=6)
        ]))
        
        bullets = []
        
        # Why this country (Reasoning)
        reasoning = r.get("reasoning")
        if reasoning:
            bullets.append(f"<b>Why this country:</b> {reasoning}")
        else:
            reasoning_list = r.get("reasoning_steps", r.get("reasons", []))
            for step_text in reasoning_list:
                bullets.append(f"• {step_text}")
        
        # Expected Benefits
        benefits = r.get("expected_benefits", [])
        if benefits:
            bullets.append("<b>Expected benefits:</b>")
            for b in benefits:
                bullets.append(f"  • {b}")
                
        if not bullets:
            bullets.append("• Critical infrastructure lacks standard security baselines in this sector.")
            bullets.append("• Cross-border alignment with geopolitical peers creates strong adoption pressures.")
            
        story.append(Paragraph("<br/>".join(bullets), styles["Body"]))
        story.append(Spacer(1, 12))

    def add_page_decor(canvas, doc_obj):
        canvas.saveState()
        if doc_obj.page > 1:
            canvas.setFont('Courier', 8)
            canvas.setFillColor(COLOR_LIGHT)
            canvas.drawString(2.5*cm, 28.2*cm, "POLICYIQ CROSS-BORDER RECS")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 28.2*cm, f"SOURCE: {src_country.upper()}")
            canvas.setStrokeColor(COLOR_RULE)
            canvas.setLineWidth(0.5)
            canvas.line(2.5*cm, 28.0*cm, doc_obj.pagesize[0] - 2.5*cm, 28.0*cm)
            canvas.line(2.5*cm, 2.0*cm, doc_obj.pagesize[0] - 2.5*cm, 2.0*cm)
            canvas.drawString(2.5*cm, 1.6*cm, "PolicyIQ Decision Intelligence")
            canvas.drawCentredString(doc_obj.pagesize[0] / 2.0, 1.6*cm, f"Page {doc_obj.page}")
            canvas.drawRightString(doc_obj.pagesize[0] - 2.5*cm, 1.6*cm, f"{src_sector.upper()} ADOPTION")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_decor, onLaterPages=add_page_decor)
    buffer.seek(0)
    return buffer.read()
