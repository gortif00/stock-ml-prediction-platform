# 🚀 Nuevas Funcionalidades Implementadas

Este documento describe las **mejoras corto plazo** implementadas según el roadmap del proyecto.

## 📦 Nuevos Módulos

### 1. 🎯 Sistema de Backtesting Automatizado

**Archivo:** `mcp_server/scripts/backtesting.py`

Sistema completo para validar la performance histórica de los modelos ML.

#### Características:
- ✅ Validación histórica de predicciones vs datos reales
- ✅ Métricas completas: accuracy, precision, recall, F1-score
- ✅ Análisis por modelo individual y ensemble
- ✅ Matrices de confusión
- ✅ Accuracy ponderada por confianza
- ✅ Generación de reportes JSON

#### Uso:

```python
from mcp_server.scripts.backtesting import generate_backtest_report
from datetime import date, timedelta

# Backtest de los últimos 30 días
end = date.today()
start = end - timedelta(days=30)

report = generate_backtest_report("^IBEX", start, end)

# Ver mejor modelo
print(f"Mejor modelo: {report['summary']['best_model']}")
print(f"Accuracy: {report['summary']['best_accuracy']:.2%}")

# Guardar reporte
from mcp_server.scripts.backtesting import save_backtest_report
save_backtest_report(report)
```

#### Funciones principales:

- `backtest_by_model()` - Evalúa cada modelo individualmente
- `backtest_ensemble()` - Evalúa votación mayoritaria
- `generate_backtest_report()` - Reporte completo
- `save_backtest_report()` - Guarda en JSON

---

### 2. 📈 Indicadores Técnicos Avanzados

**Archivo:** `mcp_server/scripts/advanced_indicators.py`

Implementa indicadores técnicos profesionales para mejorar las predicciones.

#### Indicadores Implementados:

1. **MACD** (Moving Average Convergence Divergence)
   - Línea MACD, señal e histograma
   - Identifica momentum y cambios de tendencia

2. **Bollinger Bands**
   - Bandas superior, media e inferior
   - %B (posición dentro de las bandas)
   - Ancho de banda (volatilidad)

3. **ADX** (Average Directional Index)
   - Mide fuerza de tendencia (no dirección)
   - +DI y -DI para direccionalidad
   - ADX > 25 indica tendencia fuerte

4. **ATR** (Average True Range)
   - Mide volatilidad real del mercado
   - Útil para stop-loss dinámicos

5. **Stochastic Oscillator**
   - %K y %D
   - Sobrecompra (>80) y sobreventa (<20)

6. **OBV** (On-Balance Volume)
   - Relaciona volumen con precio
   - Confirma tendencias

7. **EMAs adicionales** (12, 26, 200)

#### Uso:

```python
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol

# Calcular y guardar en BD
rows = compute_advanced_indicators_for_symbol("^IBEX")
print(f"✅ {rows} indicadores calculados")
```

Los indicadores se guardan en la tabla `advanced_indicators` en PostgreSQL.

#### Integración con modelos ML:

Para usar estos indicadores en tus modelos, modifica `models.py`:

```python
def _load_features(symbol: str, as_of_date=None) -> pd.DataFrame:
    # ... código existente ...
    
    # Añadir indicadores avanzados
    cur.execute("""
        SELECT
            p.date,
            p.close,
            i.sma_20, i.sma_50, i.vol_20, i.rsi_14,
            ai.macd, ai.adx, ai.bb_percent, ai.stoch_k
        FROM prices p
        LEFT JOIN indicators i ON p.symbol = i.symbol AND p.date = i.date
        LEFT JOIN advanced_indicators ai ON p.symbol = ai.symbol AND p.date = ai.date
        WHERE p.symbol = %s
        ORDER BY p.date
    """, (symbol,))
```

---

### 3. 🎨 Dashboard Interactivo Streamlit

**Archivo:** `streamlit_dashboard.py`

Dashboard web profesional con visualización en tiempo real.

#### Características:

**Tab 1: Precio & Predicciones**
- 📊 Gráfico de velas japonesas (candlestick)
- 🔮 Predicciones superpuestas con flechas de colores
- 📈 Volumen
- 📋 Tabla de predicciones recientes
- 💹 Métricas: precio actual, máximo/mínimo

**Tab 2: Indicadores Técnicos**
- Gráficos multi-panel:
  - Precio con Bollinger Bands
  - MACD con histograma
  - Stochastic Oscillator
  - ADX con +DI/-DI
- Interactivo con hover tooltips
- Zoom y pan

**Tab 3: Backtesting**
- 🎯 Ejecutar backtesting con un click
- 📊 Gráfico comparativo de modelos
- 📈 Tabla detallada de métricas
- 🎲 Performance del ensemble
- Comparación ensemble vs mejor modelo

**Tab 4: Heatmap** (próximamente)
- Correlaciones entre mercados

#### Ejecución:

```bash
# Instalar dependencias
pip install streamlit plotly

# Ejecutar dashboard
streamlit run streamlit_dashboard.py

# Abrirá automáticamente en http://localhost:8501
```

#### Configuración:

El dashboard se conecta automáticamente a tu base de datos PostgreSQL usando la configuración en `mcp_server/scripts/config.py`.

#### Personalización:

Puedes ajustar:
- Días a mostrar (slider en sidebar)
- Días de backtesting (slider)
- Mercado a analizar (dropdown)

---

### 4. 🤖 Bot de Telegram para Alertas

**Archivo:** `telegram_bot.py`

Bot interactivo para recibir señales y alertas en tiempo real.

#### Comandos Disponibles:

**Básicos:**
- `/start` - Iniciar bot
- `/help` - Ayuda completa
- `/mercados` - Listar mercados disponibles
- `/seguir ^IBEX` - Seguir un mercado
- `/dejar ^IBEX` - Dejar de seguir

**Consultas:**
- `/predicciones` - Ver predicciones de mercados seguidos
- `/prediccion ^IBEX` - Predicción de mercado específico
- `/resumen` - Resumen con precios actuales
- `/backtest ^IBEX` - Performance histórica (30 días)

**Alertas:**
- `/alertas` - Configurar notificaciones (próximamente)

#### Setup:

1. **Crear bot en Telegram:**
```bash
# 1. Abre Telegram y busca @BotFather
# 2. Envía: /newbot
# 3. Sigue instrucciones y copia el token
```

2. **Configurar token:**
```bash
# Linux/Mac
export TELEGRAM_BOT_TOKEN='1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'

# Windows
set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

3. **Instalar dependencias:**
```bash
pip install python-telegram-bot
```

4. **Ejecutar bot:**
```bash
python telegram_bot.py
```

5. **Usar bot:**
   - Abre Telegram
   - Busca tu bot por el nombre que le diste
   - Envía `/start`

#### Alertas Automáticas:

El bot puede enviar alertas automáticamente cuando:
- Hay nueva predicción con alta confianza (>70%)
- Consenso fuerte entre modelos
- Cambios significativos en el mercado

Para activar alertas automáticas, integra con tu pipeline de predicciones:

```python
# En tu script de predicciones diarias
from telegram_bot import TradingBot

bot = TradingBot(TELEGRAM_BOT_TOKEN)

# Después de generar predicción
if prediction['confidence'] > 0.7:
    await bot.send_alert_to_subscribers(
        symbol="^IBEX",
        prediction_data={
            'direction': 'UP',
            'confidence': 0.85,
            'model': 'Ensemble',
            'target_date': '2025-12-11'
        }
    )
```

---

## 🚀 Cómo Empezar

### 1. Instalar Nuevas Dependencias

```bash
pip install -r requirements-new-features.txt
```

### 2. Calcular Indicadores Avanzados

```bash
python -c "from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol; \
compute_advanced_indicators_for_symbol('^IBEX')"
```

### 3. Ejecutar Backtesting

```python
from mcp_server.scripts.backtesting import generate_backtest_report
from datetime import date, timedelta

report = generate_backtest_report(
    "^IBEX",
    date.today() - timedelta(days=30),
    date.today()
)

print(f"Mejor modelo: {report['summary']['best_model']}")
print(f"Accuracy: {report['summary']['best_accuracy']:.2%}")
```

### 4. Lanzar Dashboard

```bash
streamlit run streamlit_dashboard.py
```

### 5. Iniciar Bot de Telegram

```bash
export TELEGRAM_BOT_TOKEN='tu_token'
python telegram_bot.py
```

---

## 📊 Ejemplos de Uso Completo

### Workflow Diario Recomendado:

```bash
# 1. Actualizar datos (tu proceso existente)
python mcp_server/scripts/fetch_data.py

# 2. Calcular indicadores
python -c "from mcp_server.scripts.indicators import compute_indicators_for_symbol; \
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol; \
compute_indicators_for_symbol('^IBEX'); \
compute_advanced_indicators_for_symbol('^IBEX')"

# 3. Generar predicciones (tu proceso existente)
python mcp_server/scripts/models.py

# 4. Verificar performance con backtesting
python -c "from mcp_server.scripts.backtesting import generate_backtest_report; \
from datetime import date, timedelta; \
report = generate_backtest_report('^IBEX', date.today()-timedelta(30), date.today()); \
print(report['summary'])"

# 5. Dashboard y bot corren en background
```

---

## 🎓 Para tu Proyecto Académico

### Demostración Impresionante:

1. **Presentación:**
   - Muestra el dashboard en vivo
   - Ejecuta backtesting en tiempo real
   - Demuestra bot de Telegram

2. **Métricas a Destacar:**
   - Accuracy del ensemble
   - Mejora vs modelos individuales
   - Indicadores técnicos avanzados
   - Sistema completo end-to-end

3. **Documentación:**
   - Este README es parte de tu documentación
   - Incluye capturas del dashboard
   - Logs del bot de Telegram
   - Reportes de backtesting

---

## 🔮 Próximos Pasos (Roadmap Medio/Largo Plazo)

Ya implementaste el **Corto Plazo**. Siguiente:

### Medio Plazo (1 mes):
- [ ] Paper trading simulator
- [ ] Frontend React avanzado
- [ ] CI/CD pipeline
- [ ] Caché con Redis

### Largo Plazo (2-3 meses):
- [ ] Integración con brokers reales
- [ ] Hyperparameter tuning automático
- [ ] Mobile app
- [ ] Kubernetes deployment

---

## 🐛 Troubleshooting

### Dashboard no se conecta a DB:
```bash
# Verifica que PostgreSQL esté corriendo
docker ps | grep postgres

# Verifica configuración en .env
cat .env
```

### Bot de Telegram no responde:
```bash
# Verifica token
echo $TELEGRAM_BOT_TOKEN

# Prueba conexión
python -c "from telegram import Bot; bot = Bot('$TELEGRAM_BOT_TOKEN'); print(bot.get_me())"
```

### Indicadores no se calculan:
```bash
# Verifica que hay datos suficientes (min 50 días para algunos indicadores)
psql -U finanzas -d indices -c "SELECT symbol, COUNT(*) FROM prices GROUP BY symbol;"
```

---

## 📞 Soporte

Si necesitas ayuda o quieres añadir más features, revisa:
- `docs/REQUIREMENTS.md` - Requisitos del proyecto
- `docs/README.md` - Documentación principal
- `docs/BACKFILL_README.md` - Carga histórica de datos

---

**¡Éxito con tu proyecto! 🚀**
