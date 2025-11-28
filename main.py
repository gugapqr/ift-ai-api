from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

app = FastAPI(
    title="IFT Institutional Trading AI",
    description="API oficial do Sistema Inteligente Institucional – IFT Maverick",
    version="1.0"
)

# =====================================================
# === MODELO DE UNIVERSOS DE ATIVOS ====================
# =====================================================

UNIVERSE_FULL = {
    "forex": [
        "EURUSD","GBPUSD","USDJPY","USDCHF","USDCAD","AUDUSD","NZDUSD",
        "EURJPY","EURGBP","EURCHF","EURCAD","EURAUD","EURNZD",
        "GBPJPY","GBPCHF","GBPCAD","GBPAUD","GBPNZD",
        "AUDJPY","AUDCHF","AUDCAD","AUDNZD",
        "NZDJPY","NZDCHF","NZDCAD",
        "CADJPY","CADCHF",
        "CHFJPY"
    ],
    "indices": [
        "US100","US500","US30","DE40","FR40","UK100","JP225","HK50","BRAS50"
    ],
    "crypto": [
        "BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","ADAUSDT","BNBUSDT","AVAXUSDT",
        "DOGEUSDT","LINKUSDT","MATICUSDT","OPUSDT","ARBUSDT","TONUSDT"
    ],
    "stocks_usa": [
        "AAPL","MSFT","NVDA","META","GOOGL","AMZN","TSLA","AMD","NFLX","INTC",
        "JPM","BA","KO","PEP","SPY","QQQ"
    ],
    "stocks_brasil": [
        "PETR4","PETR3","VALE3","ITUB4","BBDC4","B3SA3","ABEV3","BBAS3","MGLU3",
        "LREN3","WEGE3","PRIO3","GGBR4","CSNA3","JBSS3","SUZB3"
    ]
}

CUSTOM_WATCHLIST = []   # você pode adicionar via /v1/custom_add


# =====================================================
# === MODELOS JSON (CONTRATO OFICIAL DA API) ==========
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
# === PLACEHOLDERS PARA O MOTOR DE ANÁLISE ============
# =====================================================
# Aqui você vai conectar depois:
# - código do IFT Maverick em Python
# - motores: EMA/HMA/ZZ/Supertrend
# - PVPC, Volume, ATR, Bollinger
# - Fibo MTF
# - Didi Index
# - Volumized Order Blocks
# - VPD-LEA, IFA, etc.

def run_full_market_scan(config: ScanRequest) -> List[Dict[str, Any]]:
    """
    Essa função será substituída pelo motor final.
    Aqui estamos só simulando um retorno (mock)
    """
    return [{
        "symbol": "US100",
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
    """
    Placeholder até colocarmos o motor real.
    """
    return {
        "symbol": config.symbol,
        "summary": "Ativo com tendência de alta em H1 e H4...",
        "unified_score": 0.65,
        "last_signal": "long"
    }


def register_feedback(feedback: FeedbackRequest) -> Dict[str, Any]:
    """
    Esse módulo depois alimenta o 'Maverick Score'.
    """
    return {
        "ok": True,
        "message": "Feedback registrado com sucesso"
    }


# =====================================================
# ================= ENDPOINTS ==========================
# =====================================================

@app.post("/v1/scan")
async def scan_market(request: ScanRequest):
    results = run_full_market_scan(request)
    return {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "results": results
    }


@app.post("/v1/analyze")
async def analyze_symbol(request: AnalyzeRequest):
    result = run_single_analysis(request)
    return {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "analysis": result
    }


@app.post("/v1/feedback")
async def feedback(request: FeedbackRequest):
    result = register_feedback(request)
    return result


# =====================================================
# === GERENCIAR WATCHLIST PERSONALIZADA ===============
# =====================================================

class AddSymbolRequest(BaseModel):
    symbol: str

@app.post("/v1/custom_add")
async def add_custom_symbol(request: AddSymbolRequest):
    CUSTOM_WATCHLIST.append(request.symbol.upper())
    return {"ok": True, "custom_watchlist": CUSTOM_WATCHLIST}

