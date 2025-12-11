# ✅ Checklist de Verificación - Nuevas Funcionalidades

Use este checklist para verificar que todo funciona correctamente.

## 📋 Pre-requisitos

- [ ] Python 3.8+ instalado
- [ ] PostgreSQL corriendo (Docker o local)
- [ ] Variables de entorno configuradas en `.env`
- [ ] Datos históricos cargados en la BD

### Verificar Pre-requisitos:

```bash
# Python
python3 --version

# PostgreSQL
docker ps | grep postgres
# O si es local:
psql -U finanzas -d indices -c "SELECT COUNT(*) FROM prices;"

# Variables de entorno
cat .env
```

---

## 🔧 1. Instalación de Dependencias

```bash
# Instalar nuevas dependencias
pip install -r requirements-new-features.txt
```

**Verificar:**
- [ ] streamlit instalado: `streamlit --version`
- [ ] plotly instalado: `python3 -c "import plotly; print(plotly.__version__)"`
- [ ] python-telegram-bot instalado: `python3 -c "import telegram; print('OK')"`

---

## 📈 2. Indicadores Técnicos Avanzados

```bash
# Calcular indicadores para un símbolo
python3 << EOF
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol
rows = compute_advanced_indicators_for_symbol("^IBEX")
print(f"✅ {rows} indicadores calculados")
EOF
```

**Verificar:**
- [ ] Script se ejecuta sin errores
- [ ] Imprime número de filas > 0
- [ ] Tabla `advanced_indicators` existe en PostgreSQL:
  ```bash
  psql -U finanzas -d indices -c "\d advanced_indicators"
  ```
- [ ] Datos insertados:
  ```bash
  psql -U finanzas -d indices -c "SELECT COUNT(*) FROM advanced_indicators WHERE symbol = '^IBEX';"
  ```

**Indicadores a verificar:**
- [ ] MACD (macd, macd_signal, macd_histogram)
- [ ] Bollinger Bands (bb_upper, bb_middle, bb_lower, bb_percent, bb_width)
- [ ] ADX (adx, plus_di, minus_di)
- [ ] ATR
- [ ] Stochastic (stoch_k, stoch_d)
- [ ] OBV
- [ ] EMAs (ema_12, ema_26, ema_200)

---

## 🎯 3. Sistema de Backtesting

```bash
# Ejecutar backtesting
python3 << EOF
from mcp_server.scripts.backtesting import generate_backtest_report
from datetime import date, timedelta

end = date.today()
start = end - timedelta(days=30)

report = generate_backtest_report("^IBEX", start, end)

print("\n" + "="*60)
print("BACKTESTING RESULTS")
print("="*60)

if 'summary' in report and report['summary']:
    summary = report['summary']
    if 'best_model' in summary:
        print(f"✅ Mejor modelo: {summary['best_model']}")
        print(f"✅ Accuracy: {summary['best_accuracy']:.2%}")
    
    if 'ensemble_vs_best_model' in summary:
        comp = summary['ensemble_vs_best_model']
        print(f"\n✅ Ensemble accuracy: {comp['ensemble_accuracy']:.2%}")
        print(f"✅ Mejora: {comp['improvement']:+.2%}")

# Guardar reporte
from mcp_server.scripts.backtesting import save_backtest_report
output_file = save_backtest_report(report)
print(f"\n✅ Reporte guardado: {output_file}")
EOF
```

**Verificar:**
- [ ] Script se ejecuta sin errores
- [ ] Muestra métricas por modelo
- [ ] Accuracy está entre 0-100%
- [ ] Genera archivo JSON de reporte
- [ ] JSON contiene: individual_models, ensemble, summary

**Métricas esperadas:**
- [ ] accuracy
- [ ] precision
- [ ] recall
- [ ] f1_score
- [ ] confusion_matrix
- [ ] total_predictions > 0

---

## 📊 4. Dashboard Streamlit

```bash
# Lanzar dashboard
streamlit run streamlit_dashboard.py
```

**Verificar en http://localhost:8501:**

### Tab 1: Precio & Predicciones
- [ ] Dropdown con símbolos funciona
- [ ] Gráfico candlestick se muestra
- [ ] Volumen se muestra debajo
- [ ] Métricas (Precio Actual, Máximo, Mínimo) visibles
- [ ] Tabla de predicciones se carga
- [ ] Predicciones tienen colores (verde/rojo)

### Tab 2: Indicadores Técnicos
- [ ] Gráfico multi-panel se muestra
- [ ] Bollinger Bands visibles sobre precio
- [ ] MACD con línea, señal e histograma
- [ ] Stochastic con líneas en 80 y 20
- [ ] ADX con +DI/-DI
- [ ] Hover tooltips funcionan
- [ ] Zoom funciona

### Tab 3: Backtesting
- [ ] Botón "Ejecutar Backtesting" visible
- [ ] Click ejecuta sin errores
- [ ] Gráfico comparativo se muestra
- [ ] Tabla de métricas se llena
- [ ] Métricas de ensemble visibles
- [ ] Comparación ensemble vs mejor modelo

### Tab 4: Heatmap
- [ ] Tab existe (aunque esté vacío)

### General Dashboard
- [ ] Sidebar con configuración
- [ ] Slider de días funciona
- [ ] Cambio de símbolo actualiza datos
- [ ] No hay errores en consola
- [ ] Performance aceptable (<3s carga)

---

## 🤖 5. Bot de Telegram

### Setup Inicial

```bash
# 1. Verificar token configurado
echo $TELEGRAM_BOT_TOKEN

# Debe mostrar algo como: 1234567890:ABCdefGHI...
# Si no: export TELEGRAM_BOT_TOKEN='tu_token'

# 2. Lanzar bot
python3 telegram_bot.py
```

**Verificar en terminal:**
- [ ] Mensaje "Bot de Telegram iniciado"
- [ ] No hay errores de conexión
- [ ] Bot está activo (no se cierra)

### Pruebas en Telegram

Abre Telegram y busca tu bot:

#### Comandos Básicos
- [ ] `/start` - Mensaje de bienvenida
- [ ] `/help` - Muestra lista de comandos
- [ ] `/mercados` - Lista símbolos disponibles

#### Seguimiento
- [ ] `/seguir ^IBEX` - Confirma seguimiento
- [ ] `/dejar ^IBEX` - Confirma dejó de seguir

#### Consultas
- [ ] `/predicciones` - Muestra predicciones (después de seguir)
- [ ] `/prediccion ^IBEX` - Predicción específica
- [ ] `/resumen` - Precios actuales
- [ ] `/backtest ^IBEX` - Ejecuta y muestra métricas

#### Formato y UX
- [ ] Mensajes con formato Markdown
- [ ] Emojis visibles
- [ ] Respuestas rápidas (<3s)
- [ ] Manejo de errores (comandos inválidos)

---

## 🚀 6. Script Quickstart

```bash
# Ejecutar script interactivo
./quickstart.sh
```

**Verificar:**
- [ ] Script se ejecuta
- [ ] Muestra menú con opciones 1-6
- [ ] Verifica dependencias correctamente
- [ ] Cada opción funciona:
  - [ ] 1) Lanza dashboard
  - [ ] 2) Lanza bot
  - [ ] 3) Ejecuta backtesting
  - [ ] 4) Calcula indicadores
  - [ ] 5) Lanza ambos (dashboard + bot)
  - [ ] 6) Muestra documentación

---

## 📚 7. Documentación

**Verificar archivos existen y son legibles:**

- [ ] `docs/NEW_FEATURES.md` - Guía completa
- [ ] `RESUMEN_IMPLEMENTACION.md` - Resumen ejecutivo
- [ ] `IMPLEMENTATION_SUMMARY.txt` - Resumen visual
- [ ] `requirements-new-features.txt` - Dependencias
- [ ] `quickstart.sh` - Script de inicio
- [ ] `CHECKLIST.md` - Este archivo

**Contenido de documentación:**
- [ ] Instrucciones claras de instalación
- [ ] Ejemplos de uso
- [ ] Comandos ejecutables
- [ ] Troubleshooting
- [ ] Capturas/diagramas (si aplica)

---

## 🧪 8. Tests de Integración

### Test Completo End-to-End

```bash
# 1. Limpiar datos previos (opcional)
# psql -U finanzas -d indices -c "DELETE FROM advanced_indicators WHERE symbol = '^TEST';"

# 2. Ejecutar pipeline completo
python3 << EOF
from datetime import date, timedelta

# Símbolo de prueba
symbol = "^IBEX"

print("1. Calculando indicadores avanzados...")
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol
rows = compute_advanced_indicators_for_symbol(symbol)
print(f"   ✅ {rows} indicadores calculados")

print("\n2. Ejecutando backtesting...")
from mcp_server.scripts.backtesting import generate_backtest_report
end = date.today()
start = end - timedelta(days=30)
report = generate_backtest_report(symbol, start, end)
if 'summary' in report and report['summary']:
    print(f"   ✅ Accuracy: {report['summary'].get('best_accuracy', 0):.2%}")

print("\n3. Verificando datos en BD...")
from mcp_server.scripts.config import get_db_conn
conn = get_db_conn()
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM advanced_indicators WHERE symbol = %s", (symbol,))
    count = cur.fetchone()[0]
    print(f"   ✅ {count} filas en advanced_indicators")
conn.close()

print("\n✅ PIPELINE COMPLETO EXITOSO")
EOF
```

**Verificar:**
- [ ] Todos los pasos se ejecutan sin errores
- [ ] Indicadores calculados > 0
- [ ] Backtesting retorna accuracy válida
- [ ] Datos en BD verificados

---

## 🐛 9. Troubleshooting

Si encuentras problemas, verifica:

### Error de Conexión a BD
```bash
# Verificar PostgreSQL
docker ps | grep postgres

# Verificar credenciales
cat .env | grep POSTGRES

# Test de conexión
python3 -c "from mcp_server.scripts.config import get_db_conn; conn = get_db_conn(); print('✅ OK'); conn.close()"
```

### Error de Módulos
```bash
# Reinstalar dependencias
pip install -r requirements-new-features.txt --force-reinstall
```

### Dashboard no carga
```bash
# Limpiar caché de Streamlit
rm -rf ~/.streamlit/cache/

# Ejecutar con debug
streamlit run streamlit_dashboard.py --logger.level=debug
```

### Bot no responde
```bash
# Verificar token
python3 -c "from telegram import Bot; import os; bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN')); print(bot.get_me())"
```

---

## ✅ Checklist Final

Marca cuando todo esté verificado:

- [ ] ✅ Indicadores avanzados calculan correctamente
- [ ] ✅ Backtesting genera métricas válidas
- [ ] ✅ Dashboard Streamlit funciona en todos los tabs
- [ ] ✅ Bot de Telegram responde a comandos
- [ ] ✅ Script quickstart ejecuta sin errores
- [ ] ✅ Documentación es clara y completa
- [ ] ✅ Pipeline completo (end-to-end) funciona
- [ ] ✅ No hay errores en logs

---

## 🎓 Para Presentación Académica

Lista final antes de presentar:

- [ ] Dashboard corriendo y probado
- [ ] Bot de Telegram configurado y probado
- [ ] Al menos 1 reporte de backtesting generado
- [ ] Datos recientes en BD (últimos 7 días)
- [ ] Capturas de pantalla del dashboard (opcional)
- [ ] Demo preparada (10 min):
  - [ ] Mostrar dashboard (3 min)
  - [ ] Demostrar bot (2 min)
  - [ ] Explicar backtesting (2 min)
  - [ ] Código y arquitectura (3 min)
- [ ] Respuestas preparadas para preguntas técnicas
- [ ] Métricas impresionantes destacadas (accuracy, modelos, indicadores)

---

## 📞 Soporte

Si algo no funciona después de seguir este checklist:

1. Revisa logs en terminal
2. Consulta `docs/NEW_FEATURES.md`
3. Verifica `.env` y configuración de BD
4. Prueba cada módulo por separado

---

**¡Todo listo! 🚀**

Una vez completado este checklist, tu sistema está 100% funcional y listo para demostración.
