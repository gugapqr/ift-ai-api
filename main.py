from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

# Polygon/Massive
from polygon import RESTClient

# =====================================================
# ========== VARIÁVEIS DE AMBIENTE =====================
# =====================================================

OPENAI_KEY = os.getenv("IFT_OPENAI_KEY")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

if MASSIVE_API_KEY is None:
    raise ValueError("ERRO: MASSIVE_API_KEY não encontrada no Railway!")

polygon_client = RESTClient(MASSIVE_API_KEY)

# =====================================================
# =============== CONFIGURAÇÃO DA API =================
# =====================================================

app = FastAPI(
    title="IFT Institutional Trading AI",
    description="API Inteligente – IFT Maverick",
    version="1.0"
)

# =====================================================
# === UNIVERSOS DE ATIVOS ==============================
# =====================================================

UNIVERSE_FULL = {
    "forex": [
        "C:EURUSD", "C:GBPUSD", "C:USDJPY", "C:USDCHF", "C:USDCAD",
        "C:AUDUSD", "C:NZDUSD", "C:EURJPY", "C:GBPJPY"
    ],
    "indices": [
        "I:NDX", "I:SPX", "I:DJI", "I:JP225", "I:DE40"
    ],
    "crypto": [
        "X:BTCUSD", "X:ETHUSD", "X:SOLUSD", "X:XRPUSD"
    ]
}

CUSTOM_WATCHLIST = []

# =====================================================
# === MODELOS JSON (CONTRATO OFICIAL) =================
# =====================================================

class ScanFilters(BaseModel):
    asset_classes: Optional[List[str]] = None
    min_liquidity_rank: Optional[float] = 0.0
    exclude: Optional[List[str]] = []

class ScanRequest(BaseModel):
    mode: str = "scan"
    universe: str = "full"
    extra_symbols: Optional[List[str]] = []
    timeframes: List[str] = ["15", "60", "240", "D"]
    direction: str = "both"
    min_unified_score: float = 0.0
    only_clean_flow: bool = False
    max_results: int = 20
    include_components: bool = True
    include_levels: bool = True
    signals_mode: str = "Conservador"
    filters: Optional[ScanFilters] = None

class AnalyzeRequest(BaseModel):
    mode: str = "analyze"
    symbol: str
    timeframes: List[str] = ["15","60","240","D","W"]
    signals_mode: str = "Conservador"
    include_backtest_last_signals: int = 10
    include_raw_series: bool = False
    include_text_summary: bool = True

class FeedbackRequest(BaseModel):
    signal_id: str
    symbol: str
    timeframe: str
    direction: str
    result: str

# =====================================================
# === PARTE 1 — PEGAR DADOS DO POLYGON ================
# =====================================================

def fetch_candles(symbol: str, timeframe: str) -> List[Dict[str, Any]]:
    """
    Baixa candles do Polygon/Massive
    """
    tf_map = {
        "1": "minute",
        "5": "minute",
        "15": "minute",
        "30": "minute",
        "60": "minute",
        "240": "minute",
        "D": "day",
        "W": "week",
        "M": "month"
    }

    if timeframe not in tf_map:
        raise ValueError(f"Timeframe inválido: {timeframe}")

    multiplier = 1
    if timeframe.isnumeric():
        multiplier = int(timeframe)

    candles = polygon_client.list_aggs(
        ticker=symbol,
        multiplier=multiplier,
        timespan=tf_map[timeframe],
        from_="2023-01-01",
        to="2025-12-31",
        limit=500
    )

    return candles

# =====================================================
# === PLACEHOLDER DO IFT MAVERICK ======================
# =====================================================

def run_full_market_scan(config: ScanRequest) -> List[Dict[str, Any]]:
    return [{
        "symbol": "I:NDX",
        "unified_score": 0.81,
        "direction": "long",
        "entry": 21040.5,
        "stop": 20890.2,
        "tp1": 21270,
        "tp2": 21450,
        "tp3": 21680,
        "reason": [
            "Fluxo institucional limpo",
            "EMA alinhadas",
            "Supertrend comprador",
            "IFT Maverick long"
        ]
    }]

def run_single_analysis(config: AnalyzeRequest) -> Dict[str, Any]:
    # vai usar fetch_candles()
    data = fetch_candles(config.symbol, config.timeframes[0])

    return {
        "symbol": config.symbol,
        "summary": f"{config.symbol} analisado com sucesso!",
        "unified_score": 0.65,
        "last_signal": "long",
        "bars_loaded": len(data)
    }

def register_feedback(feedback: FeedbackRequest):
    return {"ok": True, "message": "Feedback registrado"}

# =====================================================
# === ENDPOINTS =======================================
# =====================================================

@app.post("/v1/scan")
async def scan_market(request: ScanRequest):
    return {"timestamp_utc": datetime.utcnow(), "results": run_full_market_scan(request)}

@app.post("/v1/analyze")
async def analyze_symbol(request: AnalyzeRequest):
    return {"timestamp_utc": datetime.utcnow(), "analysis": run_single_analysis(request)}

@app.post("/v1/feedback")
async def feedback(request: FeedbackRequest):
    return register_feedback(request)

class AddSymbolRequest(BaseModel):
    symbol: str

@app.post("/v1/custom_add")
async def add_custom_symbol(request: AddSymbolRequest):
    CUSTOM_WATCHLIST.append(request.symbol.upper())
    return {"ok": True, "custom_watchlist": CUSTOM_WATCHLIST}
