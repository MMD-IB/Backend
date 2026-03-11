# ── STEP 1: immagine base ──────────────────────────────────────────
# Usiamo Python 3.12 slim (leggera, senza pacchetti inutili)
FROM python:3.12.7

# ── STEP 2: variabili d'ambiente ──────────────────────────────────
# PYTHONDONTWRITEBYTECODE: evita i file .pyc (inutili nel container)
# PYTHONUNBUFFERED: i log appaiono subito nel terminale senza buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── STEP 3: cartella di lavoro ────────────────────────────────────
# Tutto il codice del container vivrà in /app
WORKDIR /app

# ── STEP 4: dipendenze di sistema ─────────────────────────────────
# Servono per compilare psycopg2 (driver PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── STEP 5: installa le dipendenze Python ─────────────────────────
# Copiamo PRIMA solo requirements.txt per sfruttare la cache Docker:
# se il codice cambia ma requirements.txt no, questo step viene skippato
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ── STEP 6: copia il codice ───────────────────────────────────────
COPY . .

# ── STEP 7: porta esposta ─────────────────────────────────────────
# Django di default gira sulla 8000
EXPOSE 8000

# ── STEP 8: comando di avvio ──────────────────────────────────────
# In sviluppo usiamo il server built-in di Django
# 0.0.0.0 è necessario per essere raggiungibile fuori dal container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]