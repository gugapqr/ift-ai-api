from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI(title="IFT – Institutional Flow API")

class IFTSignal(BaseModel):
    symbol: str
    timeframe: str
    direction: str
    price: float
    core_score: Optional[float] = None
    unified_score: Optional[float] = None
    risk_tag: Optional[str] = None
    maverick_phase: Optional[str] = None
    message: Optional[str] = None
    extra: Optional[dict] = None

@app.post("/ift/signal")
async def receive_ift_signal(signal: IFTSignal):

    prompt = f"""
Você é o IFT-AI, um analista institucional avançado integrado ao indicador IFT Maverick.

Dados recebidos:
Ativo: {signal.symbol}
Timeframe: {signal.timeframe}
Direção: {signal.direction}
Preço: {signal.price}
Core Score: {signal.core_score}
Unified Score: {signal.unified_score}
Risk Tag: {signal.risk_tag}
Fase Maverick: {signal.maverick_phase}
Mensagem: {signal.message}
Extra: {signal.extra}

Analise esse sinal considerando:
• Estrutura institucional (SMC)
• Volume e agressão
• Tendência multitimeframe
• Fluxo institucional
• Variações do IFT
• Riscos macro
• Filtros do Maverick

Diga:
1. O que o fluxo mostra agora.
2. Se é oportunidade, observação ou evitar.
3. Níveis importantes do preço.
4. Score final (0–100).
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você é um analista institucional disciplinado."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_text = response.choices[0].message.content

    return {"ok": True, "analysis": ai_text}

@app.get("/")
async def root():
    return {"status": "IFT API ONLINE"}
    
