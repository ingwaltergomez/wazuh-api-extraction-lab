"""
API de laboratorio DELIBERADAMENTE VULNERABLE.

Reproduce, de forma sintética y controlada, el patrón descrito en la
Parte 1 del artículo: una API que expone registros por ID sin ningún
control de autenticación ni autorización. No contiene datos reales de
ninguna persona — todos los registros se generan con Faker en
seed_data.py.

NO EXPONER ESTA API FUERA DE UNA RED AISLADA DE LABORATORIO.

Ejecutar con:
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "beneficiarios.json"
LOG_FILE = "/var/log/api_access.log"

app = FastAPI(
    title="API Beneficiarios (LAB - vulnerable a propósito)",
    description="Laboratorio sintético para el artículo. Datos ficticios.",
)

# --- Logging de acceso en un formato propio, estable, que el decoder
# de Wazuh pueda parsear sin depender del formato interno de uvicorn. ---
access_logger = logging.getLogger("api_access")
access_logger.setLevel(logging.INFO)
_handler = logging.FileHandler(LOG_FILE)
_handler.setFormatter(logging.Formatter("%(message)s"))
access_logger.addHandler(_handler)

BENEFICIARIOS: dict[int, dict] = {}


@app.middleware("http")
async def log_every_request(request: Request, call_next):
    response = await call_next(request)
    client_ip = request.client.host if request.client else "unknown"
    access_logger.info(
        "api_access: ip:%s method:%s path:%s status:%s",
        client_ip,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.on_event("startup")
def load_data() -> None:
    global BENEFICIARIOS
    if not DATA_FILE.exists():
        raise RuntimeError(
            f"No se encontró {DATA_FILE}. Corre primero: python seed_data.py"
        )
    with open(DATA_FILE, encoding="utf-8") as f:
        records = json.load(f)
    BENEFICIARIOS = {item["id"]: item for item in records}


@app.get("/health")
def health():
    return {"status": "ok", "registros_cargados": len(BENEFICIARIOS)}


@app.get("/api/v1/beneficiarios/{beneficiario_id}")
def get_beneficiario(beneficiario_id: int):
    """
    VULNERABILIDAD INTENCIONAL (reproduce el patrón de Mintrab/Tu Empleo
    descrito en la Parte 1): no exige token, API key, sesión ni ningún
    otro control de acceso. Cualquiera que conozca o adivine un ID
    numérico puede leer el registro completo.
    """
    beneficiario = BENEFICIARIOS.get(beneficiario_id)
    if beneficiario is None:
        raise HTTPException(status_code=404, detail="No encontrado")
    return beneficiario


@app.get("/api/v1/beneficiarios")
def list_beneficiarios(limit: int = 50, offset: int = 0):
    """También sin control de acceso: permite paginar todo el dataset."""
    ids = sorted(BENEFICIARIOS.keys())[offset : offset + limit]
    return [BENEFICIARIOS[i] for i in ids]
