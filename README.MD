
---

# Piattaforma Web per Gestione Documenti e Ricerca Semantica

## Descrizione del Progetto

Il progetto consiste in una **piattaforma web** per la gestione e ricerca di documenti testuali, con funzionalità principali:

* Upload e gestione di **documenti testuali**
* **Ricerca semantica** basata su embedding vettoriali
* **Gestione utenti** e permessi
* **Notifiche di sistema asincrone**
* Architettura basata su **microservizi**
* Sviluppo secondo le regole della **DevOps**

---

## Tecnologie Utilizzate

| Componente           | Tecnologia                                                 |
| -------------------- | ---------------------------------------------------------- |
| Backend              | Python                                                     |
| Database Relazionale | PostgreSQL                                                 |
| Database Documentale | MongoDB                                                    |
| Database Vettoriale  | Qualsiasi DB vettoriale con API REST                       |
| Message Broker       | RabbitMQ oppure Kafka                                      |
| Frontend             | Tecnologie simili a HTMX                                   |
| Contenerizzazione    | Docker / Docker Compose                                    |
| Test                 | Test automatizzati per backend e frontend                  |

---

## Architettura del Progetto

# Database Relazionale (PostgreSQL)

# **1) Tabelle principali**

**users**

| Campo         | Tipo      | Note                  |
| ------------- | --------- | --------------------- |
| id            | SERIAL PK | Identificatore utente |
| name          | VARCHAR   | Nome                  |
| surname       | VARCHAR   | Cognome               |
| email         | VARCHAR   | Email unica           |
| password_hash | VARCHAR   | Password hashed       |

**documents**

| Campo      | Tipo      | Note                                                    |
| ---------- | --------- | ------------------------------------------------------- |
| id         | SERIAL PK | Identificatore documento                                |
| id_user    | INT FK    | Riferimento a users.id                                  |
| title      | VARCHAR   | Titolo del documento                                    |
| status     | VARCHAR   | Stato del documento (`uploaded`, `processing`, `ready`) |
| created_at | TIMESTAMP | Data di creazione                                       |

> I documenti SQL contengono **solo i metadati principali**.

---

# **2) Database NoSQL (MongoDB)**

**documents_collection**

```json
{
  "_id": ObjectId("..."),
  "id_document": 1,                  // FK verso documents.id
  "content": "Testo completo del documento...",
  "metadata": {
    "uploaded_at": "2026-01-21T14:00:00",
    "tags": ["report", "finance"],
    "version": 1
  },
  "owner_id": 5                       // opzionale, ridondante con id_user
}
```

* Qui vengono salvati i **contenuti completi dei documenti**, eventuali versioni e metadata
* Facilita **ricerche full-text** e gestione documenti pesanti

---

# **3) DB Vettoriale (per embedding e ricerca semantica)**

**vector_embeddings_collection**

```json
{
  "id_document": 1,                  // FK verso SQL documents.id
  "vector": [0.12, 0.33, ..., 0.88], // embedding vettoriale
  "metadata": {
    "title": "Titolo documento",
    "owner_id": 5
  }
}
```

* Tutti i documenti caricati vengono trasformati in embedding vettoriali
* Serve per **ricerca semantica** tramite nearest neighbors
* Possibili tecnologie: **Pinecone, Milvus, Weaviate, Qdrant**

---

# **4) Microservizi**

| Servizio                   | Tecnologia                | DB/Altro             | Funzioni principali                                                 |
| -------------------------- | ------------------------- | -------------------- | ------------------------------------------------------------------- |
| **User Service**           | FastAPI / Django          | PostgreSQL           | CRUD utenti, login, autenticazione JWT, gestione ruoli              |
| **Document Service**       | FastAPI                   | PostgreSQL + MongoDB | Upload documenti, versioning, salvataggio testo, gestione status    |
| **Vector Service**         | FastAPI                   | DB vettoriale        | Indicizzazione embedding, ricerca semantica                         |
| **Notification Service**   | FastAPI + Celery          | PostgreSQL / Redis   | Notifiche asincrone (email, sistema interno)                        |
| **API Gateway / Frontend** | FastAPI + HTMX + Tailwind | —                    | Interfaccia web, orchestrazione microservizi, autenticazione        |
| **Message Broker**         | RabbitMQ/Kafka            | —                    | Comunicazione asincrona tra servizi (upload → embedding → notifica) |

---

# **5) Workflow dei documenti**

1. Utente carica un documento → **Document Service**
2. Document Service salva **metadati in SQL** (`documents`)
3. Salva **contenuto e metadata in MongoDB**
4. Invia messaggio a **Vector Service** tramite RabbitMQ/Kafka
5. Vector Service calcola embedding → salva in DB vettoriale
6. Notifica l’utente tramite **Notification Service** quando il documento è pronto
7. Utente può cercare semanticamente → API Gateway → Vector Service → restituisce risultati

---

# **6) Frontend (HTMX + Tailwind)**

* Pagine principali:

  * Login / Registrazione
  * Dashboard documenti
  * Upload documento + status
  * Ricerca semantica
  * Notifiche in tempo reale (polling o WebSocket)
* Interazioni dinamiche gestite da **HTMX** (fetching e aggiornamento parti della pagina senza ricaricare tutto)

---

# **7) Contenerizzazione & DevOps**

* **Docker** per ogni microservizio
* **Docker Compose** per sviluppo locale
* **CI/CD con GitHub Actions**:

  * Test unitari e integrazione
  * Build container
  * Deploy in ambiente dev/test/prod
* **Monitoraggio**: Prometheus + Grafana
* **Logging centralizzato**: ELK o semplici log su file

---

# **8) API principali**

### **User Service**

```http
POST /users/register
POST /users/login
```

### **Document Service**

```http
POST /documents/upload
GET /documents/:id
GET /documents/user/:user_id
PATCH /documents/:id/status
```

### **Vector Service**

```http
POST /search/semantic
```

### **Notification Service**

```http
GET /notifications/user/:user_id
POST /notifications/send
```

---

# **9) Test**

* **Unit test** per ogni microservizio
* **Integration test** SQL → MongoDB → Vector Service → notifiche
* **E2E test** simulando utente che carica documento e fa ricerca
* **Load test** per DB vettoriale e pipeline embedding

---

# **10) Riepilogo Architettura**

* SQL → metadati documenti e utenti
* MongoDB → contenuti documenti
* DB vettoriale → embedding e ricerca semantica
* Microservizi orchestrati via REST + Message Broker
* Frontend HTMX dinamico e reattivo
* DevOps: Docker, CI/CD, monitoraggio, logging

---

# **1) Requisiti Funzionali (FR)**

### **FR1 – Gestione utenti**

* FR1.1: Gli utenti devono potersi registrare tramite email e password.
* FR1.2: Gli utenti devono poter effettuare login e logout.
* FR1.3: Gli utenti possono visualizzare e aggiornare i propri dati (nome, cognome, email).
* FR1.4: Il sistema deve autenticare gli utenti tramite password hash e token JWT.

### **FR2 – Gestione documenti**

* FR2.1: Gli utenti possono caricare documenti testuali (.txt).
* FR2.2: Il sistema deve salvare i metadati in PostgreSQL (`id`, `id_user`, `title`, `status`, `created_at`).
* FR2.3: Il contenuto completo deve essere salvato in MongoDB, collegato a `id_document` SQL.
* FR2.4: Gli utenti possono visualizzare l’elenco dei propri documenti con status (`uploaded`, `processing`, `ready`).
* FR2.5: Gli utenti possono modificare o eliminare documenti prima della fase di processing.

### **FR3 – Ricerca semantica**

* FR3.1: Il sistema deve indicizzare i documenti tramite embeddings vettoriali.
* FR3.2: Gli utenti possono effettuare ricerche semantiche testuali e ottenere i documenti più rilevanti.
* FR3.3: Il sistema deve restituire risultati con titolo, estratto del contenuto e metadati.

### **FR4 – Notifiche**

* FR4.1: Il sistema deve inviare notifiche asincrone quando il documento è pronto per la ricerca.
* FR4.2: Le notifiche possono essere visualizzate nella dashboard degli utenti o via email.
* FR4.3: Il sistema deve gestire lo stato delle notifiche (`pending`, `sent`, `read`).

### **FR5 – API e microservizi**

* FR5.1: Ogni microservizio deve esporre API RESTful per le proprie funzionalità.
* FR5.2: I microservizi devono comunicare tramite **message broker** (RabbitMQ o Kafka).
* FR5.3: Il frontend deve poter interagire con i microservizi tramite API o API Gateway.

---

# **2) Requisiti Non Funzionali (NFR)**

### **NFR1 – Prestazioni**

* NFR1.1: Il sistema deve gestire almeno 1000 documenti caricati simultaneamente senza rallentamenti significativi.
* NFR1.2: La ricerca semantica deve restituire risultati entro 2 secondi per query standard.

### **NFR2 – Sicurezza**

* NFR2.1: Tutti i dati sensibili devono essere salvati criptati (password hash, eventuali token).
* NFR2.2: L’accesso ai documenti deve essere limitato al proprietario o agli utenti autorizzati.
* NFR2.3: Le comunicazioni tra microservizi devono essere sicure (HTTPS o rete interna protetta).

### **NFR3 – Scalabilità**

* NFR3.1: Il sistema deve essere facilmente scalabile, sia in verticale che in orizzontale.
* NFR3.2: Ogni microservizio deve poter essere eseguito in container separati (Docker/Kubernetes).

### **NFR4 – Affidabilità**

* NFR4.1: Il sistema deve gestire eventuali fallimenti dei microservizi senza perdere dati (message broker con queue persistente).
* NFR4.2: Devono esserci log centralizzati per monitorare errori e performance.

### **NFR5 – Usabilità**

* NFR5.1: L’interfaccia utente deve essere chiara, reattiva e accessibile da browser moderni.
* NFR5.2: Le operazioni di upload, ricerca e notifica devono essere intuitive.

---

# **3) Requisiti di Sistema**

* RS1: Linguaggi consigliati: Python (FastAPI/Django) per backend e microservizi.
* RS2: DBMS:

  * PostgreSQL per metadati utenti e documenti
  * MongoDB per contenuti documenti
  * DB vettoriale (Milvus / Pinecone / Weaviate) per ricerca semantica
* RS3: Message broker: RabbitMQ o Kafka per comunicazioni asincrone.
* RS4: Frontend: HTMX + Tailwind CSS + FastAPI template.
* RS5: Contenerizzazione: Docker + Docker Compose (sviluppo), Kubernetes (produzione).
* RS6: DevOps: CI/CD pipeline (GitHub Actions) per build, test e deploy.
* RS7: Logging e monitoraggio: Prometheus + Grafana o equivalente.

---

# **4) Requisiti opzionali / futuri**

* Possibilità di aggiungere **condivisione documenti tra utenti**.
* Implementazione di **versioning avanzato** dei documenti su MongoDB.
* Notifiche push in tempo reale (WebSocket) invece di polling.
* Supporto per **tipi di documenti più complessi** (PDF, DOCX, immagini).

Perfetto! 🚀 Ora facciamo la **parte di Test** per il tuo progetto, suddividendo in **unit test, integration test, E2E test e test di performance**, in modo da coprire tutti i microservizi, DB e frontend.

---

# **1) Unit Test**

**Scopo:** verificare singole funzioni o classi dei microservizi senza dipendere da altri sistemi esterni.

### **Cosa testare**

1. **User Service**

   * Registrazione utente → hash corretto della password, email valida
   * Login → restituisce token JWT corretto
   * Funzioni CRUD → get/update user

2. **Document Service**

   * Creazione documento → SQL `documents` aggiornato correttamente
   * Salvataggio contenuto in MongoDB → `id_document` corretto
   * Aggiornamento status (`uploaded`, `processing`, `ready`)

3. **Vector Service**

   * Generazione embedding → formato corretto, dimensione corretta
   * Salvataggio embedding → DB vettoriale popolato correttamente

4. **Notification Service**

   * Creazione notifica → stato iniziale `pending`
   * Invio notifica → stato aggiornato a `sent`

**Strumenti consigliati:**

* Python: `pytest` + `pytest-mock`
* Per MongoDB: `mongomock` per mock del DB
* Per DB SQL: `pytest-postgresql` o DB in-memory

---

# **2) Integration Test**

**Scopo:** verificare l’integrazione tra più componenti, ad esempio:

1. **User → Document Service**

   * Un utente crea un documento → verificare che SQL + MongoDB siano aggiornati

2. **Document Service → Vector Service**

   * Upload documento → messaggio inviato al broker → embedding salvato correttamente

3. **Notification**

   * Documento pronto → notifica inviata → stato aggiornato in PostgreSQL

**Strumenti consigliati:**

* Docker Compose con DB reali (PostgreSQL, MongoDB, broker) per test di integrazione
* `pytest` + `httpx` per chiamate REST interne

---

# **3) E2E (End-to-End) Test**

**Scopo:** simulare un flusso completo come farebbe un utente reale.

### **Flussi principali**

1. Registrazione utente → login → upload documento → verifica che:

   * Record SQL creato
   * Contenuto in MongoDB salvato
   * Embedding calcolato e salvato
   * Notifica inviata

2. Ricerca semantica → invio query → verifica che il risultato:

   * Restituisca documenti corretti
   * Rispetti ordine di rilevanza

**Strumenti consigliati:**

* Python: `pytest` + `httpx` / `requests`
* Browser automation (opzionale): `Selenium` o `Playwright` per test frontend HTMX

---

# **4) Test di performance / carico**

**Scopo:** verificare la scalabilità e le performance del sistema

1. **Document Upload Load Test**

   * Caricare N documenti simultaneamente → verificare tempi di risposta e DB Mongo/PostgreSQL

2. **Ricerca semantica**

   * Query simultanee su DB vettoriale → verificare tempi di risposta e correttezza

**Strumenti consigliati:**

* `locust` o `JMeter` per simulare utenti multipli
* Monitoraggio CPU, RAM, latenza DB

---

# **5) Test asincroni / message broker**

* Verificare che i messaggi inviati a RabbitMQ/Kafka:

  * Vengano consumati dai servizi corretti
  * Non vadano persi (durable queue)
  * Stato documenti e notifiche siano aggiornati

---

# **6) Test automatici e pipeline CI/CD**

* Ogni commit → **GitHub Actions**

  * Esegue unit test + integration test
  * Build container Docker
  * Eventuale deploy in staging

* Struttura suggerita:

```
/tests
  /unit
  /integration
  /e2e
```

* Esempio comando unico per eseguire tutti i test:

```bash
pytest --maxfail=1 --disable-warnings -v
```


---

## Istruzioni per l’Installazione e Avvio

1. Clonare il repository:

```bash
git clone https://github.com/MMD-IB/Backend.git
cd project
```

2. Configurare i microservizi e le connessioni ai database:

* Modificare gli IP dei database PostgreSQL e MongoDB nei file di configurazione, in quanto i DB sono salvati su un altro PC.

  > Nota: cambiando connessione o macchina, l’IP dei database potrebbe cambiare.

3. Avviare Docker Compose:

```bash
docker-compose up --build
```

4. Verificare che tutti i servizi siano attivi e in ascolto sulle porte corrette.

5. Accedere al frontend tramite browser:

```
http://localhost:PORT
```

---

## Nota Importante

* **IP dei database**: poiché PostgreSQL e MongoDB sono installati su un altro PC della rete, è necessario aggiornare **l’indirizzo IP nei file di configurazione** di ogni servizio.
* Se il computer dove risiedono i database cambia connessione, sarà necessario modificare nuovamente l’IP.

* Per avviare fastAPI : (myenv) C:\Users\UTENTE\Desktop\mmd\project\mmd>uvicorn fast.app.main:app --reload --host 0.0.0.0  --port
 8001

* Per avviare django: python manage.py runserver

---

## Struttura del Repository

```
project/
│
├─ backend/          # Codice dei microservizi backend
├─ frontend/         # Codice frontend
├─ db-postgres/      # Script e configurazioni PostgreSQL
├─ db-mongodb/       # Script e configurazioni MongoDB
├─ db-vector/        # Script e configurazioni DB vettoriale
├─ mq/               # Configurazioni RabbitMQ/Kafka
├─ tests/            # Test automatizzati
├─ docker-compose.yml
└─ README.md
```

---

## DevOps e Best Practices

* Tutti i microservizi containerizzati
* CI/CD consigliata per build e deploy automatico
* Logging e monitoraggio dei servizi
* Test automatizzati prima del deploy

---

