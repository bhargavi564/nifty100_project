import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()
STATS_CSV = Path(__file__).resolve().parents[3] / "output" / "portfolio_stats.csv"

@router.get("/portfolio/stats")
def get_portfolio_stats():
    if not STATS_CSV.exists():
        raise HTTPException(status_code=404, detail="Portfolio stats file not found.")
    df = pd.read_csv(STATS_CSV)
    return df.to_dict(orient="records")