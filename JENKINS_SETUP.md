# 📋 Jenkinsfile Setup Guide

## 📌 Panoramica

Questo Jenkinsfile automatizza l'intera pipeline CI/CD del progetto MMD-Backend:

```
Checkout → Setup → Linting → Testing → Build Docker → Security Scan → Push → Deploy → Health Check
```

---

## 🔧 Prerequisiti

### Su Jenkins Server:
- **Jenkins** ≥ 2.400+
- **Docker Plugin** (`Docker` + `Docker Pipeline`)
- **Python** 3.12+
- **Git**
- **Docker** installato sulla macchina host

### Plug-in Jenkins consigliati:
```
☑️ Pipeline
☑️ Docker Pipeline
☑️ Docker API
☑️ Cobertura Plugin (per coverage reports)
☑️ junit (per test reports)
☑️ Email Extension Plugin (notification)
☑️ Slack Notification (opzionale)
```

---

## 🔐 Credenziali da Configurare

### 1. Credenziali Docker Registry

**Manage Jenkins → Manage Credentials → Add Credentials**

```
Kind: Username with password
Scope: Global
Username: <tuo_username_docker>
Password: <tuo_password_docker>
ID: docker-registry-credentials  ← IMPORTANTE: deve corrispondere al Jenkinsfile
```

### 2. Credenziali GitHub (Opzionale)

Per repository privati:

```
Kind: SSH Key / Username with password
Scope: Global
Username: <tuo_username_github>
Password: <tuo_token_github>
ID: github-credentials
```

---

## ⚙️ Configurazione Pipeline in Jenkins

### Step 1: Crea una Nuova Pipeline

1. **Jenkins Dashboard** → **New Item**
2. **Item name**: `MMD-Backend-Pipeline`
3. **Type**: `Pipeline`
4. Click **OK**

### Step 2: Configura la Pipeline

```
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/MMD-IB/Backend.git
Credentials: github-credentials (se repo privato)
Branch Specifier: */main
Script Path: Jenkinsfile  ← il file che abbiamo creato
```

### Step 3: Build Triggers (Opzionale)

Seleziona **Trigger builds when a change is pushed to GitHub**:

```
☑️ GitHub hook trigger for GITScm polling
(richiede webhook configurato su GitHub)
```

---

## 📊 Stages della Pipeline

### 🔹 Stage 1: **Checkout**
Clona il repository e mostra info sul commit.

### 🔹 Stage 2: **Setup Environment**
- Crea virtual environment Python
- Installa dipendenze da `requirements.txt`

### 🔹 Stage 3: **Code Quality**
- Esegue `flake8` (PEP8 compliance)
- Esegue `black` (code formatting)
- Esegue `isort` (import sorting)
- ⚠️ Non blocca la build (UNSTABLE se fallisce)

### 🔹 Stage 4: **Test**
- Esegue `pytest` con coverage
- Genera HTML coverage report
- **Blocca la build se i test falliscono**

### 🔹 Stage 5: **Build Docker Image**
- Builda l'immagine Docker con tag `${BUILD_NUMBER}` e `latest`

### 🔹 Stage 6: **Docker Security Scan**
- Scansiona con **Trivy** per CVE
- Eseguito solo su `staging` e `production`
- ⚠️ Non blocca la build (UNSTABLE se vulnerabilità alte)

### 🔹 Stage 7: **Push Docker Image**
- Eseguito solo su branch `main/master`
- Pushes con tag `latest` e numero di build

### 🔹 Stage 8: **Generate Reports**
- Archivia un summary della build

### 🔹 Stage 9: **Deploy** ✨
- **Opzionale**: attivare tramite parametro `DEPLOY_ENABLED = true`
- Su `development`: esegue `docker-compose up -d`
- Su `staging/production`: richiede approvazione manuale

### 🔹 Stage 10: **Health Check**
- Verifica che l'applicazione risponda su `http://localhost:8000`

---

## 🚀 Esecuzione della Pipeline

### Metodo 1: Build Manuale

1. Jenkins Dashboard → **MMD-Backend-Pipeline**
2. Click **Build with Parameters**
3. Configura i parametri:
   - **ENVIRONMENT**: `development` / `staging` / `production`
   - **DEPLOY_ENABLED**: `false` / `true` (per deployare)
4. Click **Build**

### Metodo 2: Webhook GitHub (Auto-triggered)

Configura webhook su GitHub:

```
GitHub Repo → Settings → Webhooks → Add webhook

Payload URL: http://<jenkins-server>:8080/github-webhook/
Content type: application/json
Events: Push events
Active: ✓
```

---

## 🛠️ Personalizzazione

### Cambiare Docker Registry

Nel Jenkinsfile, modifica:

```groovy
environment {
    DOCKER_REGISTRY = 'your-registry.azurecr.io'  // Azure Container Registry
    // oppure
    DOCKER_REGISTRY = 'gcr.io'  // Google Container Registry
    // oppure
    DOCKER_REGISTRY = '123456.dkr.ecr.us-east-1.amazonaws.com'  // AWS ECR
}
```

### Aggiungere Email Notifications

In **post** section, aggiungi:

```groovy
post {
    failure {
        emailext(
            subject: "❌ Pipeline Failure: ${env.JOB_NAME}",
            body: "Build #${env.BUILD_NUMBER} failed!\nCheck: ${env.BUILD_URL}",
            to: "team@example.com"
        )
    }
}
```

### Aggiungere Slack Notifications

Configura il plugin Slack in Jenkins, poi aggiungi:

```groovy
post {
    always {
        slackSend(
            channel: '#dev-notifications',
            message: "Build ${env.BUILD_NUMBER}: ${currentBuild.result}",
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger'
        )
    }
}
```

### Aggiungere Step Personalizzati

Esempio - SonarQube Code Analysis:

```groovy
stage('SonarQube Analysis') {
    steps {
        script {
            sh '''
                sonar-scanner \
                  -Dsonar.projectKey=mmd-backend \
                  -Dsonar.sources=mmd \
                  -Dsonar.host.url=http://sonarqube:9000 \
                  -Dsonar.login=${SONAR_TOKEN}
            '''
        }
    }
}
```

---

## 📝 Variabili di Ambiente Disponibili

Puoi usarle negli script:

```bash
${BUILD_NUMBER}          # Numero della build (es: 42)
${BUILD_ID}              # ID univoco della build
${JOB_NAME}              # Nome della job (es: MMD-Backend-Pipeline)
${WORKSPACE}             # Directory di lavoro
${BRANCH_NAME}           # Branch Git (es: main, develop)
${GIT_COMMIT}            # Hash del commit
${GIT_BRANCH}            # Branch completo (es: refs/heads/main)
${BUILD_URL}             # URL della build
${ENVIRONMENT}           # Parametro: development/staging/production
${DOCKER_IMAGE}          # docker.io/mmd/backend
${DOCKER_TAG}            # Numero della build
```

---

## ⚠️ Troubleshooting

### ❌ Errore: "docker: command not found"

```bash
# Assicurati che Docker sia installato su Jenkins agent
docker --version

# Se usi Jenkins in container, puoi usare Docker-in-Docker (DinD)
# O montare il socket Docker: -v /var/run/docker.sock:/var/run/docker.sock
```

### ❌ Test falliscono con Django

Aggiungi al Jenkinsfile:

```groovy
sh '''
    export PYTHONPATH=${PWD}:${PYTHONPATH}
    export DJANGO_SETTINGS_MODULE=mmd.settings
    export DEBUG=False
    # Crea il database di test
    python mmd/manage.py migrate --run-syncdb
    pytest
'''
```

### ❌ Credenziali non trovate

Verifica che l'ID delle credenziali corrisponda:

```groovy
// Nel Jenkinsfile
CREDENTIALS_ID_DOCKER = 'docker-registry-credentials'

// Deve corrispondere a Jenkins → Manage Credentials
// ID: docker-registry-credentials  ✓
```

### ❌ Health check non passa

Aggiungi un health endpoint in Django:

```python
# mmd/urls.py
from django.http import JsonResponse

urlpatterns = [
    # ...
    path('health/', lambda r: JsonResponse({'status': 'ok'})),
    path('ping/', lambda r: JsonResponse({'pong': True})),
]
```

---

## 📈 Monitoraggio

### Visualizza Log della Build

```
Jenkins Dashboard → MMD-Backend-Pipeline → Build #X → Console Output
```

### Visualizza Coverage Report

```
Build #X → Code Coverage Report
```

### Visualizza Report dei Test

```
Build #X → Test Result
```

---

## 🔄 Maintenance & Updates

### Aggiorna il Jenkinsfile

Il Jenkinsfile è sotto version control. Modifica e committa:

```bash
git add Jenkinsfile
git commit -m "chore: update Jenkinsfile with new stage"
git push origin main
```

Jenkins auto-rileverà i cambiamenti sulla prossima build.

### Versione della Pipeline

Aggiungi versione nel Jenkinsfile per tracking:

```groovy
def PIPELINE_VERSION = '1.0.0'

stage('Info') {
    steps {
        echo "Pipeline Version: ${PIPELINE_VERSION}"
    }
}
```

---

## ✅ Checklist di Setup Iniziale

- [ ] Jenkins Server installato e in esecuzione
- [ ] Plug-in necessari installati
- [ ] Credenziali Docker Registry configurate
- [ ] Credenziali GitHub configurate (se repo privato)
- [ ] Nuovo Job/Pipeline creato
- [ ] Repository URL configurato
- [ ] Script Path impostato a `Jenkinsfile`
- [ ] Primo test build eseguito manualmente
- [ ] Webhook GitHub configurato (opzionale)
- [ ] Email/Slack notifications configurate (opzionale)

---

## 🎯 Prossimi Passi

1. **Genera API Token** su Docker Hub o Registry
2. **Testa manualment** la prima build: `Build with Parameters`
3. **Monitora i log** per errori
4. **Personalizza gli step** secondo le tue esigenze
5. **Configura notifiche** per il tuo team
6. **Setup deployment** per `staging` e `production`

---

## 📚 Risorse

- [Jenkins Official Docs](https://www.jenkins.io/doc/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Plugin Docs](https://plugins.jenkins.io/docker-plugin/)
- [PyTest Django](https://pytest-django.readthedocs.io/)

---

**Domande?** Controlla i log della build o apri un issue nel repository! 🚀
