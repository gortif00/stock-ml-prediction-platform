# mcp_server/scripts/advanced_indicators.py
"""
Indicadores técnicos avanzados para análisis financiero.

Implementa:
- MACD (Moving Average Convergence Divergence): Momentum y tendencia
- Bollinger Bands: Volatilidad y niveles de sobrecompra/sobreventa
- ADX (Average Directional Index): Fuerza de tendencia
- ATR (Average True Range): Volatilidad real
- Stochastic Oscillator: Momentum
- OBV (On-Balance Volume): Análisis de volumen
"""

import pandas as pd
import numpy as np
from psycopg2 import Error as PsycopgError
from .config import get_db_conn
from . import logger


def _load_full_prices(symbol: str) -> pd.DataFrame:
    """
    Carga precios completos (OHLCV) desde la base de datos.
    
    Args:
        symbol: Símbolo del activo
        
    Returns:
        DataFrame con columnas: Open, High, Low, Close, Volume
    """
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT date, open, high, low, close, volume
                FROM prices
                WHERE symbol = %s
                ORDER BY date
                """,
                (symbol,),
            )
            rows = cur.fetchall()
    except PsycopgError as e:
        logger.error(f"Error al cargar precios completos de {symbol}: {e}")
        if conn and not conn.closed:
            conn.rollback()
        raise
    finally:
        if conn and not conn.closed:
            conn.close()

    if not rows:
        logger.warning(f"No hay precios en BD para {symbol}")
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=['date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    
    return df


def compute_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calcula MACD (Moving Average Convergence Divergence).
    
    MACD = EMA(fast) - EMA(slow)
    Signal line = EMA(MACD, signal)
    Histogram = MACD - Signal
    
    Args:
        close: Serie de precios de cierre
        fast: Período EMA rápida (default: 12)
        slow: Período EMA lenta (default: 26)
        signal: Período de señal (default: 9)
        
    Returns:
        DataFrame con columnas: macd, macd_signal, macd_histogram
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_histogram = macd - macd_signal
    
    return pd.DataFrame({
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_histogram': macd_histogram
    })


def compute_bollinger_bands(close: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    Calcula Bandas de Bollinger.
    
    Middle Band = SMA(window)
    Upper Band = Middle + (num_std × std)
    Lower Band = Middle - (num_std × std)
    
    Args:
        close: Serie de precios de cierre
        window: Ventana para SMA (default: 20)
        num_std: Número de desviaciones estándar (default: 2.0)
        
    Returns:
        DataFrame con columnas: bb_middle, bb_upper, bb_lower, bb_width, bb_percent
    """
    sma = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std()
    
    bb_upper = sma + (std * num_std)
    bb_lower = sma - (std * num_std)
    bb_width = bb_upper - bb_lower
    
    # %B: posición del precio dentro de las bandas (0-1)
    bb_percent = (close - bb_lower) / (bb_upper - bb_lower)
    
    return pd.DataFrame({
        'bb_middle': sma,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower,
        'bb_width': bb_width,
        'bb_percent': bb_percent
    })


def compute_adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.DataFrame:
    """
    Calcula ADX (Average Directional Index).
    
    Mide la fuerza de la tendencia (no la dirección):
    - ADX < 25: Tendencia débil/rango
    - ADX 25-50: Tendencia fuerte
    - ADX > 50: Tendencia muy fuerte
    
    Args:
        high: Serie de precios máximos
        low: Serie de precios mínimos
        close: Serie de precios de cierre
        window: Período de cálculo (default: 14)
        
    Returns:
        DataFrame con columnas: adx, plus_di, minus_di
    """
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = tr.rolling(window=window).mean()
    
    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    plus_dm_smooth = pd.Series(plus_dm).rolling(window=window).mean()
    minus_dm_smooth = pd.Series(minus_dm).rolling(window=window).mean()
    
    # Directional Indicators
    plus_di = 100 * (plus_dm_smooth / atr)
    minus_di = 100 * (minus_dm_smooth / atr)
    
    # ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=window).mean()
    
    return pd.DataFrame({
        'adx': adx,
        'plus_di': plus_di,
        'minus_di': minus_di
    })


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """
    Calcula ATR (Average True Range).
    
    Mide la volatilidad del mercado. Valores altos = mayor volatilidad.
    
    Args:
        high: Serie de precios máximos
        low: Serie de precios mínimos
        close: Serie de precios de cierre
        window: Período de cálculo (default: 14)
        
    Returns:
        Serie con valores ATR
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    
    atr = tr.rolling(window=window).mean()
    return atr


def compute_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                       k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
    """
    Calcula Oscilador Estocástico.
    
    Compara el precio de cierre con el rango de precios en un período.
    %K = 100 * (Close - Low(n)) / (High(n) - Low(n))
    %D = SMA(%K, d_window)
    
    Args:
        high: Serie de precios máximos
        low: Serie de precios mínimos
        close: Serie de precios de cierre
        k_window: Período para %K (default: 14)
        d_window: Período para %D (default: 3)
        
    Returns:
        DataFrame con columnas: stoch_k, stoch_d
    """
    low_min = low.rolling(window=k_window).min()
    high_max = high.rolling(window=k_window).max()
    
    stoch_k = 100 * (close - low_min) / (high_max - low_min)
    stoch_d = stoch_k.rolling(window=d_window).mean()
    
    return pd.DataFrame({
        'stoch_k': stoch_k,
        'stoch_d': stoch_d
    })


def compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calcula OBV (On-Balance Volume).
    
    Relaciona volumen con cambio de precio. Útil para confirmar tendencias.
    
    Args:
        close: Serie de precios de cierre
        volume: Serie de volumen
        
    Returns:
        Serie con valores OBV
    """
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return obv


def compute_all_advanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula todos los indicadores avanzados.
    
    Args:
        df: DataFrame con columnas: Open, High, Low, Close, Volume
        
    Returns:
        DataFrame con todos los indicadores calculados
    """
    result = pd.DataFrame(index=df.index)
    
    # MACD
    macd_df = compute_macd(df['Close'])
    result = result.join(macd_df)
    
    # Bollinger Bands
    bb_df = compute_bollinger_bands(df['Close'])
    result = result.join(bb_df)
    
    # ADX
    adx_df = compute_adx(df['High'], df['Low'], df['Close'])
    result = result.join(adx_df)
    
    # ATR
    result['atr'] = compute_atr(df['High'], df['Low'], df['Close'])
    
    # Stochastic
    stoch_df = compute_stochastic(df['High'], df['Low'], df['Close'])
    result = result.join(stoch_df)
    
    # OBV
    result['obv'] = compute_obv(df['Close'], df['Volume'])
    
    # EMA adicionales (útiles para estrategias)
    result['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    result['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    result['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    return result


def compute_advanced_indicators_for_symbol(symbol: str) -> int:
    """
    Calcula indicadores avanzados y los guarda en la base de datos.
    
    Crea una nueva tabla 'advanced_indicators' si no existe.
    
    Args:
        symbol: Símbolo del activo
        
    Returns:
        Número de filas insertadas/actualizadas
    """
    df_prices = _load_full_prices(symbol)
    if df_prices.empty:
        return 0

    indicators_df = compute_all_advanced_indicators(df_prices)
    indicators_df = indicators_df.dropna(how='all')
    
    if indicators_df.empty:
        logger.warning(f"No se pudieron calcular indicadores avanzados para {symbol}")
        return 0

    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            # Crear tabla si no existe
            cur.execute("""
                CREATE TABLE IF NOT EXISTS advanced_indicators (
                    symbol VARCHAR(20),
                    date DATE,
                    macd DOUBLE PRECISION,
                    macd_signal DOUBLE PRECISION,
                    macd_histogram DOUBLE PRECISION,
                    bb_middle DOUBLE PRECISION,
                    bb_upper DOUBLE PRECISION,
                    bb_lower DOUBLE PRECISION,
                    bb_width DOUBLE PRECISION,
                    bb_percent DOUBLE PRECISION,
                    adx DOUBLE PRECISION,
                    plus_di DOUBLE PRECISION,
                    minus_di DOUBLE PRECISION,
                    atr DOUBLE PRECISION,
                    stoch_k DOUBLE PRECISION,
                    stoch_d DOUBLE PRECISION,
                    obv DOUBLE PRECISION,
                    ema_12 DOUBLE PRECISION,
                    ema_26 DOUBLE PRECISION,
                    ema_200 DOUBLE PRECISION,
                    PRIMARY KEY (symbol, date)
                );
            """)
            
            # Insertar/actualizar indicadores
            for date, row in indicators_df.iterrows():
                cur.execute(
                    """
                    INSERT INTO advanced_indicators (
                        symbol, date,
                        macd, macd_signal, macd_histogram,
                        bb_middle, bb_upper, bb_lower, bb_width, bb_percent,
                        adx, plus_di, minus_di, atr,
                        stoch_k, stoch_d, obv,
                        ema_12, ema_26, ema_200
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO UPDATE SET
                        macd = EXCLUDED.macd,
                        macd_signal = EXCLUDED.macd_signal,
                        macd_histogram = EXCLUDED.macd_histogram,
                        bb_middle = EXCLUDED.bb_middle,
                        bb_upper = EXCLUDED.bb_upper,
                        bb_lower = EXCLUDED.bb_lower,
                        bb_width = EXCLUDED.bb_width,
                        bb_percent = EXCLUDED.bb_percent,
                        adx = EXCLUDED.adx,
                        plus_di = EXCLUDED.plus_di,
                        minus_di = EXCLUDED.minus_di,
                        atr = EXCLUDED.atr,
                        stoch_k = EXCLUDED.stoch_k,
                        stoch_d = EXCLUDED.stoch_d,
                        obv = EXCLUDED.obv,
                        ema_12 = EXCLUDED.ema_12,
                        ema_26 = EXCLUDED.ema_26,
                        ema_200 = EXCLUDED.ema_200;
                    """,
                    (
                        symbol, date.date(),
                        float(row['macd']) if pd.notna(row['macd']) else None,
                        float(row['macd_signal']) if pd.notna(row['macd_signal']) else None,
                        float(row['macd_histogram']) if pd.notna(row['macd_histogram']) else None,
                        float(row['bb_middle']) if pd.notna(row['bb_middle']) else None,
                        float(row['bb_upper']) if pd.notna(row['bb_upper']) else None,
                        float(row['bb_lower']) if pd.notna(row['bb_lower']) else None,
                        float(row['bb_width']) if pd.notna(row['bb_width']) else None,
                        float(row['bb_percent']) if pd.notna(row['bb_percent']) else None,
                        float(row['adx']) if pd.notna(row['adx']) else None,
                        float(row['plus_di']) if pd.notna(row['plus_di']) else None,
                        float(row['minus_di']) if pd.notna(row['minus_di']) else None,
                        float(row['atr']) if pd.notna(row['atr']) else None,
                        float(row['stoch_k']) if pd.notna(row['stoch_k']) else None,
                        float(row['stoch_d']) if pd.notna(row['stoch_d']) else None,
                        float(row['obv']) if pd.notna(row['obv']) else None,
                        float(row['ema_12']) if pd.notna(row['ema_12']) else None,
                        float(row['ema_26']) if pd.notna(row['ema_26']) else None,
                        float(row['ema_200']) if pd.notna(row['ema_200']) else None,
                    ),
                )
        
        conn.commit()
        logger.info(f"Indicadores avanzados calculados para {symbol}: {len(indicators_df)} filas")
        return len(indicators_df)

    except PsycopgError as e:
        logger.error(f"Error al guardar indicadores avanzados de {symbol}: {e}")
        if conn and not conn.closed:
            conn.rollback()
        raise
    finally:
        if conn and not conn.closed:
            conn.close()


# Ejemplo de uso
if __name__ == "__main__":
    symbol = "^IBEX"
    print(f"Calculando indicadores avanzados para {symbol}...")
    
    rows = compute_advanced_indicators_for_symbol(symbol)
    print(f"✅ {rows} filas de indicadores guardadas")
