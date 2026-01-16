
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
| Backend              | Linguaggio a scelta del gruppo (es. Python, Node.js, Java) |
| Database Relazionale | PostgreSQL                                                 |
| Database Documentale | MongoDB                                                    |
| Database Vettoriale  | Qualsiasi DB vettoriale con API REST                       |
| Message Broker       | RabbitMQ oppure Kafka                                      |
| Frontend             | Tecnologie simili a HTMX                                   |
| Contenerizzazione    | Docker / Docker Compose                                    |
| Test                 | Test automatizzati per backend e frontend                  |

---

## Architettura del Progetto

Il progetto sarà sviluppato secondo **microservizi**, suddivisi in:

1. **Backend**

   * API REST per gestione utenti, documenti e ricerca semantica
   * Connessione ai DB (PostgreSQL, MongoDB, DB Vettoriale)
2. **Database Relazionale**

   * PostgreSQL per la gestione dati strutturati (utenti, permessi)
3. **Database NoSQL**

   * MongoDB per salvare documenti e contenuti testuali
4. **Database Vettoriale**

   * Memorizzazione degli embedding vettoriali per la ricerca semantica
5. **Message Queue**

   * RabbitMQ o Kafka per notifiche asincrone tra microservizi
6. **Frontend**

   * Interfaccia web leggera, interattiva con approccio simile a HTMX
7. **Test**

   * Test automatici per garantire la qualità e stabilità dei servizi
8. **Contenerizzazione**

   * Tutti i servizi containerizzati con Docker per facilità di deploy

---

## Istruzioni per l’Installazione e Avvio

1. Clonare il repository:

```bash
git clone https://github.com/ORG/NOME-PROGETTO.git
cd NOME-PROGETTO
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

* Per avviare fastAPI : uvicorn app.main:app --reload --port 8001

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

