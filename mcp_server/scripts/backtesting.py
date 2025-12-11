# mcp_server/scripts/backtesting.py
"""
Sistema de backtesting automatizado para validar modelos ML.

Este módulo permite:
- Validación histórica de predicciones vs datos reales
- Cálculo de métricas: accuracy, precision, recall, F1-score, MAE, RMSE
- Análisis de performance por modelo individual y ensemble
- Generación de reportes comparativos
"""

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error
)
from psycopg2 import Error as PsycopgError
import json

from .config import get_db_conn
from . import logger


def load_historical_predictions(
    symbol: str, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> pd.DataFrame:
    """
    Carga predicciones históricas desde la base de datos.
    
    Args:
        symbol: Símbolo del activo
        start_date: Fecha inicial (None = sin límite)
        end_date: Fecha final (None = sin límite)
        
    Returns:
        DataFrame con columnas: prediction_date, target_date, model_name, 
                                predicted_direction, confidence, actual_price
    """
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            query = """
                SELECT 
                    p.prediction_date,
                    p.target_date,
                    p.model_name,
                    p.predicted_direction,
                    p.confidence,
                    pr.close as actual_price
                FROM ml_predictions p
                LEFT JOIN prices pr 
                    ON p.symbol = pr.symbol 
                    AND p.target_date = pr.date
                WHERE p.symbol = %s
            """
            params = [symbol]
            
            if start_date:
                query += " AND p.target_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND p.target_date <= %s"
                params.append(end_date)
                
            query += " ORDER BY p.target_date, p.prediction_date, p.model_name"
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            
        if not rows:
            logger.warning(f"No hay predicciones históricas para {symbol}")
            return pd.DataFrame()
            
        df = pd.DataFrame(rows)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        df['target_date'] = pd.to_datetime(df['target_date'])
        
        return df
        
    except PsycopgError as e:
        logger.error(f"Error al cargar predicciones históricas: {e}")
        raise
    finally:
        if conn and not conn.closed:
            conn.close()


def calculate_actual_direction(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Calcula la dirección real del mercado comparando precios consecutivos.
    
    Args:
        df: DataFrame con predicciones
        symbol: Símbolo del activo
        
    Returns:
        DataFrame con columna 'actual_direction' añadida
    """
    conn = None
    try:
        conn = get_db_conn()
        
        # Obtener precios de cierre para calcular dirección real
        dates = df['target_date'].unique()
        date_list = [d.date() if isinstance(d, pd.Timestamp) else d for d in dates]
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT date, close
                FROM prices
                WHERE symbol = %s AND date = ANY(%s)
                ORDER BY date
            """, (symbol, date_list))
            
            price_rows = cur.fetchall()
            
        if not price_rows:
            logger.warning(f"No hay precios para calcular dirección real de {symbol}")
            return df
            
        # Crear DataFrame de precios
        prices_df = pd.DataFrame(price_rows, columns=['date', 'close'])
        prices_df['date'] = pd.to_datetime(prices_df['date'])
        prices_df = prices_df.sort_values('date')
        
        # Calcular cambio de precio (dirección real)
        prices_df['prev_close'] = prices_df['close'].shift(1)
        prices_df['actual_direction'] = np.where(
            prices_df['close'] > prices_df['prev_close'], 
            'UP', 
            'DOWN'
        )
        
        # Merge con predicciones
        df = df.merge(
            prices_df[['date', 'actual_direction', 'prev_close']], 
            left_on='target_date', 
            right_on='date',
            how='left'
        )
        df = df.drop('date', axis=1)
        
        return df
        
    except PsycopgError as e:
        logger.error(f"Error al calcular dirección real: {e}")
        raise
    finally:
        if conn and not conn.closed:
            conn.close()


def calculate_metrics(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de performance del modelo.
    
    Args:
        df: DataFrame con columnas 'predicted_direction' y 'actual_direction'
        
    Returns:
        Dict con métricas: accuracy, precision, recall, f1_score, confusion_matrix
    """
    # Filtrar solo filas con datos completos
    valid_df = df.dropna(subset=['predicted_direction', 'actual_direction'])
    
    if len(valid_df) == 0:
        return {
            'total_predictions': 0,
            'error': 'No hay datos válidos para calcular métricas'
        }
    
    y_true = valid_df['actual_direction']
    y_pred = valid_df['predicted_direction']
    
    # Convertir a binario (UP=1, DOWN=0)
    y_true_binary = (y_true == 'UP').astype(int)
    y_pred_binary = (y_pred == 'UP').astype(int)
    
    metrics = {
        'total_predictions': len(valid_df),
        'accuracy': accuracy_score(y_true_binary, y_pred_binary),
        'precision': precision_score(y_true_binary, y_pred_binary, zero_division=0),
        'recall': recall_score(y_true_binary, y_pred_binary, zero_division=0),
        'f1_score': f1_score(y_true_binary, y_pred_binary, zero_division=0),
        'confusion_matrix': confusion_matrix(y_true_binary, y_pred_binary).tolist()
    }
    
    # Calcular métricas adicionales si hay confidence
    if 'confidence' in valid_df.columns:
        metrics['avg_confidence'] = valid_df['confidence'].mean()
        
        # Precisión ponderada por confidence
        correct = (y_true == y_pred).astype(int)
        weighted_accuracy = (correct * valid_df['confidence']).sum() / valid_df['confidence'].sum()
        metrics['weighted_accuracy'] = weighted_accuracy
    
    return metrics


def backtest_by_model(
    symbol: str, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Dict]:
    """
    Realiza backtesting separado por cada modelo ML.
    
    Args:
        symbol: Símbolo del activo
        start_date: Fecha inicial del backtest
        end_date: Fecha final del backtest
        
    Returns:
        Dict con métricas por modelo: {model_name: metrics_dict}
    """
    logger.info(f"Iniciando backtesting para {symbol} desde {start_date} hasta {end_date}")
    
    # Cargar predicciones históricas
    df = load_historical_predictions(symbol, start_date, end_date)
    
    if df.empty:
        return {'error': 'No hay datos de predicciones para el período especificado'}
    
    # Calcular dirección real
    df = calculate_actual_direction(df, symbol)
    
    # Agrupar por modelo y calcular métricas
    results = {}
    
    for model_name in df['model_name'].unique():
        if pd.isna(model_name):
            continue
            
        model_df = df[df['model_name'] == model_name].copy()
        metrics = calculate_metrics(model_df)
        
        # Añadir información temporal
        metrics['start_date'] = model_df['target_date'].min().strftime('%Y-%m-%d')
        metrics['end_date'] = model_df['target_date'].max().strftime('%Y-%m-%d')
        metrics['model_name'] = model_name
        
        results[model_name] = metrics
    
    logger.info(f"Backtesting completado para {symbol}. Modelos evaluados: {len(results)}")
    return results


def backtest_ensemble(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_models: int = 3
) -> Dict:
    """
    Evalúa performance del ensemble (votación mayoritaria).
    
    Args:
        symbol: Símbolo del activo
        start_date: Fecha inicial
        end_date: Fecha final
        min_models: Mínimo de modelos requeridos para considerar ensemble válido
        
    Returns:
        Dict con métricas del ensemble
    """
    df = load_historical_predictions(symbol, start_date, end_date)
    
    if df.empty:
        return {'error': 'No hay datos de predicciones'}
    
    df = calculate_actual_direction(df, symbol)
    
    # Agrupar por target_date y hacer votación
    ensemble_predictions = []
    
    for target_date in df['target_date'].unique():
        date_df = df[df['target_date'] == target_date].copy()
        
        # Contar votos
        votes = date_df['predicted_direction'].value_counts()
        total_models = len(date_df)
        
        if total_models < min_models:
            continue
        
        # Dirección ganadora
        ensemble_direction = votes.idxmax()
        ensemble_confidence = votes.max() / total_models
        
        # Dirección real (debería ser la misma para todos los modelos en esta fecha)
        actual_direction = date_df['actual_direction'].iloc[0]
        
        ensemble_predictions.append({
            'target_date': target_date,
            'predicted_direction': ensemble_direction,
            'actual_direction': actual_direction,
            'confidence': ensemble_confidence,
            'num_models': total_models
        })
    
    ensemble_df = pd.DataFrame(ensemble_predictions)
    
    if ensemble_df.empty:
        return {'error': f'No hay suficientes datos de ensemble (mínimo {min_models} modelos)'}
    
    metrics = calculate_metrics(ensemble_df)
    metrics['start_date'] = ensemble_df['target_date'].min().strftime('%Y-%m-%d')
    metrics['end_date'] = ensemble_df['target_date'].max().strftime('%Y-%m-%d')
    metrics['avg_models_per_prediction'] = ensemble_df['num_models'].mean()
    
    return metrics


def generate_backtest_report(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    output_format: str = 'dict'
) -> Dict:
    """
    Genera reporte completo de backtesting.
    
    Args:
        symbol: Símbolo del activo
        start_date: Fecha inicial
        end_date: Fecha final
        output_format: 'dict' o 'json'
        
    Returns:
        Reporte completo con métricas por modelo y ensemble
    """
    report = {
        'symbol': symbol,
        'backtest_period': {
            'start': start_date.isoformat() if start_date else None,
            'end': end_date.isoformat() if end_date else None
        },
        'generated_at': datetime.now().isoformat(),
        'individual_models': {},
        'ensemble': {},
        'summary': {}
    }
    
    # Backtesting por modelo
    model_results = backtest_by_model(symbol, start_date, end_date)
    report['individual_models'] = model_results
    
    # Backtesting ensemble
    ensemble_results = backtest_ensemble(symbol, start_date, end_date)
    report['ensemble'] = ensemble_results
    
    # Summary: mejor modelo
    if model_results and 'error' not in model_results:
        best_model = max(
            model_results.items(),
            key=lambda x: x[1].get('accuracy', 0) if isinstance(x[1], dict) else 0
        )
        report['summary']['best_model'] = best_model[0]
        report['summary']['best_accuracy'] = best_model[1].get('accuracy', 0)
        
        # Comparar ensemble vs mejor modelo
        if 'error' not in ensemble_results:
            report['summary']['ensemble_vs_best_model'] = {
                'ensemble_accuracy': ensemble_results.get('accuracy', 0),
                'best_model_accuracy': best_model[1].get('accuracy', 0),
                'improvement': ensemble_results.get('accuracy', 0) - best_model[1].get('accuracy', 0)
            }
    
    if output_format == 'json':
        return json.dumps(report, indent=2)
    
    return report


def save_backtest_report(report: Dict, output_file: str = None):
    """
    Guarda reporte de backtesting en archivo JSON.
    
    Args:
        report: Diccionario con el reporte
        output_file: Path del archivo (None = auto-generar nombre)
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        symbol = report.get('symbol', 'unknown').replace('^', '')
        output_file = f"backtest_report_{symbol}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Reporte de backtesting guardado en: {output_file}")
    return output_file


# Ejemplo de uso
if __name__ == "__main__":
    # Backtest de últimos 30 días
    end = date.today()
    start = end - timedelta(days=30)
    
    symbol = "^IBEX"
    
    print(f"\n{'='*60}")
    print(f"BACKTESTING: {symbol}")
    print(f"Período: {start} a {end}")
    print(f"{'='*60}\n")
    
    # Generar reporte completo
    report = generate_backtest_report(symbol, start, end)
    
    # Mostrar resumen
    if 'summary' in report and report['summary']:
        print("\n📊 RESUMEN:")
        summary = report['summary']
        if 'best_model' in summary:
            print(f"  Mejor modelo: {summary['best_model']}")
            print(f"  Accuracy: {summary['best_accuracy']:.2%}")
        
        if 'ensemble_vs_best_model' in summary:
            comp = summary['ensemble_vs_best_model']
            print(f"\n  Ensemble accuracy: {comp['ensemble_accuracy']:.2%}")
            print(f"  Mejora vs mejor modelo: {comp['improvement']:.2%}")
    
    # Guardar reporte
    output_file = save_backtest_report(report)
    print(f"\n✅ Reporte guardado: {output_file}")
