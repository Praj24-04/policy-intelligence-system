from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
    PageBreak, KeepTogether, Image, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os

def get_logo_header(styles: dict):
    """
    Returns a borderless Table flowable with the brand logo and powered-by text
    if the logo exists, or just the text styled beautifully.
    """
    logo_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png"))
    powered_text = "POWERED BY PASSIONIT PRUTL KALKI AIDHARMA"
    powered_p = Paragraph(powered_text, styles.get("PoweredByHeader", styles.get("SmallMono")))
    
    if os.path.exists(logo_path):
        try:
            # Scale logo to a clean size: 1.6cm width, 1.6cm height (or 45pt x 45pt)
            logo_img = Image(logo_path, width=1.6*cm, height=1.6*cm)
            
            # Create a 2-column table: col1 for logo, col2 for text
            logo_table = Table([[logo_img, powered_p]], colWidths=[2.0*cm, 14.0*cm])
            logo_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (1,0), (1,0), 8),
                ('PADDING', (0,0), (-1,-1), 0),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ]))
            return logo_table
        except Exception as e:
            print(f"[WARN] Error loading logo in PDF generator: {e}")
            
    # Fallback to text only if image is not found or fails to load
    return Table([[powered_p]], colWidths=[16.0*cm], style=TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))

# Color Palette Definitions
COLOR_BLACK = colors.HexColor('#0a0a0a')
COLOR_DARK  = colors.HexColor('#1f2937')
COLOR_MID   = colors.HexColor('#6b7280')
COLOR_LIGHT = colors.HexColor('#9ca3af')
COLOR_RULE  = colors.HexColor('#e8e8e8')
COLOR_ACCENT= colors.HexColor('#5c9e2e')
COLOR_BG    = colors.HexColor('#fafafa')

# Shared dictionary to store page numbers dynamically during compilation
_page_registry = {}

class PageTracker(Flowable):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def draw(self):
        # Record the page number of this specific location in the document flow
        _page_registry[self.key] = self.canv.getPageNumber()

    def wrap(self, availWidth, availHeight):
        # Return tiny size (1pt x 1pt) so the layout engine evaluates and executes draw()
        return 1.0, 1.0


class HeaderFooterCanvas(canvas.Canvas):
    def __init__(self, *args, doc_info=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._doc_info = doc_info or {}
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_header_footer(self, total_pages):
        page_num = self._pageNumber
        w, h = A4

        country  = self._doc_info.get("country",  "Global")
        doc_type = self._doc_info.get("doc_type", "POLICY FRAMEWORK")
        logo_path = os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        )

        # ─────────────────────────────────────────────────────────────
        # HEADER  (top band)
        # ─────────────────────────────────────────────────────────────
        HEADER_TOP    = h - 0.6*cm   # top of the header zone
        HEADER_BOTTOM = h - 2.0*cm   # bottom of the header zone
        header_mid_y  = (HEADER_TOP + HEADER_BOTTOM) / 2  # vertical centre

        # Subtle light background strip
        self.setFillColor(colors.HexColor('#f8faf7'))
        self.rect(0, HEADER_BOTTOM, w, HEADER_TOP - HEADER_BOTTOM, fill=1, stroke=0)

        # LEFT: logo  +  platform name
        logo_x   = 2.5*cm
        text_x   = logo_x
        logo_size = 1.1*cm

        if os.path.exists(logo_path):
            try:
                logo_y = header_mid_y - logo_size / 2
                self.drawImage(logo_path, logo_x, logo_y,
                               width=logo_size, height=logo_size,
                               preserveAspectRatio=True, mask='auto')
                text_x = logo_x + logo_size + 0.35*cm
            except Exception:
                pass

        # Platform name (primary, bold, dark)
        self.setFont("Helvetica-Bold", 9.0)
        self.setFillColor(colors.HexColor('#1a2e1a'))
        self.drawString(text_x, header_mid_y + 0.10*cm, "PolicyIQ Intelligence Platform")

        # Tagline below (smaller, muted)
        self.setFont("Helvetica", 7.0)
        self.setFillColor(colors.HexColor('#6b7280'))
        self.drawString(text_x, header_mid_y - 0.30*cm, "Powered by PASSIONIT PRUTL KALKI AIDHARMA")

        # RIGHT: document descriptor  +  country/sector chip
        right_x = w - 2.5*cm
        doc_label = f"{country.upper()}  ·  {doc_type.upper()}"
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#374151'))
        self.drawRightString(right_x, header_mid_y + 0.10*cm, doc_label)

        # Accent dot line separator under RIGHT text
        self.setFont("Helvetica", 6.5)
        self.setFillColor(colors.HexColor('#9ca3af'))
        generated_label = f"Generated  {datetime.now().strftime('%d %b %Y')}"
        self.drawRightString(right_x, header_mid_y - 0.30*cm, generated_label)

        # Thick accent rule at the very bottom of the header zone
        self.setStrokeColor(COLOR_ACCENT)
        self.setLineWidth(2.0)
        self.line(0, HEADER_BOTTOM, w, HEADER_BOTTOM)

        # Hairline just below the accent rule for depth
        self.setStrokeColor(colors.HexColor('#d1fae5'))
        self.setLineWidth(0.5)
        self.line(0, HEADER_BOTTOM - 0.5, w, HEADER_BOTTOM - 0.5)

        # ─────────────────────────────────────────────────────────────
        # FOOTER  (bottom band)
        # ─────────────────────────────────────────────────────────────
        FOOTER_TOP    = 2.4*cm
        FOOTER_BOTTOM = 0.5*cm

        # Solid dark footer background
        self.setFillColor(colors.HexColor('#1a2e1a'))
        self.rect(0, FOOTER_BOTTOM, w, FOOTER_TOP - FOOTER_BOTTOM, fill=1, stroke=0)

        footer_mid_y = (FOOTER_TOP + FOOTER_BOTTOM) / 2

        # LEFT: platform name in white
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.white)
        self.drawString(2.5*cm, footer_mid_y + 0.14*cm, "PolicyIQ")

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#86efac'))   # soft green
        self.drawString(2.5*cm + 1.55*cm, footer_mid_y + 0.14*cm, "Intelligence Platform")

        # CENTRE: disclaimer — subdued
        self.setFont("Helvetica-Oblique", 6.0)
        self.setFillColor(colors.HexColor('#9ca3af'))
        disclaimer = "AI-assisted content — human review required before formal adoption."
        self.drawCentredString(w / 2, footer_mid_y + 0.14*cm, disclaimer)

        # RIGHT: page counter
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#86efac'))
        self.drawRightString(w - 2.5*cm, footer_mid_y + 0.14*cm,
                             f"Page  {page_num} / {total_pages}")

        # Thin accent stripe at the very top edge of the footer band
        self.setStrokeColor(COLOR_ACCENT)
        self.setLineWidth(1.5)
        self.line(0, FOOTER_TOP, w, FOOTER_TOP)

def generate_policy_pdf(policy_data: dict) -> bytes:
    """
    Generates a professional government-style A4 PDF of the generated policy framework
    using a standard double-pass layout compiler to resolve dynamic page numbers.
    """
    _page_registry.clear()  # Clear registry in-place so imported references remain valid
    
    # Pass 1: Build document to discover exact layout page boundaries
    _build_policy_pdf_flow(policy_data)
    
    # Pass 2: Re-build document using recorded section page numbers in TOC
    return _build_policy_pdf_flow(policy_data)

def _build_policy_pdf_flow(policy_data: dict) -> bytes:
    """
    Core layout builder for generating a government-style policy blueprint PDF.
    """
    country = policy_data.get("country", "Global")
    sector = policy_data.get("sector", "Cybersecurity")
    document = policy_data.get("document", {})
    
    title = document.get("title", f"{country} {sector} Policy Framework")
    short_title = document.get("short_title", f"{sector} Framework")
    
    buffer = BytesIO()
    
    # Doc Template Configuration — margins clear the full-bleed header (2.0cm) and footer (2.4cm)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2.4*cm,
        bottomMargin=3.0*cm,
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
        ),
        "PoweredByHeader": ParagraphStyle(
            "PoweredByHeader",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=COLOR_ACCENT,
            leading=11,
            alignment=TA_LEFT
        ),
        "DisclaimerText": ParagraphStyle(
            "DisclaimerText",
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            textColor=COLOR_MID,
            spaceBefore=6,
            leading=10,
            alignment=TA_JUSTIFY
        )
    }

    story = []

    # ----------------- PAGE 1: COVER PAGE -----------------
    story.append(Spacer(1, 10))
    
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
    story.append(Spacer(1, 12))
    
    # AI Human-in-the-loop Advisory Note
    disclaimer_box = Table(
        [[Paragraph("<b>Disclaimer:</b> Use of AI exists, so user human-in-loop needed for decision making.", styles["DisclaimerText"])]],
        colWidths=[16*cm]
    )
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ]))
    story.append(disclaimer_box)
    
    story.append(PageBreak())

    # ----------------- PAGE 2: TABLE OF CONTENTS & SUMMARIES -----------------
    story.append(Paragraph("TABLE OF CONTENTS", styles["SectionNumber"]))
    story.append(Spacer(1, 2))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_RULE, spaceAfter=14))
    
    # TOC Entries
    toc_data = []
    sections = document.get("sections", [])
    for sec in sections:
        sec_num = sec.get("number")
        toc_title = Paragraph(f"Section {sec_num} — {sec.get('title')}", styles["BodyText"])
        # Query the page registry for the resolved page number from Pass 1
        p_num = _page_registry.get(f"sec_{sec_num}", "—")
        toc_page = Paragraph(str(p_num), styles["SmallMono"])
        toc_data.append([toc_title, toc_page])
        
    timeline = document.get("implementation_timeline", [])
    if timeline:
        road_page = _page_registry.get("timeline", "—")
        toc_data.append([
            Paragraph("Roadmap & Implementation Timeline", styles["BodyText"]),
            Paragraph(str(road_page), styles["SmallMono"])
        ])
        
    refs = document.get("references", [])
    if refs:
        refs_page = _page_registry.get("references", "—")
        toc_data.append([
            Paragraph("Regulatory References & Basis", styles["BodyText"]),
            Paragraph(str(refs_page), styles["SmallMono"])
        ])
        
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
        # Register the page tracker Flowable so it logs the section's exact resolved page
        story.append(PageTracker(f"sec_{sec.get('number')}"))
        
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
        story.append(PageTracker("timeline"))
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
        story.append(PageTracker("references"))
        story.append(Paragraph("REGULATORY REFERENCES & BASIS", styles["SectionNumber"]))
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_RULE, spaceAfter=12))
        
        ref_rows = []
        for idx, ref in enumerate(refs, 1):
            ref_badge = Paragraph(f"[{ref.get('id', idx)}]", styles["SectionNumber"])
            
            # Clickable dynamic reference link
            source_link = ref.get("source_url")
            link_html = ""
            if source_link:
                link_html = f"<br/><font size='8' color='#5c9e2e'>Source Link: <u><a href='{source_link}'>{source_link}</a></u></font>"
                
            ref_details = Paragraph(f"<b>{ref.get('title')}</b> — {ref.get('country')} ({ref.get('year')}){link_html}", styles["BodyText"])
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

    class MyCanvas(HeaderFooterCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, doc_info={
                "country": country,
                "sector": sector,
                "doc_type": "POLICY FRAMEWORK Blueprint",
                "short_title": short_title
            }, **kwargs)

    # Build the document flow
    doc.build(
        story,
        canvasmaker=MyCanvas
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
        topMargin=2.4*cm,
        bottomMargin=3.0*cm,
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
        "Mono": ParagraphStyle("M", fontName="Courier", fontSize=8, textColor=COLOR_MID, spaceAfter=2, leading=10),
        "PoweredByHeader": ParagraphStyle("PH", fontName="Helvetica-Bold", fontSize=8.5, textColor=COLOR_ACCENT, leading=11, alignment=TA_LEFT),
        "DisclaimerText": ParagraphStyle("DT", fontName="Helvetica-Oblique", fontSize=7.5, textColor=COLOR_MID, spaceBefore=6, leading=10, alignment=TA_JUSTIFY)
    }

    story = []

    # COVER PAGE
    story.append(Spacer(1, 10))
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

    p1_url = p1.get("source_url") or ""
    p2_url = p2.get("source_url") or ""
    
    p1_link_html = f"<br/><font size='8' color='#5c9e2e'>Source Link: <u><a href='{p1_url}'>{p1_url}</a></u></font>" if p1_url else ""
    p2_link_html = f"<br/><font size='8' color='#5c9e2e'>Source Link: <u><a href='{p2_url}'>{p2_url}</a></u></font>" if p2_url else ""

    # Meta Comparison Table
    meta_rows = [
        [Paragraph("COMPLETED JURISDICTIONS", styles["Mono"]), Paragraph(f"<b>Policy A:</b> {p1_country} ({p1_year})<br/><b>Policy B:</b> {p2_country} ({p2_year})", styles["Body"])],
        [Paragraph("POLICY A TITLE", styles["Mono"]), Paragraph(f"<b>{p1_title}</b>{p1_link_html}", styles["Body"])],
        [Paragraph("POLICY B TITLE", styles["Mono"]), Paragraph(f"<b>{p2_title}</b>{p2_link_html}", styles["Body"])],
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
    story.append(Spacer(1, 14))
    
    # AI Human-in-the-loop Advisory Note
    disclaimer_box = Table(
        [[Paragraph("<b>Disclaimer:</b> Use of AI exists, so user human-in-loop needed for decision making.", styles["DisclaimerText"])]],
        colWidths=[16*cm]
    )
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ]))
    story.append(disclaimer_box)
    
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

    class MyCanvas(HeaderFooterCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, doc_info={
                "country": f"{p1_country} vs {p2_country}",
                "sector": p1_sector,
                "doc_type": "COHERENCE COMPARISON"
            }, **kwargs)

    doc.build(story, canvasmaker=MyCanvas)
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
        topMargin=2.4*cm,
        bottomMargin=3.0*cm,
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
        "Mono": ParagraphStyle("M", fontName="Courier", fontSize=8, textColor=COLOR_MID, spaceAfter=2, leading=10),
        "PoweredByHeader": ParagraphStyle("PH", fontName="Helvetica-Bold", fontSize=8.5, textColor=COLOR_ACCENT, leading=11, alignment=TA_LEFT),
        "DisclaimerText": ParagraphStyle("DT", fontName="Helvetica-Oblique", fontSize=7.5, textColor=COLOR_MID, spaceBefore=6, leading=10, alignment=TA_JUSTIFY)
    }

    story = []

    # COVER PAGE
    story.append(Spacer(1, 10))
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

    src_url = src_pol.get("source_url") or ""
    src_link_html = f"<br/><font size='8' color='#5c9e2e'>Source Link: <u><a href='{src_url}'>{src_url}</a></u></font>" if src_url else ""

    # Meta Info Table
    meta_rows = [
        [Paragraph("SOURCE FRAMEWORK", styles["Mono"]), Paragraph(f"<b>{src_title}</b>{src_link_html}", styles["Body"])],
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
    story.append(Spacer(1, 14))
    
    # AI Human-in-the-loop Advisory Note
    disclaimer_box = Table(
        [[Paragraph("<b>Disclaimer:</b> Use of AI exists, so user human-in-loop needed for decision making.", styles["DisclaimerText"])]],
        colWidths=[16*cm]
    )
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_RULE),
    ]))
    story.append(disclaimer_box)
    
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

    class MyCanvas(HeaderFooterCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, doc_info={
                "country": src_country,
                "sector": src_sector,
                "doc_type": "ADOPTION STUDY"
            }, **kwargs)

    doc.build(story, canvasmaker=MyCanvas)
    buffer.seek(0)
    return buffer.read()
