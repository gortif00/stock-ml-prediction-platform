"""Paquete de scripts para el servidor MCP Finance.

Proporciona módulos para:
- Descarga de datos (prices, news)
- Cálculo de indicadores técnicos
- Entrenamiento y predicción con modelos ML
- Validación y reporting de resultados

Configuración:
- Logger configurado a nivel INFO por defecto
- Símbolos por defecto: Principales índices globales (Europa, América, Asia)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Configurar logger para todos los módulos del paquete
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "0") == "1"

logger = logging.getLogger("mcp_finance")
logger.setLevel(LOG_LEVEL)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if LOG_TO_FILE:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "mcp_finance.log"),
            maxBytes=5_000_000,
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False

# Símbolos por defecto para operaciones batch
# Incluye principales índices de cada región
# Por defecto, procesaremos estos símbolos:
DEFAULT_SYMBOLS = ["^IBEX", "^GSPC", "^N225"]
