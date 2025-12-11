"""
Dashboard Streamlit para visualización de predicciones ML y análisis de mercados.

Funcionalidades:
- Visualización de precios y predicciones en tiempo real
- Comparación de modelos ML
- Métricas de backtesting
- Indicadores técnicos interactivos
- Heatmap de correlaciones entre mercados
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import sys
import os

# Añadir path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_server', 'scripts'))

from mcp_server.scripts.config import get_db_conn
from mcp_server.scripts.backtesting import (
    generate_backtest_report,
    backtest_by_model,
    backtest_ensemble
)
from mcp_server.scripts.advanced_indicators import (
    _load_full_prices,
    compute_all_advanced_indicators
)


# Configuración de la página
st.set_page_config(
    page_title="ML Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1e3c72;
    }
    .stAlert {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_symbols():
    """Carga la lista de símbolos disponibles."""
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT symbol FROM prices ORDER BY symbol")
            symbols = [row[0] for row in cur.fetchall()]
        return symbols
    finally:
        conn.close()


@st.cache_data(ttl=300)
def load_prices(symbol: str, days: int = 365):
    """Carga precios históricos."""
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT date, open, high, low, close, volume
                FROM prices
                WHERE symbol = %s AND date >= %s
                ORDER BY date
            """, (symbol, datetime.now() - timedelta(days=days)))
            
            rows = cur.fetchall()
            if not rows:
                return pd.DataFrame()
                
            df = pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    finally:
        conn.close()


@st.cache_data(ttl=300)
def load_predictions(symbol: str, days: int = 30):
    """Carga predicciones recientes."""
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    prediction_date,
                    target_date,
                    model_name,
                    predicted_direction,
                    confidence
                FROM ml_predictions
                WHERE symbol = %s AND target_date >= %s
                ORDER BY target_date DESC, model_name
            """, (symbol, datetime.now() - timedelta(days=days)))
            
            rows = cur.fetchall()
            if not rows:
                return pd.DataFrame()
                
            df = pd.DataFrame(rows, columns=[
                'Prediction Date', 'Target Date', 'Model', 'Direction', 'Confidence'
            ])
            df['Prediction Date'] = pd.to_datetime(df['Prediction Date'])
            df['Target Date'] = pd.to_datetime(df['Target Date'])
            return df
    finally:
        conn.close()


def plot_candlestick_with_predictions(prices_df: pd.DataFrame, predictions_df: pd.DataFrame, symbol: str):
    """Crea gráfico de velas con predicciones."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} - Precios y Predicciones', 'Volumen')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=prices_df['Date'],
            open=prices_df['Open'],
            high=prices_df['High'],
            low=prices_df['Low'],
            close=prices_df['Close'],
            name='Precio'
        ),
        row=1, col=1
    )
    
    # Añadir predicciones (si hay)
    if not predictions_df.empty:
        latest_predictions = predictions_df[
            predictions_df['Target Date'] == predictions_df['Target Date'].max()
        ]
        
        for _, pred in latest_predictions.iterrows():
            color = 'green' if pred['Direction'] == 'UP' else 'red'
            fig.add_annotation(
                x=pred['Target Date'],
                y=prices_df['High'].max(),
                text=f"{pred['Model']}: {pred['Direction']}<br>Conf: {pred['Confidence']:.0%}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=color,
                ax=0,
                ay=-40,
                font=dict(size=10, color=color),
                row=1, col=1
            )
    
    # Volumen
    colors = ['red' if row['Open'] > row['Close'] else 'green' for _, row in prices_df.iterrows()]
    fig.add_trace(
        go.Bar(
            x=prices_df['Date'],
            y=prices_df['Volume'],
            name='Volumen',
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


def plot_technical_indicators(prices_df: pd.DataFrame, symbol: str):
    """Gráficos de indicadores técnicos."""
    from mcp_server.scripts.advanced_indicators import compute_all_advanced_indicators
    
    # Preparar datos
    df = prices_df.copy()
    df = df.set_index('Date')
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    indicators = compute_all_advanced_indicators(df)
    
    # Crear subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Precio y Bollinger Bands', 'MACD', 'RSI & Stochastic', 'ADX'),
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # 1. Precio con Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Precio', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['bb_upper'], name='BB Superior', 
                            line=dict(color='gray', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['bb_middle'], name='BB Media', 
                            line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['bb_lower'], name='BB Inferior', 
                            line=dict(color='gray', dash='dash')), row=1, col=1)
    
    # 2. MACD
    fig.add_trace(go.Scatter(x=df.index, y=indicators['macd'], name='MACD', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['macd_signal'], name='Señal', 
                            line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=indicators['macd_histogram'], name='Histograma'), row=2, col=1)
    
    # 3. Stochastic (cargar desde DB si existe)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['stoch_k'], name='Stochastic %K', 
                            line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['stoch_d'], name='Stochastic %D', 
                            line=dict(color='red')), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="green", row=3, col=1)
    
    # 4. ADX
    fig.add_trace(go.Scatter(x=df.index, y=indicators['adx'], name='ADX', line=dict(color='purple')), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['plus_di'], name='+DI', 
                            line=dict(color='green')), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=indicators['minus_di'], name='-DI', 
                            line=dict(color='red')), row=4, col=1)
    fig.add_hline(y=25, line_dash="dash", line_color="gray", row=4, col=1)
    
    fig.update_layout(height=1000, showlegend=True, hovermode='x unified')
    fig.update_xaxes(rangeslider_visible=False)
    
    return fig


def plot_model_comparison(backtest_results: dict):
    """Gráfico comparativo de modelos."""
    if not backtest_results or 'error' in backtest_results:
        st.warning("No hay datos de backtesting disponibles")
        return
    
    # Extraer métricas
    models = []
    accuracies = []
    precisions = []
    recalls = []
    f1_scores = []
    
    for model_name, metrics in backtest_results.items():
        if isinstance(metrics, dict) and 'accuracy' in metrics:
            models.append(model_name)
            accuracies.append(metrics['accuracy'])
            precisions.append(metrics.get('precision', 0))
            recalls.append(metrics.get('recall', 0))
            f1_scores.append(metrics.get('f1_score', 0))
    
    if not models:
        st.warning("No hay métricas disponibles")
        return
    
    # Crear gráfico de barras
    fig = go.Figure()
    
    fig.add_trace(go.Bar(name='Accuracy', x=models, y=accuracies, marker_color='lightblue'))
    fig.add_trace(go.Bar(name='Precision', x=models, y=precisions, marker_color='lightgreen'))
    fig.add_trace(go.Bar(name='Recall', x=models, y=recalls, marker_color='lightyellow'))
    fig.add_trace(go.Bar(name='F1-Score', x=models, y=f1_scores, marker_color='lightcoral'))
    
    fig.update_layout(
        title='Comparación de Modelos ML',
        xaxis_title='Modelo',
        yaxis_title='Score',
        barmode='group',
        height=500
    )
    
    return fig


# ========== INTERFAZ PRINCIPAL ==========

st.markdown('<h1 class="main-header">📈 ML Trading Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuración")

symbols = load_symbols()
if not symbols:
    st.error("No hay símbolos disponibles en la base de datos")
    st.stop()

selected_symbol = st.sidebar.selectbox("Seleccionar Mercado", symbols)
days_to_show = st.sidebar.slider("Días a mostrar", 30, 365, 90)
backtest_days = st.sidebar.slider("Días de Backtesting", 7, 90, 30)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Precio & Predicciones", "📈 Indicadores Técnicos", 
                                    "🎯 Backtesting", "🔥 Heatmap"])

# ===== TAB 1: Precio & Predicciones =====
with tab1:
    st.header(f"Análisis de {selected_symbol}")
    
    col1, col2, col3 = st.columns(3)
    
    # Cargar datos
    prices = load_prices(selected_symbol, days_to_show)
    predictions = load_predictions(selected_symbol, 30)
    
    if prices.empty:
        st.warning(f"No hay datos de precios para {selected_symbol}")
    else:
        # Métricas básicas
        last_price = prices['Close'].iloc[-1]
        prev_price = prices['Close'].iloc[-2] if len(prices) > 1 else last_price
        change = last_price - prev_price
        change_pct = (change / prev_price) * 100
        
        with col1:
            st.metric("Precio Actual", f"${last_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
        
        with col2:
            max_price = prices['High'].tail(30).max()
            st.metric("Máximo (30d)", f"${max_price:.2f}")
        
        with col3:
            min_price = prices['Low'].tail(30).min()
            st.metric("Mínimo (30d)", f"${min_price:.2f}")
        
        # Gráfico principal
        st.plotly_chart(
            plot_candlestick_with_predictions(prices, predictions, selected_symbol),
            use_container_width=True
        )
        
        # Tabla de predicciones recientes
        if not predictions.empty:
            st.subheader("🔮 Predicciones Recientes")
            st.dataframe(
                predictions.head(10).style.applymap(
                    lambda x: 'background-color: lightgreen' if x == 'UP' else 'background-color: lightcoral',
                    subset=['Direction']
                ),
                use_container_width=True
            )

# ===== TAB 2: Indicadores Técnicos =====
with tab2:
    st.header("Indicadores Técnicos Avanzados")
    
    if not prices.empty:
        st.plotly_chart(
            plot_technical_indicators(prices, selected_symbol),
            use_container_width=True
        )
    else:
        st.warning("No hay datos disponibles")

# ===== TAB 3: Backtesting =====
with tab3:
    st.header("🎯 Análisis de Backtesting")
    
    if st.button("🔄 Ejecutar Backtesting", type="primary"):
        with st.spinner("Ejecutando backtesting..."):
            end_date = date.today()
            start_date = end_date - timedelta(days=backtest_days)
            
            # Backtesting por modelo
            results_by_model = backtest_by_model(selected_symbol, start_date, end_date)
            
            # Backtesting ensemble
            ensemble_results = backtest_ensemble(selected_symbol, start_date, end_date)
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Performance por Modelo")
                if results_by_model and 'error' not in results_by_model:
                    fig = plot_model_comparison(results_by_model)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabla detallada
                    metrics_df = pd.DataFrame(results_by_model).T
                    st.dataframe(metrics_df, use_container_width=True)
                else:
                    st.warning("No hay datos de backtesting disponibles")
            
            with col2:
                st.subheader("🎲 Performance Ensemble")
                if ensemble_results and 'error' not in ensemble_results:
                    st.metric("Accuracy Ensemble", f"{ensemble_results['accuracy']:.2%}")
                    st.metric("Precision", f"{ensemble_results['precision']:.2%}")
                    st.metric("Recall", f"{ensemble_results['recall']:.2%}")
                    st.metric("F1-Score", f"{ensemble_results['f1_score']:.2%}")
                    st.metric("Promedio Modelos/Predicción", 
                             f"{ensemble_results.get('avg_models_per_prediction', 0):.1f}")
                else:
                    st.warning("No hay datos de ensemble disponibles")

# ===== TAB 4: Heatmap =====
with tab4:
    st.header("🔥 Correlaciones entre Mercados")
    st.info("Esta funcionalidad estará disponible próximamente")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "ML Trading Dashboard | Desarrollado con Streamlit | "
    f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True
)
