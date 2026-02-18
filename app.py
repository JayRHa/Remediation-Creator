from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import streamlit as st
from azure.identity import InteractiveBrowserCredential

from modules.community_search import (
    DEFAULT_OWNER,
    DEFAULT_REF,
    DEFAULT_REPO,
    build_project_catalog,
    fetch_repo_tree,
    search_projects,
)
from modules.prompts import SCENARIO_TEMPLATES
from modules.utility import Utility, ValidationReport

st.set_page_config(
    page_title="Remediation Creator Next",
    page_icon="🛠️",
    layout="wide",
)


def _secret(name: str, default: str = "") -> str:
    return st.secrets[name] if name in st.secrets else default


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }

        .hero {
            background: linear-gradient(120deg, #0054d1 0%, #0f9b7a 100%);
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 14px 35px rgba(0, 84, 209, 0.22);
        }

        .hero p {
            margin: 0.25rem 0 0 0;
            opacity: 0.96;
        }

        .stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(0, 84, 209, 0.25);
            background: linear-gradient(120deg, #ffffff 0%, #f1f6ff 100%);
            font-weight: 600;
        }

        .stTextArea textarea, .stTextInput input {
            border-radius: 10px;
        }

        pre, code {
            font-family: 'IBM Plex Mono', monospace !important;
        }

        .stat-card {
            border: 1px solid rgba(15, 155, 122, 0.25);
            background: linear-gradient(180deg, #f3fffb 0%, #eff7ff 100%);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _default_state() -> dict[str, object]:
    return {
        "mode": "Detection and Remediation",
        "scope": "System",
        "description": "",
        "script_name": "WIN-NAMEOFYOURSCRIPT",
        "publisher": "Remediation Creator Next",
        "extra_requirements": "",
        "temperature": 0.2,
        "max_tokens": 1600,
        "run_as_32_bit": True,
        "enforce_signature_check": False,
        "detection_script": "",
        "remediation_script": "",
        "generated": False,
        "history": [],
        "graph_auth_header": {},
        "graph_scope": _secret("GRAPH_SCOPE", "https://graph.microsoft.com/.default"),
        "last_validation": None,
        "github_token": "",
        "community_query": "",
        "community_results": [],
        "community_error": "",
    }


def _init_state() -> None:
    for key, value in _default_state().items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_scripts() -> None:
    st.session_state.description = ""
    st.session_state.script_name = "WIN-NAMEOFYOURSCRIPT"
    st.session_state.extra_requirements = ""
    st.session_state.detection_script = ""
    st.session_state.remediation_script = ""
    st.session_state.generated = False
    st.session_state.last_validation = None


def _create_utility() -> tuple[Utility | None, list[str]]:
    required = ["AZURE_OPENAI_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_CHATGPT_DEPLOYMENT"]
    missing = [key for key in required if key not in st.secrets]
    if missing:
        return None, missing

    utility = Utility(
        azure_openai_key=st.secrets["AZURE_OPENAI_KEY"],
        azure_openai_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
        azure_openai_deployment=st.secrets["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
        azure_openai_api_version=_secret("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        graph_auth_header=st.session_state.graph_auth_header,
    )
    return utility, []


def _history_label(item: dict[str, str]) -> str:
    return f"{item['created_at']} | {item['mode']} | {item['fingerprint']}"


def _save_history(mode: str) -> None:
    if not st.session_state.detection_script.strip():
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    key = hashlib.sha1(
        (st.session_state.detection_script + "\n--\n" + st.session_state.remediation_script).encode(
            "utf-8"
        )
    ).hexdigest()

    entry = {
        "id": key,
        "created_at": now,
        "mode": mode,
        "description": st.session_state.description.strip(),
        "detection_script": st.session_state.detection_script,
        "remediation_script": st.session_state.remediation_script,
        "fingerprint": key[:8],
    }

    st.session_state.history = [entry] + [
        item for item in st.session_state.history if item["id"] != entry["id"]
    ]
    st.session_state.history = st.session_state.history[:12]


def _render_validation(report: ValidationReport | None) -> None:
    if report is None:
        st.info("Noch keine Validierung ausgeführt.")
        return

    st.markdown(
        f"""
        <div class="stat-card">
            <strong>Validation Summary</strong><br>
            Errors: {len(report.errors)} | Warnings: {len(report.warnings)} | Infos: {len(report.infos)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    for err in report.errors:
        st.error(err)
    for warn in report.warnings:
        st.warning(warn)
    for info in report.infos:
        st.info(info)


def _build_graph_header(token: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


@st.cache_data(ttl=1800, show_spinner=False)
def _load_community_catalog(owner: str, repo: str, ref: str, github_token: str) -> list:
    tree = fetch_repo_tree(owner=owner, repo=repo, ref=ref, github_token=github_token)
    return build_project_catalog(tree)


_init_state()
_inject_styles()

utility, missing_secrets = _create_utility()

st.markdown(
    """
    <div class="hero">
      <h2 style="margin:0;">Remediation Creator Next</h2>
      <p>Generate, review, validate and publish Intune detection/remediation scripts with Azure OpenAI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Control Center")

    if missing_secrets:
        st.error(
            "Missing secrets: " + ", ".join(missing_secrets) + ". Please update .streamlit/secrets.toml"
        )

    st.subheader("Generation")
    st.session_state.mode = st.radio(
        "Mode",
        options=["Detection only", "Detection and Remediation"],
        index=1 if st.session_state.mode == "Detection and Remediation" else 0,
    )
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, float(st.session_state.temperature), 0.05)
    st.session_state.max_tokens = st.slider("Max tokens", 400, 4000, int(st.session_state.max_tokens), 100)

    st.subheader("Publish")
    st.session_state.scope = st.selectbox("Run as", options=["System", "User"], index=0 if st.session_state.scope == "System" else 1)
    st.session_state.run_as_32_bit = st.toggle("Run as 32-bit", value=bool(st.session_state.run_as_32_bit))
    st.session_state.enforce_signature_check = st.toggle(
        "Enforce signature check", value=bool(st.session_state.enforce_signature_check)
    )

    st.subheader("Graph Login")
    st.session_state.graph_scope = st.text_input("Scope", value=st.session_state.graph_scope)
    app_registration_id = _secret("APP_REGISTRATION_ID")

    c1, c2 = st.columns(2)
    if c1.button("Connect", use_container_width=True):
        if not app_registration_id:
            st.error("APP_REGISTRATION_ID is missing in secrets.")
        else:
            try:
                credential = InteractiveBrowserCredential(client_id=app_registration_id)
                token = credential.get_token(st.session_state.graph_scope).token
                st.session_state.graph_auth_header = _build_graph_header(token)
                st.success("Graph token acquired.")
            except Exception as exc:
                st.error(f"Graph authentication failed: {exc}")

    if c2.button("Disconnect", use_container_width=True):
        st.session_state.graph_auth_header = {}
        st.info("Graph token removed.")

    if "Authorization" in st.session_state.graph_auth_header:
        st.caption("Graph status: Connected")
    else:
        st.caption("Graph status: Not connected")

    st.subheader("Community Search")
    st.caption("Searches JayRHa/EndpointAnalyticsRemediationScripts via GitHub API.")
    st.session_state.github_token = st.text_input(
        "GitHub token (optional)",
        value=st.session_state.github_token,
        type="password",
        help="Optional: increases API rate limits for search.",
    )

col_a, col_b = st.columns([0.65, 0.35])

with col_a:
    tabs = st.tabs(["Generate", "Review", "Publish"])

    with tabs[0]:
        st.subheader("Describe your remediation scenario")

        template_names = [item["name"] for item in SCENARIO_TEMPLATES]
        selected_template_name = st.selectbox("Template starter", options=["Custom"] + template_names)

        if st.button("Insert template into description"):
            if selected_template_name != "Custom":
                selected_template = next(item for item in SCENARIO_TEMPLATES if item["name"] == selected_template_name)
                if st.session_state.description.strip():
                    st.session_state.description += "\n\n" + selected_template["description"]
                else:
                    st.session_state.description = selected_template["description"]

        st.session_state.description = st.text_area(
            "Description",
            value=st.session_state.description,
            height=220,
            placeholder="Explain what should be detected and how it should be remediated...",
        )

        st.session_state.extra_requirements = st.text_area(
            "Additional requirements (optional)",
            value=st.session_state.extra_requirements,
            height=120,
            placeholder="e.g. keep all actions idempotent, include event log output",
        )

        with st.expander("Find matching scripts from community repository"):
            st.session_state.community_query = st.text_input(
                "Search query",
                value=st.session_state.community_query,
                placeholder="e.g. bitlocker, teams, dns, browser cache",
            )
            c_search, c_use = st.columns([0.3, 0.7])
            if c_search.button("Search community projects", use_container_width=True):
                try:
                    catalog = _load_community_catalog(
                        owner=DEFAULT_OWNER,
                        repo=DEFAULT_REPO,
                        ref=DEFAULT_REF,
                        github_token=st.session_state.github_token,
                    )
                    st.session_state.community_results = search_projects(
                        query=st.session_state.community_query,
                        catalog=catalog,
                        limit=8,
                    )
                    st.session_state.community_error = ""
                except Exception as exc:
                    st.session_state.community_results = []
                    st.session_state.community_error = str(exc)

            if st.session_state.community_error:
                st.error(f"Community search failed: {st.session_state.community_error}")

            if st.session_state.community_results:
                for item in st.session_state.community_results:
                    project = item.project
                    st.markdown(f"**{project.name}**  \nScore: `{item.score}`")
                    st.markdown(
                        f"[Open project]({project.folder_url()})  "
                        f"| Detection scripts: `{len(project.detection_files)}`  "
                        f"| Remediation scripts: `{len(project.remediation_files)}`"
                    )
                    if item.reasons:
                        st.caption("Reasons: " + ", ".join(item.reasons))
                    if c_use.button(
                        f"Use project name in description: {project.name}",
                        key=f"use_{project.name}",
                        use_container_width=True,
                    ):
                        if st.session_state.description.strip():
                            st.session_state.description += (
                                "\n\nReference from community repo: " + project.name
                            )
                        else:
                            st.session_state.description = (
                                "Reference from community repo: " + project.name
                            )
            elif st.session_state.community_query.strip():
                st.info("No matching community projects found for the current query.")

        c_generate, c_clear = st.columns([0.25, 0.2])

        if c_generate.button("Generate scripts", use_container_width=True, type="primary"):
            if utility is None:
                st.error("OpenAI configuration missing. Check secrets.")
            elif not st.session_state.description.strip():
                st.error("Please enter a description first.")
            else:
                with st.spinner("Generating scripts..."):
                    try:
                        artifact = utility.generate(
                            description=st.session_state.description,
                            include_remediation=st.session_state.mode == "Detection and Remediation",
                            temperature=float(st.session_state.temperature),
                            max_tokens=int(st.session_state.max_tokens),
                            extra_requirements=st.session_state.extra_requirements,
                        )
                        st.session_state.detection_script = artifact.detection_script
                        st.session_state.remediation_script = artifact.remediation_script
                        st.session_state.generated = True
                        _save_history(artifact.mode)
                        st.session_state.last_validation = utility.validate_scripts(
                            detection_script=st.session_state.detection_script,
                            remediation_script=st.session_state.remediation_script,
                        )
                        st.success("Scripts generated and validated.")
                    except Exception as exc:
                        st.error(f"Generation failed: {exc}")

        if c_clear.button("Clear", use_container_width=True):
            _reset_scripts()

    with tabs[1]:
        st.subheader("Review and validate")

        st.session_state.detection_script = st.text_area(
            "Detection script",
            value=st.session_state.detection_script,
            height=280,
            placeholder="Detection script appears here...",
        )

        st.session_state.remediation_script = st.text_area(
            "Remediation script",
            value=st.session_state.remediation_script,
            height=280,
            placeholder="Remediation script appears here...",
        )

        c_validate, c_save = st.columns(2)
        if c_validate.button("Run validation", use_container_width=True):
            if utility is None:
                st.error("OpenAI configuration missing. Check secrets.")
            else:
                st.session_state.last_validation = utility.validate_scripts(
                    detection_script=st.session_state.detection_script,
                    remediation_script=st.session_state.remediation_script,
                )

        if c_save.button("Save snapshot", use_container_width=True):
            _save_history(st.session_state.mode)
            st.success("Snapshot saved to history.")

        _render_validation(st.session_state.last_validation)

        d_col, r_col = st.columns(2)
        d_col.download_button(
            label="Download detection.ps1",
            data=st.session_state.detection_script,
            file_name="detection.ps1",
            mime="text/plain",
            disabled=not bool(st.session_state.detection_script.strip()),
            use_container_width=True,
        )
        r_col.download_button(
            label="Download remediation.ps1",
            data=st.session_state.remediation_script,
            file_name="remediation.ps1",
            mime="text/plain",
            disabled=not bool(st.session_state.remediation_script.strip()),
            use_container_width=True,
        )

    with tabs[2]:
        st.subheader("Publish to Intune")

        st.session_state.script_name = st.text_input("Script name", value=st.session_state.script_name)
        st.session_state.publisher = st.text_input("Publisher", value=st.session_state.publisher)

        payload = None
        if utility is not None:
            try:
                payload = utility.build_upload_payload(
                    script_name=st.session_state.script_name,
                    description=st.session_state.description,
                    scope=st.session_state.scope,
                    detection_script=st.session_state.detection_script,
                    remediation_script=st.session_state.remediation_script,
                    run_as_32_bit=bool(st.session_state.run_as_32_bit),
                    enforce_signature_check=bool(st.session_state.enforce_signature_check),
                    publisher=st.session_state.publisher.strip() or "Remediation Creator Next",
                )
            except Exception as exc:
                st.warning(f"Payload preview unavailable: {exc}")

        if payload:
            st.code(utility.pretty_json(payload), language="json")
            st.download_button(
                label="Download payload.json",
                data=json.dumps(payload, indent=2),
                file_name="intune_device_health_script_payload.json",
                mime="application/json",
                use_container_width=True,
            )

            if st.button("Upload to Graph", type="primary", use_container_width=True):
                if utility is None:
                    st.error("OpenAI configuration missing. Check secrets.")
                elif "Authorization" not in st.session_state.graph_auth_header:
                    st.error("Authenticate to Graph in the sidebar first.")
                else:
                    try:
                        result = utility.upload_payload(payload)
                        st.success("Upload successful.")
                        st.json(result)
                    except Exception as exc:
                        st.error(f"Upload failed: {exc}")

with col_b:
    st.subheader("History")
    if st.session_state.history:
        labels = [_history_label(item) for item in st.session_state.history]
        selected = st.selectbox("Saved snapshots", options=labels)
        selected_item = st.session_state.history[labels.index(selected)]

        if st.button("Restore snapshot", use_container_width=True):
            st.session_state.description = selected_item["description"]
            st.session_state.detection_script = selected_item["detection_script"]
            st.session_state.remediation_script = selected_item["remediation_script"]
            st.session_state.generated = True
            st.success("Snapshot restored.")

        st.caption("Snapshot description")
        st.write(selected_item["description"] or "(empty)")
    else:
        st.info("No history yet. Generate a script to create snapshots.")

    st.subheader("Quick facts")
    st.markdown(
        f"""
        <div class="stat-card">
          Active mode: <strong>{st.session_state.mode}</strong><br>
          Scope: <strong>{st.session_state.scope}</strong><br>
          Detection chars: <strong>{len(st.session_state.detection_script)}</strong><br>
          Remediation chars: <strong>{len(st.session_state.remediation_script)}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
