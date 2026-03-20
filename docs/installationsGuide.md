# Installations-Guide

## 1. Projektverzeichnis öffnen

Wechsle im Terminal in das Projektverzeichnis:

```bash
cd src
```

---

## 2. Virtuelle Umgebung erstellen

```bash
python -m venv .venv
```

---

## 3. Virtuelle Umgebung aktivieren

### Windows (PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Backend vorbereiten

In den Backend-Ordner wechseln:

```bash
cd backend
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

---

## 5. Standard-Nutzer anlegen

```bash
python seed_users.py
```

---

## 6. Backend starten

```bash
uvicorn app.main:app --reload
```

Das Backend ist nun unter `http://127.0.0.1:8000` erreichbar.

---

## 7. Testdaten erzeugen

Um Testdaten (z. B. Nutzer und Aktivitäten) anzulegen, gehe wie folgt vor:

### 7.1 Zweites Terminal öffnen

Öffne ein neues Terminal und führe die folgenden Schritte aus:

```bash
cd src
```

Virtuelle Umgebung aktivieren:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

---

### 7.2 Testnutzer erstellen

Falls noch nicht geschehen, erstelle die Standard-Nutzer:

```bash
python seed_users.py
```

---

### 7.3 API-Dokumentation öffnen

Öffne im Browser die API-Oberfläche:

```text
http://localhost:8000/docs
```

---

### 7.4 Anmeldung durchführen

1. Klicke auf den **„Authorize“**-Button (Schloss-Symbol)
2. Melde dich mit folgenden Zugangsdaten an:

```
Benutzername: Anbieter123@example.com
Passwort: string
```

---

### 7.5 Testaktivitäten erzeugen

Nach erfolgreicher Anmeldung kannst du im Terminal folgenden Befehl ausführen:

```bash
python seed_activities.py
```

Damit werden Beispiel-Aktivitäten in der Datenbank angelegt.

---

### Ergebnis

Nach Abschluss dieses Schrittes stehen dir:

* Testnutzer
* Beispiel-Aktivitäten

für die weitere Nutzung und Entwicklung zur Verfügung.

---

## 8. Frontend starten

In den Frontend-Ordner wechseln:

```bash
cd frontend
```

Abhängigkeiten installieren:

```bash
npm install
npm install leaflet
```

Frontend starten:

```bash
npm run dev
```

---

## 9. Anwendung im Browser öffnen

```text
http://localhost:5173
```

---

# Anwendung im Netzwerk verfügbar machen

## Frontend konfigurieren

Erstelle im Ordner `frontend` eine Datei namens:

```text
.env.local
```

Mit folgendem Inhalt:

```env
VITE_API_BASE_URL=http://<DEINE-IP>:8000
```

---

## Backend im Netzwerk starten

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Frontend builden und bereitstellen

```bash
npm run build
serve -s dist
```

Die Anwendung ist nun im Netzwerk erreichbar.

---

# Test-Nutzer

### Anbieter

* **E-Mail:** [Anbieter123@example.com](mailto:Anbieter123@example.com)
* **Passwort:** string

### Anwender

* Registrierung erfolgt direkt über die Anwendung

---

# Ergebnis

Nach erfolgreicher Installation:

* Backend läuft
* Frontend läuft
* Anwendung ist im Browser erreichbar
* Optional: Zugriff im lokalen Netzwerk möglich
