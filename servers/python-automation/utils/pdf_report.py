"""
pdf_report.py — Lizard Interactive branded PDF generator.
Called from tools/lighthouse.py after AI analysis is complete.
"""

import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

# ── Brand tokens ──────────────────────────────────────────────────────────────
GREEN  = colors.HexColor("#4ADE80")
DARK   = colors.HexColor("#0F172A")
MID    = colors.HexColor("#1E293B")
GRAY   = colors.HexColor("#64748B")
RED    = colors.HexColor("#F87171")
AMBER  = colors.HexColor("#FBBF24")
BLUE   = colors.HexColor("#60A5FA")
WHITE  = colors.white
LIGHT  = colors.HexColor("#F8FAFC")
STRIPE = colors.HexColor("#F1F5F9")
GRID_C = colors.HexColor("#CBD5E1")


def _score_color(score):
    if score is None: return GRAY
    s = float(score)
    if s >= 0.90: return GREEN
    if s >= 0.50: return AMBER
    return RED


def _score_label(score):
    if score is None: return "N/A"
    s = float(score)
    if s >= 0.90: return "GOOD"
    if s >= 0.50: return "NEEDS WORK"
    return "POOR"


def _pct(score):
    if score is None: return "N/A"
    return f"{int(round(float(score) * 100))}%"


def _S(name, **kw):
    return ParagraphStyle(name, **kw)


# ── Public entry point ────────────────────────────────────────────────────────

def build(url: str, metrics: dict, ai: dict, output_path: str):
    """Generate the branded Lighthouse AI PDF report."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm, bottomMargin=14*mm,
    )
    W = A4[0] - 36*mm

    # Styles
    sTitle   = _S("sTitle",  fontSize=20, textColor=GREEN,  fontName="Helvetica-Bold", spaceAfter=2)
    sH1      = _S("sH1",     fontSize=13, textColor=GREEN,  fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)
    sBody    = _S("sBody",   fontSize=9,  textColor=DARK,   fontName="Helvetica", leading=14, spaceAfter=4)
    sBodyW   = _S("sBodyW",  fontSize=9,  textColor=WHITE,  fontName="Helvetica", leading=14, spaceAfter=4)
    sMono    = _S("sMono",   fontSize=8,  textColor=GRAY,   fontName="Courier",   spaceAfter=4)
    sBulletW = _S("sBulletW",fontSize=9,  textColor=WHITE,  fontName="Helvetica", leading=13, leftIndent=10, spaceAfter=3)
    sFooter  = _S("sFooter", fontSize=7,  textColor=GRAY,   fontName="Helvetica", alignment=TA_CENTER)

    ts_str = datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")
    story  = []

    # ── Header ──────────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph("🦎 LIZARD INTERACTIVE", _S("hb", fontSize=10, textColor=GREEN, fontName="Helvetica-Bold")),
        Paragraph(f"Lighthouse AI Report<br/><font color='#64748B' size='7'>{ts_str}</font>",
                  _S("hr", fontSize=9, textColor=WHITE, fontName="Helvetica", alignment=TA_RIGHT)),
    ]], colWidths=[W*0.6, W*0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), DARK),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING",  (0,0),(0,-1),  12),
        ("RIGHTPADDING", (-1,0),(-1,-1),12),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [hdr, Spacer(1,8),
              Paragraph("Performance Audit", sTitle),
              Paragraph(url, sMono),
              HRFlowable(width=W, color=GREEN, thickness=1.5, spaceAfter=10)]

    # ── Score cards ──────────────────────────────────────────────────────────
    story.append(Paragraph("Overall Scores", sH1))
    cats = [
        ("Performance",    metrics.get("performance")),
        ("Accessibility",  metrics.get("accessibility")),
        ("Best Practices", metrics.get("best_practices")),
        ("SEO",            metrics.get("seo")),
    ]
    card_row = []
    for label, score in cats:
        col = _score_color(score)
        card_row.append([
            Paragraph(label, _S(f"cl{label}", fontSize=8, textColor=GRAY, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(f'<font color="{col.hexval()}">{_pct(score)}</font>',
                      _S(f"cs{label}", fontSize=24, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(_score_label(score), _S(f"cv{label}", fontSize=7, textColor=col, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        ])
    score_tbl = Table([card_row], colWidths=[W/4]*4)
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), LIGHT),
        ("BOX",          (0,0),(-1,-1), 0.5, GRAY),
        ("INNERGRID",    (0,0),(-1,-1), 0.5, GRAY),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [score_tbl, Spacer(1,12)]

    # ── Core Web Vitals ──────────────────────────────────────────────────────
    story.append(Paragraph("Core Web Vitals", sH1))
    vitals = [
        ("LCP",         metrics.get("lcp","N/A"),         "Largest Contentful Paint — target < 2.5s"),
        ("TBT / FID",   metrics.get("tbt","N/A"),         "Total Blocking Time — target < 200ms"),
        ("CLS",         metrics.get("cls","N/A"),         "Cumulative Layout Shift — target < 0.1"),
        ("FCP",         metrics.get("fcp","N/A"),         "First Contentful Paint — target < 1.8s"),
        ("TTI",         metrics.get("tti","N/A"),         "Time to Interactive — target < 3.8s"),
        ("Speed Index", metrics.get("speed_index","N/A"), "Speed Index — target < 3.4s"),
    ]
    vrows = [["Metric","Value","Benchmark"]]
    for n, v, b in vitals:
        vrows.append([
            Paragraph(f"<b>{n}</b>", sBody),
            Paragraph(str(v), sBody),
            Paragraph(b, _S("bench", fontSize=8, textColor=GRAY, fontName="Helvetica")),
        ])
    vtbl = Table(vrows, colWidths=[W*0.2, W*0.18, W*0.62])
    vtbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), DARK),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("GRID",          (0,0),(-1,-1), 0.4, GRID_C),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [vtbl, Spacer(1,12)]

    # ── Executive Summary ────────────────────────────────────────────────────
    story.append(Paragraph("AI Executive Summary", sH1))
    summ = Table([[Paragraph(ai.get("executive_summary",""), sBodyW)]], colWidths=[W])
    summ.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), MID),
        ("TOPPADDING",   (0,0),(-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
    ]))
    story += [summ, Spacer(1,12)]

    # ── Critical Issues + Quick Wins ─────────────────────────────────────────
    story.append(Paragraph("Key Findings", sH1))
    def bullets(items):
        return [Paragraph(f"•  {i}", sBulletW) for i in items]

    two_col = Table([[
        [Paragraph("Critical Issues", _S("ci", fontSize=11, textColor=RED,   fontName="Helvetica-Bold", spaceAfter=4))]
        + bullets(ai.get("critical_issues",[])),
        [Paragraph("Quick Wins",      _S("qw", fontSize=11, textColor=GREEN, fontName="Helvetica-Bold", spaceAfter=4))]
        + bullets(ai.get("quick_wins",[])),
    ]], colWidths=[W*0.5-4, W*0.5-4])
    two_col.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,-1), colors.HexColor("#3B0000")),
        ("BACKGROUND",   (1,0),(1,-1), colors.HexColor("#052E16")),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING",  (0,0),(-1,-1), 12),
        ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]))
    story += [two_col, Spacer(1,12)]

    # ── Priority Actions ─────────────────────────────────────────────────────
    story.append(Paragraph("Priority Action Plan", sH1))
    arows = [["#", "Action", "Impact", "Effort", "Detail"]]
    for i, a in enumerate(ai.get("priority_actions",[]), 1):
        impact = a.get("impact","")
        effort = a.get("effort","")
        ic = RED if impact=="High" else (AMBER if impact=="Medium" else GREEN)
        ec = AMBER if effort=="High" else (BLUE  if effort=="Medium" else GREEN)
        arows.append([
            Paragraph(f"<b>{i}</b>", sBody),
            Paragraph(f"<b>{a.get('title','')}</b>", sBody),
            Paragraph(f'<font color="{ic.hexval()}"><b>{impact}</b></font>', sBody),
            Paragraph(f'<font color="{ec.hexval()}"><b>{effort}</b></font>', sBody),
            Paragraph(a.get("detail",""), _S("det", fontSize=8, textColor=DARK, fontName="Helvetica", leading=12)),
        ])
    atbl = Table(arows, colWidths=[W*0.05, W*0.22, W*0.1, W*0.1, W*0.53])
    atbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), DARK),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("GRID",          (0,0),(-1,-1), 0.4, GRID_C),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story += [atbl, Spacer(1,12)]

    # ── Opportunities ────────────────────────────────────────────────────────
    if metrics.get("opportunities"):
        story.append(Paragraph("Top Opportunities", sH1))
        orows = [["Opportunity","Savings","Score"]]
        for o in metrics["opportunities"]:
            sc = o.get("score") or 0
            col = _score_color(sc)
            orows.append([
                Paragraph(o["title"], sBody),
                Paragraph(f"<b>{o['savings']}</b>", sBody),
                Paragraph(f'<font color="{col.hexval()}"><b>{_pct(sc)}</b></font>', sBody),
            ])
        otbl = Table(orows, colWidths=[W*0.65, W*0.2, W*0.15])
        otbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), DARK),
            ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
            ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,0), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
            ("GRID",          (0,0),(-1,-1), 0.4, GRID_C),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story += [otbl, Spacer(1,12)]

    # ── Detailed verdicts (page 2) ───────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Detailed AI Analysis", sH1))
    for title_v, body_v in [
        ("Performance Deep-Dive",  ai.get("performance_verdict","")),
        ("SEO Analysis",           ai.get("seo_verdict","")),
        ("Accessibility Review",   ai.get("accessibility_verdict","")),
    ]:
        story.append(Paragraph(title_v, _S("vH", fontSize=11, textColor=DARK,
                                           fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)))
        story.append(HRFlowable(width=W, color=GREEN, thickness=0.8, spaceAfter=4))
        story.append(Paragraph(body_v, sBody))
        story.append(Spacer(1,6))

    # ── Next Steps ───────────────────────────────────────────────────────────
    story += [Spacer(1,8), Paragraph("Recommended Next Steps", sH1)]
    ns = Table([[Paragraph(ai.get("next_steps",""), sBodyW)]], colWidths=[W])
    ns.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#0C2340")),
        ("TOPPADDING",   (0,0),(-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
    ]))
    story += [ns, Spacer(1,16),
              HRFlowable(width=W, color=GRAY, thickness=0.5, spaceAfter=6),
              Paragraph(f"Generated by Lizard Interactive AI Auditor  •  {ts_str}  •  {url}", sFooter)]

    doc.build(story)