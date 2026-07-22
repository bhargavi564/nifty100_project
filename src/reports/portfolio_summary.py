import os
import sqlite3
import pandas as pd
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

# Resolve paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
PORTFOLIO_DIR = BASE_DIR / "reports" / "portfolio"
OUTPUT_PDF = PORTFOLIO_DIR / "portfolio_summary.pdf"

PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)

def evaluate_trend(curr, prev, is_lower_better=False):
    """Evaluates the trend between two periods and returns a formatted string with colors."""
    if pd.isna(curr) or pd.isna(prev) or prev == 0:
        return "<font color='grey'><b>[ = ] Flat (N/A)</b></font>"
    
    pct_change = ((curr - prev) / abs(prev)) * 100
    
    if is_lower_better:
        if pct_change < -2.0:
            return "<font color='green'><b>[ ↑ ] Improved</b></font>"
        elif pct_change > 2.0:
            return "<font color='red'><b>[ ↓ ] Declined</b></font>"
        else:
            return "<font color='grey'><b>[ → ] Flat</b></font>"
    else:
        if pct_change > 2.0:
            return "<font color='green'><b>[ ↑ ] Improved</b></font>"
        elif pct_change < -2.0:
            return "<font color='red'><b>[ ↓ ] Declined</b></font>"
        else:
            return "<font color='grey'><b>[ → ] Flat</b></font>"

def run_portfolio_summary():
    print("[INFO] Generating Day 35 Portfolio Summary PDF...")

    if not DB_PATH.exists():
        print(f"[CRITICAL] Database missing at {DB_PATH}")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios ORDER BY company_id ASC, year ASC", conn)
    df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    conn.close()

    if df_ratios.empty:
        return False

    # Initialize PDF Document
    doc = SimpleDocTemplate(str(OUTPUT_PDF), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('NavyHeader', parent=styles['Heading1'], backColor=colors.navy, textColor=colors.white, alignment=1, spaceAfter=20, padding=15)
    sub_style = ParagraphStyle('SubHeader', parent=styles['Heading2'], textColor=colors.dimgrey, alignment=1, spaceAfter=30)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=10, leading=14)

    story = []
    companies = df_ratios["company_id"].unique()

    for comp in companies:
        comp_df = df_ratios[df_ratios["company_id"] == comp]
        sector_val = df_peers[df_peers["company_id"] == comp]["peer_group_name"].values
        sector = sector_val[0] if len(sector_val) > 0 else "General Sector"

        if len(comp_df) < 1:
            continue
            
        latest = comp_df.iloc[-1]
        prev = comp_df.iloc[-2] if len(comp_df) >= 2 else latest

        # Page Header
        story.append(Paragraph(f"<b>{comp} Ltd.</b>", header_style))
        story.append(Paragraph(f"Sector Classification: {sector}", sub_style))

        # KPI Setup
        kpis = [
            ("Return on Equity (%)", latest.get("return_on_equity_pct"), prev.get("return_on_equity_pct"), False),
            ("Net Profit Margin (%)", latest.get("net_profit_margin_pct"), prev.get("net_profit_margin_pct"), False),
            ("Debt to Equity (x)", latest.get("debt_to_equity"), prev.get("debt_to_equity"), True),
            ("5Yr Revenue CAGR (%)", latest.get("revenue_cagr_5yr"), prev.get("revenue_cagr_5yr"), False),
            ("Free Cash Flow (Cr)", latest.get("free_cash_flow"), prev.get("free_cash_flow"), False),
            ("Interest Coverage (x)", latest.get("interest_coverage"), prev.get("interest_coverage"), False)
        ]

        # Table Construction
        table_data = [[
            Paragraph("<b>Core Metric</b>", styles['Normal']), 
            Paragraph("<b>Latest Year</b>", styles['Normal']), 
            Paragraph("<b>Previous Year</b>", styles['Normal']), 
            Paragraph("<b>YoY Trend</b>", styles['Normal'])
        ]]

        for name, curr_val, prev_val, is_lower_better in kpis:
            c_val = f"{curr_val:.2f}" if pd.notna(curr_val) else "N/A"
            p_val = f"{prev_val:.2f}" if pd.notna(prev_val) else "N/A"
            trend = evaluate_trend(curr_val, prev_val, is_lower_better)
            
            table_data.append([
                Paragraph(name, cell_style),
                Paragraph(c_val, cell_style),
                Paragraph(p_val, cell_style),
                Paragraph(trend, cell_style)
            ])

        t = Table(table_data, colWidths=[150, 100, 100, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(t)
        story.append(PageBreak()) # One page per company

    doc.build(story)
    print(f"[SUCCESS] Portfolio Summary generated at: {OUTPUT_PDF}")
    return True

if __name__ == "__main__":
    run_portfolio_summary()