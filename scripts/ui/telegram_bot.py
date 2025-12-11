"""
Telegram Bot para alertas de trading.

Funcionalidades:
- Enviar señales de trading en tiempo real
- Alertas personalizadas por usuario
- Comandos interactivos para consultar predicciones
- Notificaciones cuando hay alta confianza
- Resúmenes diarios de mercado
"""

import os
import asyncio
from datetime import datetime, timedelta, date
from typing import List, Dict
import logging

# Telegram Bot API
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        ContextTypes,
        MessageHandler,
        filters
    )
except ImportError:
    print("⚠️  Instala python-telegram-bot: pip install python-telegram-bot")
    exit(1)

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_server', 'scripts'))

from mcp_server.scripts.config import get_db_conn
from mcp_server.scripts.backtesting import backtest_ensemble

# Configuración
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ALERT_CONFIDENCE_THRESHOLD = float(os.getenv('ALERT_CONFIDENCE_THRESHOLD', '0.7'))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Bot de Telegram para alertas de trading."""
    
    def __init__(self, token: str):
        self.token = token
        self.subscribers = set()  # Chat IDs suscritos
        self.user_symbols = {}  # Símbolos seguidos por usuario
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Bienvenida."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        self.subscribers.add(chat_id)
        
        welcome_message = f"""
🤖 **Bienvenido al Trading Bot ML!**

Hola {user.first_name}! 👋

Estoy aquí para ayudarte con señales de trading basadas en Machine Learning.

**Comandos disponibles:**
/start - Mostrar este mensaje
/help - Ayuda detallada
/mercados - Ver mercados disponibles
/seguir <símbolo> - Seguir un mercado
/dejar <símbolo> - Dejar de seguir
/predicciones - Ver predicciones actuales
/resumen - Resumen del mercado
/backtest <símbolo> - Ver performance histórica
/alertas - Configurar alertas

Usa /help para más información.
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"Usuario {user.id} ({user.username}) inició el bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Ayuda detallada."""
        help_text = """
📚 **Guía de Uso del Trading Bot**

**Comandos Básicos:**
• `/mercados` - Lista de mercados disponibles
• `/seguir ^IBEX` - Seguir el IBEX 35
• `/dejar ^IBEX` - Dejar de seguir
• `/predicciones` - Ver todas las predicciones
• `/prediccion ^IBEX` - Predicción específica

**Análisis:**
• `/resumen` - Resumen de todos tus mercados
• `/backtest ^IBEX` - Performance histórica
• `/indicadores ^IBEX` - Indicadores técnicos

**Alertas:**
• `/alertas` - Configurar notificaciones
• `/alertas alta` - Solo alta confianza (>70%)
• `/alertas todas` - Todas las predicciones

**Información:**
• `/estado` - Estado del sistema
• `/ayuda` - Esta ayuda

💡 **Tip:** Las alertas se envían automáticamente cuando hay nuevas predicciones con alta confianza.
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def list_markets(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /mercados - Lista mercados disponibles."""
        conn = get_db_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT symbol, COUNT(*) as num_prices
                    FROM prices
                    GROUP BY symbol
                    ORDER BY symbol
                """)
                markets = cur.fetchall()
            
            if not markets:
                await update.message.reply_text("❌ No hay mercados disponibles")
                return
            
            message = "📊 **Mercados Disponibles:**\n\n"
            for symbol, count in markets:
                message += f"• `{symbol}` ({count} datos)\n"
            
            message += "\n💡 Usa `/seguir <símbolo>` para recibir alertas"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        finally:
            conn.close()
    
    async def follow_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /seguir <símbolo> - Seguir un mercado."""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Debes especificar un símbolo. Ejemplo: `/seguir ^IBEX`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0].upper()
        
        # Verificar que el símbolo existe
        conn = get_db_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM prices WHERE symbol = %s", (symbol,))
                exists = cur.fetchone()[0] > 0
            
            if not exists:
                await update.message.reply_text(
                    f"❌ El símbolo `{symbol}` no existe. Usa /mercados para ver disponibles.",
                    parse_mode='Markdown'
                )
                return
            
            # Añadir a seguimiento
            if chat_id not in self.user_symbols:
                self.user_symbols[chat_id] = set()
            
            self.user_symbols[chat_id].add(symbol)
            
            await update.message.reply_text(
                f"✅ Ahora sigues `{symbol}`\n"
                f"Recibirás alertas cuando haya predicciones nuevas.",
                parse_mode='Markdown'
            )
            logger.info(f"Usuario {chat_id} sigue {symbol}")
        finally:
            conn.close()
    
    async def unfollow_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /dejar <símbolo> - Dejar de seguir."""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Especifica el símbolo. Ejemplo: `/dejar ^IBEX`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0].upper()
        
        if chat_id in self.user_symbols and symbol in self.user_symbols[chat_id]:
            self.user_symbols[chat_id].remove(symbol)
            await update.message.reply_text(
                f"✅ Dejaste de seguir `{symbol}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ No estás siguiendo `{symbol}`",
                parse_mode='Markdown'
            )
    
    async def show_predictions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /predicciones - Mostrar predicciones actuales."""
        chat_id = update.effective_chat.id
        
        # Si se especifica símbolo
        if context.args:
            symbol = context.args[0].upper()
            symbols = [symbol]
        # Si no, usar símbolos seguidos
        elif chat_id in self.user_symbols and self.user_symbols[chat_id]:
            symbols = list(self.user_symbols[chat_id])
        else:
            await update.message.reply_text(
                "❌ Primero debes seguir algún mercado con `/seguir <símbolo>`",
                parse_mode='Markdown'
            )
            return
        
        conn = get_db_conn()
        try:
            message = "🔮 **Predicciones Actuales:**\n\n"
            
            for symbol in symbols:
                with conn.cursor() as cur:
                    # Última predicción de cada modelo
                    cur.execute("""
                        SELECT 
                            model_name,
                            predicted_direction,
                            confidence,
                            target_date
                        FROM ml_predictions
                        WHERE symbol = %s 
                          AND target_date = (
                              SELECT MAX(target_date)
                              FROM ml_predictions
                              WHERE symbol = %s
                          )
                        ORDER BY confidence DESC
                    """, (symbol, symbol))
                    
                    predictions = cur.fetchall()
                
                if not predictions:
                    message += f"📊 `{symbol}`: Sin predicciones recientes\n\n"
                    continue
                
                # Calcular consenso (votación)
                up_votes = sum(1 for p in predictions if p[1] == 'UP')
                down_votes = len(predictions) - up_votes
                consensus = 'UP ⬆️' if up_votes > down_votes else 'DOWN ⬇️'
                
                message += f"📊 **{symbol}**\n"
                message += f"Consenso: **{consensus}** ({up_votes}/{len(predictions)} modelos)\n"
                message += f"Fecha objetivo: {predictions[0][3]}\n\n"
                
                # Top 3 modelos
                message += "Top Modelos:\n"
                for i, (model, direction, conf, _) in enumerate(predictions[:3], 1):
                    emoji = '⬆️' if direction == 'UP' else '⬇️'
                    message += f"{i}. {model}: {emoji} ({conf:.0%})\n"
                
                message += "\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        finally:
            conn.close()
    
    async def market_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /resumen - Resumen del mercado."""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_symbols or not self.user_symbols[chat_id]:
            await update.message.reply_text(
                "❌ No sigues ningún mercado. Usa `/seguir <símbolo>`",
                parse_mode='Markdown'
            )
            return
        
        conn = get_db_conn()
        try:
            message = "📈 **Resumen de Mercado**\n\n"
            
            for symbol in self.user_symbols[chat_id]:
                with conn.cursor() as cur:
                    # Último precio
                    cur.execute("""
                        SELECT close, date
                        FROM prices
                        WHERE symbol = %s
                        ORDER BY date DESC
                        LIMIT 2
                    """, (symbol,))
                    
                    prices = cur.fetchall()
                    
                    if len(prices) >= 2:
                        current_price = prices[0][0]
                        prev_price = prices[1][0]
                        change = ((current_price - prev_price) / prev_price) * 100
                        
                        emoji = '🟢' if change > 0 else '🔴'
                        message += f"{emoji} **{symbol}**: ${current_price:.2f} ({change:+.2f}%)\n"
                    else:
                        message += f"📊 **{symbol}**: Datos insuficientes\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        finally:
            conn.close()
    
    async def show_backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /backtest <símbolo> - Performance histórica."""
        if not context.args:
            await update.message.reply_text(
                "❌ Especifica un símbolo. Ejemplo: `/backtest ^IBEX`",
                parse_mode='Markdown'
            )
            return
        
        symbol = context.args[0].upper()
        
        await update.message.reply_text(f"⏳ Calculando backtest para {symbol}...")
        
        try:
            end = date.today()
            start = end - timedelta(days=30)
            
            results = backtest_ensemble(symbol, start, end)
            
            if 'error' in results:
                await update.message.reply_text(f"❌ {results['error']}")
                return
            
            message = f"""
📊 **Backtest {symbol}** (30 días)

**Métricas del Ensemble:**
• Accuracy: {results['accuracy']:.2%}
• Precision: {results['precision']:.2%}
• Recall: {results['recall']:.2%}
• F1-Score: {results['f1_score']:.2%}

**Detalles:**
• Predicciones: {results['total_predictions']}
• Período: {results['start_date']} a {results['end_date']}
• Modelos promedio: {results.get('avg_models_per_prediction', 0):.1f}

{'✅ Performance sólida!' if results['accuracy'] > 0.6 else '⚠️ Performance moderada'}
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error en backtest: {e}")
            await update.message.reply_text(f"❌ Error al calcular backtest: {str(e)}")
    
    async def send_alert_to_subscribers(self, symbol: str, prediction_data: Dict):
        """Envía alerta a todos los suscriptores del símbolo."""
        if not self.subscribers:
            return
        
        message = f"""
🚨 **Nueva Señal de Trading**

📊 Mercado: `{symbol}`
🎯 Dirección: **{prediction_data['direction']}** {'⬆️' if prediction_data['direction'] == 'UP' else '⬇️'}
📈 Confianza: {prediction_data['confidence']:.0%}
🤖 Modelo: {prediction_data['model']}
📅 Fecha objetivo: {prediction_data['target_date']}

{'🔥 Alta confianza!' if prediction_data['confidence'] >= 0.7 else ''}
        """
        
        for chat_id in self.subscribers:
            # Solo enviar si el usuario sigue este símbolo
            if chat_id in self.user_symbols and symbol in self.user_symbols[chat_id]:
                try:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error enviando alerta a {chat_id}: {e}")
    
    def run(self):
        """Inicia el bot."""
        # Crear aplicación
        self.application = Application.builder().token(self.token).build()
        
        # Registrar comandos
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("ayuda", self.help_command))
        self.application.add_handler(CommandHandler("mercados", self.list_markets))
        self.application.add_handler(CommandHandler("seguir", self.follow_symbol))
        self.application.add_handler(CommandHandler("dejar", self.unfollow_symbol))
        self.application.add_handler(CommandHandler("predicciones", self.show_predictions))
        self.application.add_handler(CommandHandler("prediccion", self.show_predictions))
        self.application.add_handler(CommandHandler("resumen", self.market_summary))
        self.application.add_handler(CommandHandler("backtest", self.show_backtest))
        
        # Iniciar bot
        logger.info("🤖 Bot de Telegram iniciado")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: Configura TELEGRAM_BOT_TOKEN en las variables de entorno")
        print("Pasos:")
        print("1. Habla con @BotFather en Telegram")
        print("2. Crea un nuevo bot con /newbot")
        print("3. Copia el token")
        print("4. Configura: export TELEGRAM_BOT_TOKEN='tu_token'")
        exit(1)
    
    bot = TradingBot(TELEGRAM_BOT_TOKEN)
    bot.run()
