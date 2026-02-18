# Remediation Creator Next

Modernisierte Streamlit-App zum Erstellen, Prüfen und Publizieren von Microsoft Intune Detection- und Remediation-Skripten mit Azure OpenAI.

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

## Tech-Update (Stand: 18. Februar 2026)

- `streamlit==1.54.0`
- `azure-identity==1.25.2`
- `openai==2.21.0`
- `requests==2.32.5`

## Voraussetzungen

- Python 3.10+
- Azure OpenAI Resource + Deployment
- App Registration mit passenden Graph-Rechten für Device Health Scripts

## Einrichtung

1. Repository klonen.
2. `.streamlit/secrets.toml.example` nach `.streamlit/secrets.toml` kopieren.
3. Secrets ausfüllen:

```toml
AZURE_OPENAI_KEY = "..."
AZURE_OPENAI_ENDPOINT = "https://YOUR-ENDPOINT.openai.azure.com"
AZURE_OPENAI_CHATGPT_DEPLOYMENT = "gpt-4.1-mini"
AZURE_OPENAI_API_VERSION = "2024-10-21"
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

## Sicherheitshinweis

KI-generierte Skripte müssen vor produktivem Einsatz technisch und fachlich geprüft werden.

## Lizenz

Apache 2.0
