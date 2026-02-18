"""Search helpers for community remediation script repositories."""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field

import requests

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_OWNER = "JayRHa"
DEFAULT_REPO = "EndpointAnalyticsRemediationScripts"
DEFAULT_REF = "main"
REQUEST_TIMEOUT = 30


@dataclass(slots=True)
class CommunityProject:
    """Represents one top-level project folder in the community repository."""

    name: str
    folder: str
    files: list[str] = field(default_factory=list)
    detection_files: list[str] = field(default_factory=list)
    remediation_files: list[str] = field(default_factory=list)
    readme_file: str = ""

    def folder_url(self, owner: str = DEFAULT_OWNER, repo: str = DEFAULT_REPO, ref: str = DEFAULT_REF) -> str:
        encoded = urllib.parse.quote(self.folder, safe="/")
        return f"https://github.com/{owner}/{repo}/tree/{ref}/{encoded}"


@dataclass(slots=True)
class CommunityMatch:
    """Search result with relevance metadata."""

    project: CommunityProject
    score: float
    reasons: list[str]


def fetch_repo_tree(
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    ref: str = DEFAULT_REF,
    github_token: str = "",
) -> list[dict]:
    """Fetch recursive tree metadata from GitHub."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "remediation-creator-next",
    }
    if github_token.strip():
        headers["Authorization"] = f"Bearer {github_token.strip()}"

    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub API error ({response.status_code}): {response.text[:300]}")

    data = response.json()
    if "tree" not in data or not isinstance(data["tree"], list):
        raise RuntimeError("GitHub tree response was missing expected data.")

    return data["tree"]


def build_project_catalog(tree_items: list[dict]) -> list[CommunityProject]:
    """Group repository tree data by top-level folder projects."""
    projects: dict[str, CommunityProject] = {}

    for item in tree_items:
        path = item.get("path")
        item_type = item.get("type")
        if not isinstance(path, str) or item_type != "blob":
            continue

        parts = path.split("/", 1)
        if len(parts) < 2:
            continue

        folder = parts[0]
        lower_folder = folder.lower()
        if lower_folder.startswith("."):
            continue

        filename = path.split("/")[-1]
        lower_name = filename.lower()

        is_script = lower_name.endswith(".ps1")
        is_readme = lower_name in {"readme.md", "readme.mdown", "readme.txt", "readme.mkd", "readme.markdown", "readme"}

        if not is_script and not is_readme:
            continue

        project = projects.get(folder)
        if project is None:
            project = CommunityProject(name=folder, folder=folder)
            projects[folder] = project

        project.files.append(path)

        if is_script:
            if "detect" in lower_name or "detection" in lower_name:
                project.detection_files.append(path)
            if "remedi" in lower_name or "remediation" in lower_name:
                project.remediation_files.append(path)

        if is_readme and not project.readme_file:
            project.readme_file = path

    # keep only folders that actually contain scripts
    output = [project for project in projects.values() if any(file_path.lower().endswith(".ps1") for file_path in project.files)]
    output.sort(key=lambda item: item.name.lower())
    return output


def search_projects(query: str, catalog: list[CommunityProject], limit: int = 8) -> list[CommunityMatch]:
    """Return best matching projects for a user query."""
    clean_query = query.strip().lower()
    if not clean_query:
        return []

    query_tokens = [token for token in re.split(r"[^a-z0-9]+", clean_query) if token]
    if not query_tokens:
        return []

    matches: list[CommunityMatch] = []

    for project in catalog:
        name_lower = project.name.lower()
        all_text = " ".join(project.files).lower()

        score = 0.0
        reasons: list[str] = []

        for token in query_tokens:
            if token in name_lower:
                score += 3.0
                reasons.append(f"Folder match: {token}")
            if token in all_text:
                score += 1.5
                reasons.append(f"File match: {token}")

        if clean_query in name_lower:
            score += 4.0
            reasons.append("Exact folder phrase match")
        if clean_query in all_text:
            score += 2.0
            reasons.append("Exact file phrase match")

        if score > 0:
            coverage_bonus = min(len(project.detection_files), 1) + min(len(project.remediation_files), 1)
            score += float(coverage_bonus) * 0.5
            if coverage_bonus == 2:
                reasons.append("Has detection + remediation scripts")

            matches.append(
                CommunityMatch(
                    project=project,
                    score=round(score, 2),
                    reasons=_dedupe(reasons)[:5],
                )
            )

    matches.sort(key=lambda item: (item.score, len(item.project.files)), reverse=True)
    return matches[:limit]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
