# Remediation Creator Next

Modernisierte Streamlit-App zum Erstellen, Prüfen und Publizieren von Microsoft Intune Detection- und Remediation-Skripten mit Azure OpenAI oder OpenAI.

![Tool UI](https://github.com/JayRHa/Remediation-Creator/blob/main/.pictures/tool.png)

## Was ist neu

- Modernes UI mit klarem Workflow: `Generate` -> `Review` -> `Publish`
- Sidebar-Control-Center für Modell- und Publish-Settings
- Szenario-Vorlagen (BitLocker, Disk Cleanup, Time Service, Local Admin Drift)
- Zusätzliche Requirement-Box für präzisere Script-Vorgaben
- Script-Validierung mit Checks für Exit-Codes und riskante Detection-Kommandos
- Snapshot-History inkl. Restore
- Download von `detection.ps1`, `remediation.ps1` und `payload.json`
- Upload-Payload-Preview vor dem Graph-Upload
- Graph Connect/Disconnect direkt aus der UI
- Community-Suche in `JayRHa/EndpointAnalyticsRemediationScripts` mit Treffer-Scoring und Direktlinks
- Modell-Presets für `GPT-5.3-Codex` und optional `GPT-5.3` (Stand: 5. Februar 2026)
- Provider-Auswahl: `Azure OpenAI` oder `OpenAI`

## Tech-Update (Stand: 18. Februar 2026)

- `streamlit==1.54.0`
- `azure-identity==1.25.2`
- `openai==2.21.0`
- `requests==2.32.5`

## Modell-Stand (verifiziert am 18. Februar 2026)

- Empfohlene Coding-Option: `gpt-5.3-codex`
- Optionale Alternative: `gpt-5.3` (nur wenn in deinem Provider/Tenant verfügbar)
- In Azure muss der Name als Deployment existieren (z. B. Deployment-Name `gpt-5.3-codex`).

## Voraussetzungen

- Python 3.10+
- Azure OpenAI Resource + Deployment oder OpenAI API Key
- App Registration mit passenden Graph-Rechten für Device Health Scripts

## Einrichtung

1. Repository klonen.
2. `.streamlit/secrets.toml.example` nach `.streamlit/secrets.toml` kopieren.
3. Secrets ausfüllen:

```toml
AZURE_OPENAI_KEY = "..."
AZURE_OPENAI_ENDPOINT = "https://YOUR-ENDPOINT.openai.azure.com"
AZURE_OPENAI_CHATGPT_DEPLOYMENT = "gpt-5.3-codex" # Azure deployment name
AZURE_OPENAI_API_VERSION = "2024-10-21"
OPENAI_API_KEY = "" # optional for provider OpenAI
OPENAI_MODEL = "gpt-5.3-codex"
APP_REGISTRATION_ID = "..."
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
```

## Start

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

oder mit dem Helper:

```bash
./run.sh
```

## Typischer Workflow

1. Modus und Parameter im Sidebar-Control-Center setzen.
2. Beschreibung (ggf. mit Template) erfassen.
3. Skripte generieren.
4. Im Review-Tab prüfen, validieren und bei Bedarf manuell anpassen.
5. Im Publish-Tab Payload prüfen und zu Graph hochladen.

## Community-Suche

- Im Tab `Generate` gibt es den Bereich **Find matching scripts from community repository**.
- Die Suche durchsucht das öffentliche Repo `JayRHa/EndpointAnalyticsRemediationScripts`.
- Optional kann ein GitHub Token gesetzt werden, um API-Limits zu erhöhen.

## Sicherheitshinweis

KI-generierte Skripte müssen vor produktivem Einsatz technisch und fachlich geprüft werden.

## Lizenz

Apache 2.0
