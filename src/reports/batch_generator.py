import os
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Resolve paths and inject reports module
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "reports"))

import tearsheet

# Setup Day 34 specific directories
REPORTS_DIR = BASE_DIR / "reports"
TEARSHEETS_DIR = REPORTS_DIR / "tearsheets"
SECTOR_DIR = REPORTS_DIR / "sector"
SKIPPED_CSV = BASE_DIR / "output" / "skipped_tearsheets.csv"
DB_PATH = BASE_DIR / "data" / "nifty100.db"

# Override Day 33's output directory dynamically
tearsheet.OUTPUT_DIR = TEARSHEETS_DIR
TEARSHEETS_DIR.mkdir(parents=True, exist_ok=True)
SECTOR_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "output").mkdir(parents=True, exist_ok=True)

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def run_batch_generation():
    print("[INFO] Starting Day 34 Batch Report Generation...")

    if not DB_PATH.exists():
        print(f"[CRITICAL] Database missing at {DB_PATH}")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    conn.close()

    if df_ratios.empty:
        print("[WARNING] No data found in financial_ratios.")
        return False

    # 1. Batch Tearsheets & Skip Logic
    print("\n[PHASE 1] Generating Company Tearsheets...")
    companies = df_ratios["company_id"].unique()
    skipped = []
    generated_count = 0

    for comp in companies:
        comp_df = df_ratios[df_ratios["company_id"] == comp]
        if len(comp_df) < 3:
            skipped.append({"company_id": comp, "years_available": len(comp_df), "reason": "Fewer than 3 years of data"})
            continue
        
        # Call the tearsheet generator from Day 33
        try:
            tearsheet.generate_tearsheet(comp)
            generated_count += 1
        except Exception as e:
            skipped.append({"company_id": comp, "years_available": len(comp_df), "reason": f"Error: {e}"})

    df_skipped = pd.DataFrame(skipped)
    df_skipped.to_csv(SKIPPED_CSV, index=False)
    print(f" -> Generated {generated_count} tearsheets.")
    print(f" -> Skipped {len(skipped)} companies (logged to {SKIPPED_CSV.name}).")

    # 2. Batch Sector Reports
    print("\n[PHASE 2] Generating Sector Reports...")
    latest_year = df_ratios["year"].max()
    df_latest = df_ratios[df_ratios["year"] == latest_year].copy()
    
    # Merge with sectors
    df_merged = pd.merge(df_latest, df_peers, on="company_id", how="left")
    df_merged["peer_group_name"] = df_merged["peer_group_name"].fillna("General")
    
    sectors = df_merged["peer_group_name"].unique()
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('NavyHeader', parent=styles['Heading1'], backColor=colors.navy, textColor=colors.white, alignment=1, spaceAfter=20, padding=10)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)

    for sector in sectors:
        sector_df = df_merged[df_merged["peer_group_name"] == sector].copy()
        
        # Calculate Medians
        med_roe = sector_df["return_on_equity_pct"].median()
        med_de = sector_df["debt_to_equity"].median()
        med_opm = sector_df["operating_profit_margin_pct"].median()
        
        pdf_path = SECTOR_DIR / f"{sector.replace(' ', '_')}_report.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        
        story = []
        story.append(Paragraph(f"<b>{sector} Sector | Executive Summary</b>", header_style))
        story.append(Paragraph(f"<b>Sector Median ROE:</b> {med_roe:.2f}% | <b>Median D/E:</b> {med_de:.2f}x | <b>Median OPM:</b> {med_opm:.2f}%", styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Table of all companies (8 Metrics)
        # Using Paragraphs inside the table forces WORDWRAP automatically
        headers = ["Company", "ROE (%)", "D/E (x)", "OPM (%)", "Rev CAGR (%)", "PAT CAGR (%)", "FCF (Cr)", "Comp Score"]
        table_data = [[Paragraph(f"<b>{h}</b>", cell_style) for h in headers]]
        
        for _, row in sector_df.iterrows():
            row_data = [
                Paragraph(str(row["company_id"]), cell_style),
                Paragraph(f"{row.get('return_on_equity_pct', 0):.2f}", cell_style),
                Paragraph(f"{row.get('debt_to_equity', 0):.2f}", cell_style),
                Paragraph(f"{row.get('operating_profit_margin_pct', 0):.2f}", cell_style),
                Paragraph(f"{row.get('revenue_cagr_5yr', 0):.2f}", cell_style),
                Paragraph(f"{row.get('pat_cagr_5yr', 0):.2f}", cell_style),
                Paragraph(f"{row.get('free_cash_flow', 0):.0f}", cell_style),
                Paragraph(f"{row.get('composite_quality_score', 0):.2f}", cell_style)
            ]
            table_data.append(row_data)
        
        t = Table(table_data, colWidths=[90, 80, 80, 80, 90, 90, 90, 90])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ]))
        
        story.append(t)
        doc.build(story)
        
    print(f" -> Generated {len(sectors)} sector reports.")
    print("\n[SUCCESS] Batch Generation Complete!")
    return True

if __name__ == "__main__":
    run_batch_generation()