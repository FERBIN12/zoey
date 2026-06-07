"""The workspace: the markdown files that *are* the agent's identity and memory.

This module knows how to find the workspace, scaffold it from the bundled
template, load the persona/rule files, and read/write memory. Everything is
plain text on disk — you can open and edit any of it by hand.
"""
from __future__ import annotations

import datetime as _dt
import shutil
from pathlib import Path

try:
    from importlib.resources import files as _res_files
except ImportError:  # pragma: no cover - very old pythons
    _res_files = None

# Files loaded into the system prompt every session, in this order.
CORE_FILES = ["IDENTITY.md", "SOUL.md", "AGENTS.md"]
PRIVATE_FILES = ["USER.md"]            # main session only
TEMPLATE_FILES = [
    "IDENTITY.md", "SOUL.md", "AGENTS.md", "USER.md",
    "TOOLS.md", "BOOTSTRAP.md", "HEARTBEAT.md",
]


def template_dir() -> Path:
    """Path to the bundled starter template shipped inside the package."""
    if _res_files is not None:
        return Path(str(_res_files("zoey") / "template"))
    return Path(__file__).parent / "template"


def read(ws: Path, name: str) -> str:
    p = ws / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def exists(ws: Path, name: str) -> bool:
    return (ws / name).exists()


def is_initialized(ws: Path) -> bool:
    return (ws / "SOUL.md").exists()


def init(ws: Path, force: bool = False) -> list[str]:
    """Scaffold a workspace from the template. Returns the files written."""
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "memory").mkdir(exist_ok=True)
    written = []
    src = template_dir()
    for name in TEMPLATE_FILES:
        dest = ws / name
        if dest.exists() and not force:
            continue
        sp = src / name
        if sp.exists():
            shutil.copyfile(sp, dest)
            written.append(name)
    return written


# ── memory ────────────────────────────────────────────────────────────────

def _today() -> str:
    return _dt.date.today().isoformat()


def daily_path(ws: Path, day: str | None = None) -> Path:
    return ws / "memory" / f"{day or _today()}.md"


def append_daily(ws: Path, role: str, text: str) -> None:
    """Append a line to today's raw log. This is the cheap, always-on layer."""
    (ws / "memory").mkdir(parents=True, exist_ok=True)
    p = daily_path(ws)
    stamp = _dt.datetime.now().strftime("%H:%M")
    header = "" if p.exists() else f"# {_today()}\n\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(f"{header}- **{stamp} {role}:** {text.strip()}\n")


def read_recent_daily(ws: Path, days: int) -> str:
    mem = ws / "memory"
    if not mem.exists():
        return ""
    today = _dt.date.today()
    chunks = []
    for i in range(days):
        d = (today - _dt.timedelta(days=i)).isoformat()
        p = mem / f"{d}.md"
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8").strip())
    return "\n\n".join(reversed(chunks))


def read_memory(ws: Path) -> str:
    return read(ws, "MEMORY.md")


def append_memory(ws: Path, fact: str) -> None:
    """Promote a durable fact into curated long-term memory."""
    p = ws / "MEMORY.md"
    if not p.exists():
        p.write_text("# MEMORY.md — curated long-term memory\n\n", encoding="utf-8")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"- {fact.strip()}\n")


def set_fields(ws: Path, name: str, fields: dict[str, str]) -> None:
    """Update `- **Key:** value` lines in a persona file (IDENTITY/USER)."""
    p = ws / name
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    for key, value in fields.items():
        needle = f"- **{key}:**"
        replaced = False
        for i, line in enumerate(lines):
            if line.strip().startswith(needle):
                lines[i] = f"- **{key}:** {value}"
                replaced = True
                break
        if not replaced:
            lines.append(f"- **{key}:** {value}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
