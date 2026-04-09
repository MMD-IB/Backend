pipeline {
    agent any
    
    // ── Configurazione globali ──────────────────────────────────────
    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    
    // ── Parametri della pipeline ────────────────────────────────────
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Environment di destinazione'
        )
        booleanParam(
            name: 'DEPLOY_ENABLED',
            defaultValue: false,
            description: 'Abilita il deploy dopo il build'
        )
    }
    
    // ── Variabili d'ambiente ────────────────────────────────────────
    environment {
        // Docker Registry
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_REPOSITORY = 'mmd/backend'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${DOCKER_REPOSITORY}"
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // Python
        PYTHON_VERSION = '3.12'
        VENV_DIR = '.venv'
        
        // Progetto
        PROJECT_NAME = 'MMD-Backend'
        PROJECT_DIR = '/mmd'
        
        // Credenziali (da configurare in Jenkins)
        CREDENTIALS_ID_DOCKER = 'docker-registry-credentials'
        CREDENTIALS_ID_GIT = 'github-credentials'
    }
    
    stages {
        // ── STAGE 1: Checkout ──────────────────────────────────────
        stage('Checkout') {
            steps {
                script {
                    echo "📦 Clonando il repository..."
                    checkout scm
                    
                    // Mostra le info del commit
                    sh '''
                        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                        echo "Git Info:"
                        echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
                        echo "Commit: $(git rev-parse --short HEAD)"
                        echo "Author: $(git log -1 --pretty=format:'%an')"
                        echo "Message: $(git log -1 --pretty=format:'%s')"
                        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    '''
                }
            }
        }
        
        // ── STAGE 2: Setup Environment ─────────────────────────────
        stage('Setup Environment') {
            steps {
                script {
                    echo "⚙️  Configurando l'ambiente..."
                    sh '''
                        # Crea il virtual environment
                        python${PYTHON_VERSION} -m venv ${VENV_DIR}
                        
                        # Attiva il venv e installa le dipendenze
                        source ${VENV_DIR}/bin/activate || . ${VENV_DIR}/Scripts/activate
                        pip install --upgrade pip setuptools wheel
                        pip install -r requirements.txt
                        
                        # Mostra le versioni installate
                        pip --version
                        which python
                        python --version
                    '''
                }
            }
        }
        
        // ── STAGE 3: Code Quality & Linting ────────────────────────
        stage('Code Quality') {
            steps {
                script {
                    echo "🔍 Analizzando la qualità del codice..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            source ${VENV_DIR}/bin/activate || . ${VENV_DIR}/Scripts/activate
                            
                            # Installa gli strumenti di qualità
                            pip install flake8 black isort pylint --quiet
                            
                            # Esegui i controlli
                            echo "Running flake8..."
                            flake8 mmd/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
                            
                            echo "Running black check..."
                            black --check mmd/ || true
                            
                            echo "Running isort check..."
                            isort --check-only mmd/ || true
                        '''
                    }
                }
            }
        }
        
        // ── STAGE 4: Unit Tests ────────────────────────────────────
        stage('Test') {
            steps {
                script {
                    echo "🧪 Eseguendo i test unitari..."
                    sh '''
                        source ${VENV_DIR}/bin/activate || . ${VENV_DIR}/Scripts/activate
                        
                        # Configura Django
                        export PYTHONPATH=${PWD}:${PYTHONPATH}
                        export DJANGO_SETTINGS_MODULE=mmd.settings
                        
                        # Esegui pytest
                        cd mmd
                        pytest --version
                        pytest -v --tb=short --cov=. --cov-report=xml --cov-report=html || exit 1
                        cd ..
                    '''
                }
            }
            post {
                always {
                    // Pubblica i risultati dei test
                    junit 'mmd/test-results.xml'
                    
                    // Pubblica il coverage report
                    publishHTML([
                        reportDir: 'mmd/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Code Coverage Report',
                        keepAll: true
                    ])
                }
            }
        }
        
        // ── STAGE 5: Build Docker Image ────────────────────────────
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Buildando l'immagine Docker..."
                    sh '''
                        docker --version
                        
                        # Build dell'immagine
                        docker build \
                            -t ${DOCKER_IMAGE}:${DOCKER_TAG} \
                            -t ${DOCKER_IMAGE}:latest \
                            -f Dockerfile \
                            .
                        
                        # Mostra le informazioni dell'immagine
                        docker images ${DOCKER_IMAGE}
                    '''
                }
            }
        }
        
        // ── STAGE 6: Docker Security Scan ──────────────────────────
        stage('Docker Security Scan') {
            when {
                expression { env.ENVIRONMENT != 'development' }
            }
            steps {
                script {
                    echo "🔒 Scansionando l'immagine Docker per vulnerabilità..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            # Installa Trivy (se non presente)
                            if ! command -v trivy &> /dev/null; then
                                echo "Installando Trivy..."
                                wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - 
                                echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list 2>/dev/null
                                apt-get update && apt-get install -y trivy
                            fi
                            
                            # Scansiona l'immagine
                            trivy image ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                        '''
                    }
                }
            }
        }
        
        // ── STAGE 7: Push Docker Image to Registry ─────────────────
        stage('Push Docker Image') {
            when {
                expression { env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' }
            }
            steps {
                script {
                    echo "📤 Pushando l'immagine Docker al registry..."
                    withCredentials([usernamePassword(credentialsId: "${CREDENTIALS_ID_DOCKER}", usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
                            echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
                            
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                            docker push ${DOCKER_IMAGE}:latest
                            
                            docker logout
                        '''
                    }
                }
            }
        }
        
        // ── STAGE 8: Generate Reports ──────────────────────────────
        stage('Generate Reports') {
            steps {
                script {
                    echo "📊 Generando i report..."
                    sh '''
                        echo "Build Summary Report" > build_summary.txt
                        echo "===================" >> build_summary.txt
                        echo "Project: ${PROJECT_NAME}" >> build_summary.txt
                        echo "Build Number: ${BUILD_NUMBER}" >> build_summary.txt
                        echo "Environment: ${ENVIRONMENT}" >> build_summary.txt
                        echo "Branch: $(git rev-parse --abbrev-ref HEAD)" >> build_summary.txt
                        echo "Commit: $(git rev-parse --short HEAD)" >> build_summary.txt
                        echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}" >> build_summary.txt
                        echo "Docker Image: ${DOCKER_IMAGE}:latest" >> build_summary.txt
                        echo "Build Time: $(date)" >> build_summary.txt
                    '''
                    
                    // Archivia i file generati
                    archiveArtifacts artifacts: 'build_summary.txt', allowEmptyArchive: true
                }
            }
        }
        
        // ── STAGE 9: Deploy (Opzionale) ─────────────────────────────
        stage('Deploy') {
            when {
                expression { params.DEPLOY_ENABLED && (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') }
            }
            steps {
                script {
                    echo "🚀 Deployando su ${ENVIRONMENT}..."
                    
                    // Esempio di deploy su Docker Compose
                    if (env.ENVIRONMENT == 'development') {
                        sh '''
                            echo "🔄 Stoppando i container precedenti..."
                            docker-compose down || true
                            
                            echo "🚀 Avviando i nuovi container..."
                            docker-compose up -d
                            
                            echo "⏳ Aspettando che i servizi si stabilizzino..."
                            sleep 10
                            
                            echo "✅ Verificando lo stato dei container..."
                            docker-compose ps
                        '''
                    } else if (env.ENVIRONMENT == 'staging' || env.ENVIRONMENT == 'production') {
                        sh '''
                            echo "📢 Deploy su ${ENVIRONMENT} richiede approvazione manuale"
                            echo "Implementare il deploy secondo la tua infrastruttura:"
                            echo "- Kubernetes: kubectl apply -f k8s-manifest.yaml"
                            echo "- Docker Swarm: docker service update"
                            echo "- Cloud Provider: AWS/Azure/GCP deployment"
                        '''
                    }
                }
            }
        }
        
        // ── STAGE 10: Health Check ─────────────────────────────────
        stage('Health Check') {
            when {
                expression { params.DEPLOY_ENABLED }
            }
            steps {
                script {
                    echo "🏥 Eseguendo health check..."
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        sh '''
                            # Aspetta che il server sia pronto
                            MAX_ATTEMPTS=30
                            ATTEMPT=0
                            
                            while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
                                if curl -f http://localhost:8000/health || curl -f http://localhost:8000/ping; then
                                    echo "✅ Server è online!"
                                    exit 0
                                fi
                                ATTEMPT=$((ATTEMPT + 1))
                                sleep 2
                            done
                            
                            echo "❌ Server non ha risposto dopo ${MAX_ATTEMPTS} tentativi"
                            exit 1
                        '''
                    }
                }
            }
        }
    }
    
    // ── Post Actions ────────────────────────────────────────────────
    post {
        always {
            script {
                echo "🧹 Pulendo l'ambiente..."
                sh '''
                    # Pulizia opzionale
                    rm -rf ${VENV_DIR} || true
                    docker system prune -f || true
                '''
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completata con successo!"
                // Puoi aggiungere notifiche (Slack, Email, etc.)
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline fallita!"
                // Puoi aggiungere notifiche (Slack, Email, etc.)
            }
        }
        
        unstable {
            script {
                echo "⚠️  Pipeline non stabile (warnings/test issues)"
                // Puoi aggiungere notifiche (Slack, Email, etc.)
            }
        }
        
        cleanup {
            // Log della fine della pipeline
            sh '''
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "Pipeline terminata"
                echo "Build: ${BUILD_NUMBER}"
                echo "Result: ${currentBuild.result}"
                echo "Duration: $((${currentBuild.durationString}))"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            '''
        }
    }
}
