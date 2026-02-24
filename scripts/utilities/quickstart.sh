#!/bin/bash
# Quick start script para las nuevas funcionalidades

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🚀 ML TRADING PLATFORM - QUICK START                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones auxiliares
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar dependencias
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 1. VERIFICANDO DEPENDENCIAS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi
print_success "Python3 encontrado: $(python3 --version)"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_warning "Docker no está instalado (necesario para PostgreSQL)"
else
    print_success "Docker encontrado: $(docker --version | head -n 1)"
fi

# 2. Instalar dependencias Python
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 2. INSTALANDO DEPENDENCIAS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "requirements.txt" ]; then
    print_info "Instalando dependencias del proyecto..."
    pip3 install -r requirements.txt --quiet
    print_success "Dependencias instaladas"
else
    print_warning "requirements.txt no encontrado"
fi

# 3. Verificar PostgreSQL
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🗄️  3. VERIFICANDO BASE DE DATOS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker ps | grep -q postgres; then
    print_success "PostgreSQL está corriendo"
else
    print_warning "PostgreSQL no está corriendo"
    print_info "Iniciando PostgreSQL con docker-compose..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d db
        sleep 3
        print_success "PostgreSQL iniciado"
    else
        print_error "docker-compose.yml no encontrado"
    fi
fi

# 4. Menú interactivo
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎯 4. ¿QUÉ QUIERES HACER?${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1) 📊 Lanzar Dashboard Streamlit"
echo "2) 🤖 Iniciar Bot de Telegram"
echo "3) 🎯 Ejecutar Backtesting"
echo "4) 📈 Calcular Indicadores Avanzados"
echo "5) 🔄 Ejecutar Todo (Dashboard + Bot)"
echo "6) ⏰ Iniciar Scheduler Automatizado (alternativa a n8n)"
echo "7) ℹ️  Ver Documentación"
echo "0) ❌ Salir"
echo ""
echo -n "Selecciona una opción [0-7]: "
read -r option

echo ""

case $option in
    1)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}📊 LANZANDO DASHBOARD STREAMLIT${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        print_info "Dashboard estará disponible en http://localhost:8501"
        print_info "Presiona Ctrl+C para detener"
        echo ""
        streamlit run scripts/ui/streamlit_dashboard.py
        ;;
    
    2)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🤖 INICIANDO BOT DE TELEGRAM${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
            print_error "Variable TELEGRAM_BOT_TOKEN no configurada"
            print_info "Configúrala con: export TELEGRAM_BOT_TOKEN='tu_token'"
            print_info "Obtén token en: https://t.me/BotFather"
            exit 1
        fi
        
        print_success "Token configurado"
        print_info "Bot iniciando... Presiona Ctrl+C para detener"
        echo ""
        python3 scripts/ui/telegram_bot.py
        ;;
    
    3)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🎯 EJECUTANDO BACKTESTING${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -n "Símbolo a testear (ej: ^IBEX): "
        read -r symbol
        echo -n "Días de backtest (default: 30): "
        read -r days
        days=${days:-30}
        
        print_info "Ejecutando backtesting para $symbol (últimos $days días)..."
        python3 << EOF
from mcp_server.scripts.backtesting import generate_backtest_report, save_backtest_report
from datetime import date, timedelta

end = date.today()
start = end - timedelta(days=$days)

print(f"\n{'='*60}")
print(f"BACKTESTING: $symbol")
print(f"Período: {start} a {end}")
print(f"{'='*60}\n")

report = generate_backtest_report("$symbol", start, end)

if 'summary' in report and report['summary']:
    summary = report['summary']
    if 'best_model' in summary:
        print(f"✅ Mejor modelo: {summary['best_model']}")
        print(f"✅ Accuracy: {summary['best_accuracy']:.2%}")
    
    if 'ensemble_vs_best_model' in summary:
        comp = summary['ensemble_vs_best_model']
        print(f"\n📊 Ensemble accuracy: {comp['ensemble_accuracy']:.2%}")
        print(f"📊 Mejora vs mejor modelo: {comp['improvement']:+.2%}")

output_file = save_backtest_report(report)
print(f"\n💾 Reporte guardado: {output_file}")
EOF
        print_success "Backtesting completado"
        ;;
    
    4)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}📈 CALCULANDO INDICADORES AVANZADOS${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -n "Símbolo (ej: ^IBEX): "
        read -r symbol
        
        print_info "Calculando indicadores para $symbol..."
        python3 << EOF
from mcp_server.scripts.advanced_indicators import compute_advanced_indicators_for_symbol

rows = compute_advanced_indicators_for_symbol("$symbol")
print(f"\n✅ {rows} filas de indicadores guardadas en la BD")
print("\nIndicadores calculados:")
print("  • MACD (línea, señal, histograma)")
print("  • Bollinger Bands (superior, media, inferior)")
print("  • ADX (+DI, -DI)")
print("  • ATR")
print("  • Stochastic Oscillator")
print("  • OBV")
print("  • EMAs (12, 26, 200)")
EOF
        print_success "Indicadores calculados"
        ;;
    
    5)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🔄 EJECUTANDO TODO${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Verificar token de Telegram
        if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
            print_warning "TELEGRAM_BOT_TOKEN no configurado, solo se lanzará Dashboard"
            print_info "Lanzando Dashboard en el puerto 8501..."
            streamlit run scripts/ui/streamlit_dashboard.py
        else
            print_info "Lanzando Dashboard (puerto 8501) y Bot de Telegram..."
            print_info "Presiona Ctrl+C para detener ambos"
            
            # Lanzar ambos en background
            streamlit run scripts/ui/streamlit_dashboard.py &
            STREAMLIT_PID=$!
            
            sleep 2
            
            python3 scripts/ui/telegram_bot.py &
            BOT_PID=$!
            
            print_success "Dashboard: http://localhost:8501 (PID: $STREAMLIT_PID)"
            print_success "Bot Telegram: Activo (PID: $BOT_PID)"
            
            # Esperar a Ctrl+C
            trap "kill $STREAMLIT_PID $BOT_PID 2>/dev/null; print_info 'Servicios detenidos'; exit 0" INT
            
            wait
        fi
        ;;
    
    6)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}⏰ INICIANDO SCHEDULER AUTOMATIZADO${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        print_info "El scheduler automatiza actualizaciones diarias (alternativa a n8n)"
        print_info ""
        print_info "Tareas programadas:"
        print_info "  • 8:00 AM  - Obtener datos de mercado"
        print_info "  • 8:30 AM  - Calcular indicadores"
        print_info "  • 9:00 AM  - Ejecutar predicciones ML"
        print_info "  • 9:30 AM  - Validar predicciones"
        print_info "  • 10:00 AM - Generar reportes"
        print_info "  • Domingos 2:00 AM - Reentrenar modelos"
        echo ""
        print_info "Para probar una tarea ahora:"
        print_info "  python3 scripts/automation/scheduler.py --run fetch"
        print_info "  python3 scripts/automation/scheduler.py --run all"
        echo ""
        print_info "Iniciando scheduler... Presiona Ctrl+C para detener"
        echo ""
        
        # Verificar dependencias
        python3 -c "import apscheduler" 2>/dev/null
        if [ $? -ne 0 ]; then
            print_warning "APScheduler no instalado"
            print_info "Instalando..."
            pip3 install apscheduler
        fi
        
        python3 scripts/automation/scheduler.py
        ;;
    
    7)
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}ℹ️  DOCUMENTACIÓN${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        print_info "Documentación disponible:"
        echo ""
        echo "  📄 docs/NEW_FEATURES.md - Nuevas funcionalidades"
        echo "  📄 README.md - Documentación principal"
        echo "  📄 docs/BACKFILL_README.md - Carga de datos históricos"
        echo "  📄 docs/REQUIREMENTS.md - Requisitos del proyecto"
        echo ""
        print_info "Para ver un archivo:"
        echo "  cat docs/NEW_FEATURES.md"
        echo ""
        ;;
    
    0)
        print_info "¡Hasta luego! 👋"
        exit 0
        ;;
    
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac
