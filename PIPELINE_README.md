# 🚀 CI/CD Pipeline - MMD Backend

## 📋 Cosa è stato creato

Ho generato una **pipeline CI/CD completa** per il tuo progetto MMD usando **Jenkins**. Ecco cosa troverai:

### 📁 File Creati

```
Backend/
├── Jenkinsfile                  ← 🎯 Pipeline principale (10 stages)
├── JENKINS_SETUP.md             ← 📖 Guida completa di setup
├── .env.example                 ← 🔐 Template variabili d'ambiente
└── build.sh                     ← 🛠️  Script helper per esecuzione locale
```

---

## 🎯 Cosa fa la Pipeline?

### ✨ 10 Stages Automatici:

```
┌─────────────────────────────────────────────────────────────────┐
│                    JENKINS CI/CD PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│ 1️⃣  Checkout          → Clona il repo Git                       │
│ 2️⃣  Setup Env         → Crea venv + installa dipendenze         │
│ 3️⃣  Linting           → flake8, black, isort                    │
│ 4️⃣  Testing           → pytest + coverage report                │
│ 5️⃣  Docker Build      → Build immagine Docker                   │
│ 6️⃣  Security Scan    → Scansione CVE con Trivy                 │
│ 7️⃣  Push Image        → Push a Docker Registry                  │
│ 8️⃣  Generate Reports  → Archivio report build                   │
│ 9️⃣  Deploy            → Deploy con docker-compose (opzionale)   │
│ 🔟 Health Check      → Verifica l'app sia online                │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### 1️⃣ Setup Jenkins (5 min)

Leggi la **guida completa** qui:
```bash
cat JENKINS_SETUP.md
```

Quick steps:
1. Installa Jenkins + Docker plugin
2. Configura 2 credenziali (Docker + GitHub)
3. Crea nuovo Job → Pipeline from SCM
4. Punta al repo con questo `Jenkinsfile`

### 2️⃣ Esegui la Pipeline (Automatico)

```bash
# Opzione A: Web UI
Jenkins Dashboard → MMD-Backend-Pipeline → Build with Parameters

# Opzione B: Webhook (auto su push)
GitHub: Settings → Webhooks → http://jenkins:8080/github-webhook/
```

### 3️⃣ Oppure Testa Localmente (Development)

```bash
# Esegui gli step localmente senza Jenkins
./build.sh all

# Oppure step singoli:
./build.sh setup    # Setup venv
./build.sh lint     # Linting
./build.sh test     # Test
./build.sh build    # Docker build
```

---

## 📊 Visualizza i Risultati

| Cosa Controllare | Dove |
|------------------|------|
| **Log della build** | Jenkins → Build #X → Console Output |
| **Test Report** | Jenkins → Build #X → Test Result |
| **Coverage** | Jenkins → Build #X → Code Coverage Report |
| **Docker image** | `docker images mmd/backend` |
| **Build Summary** | Jenkins → Build #X → Artifacts → build_summary.txt |

---

## 🔧 Configurazione Richiesta

### 1. Variabili d'Ambiente

```bash
# Copia il template
cp .env.example .env

# Compila i valori:
nano .env
```

Key variables:
```
DEBUG=False
DB_NAME=mmd_db
DOCKER_REGISTRY=docker.io
```

### 2. Credenziali Jenkins

**Jenkins → Manage Credentials → Add**

```
✅ docker-registry-credentials (username + password Docker)
✅ github-credentials (token GitHub per repo privati)
```

### 3. Personalizazioni

Modifica il `Jenkinsfile` per le tue esigenze:

```groovy
// Change docker registry
DOCKER_REGISTRY = 'your-registry.azurecr.io'

// Add notifications
post {
    failure {
        emailext(to: 'team@example.com', ...)
    }
}

// Add more stages
stage('SonarQube') { ... }
```

---

## 📈 Parametri della Pipeline

Quando esegui la build, puoi scegliere:

```
ENVIRONMENT:
  • development  → Test su env locale
  • staging      → Pre-production
  • production   → Production

DEPLOY_ENABLED:
  • false  → Solo build (default)
  • true   → Build + Deploy
```

---

## 🐳 Output Docker

### Immagne Creata:
```
docker.io/mmd/backend:${BUILD_NUMBER}
docker.io/mmd/backend:latest
```

### Run Localmente:
```bash
docker run -d -p 8000:8000 \
  --name mmd-backend \
  --env-file .env \
  mmd/backend:latest
```

---

## 🧪 Test & Coverage

La pipeline esegue **pytest** e genera:

```
✓ Unit tests (pytest)
✓ Code coverage (HTML report)
✓ Coverage threshold check
```

Visualizza:
```bash
# Coverage report
open htmlcov/index.html

# Test output
grep -r "PASSED\|FAILED" .
```

---

## 🔒 Security

### Automated Checks:

1. **Linting** - Codice conforme PEP8
2. **Dependency Check** - Vulnerabilità Python
3. **Docker Scan** - CVE nell'immagine (Trivy)

### Esegui manualmente Security Scan:

```bash
./build.sh scan
```

---

## 🚢 Deploy

### Development:
```bash
# Automatico con docker-compose up
DEPLOY_ENABLED=true ENVIRONMENT=development
```

### Staging/Production:
```bash
# Richiede approvazione manuale
# Implementa il tuo deploy:
# - Kubernetes: kubectl apply -f k8s/
# - Docker Swarm: docker service update
# - Cloud: AWS/Azure deploy
```

---

## 🐛 Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| `docker: command not found` | Installa Docker o usa DinD |
| Test falliscono | Controlla `.env` + DB setup |
| Credenziali non trovate | Verifica ID credenziali in Jenkins |
| Health check fallisce | Aggiungi endpoint `/health` in Django |
| Coverage basso | Aggiungi test al progetto |

Vedi **JENKINS_SETUP.md** per troubleshooting dettagliato.

---

## 📚 File Principali

### `Jenkinsfile`
La pipeline vera e propria. 10 stages con:
- Checkout, Setup, Linting, Testing
- Docker build, Security scan, Push
- Deploy, Health checks

### `JENKINS_SETUP.md`
Guida **completa** con:
- Prerequisiti
- Setup Jenkins step-by-step
- Configurazione credenziali
- Customizzazioni avanzate
- Troubleshooting

### `build.sh`
Script helper per development. Esegui:

```bash
./build.sh setup    # Installa dipendenze
./build.sh test     # Esegui pytest
./build.sh build    # Build Docker
./build.sh all      # Tutti gli step
./build.sh help     # Mostra aiuto
```

### `.env.example`
Template per variabili di ambiente:

```bash
cp .env.example .env
# Modifica secondo il tuo ambiente
```

---

## 🎯 Prossimi Step

### ✅ Setup Immediato:
- [ ] Leggi `JENKINS_SETUP.md`
- [ ] Installa Jenkins + plugin
- [ ] Configura credenziali Docker/GitHub
- [ ] Crea nuovo Job Jenkins con questo repo
- [ ] Esegui primo build manuale

### ✅ Integrazione:
- [ ] Configura webhook GitHub
- [ ] Aggiungi email/Slack notifications
- [ ] Setup deploy per staging
- [ ] Setup deploy per production

### ✅ Ottimizzazioni:
- [ ] Aggiungi SonarQube coverage
- [ ] Aggiungi performance tests
- [ ] Configura backup database
- [ ] Setup monitoring logs

---

## 📞 Supporto

### Risorse:
- [Jenkins Docs](https://www.jenkins.io/doc/)
- [Jenkinsfile Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Plugin](https://plugins.jenkins.io/docker-plugin/)
- [PyTest](https://docs.pytest.org/)

### Comandi Utili:

```bash
# Verifica dipendenze
python --version
docker --version
docker-compose --version

# Test locale senza Jenkins
./build.sh all

# Build Docker manuale
docker build -t mmd/backend:v1.0 .

# Esegui container
docker-compose up -d
docker logs -f myyy_container
```

---

## 🎉 Sei Pronto!

La pipeline è **completa e pronta**. Hai tutto quello che serve:

✅ **Jenkinsfile** - Pipeline automatica  
✅ **Setup Guide** - Configurazione step-by-step  
✅ **Build Script** - Per testing locale  
✅ **Env Template** - Variabili d'ambiente  

Prossimo passo: **Leggi JENKINS_SETUP.md e configura Jenkins!** 🚀

---

**Domande?** Controlla i log dettagliati nella console Jenkins o apri un issue nel repo.

**Buon deploy!** 🎊
