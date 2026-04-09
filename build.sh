#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# 🚀 PIPELINE HELPER SCRIPT
# Esegui gli step della pipeline localmente durante lo sviluppo
# ═══════════════════════════════════════════════════════════════════

set -e

# ── Colori per output ────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Variabili ────────────────────────────────────────────────────
VENV_DIR=".venv"
PROJECT_DIR="mmd"
PYTHON_VERSION="3.12"

# ── Funzioni Helper ──────────────────────────────────────────────

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}\n"
}

print_error() {
    echo -e "${RED}❌ $1${NC}\n"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}\n"
}

# ── Dosa controlla se il comando esiste ──
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 non è installato. Installalo prima di continuare."
        exit 1
    fi
}

# ── Attiva il virtual environment ────────
activate_venv() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        source "$VENV_DIR/Scripts/activate"
    else
        # Unix-like
        source "$VENV_DIR/bin/activate"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 🚀 MAIN STAGES
# ═══════════════════════════════════════════════════════════════════

stage_help() {
    echo "Sintassi: ./build.sh [stage]"
    echo ""
    echo "Stage disponibili:"
    echo "  • setup          - Crea virtualenv e installa dipendenze"
    echo "  • lint           - Esegui flake8, black, isort"
    echo "  • test           - Esegui pytest con coverage"
    echo "  • build          - Build immagine Docker"
    echo "  • scan           - Scansiona immagine Docker (Trivy)"
    echo "  • all            - Esegui tutti gli step (setup → lint → test → build)"
    echo "  • clean          - Pulisce virtualenv e cache"
    echo "  • help           - Mostra questo messaggio"
    echo ""
    echo "Esempi:"
    echo "  ./build.sh setup"
    echo "  ./build.sh test"
    echo "  ./build.sh all"
}

stage_setup() {
    print_header "⚙️  SETUP ENVIRONMENT"

    # Verifica Python
    check_command python${PYTHON_VERSION}
    
    # Se il venv non esiste, crealo
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creando virtual environment..."
        python${PYTHON_VERSION} -m venv ${VENV_DIR}
    fi
    
    # Attiva il venv
    activate_venv
    
    # Upgrade pip
    echo "Aggiornando pip..."
    pip install --upgrade pip setuptools wheel --quiet
    
    # Installa le dipendenze
    echo "Installando dipendenze da requirements.txt..."
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt --quiet
    else
        print_error "Non trovato: requirements.txt"
        return 1
    fi
    
    print_success "Setup completato!"
    echo "Per attivare il venv: source ${VENV_DIR}/bin/activate"
}

stage_lint() {
    print_header "🔍 CODE QUALITY CHECKS"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment non trovato. Esegui: ./build.sh setup"
        return 1
    fi
    
    activate_venv
    
    # Installa strumenti di linting
    echo "Installando strumenti di linting..."
    pip install flake8 black isort pylint --quiet
    
    # flake8
    echo "Eseguendo flake8..."
    if flake8 ${PROJECT_DIR} --count --select=E9,F63,F7,F82 --show-source; then
        print_success "flake8 passed ✓"
    else
        print_warning "flake8 ha trovato problemi (non bloccante)"
    fi
    
    # black
    echo "Eseguendo black check..."
    if black --check ${PROJECT_DIR}; then
        print_success "black check passed ✓"
    else
        print_warning "File non formattati. Esegui: black ${PROJECT_DIR}"
    fi
    
    # isort
    echo "Eseguendo isort check..."
    if isort --check-only ${PROJECT_DIR}; then
        print_success "isort check passed ✓"
    else
        print_warning "Import non ordinati. Esegui: isort ${PROJECT_DIR}"
    fi
    
    print_success "Code Quality check completato!"
}

stage_test() {
    print_header "🧪 RUNNING TESTS"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment non trovato. Esegui: ./build.sh setup"
        return 1
    fi
    
    activate_venv
    
    # Configura Django
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    export DJANGO_SETTINGS_MODULE=mmd.settings
    
    # Installa pytest con plugin Django
    echo "Installando pytest..."
    pip install pytest pytest-cov pytest-django --quiet
    
    # Database migrations (se necessario)
    echo "Eseguendo Django migrations..."
    cd ${PROJECT_DIR}
    # python manage.py migrate --run-syncdb || true
    
    # Esegui pytest
    echo "Eseguendo test suite..."
    if pytest -v --tb=short --cov=. --cov-report=html --cov-report=term; then
        print_success "Tutti i test passati! ✓"
        echo "Coverage report disponibile in: htmlcov/index.html"
    else
        print_error "Alcuni test sono falliti!"
        return 1
    fi
    
    cd ..
    print_success "Testing completato!"
}

stage_build() {
    print_header "🐳 BUILDING DOCKER IMAGE"
    
    check_command docker
    
    # Variabili
    BUILD_TAG=$(date +%s)
    DOCKER_IMAGE="mmd/backend"
    
    echo "Buildando: ${DOCKER_IMAGE}:${BUILD_TAG}"
    
    if docker build -t "${DOCKER_IMAGE}:${BUILD_TAG}" -t "${DOCKER_IMAGE}:latest" .; then
        print_success "Docker image creato!"
        echo "Tag immagine: ${DOCKER_IMAGE}:${BUILD_TAG}"
        echo "Comandi utili:"
        echo "  docker run -p 8000:8000 ${DOCKER_IMAGE}:${BUILD_TAG}"
        echo "  docker images ${DOCKER_IMAGE}"
    else
        print_error "Docker build fallito!"
        return 1
    fi
}

stage_scan() {
    print_header "🔒 DOCKER SECURITY SCAN"
    
    check_command docker
    
    DOCKER_IMAGE="mmd/backend:latest"
    
    # Installa Trivy se non presente
    if ! command -v trivy &> /dev/null; then
        print_warning "Trivy non trovato. Installando..."
        # Installazione semplificata (per l'ambiente locale)
        echo "Per installare Trivy: https://github.com/aquasecurity/trivy#installation"
        return 0
    fi
    
    echo "Scansionando: ${DOCKER_IMAGE}"
    
    if trivy image "${DOCKER_IMAGE}"; then
        print_success "Scansione completata!"
    else
        print_warning "Vulnerabilità trovate! Rivedi il report sopra."
    fi
}

stage_clean() {
    print_header "🧹 CLEANUP"
    
    echo "Rimuovendo virtual environment..."
    rm -rf ${VENV_DIR}
    
    echo "Rimuovendo cache Python..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name ".coverage*" -delete
    
    echo "Rimuovendo htmlcov..."
    rm -rf htmlcov .coverage
    
    print_success "Cleanup completato!"
}

stage_all() {
    print_header "🚀 ESEGUENDO TUTTI GLI STEP"
    
    stage_setup || return 1
    stage_lint || true  # Non blocca su falso positivi
    stage_test || return 1
    stage_build || return 1
    
    print_header "✅ PIPELINE COMPLETATA CON SUCCESSO!"
    echo "Prossimi step:"
    echo "  • Testare l'immagine: docker run -p 8000:8000 mmd/backend:latest"
    echo "  • Pushare su registry: docker push mmd/backend:latest"
    echo "  • Deployare su production"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN LOGIC
# ═══════════════════════════════════════════════════════════════════

main() {
    STAGE="${1:-help}"
    
    case $STAGE in
        setup)
            stage_setup
            ;;
        lint)
            stage_lint
            ;;
        test)
            stage_test
            ;;
        build)
            stage_build
            ;;
        scan)
            stage_scan
            ;;
        clean)
            stage_clean
            ;;
        all)
            stage_all
            ;;
        help)
            stage_help
            ;;
        *)
            print_error "Stage sconosciuto: $STAGE"
            stage_help
            exit 1
            ;;
    esac
}

# Esegui main
main "$@"
