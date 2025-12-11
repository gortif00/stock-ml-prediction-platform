#!/usr/bin/env python3
"""
Test de backfill para los 3 mercados configurados.
Verifica que el sistema funciona correctamente con IBEX35, SP500 y NIKKEI.
"""

import sys
import os
sys.path.insert(0, '/app')
os.chdir('/app')

from datetime import date
from scripts.backfill_predictions import backfill_predictions_for_symbol

print("🚀 BACKFILL - 3 MERCADOS GLOBALES")
print("=" * 70)

# Usar fecha con suficientes datos previos (2025-11-20)
# SP500 y NIKKEI tienen datos desde 2024-12-10, necesitan 50+ días antes
test_date = date(2025, 11, 20)
print(f"Test: 1 día ({test_date})\n")

markets = [
    ('^IBEX', '🇪🇸 IBEX35 - España'),
    ('^GSPC', '🇺🇸 SP500 - USA'),
    ('^N225', '🇯🇵 NIKKEI - Japón')
]

results = []

for symbol, name in markets:
    print(f"📊 {name}")
    try:
        backfill_predictions_for_symbol(symbol, test_date, test_date)
        results.append((name, 'SUCCESS'))
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append((name, f'ERROR: {str(e)[:50]}'))
    print()

# Resumen
print()
print("╔" + "═" * 66 + "╗")
print("║" + " " * 24 + "📋 RESUMEN" + " " * 32 + "║")
print("╠" + "═" * 66 + "╣")
for name, status in results:
    icon = "✅" if status == "SUCCESS" else "❌"
    print(f"║  {icon} {name:40s} {status:10s}  ║")
print("╚" + "═" * 66 + "╝")
