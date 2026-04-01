# Developed by Henrique Fernandes
# Auto-update system for Background Remover Studio
# Checks GitHub for new commits and downloads changed files on startup.

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

REPO   = "sabnck/background-remover-studio"
BRANCH = "main"
TIMEOUT_SHORT = 5   # segundos para checar o SHA remoto
TIMEOUT_DL    = 30  # segundos para baixar cada arquivo

ROOT_DIR = Path(__file__).resolve().parent.parent
SHA_FILE = Path(__file__).resolve().parent / ".last_commit"

# Arquivos que serão baixados/atualizados (caminhos relativos à raiz do repo)
TRACKED_FILES = [
    "src/background_remover.py",
    "src/main.py",
    "src/api_server.py",
    "src/setup_assistant.pyw",
    "src/updater.py",
    "src/webui/app.js",
    "src/webui/index.html",
    "src/webui/styles.css",
    "requirements.txt",
]


# ── Helpers GitHub API ─────────────────────────────────────────

def _api(url: str, timeout: int = TIMEOUT_SHORT) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "BackgroundRemoverStudio-Updater/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _get_remote_sha() -> str:
    data = _api(f"https://api.github.com/repos/{REPO}/commits/{BRANCH}")
    return data["sha"]


def _get_changed_files(local_sha: str, remote_sha: str) -> list[str]:
    data = _api(
        f"https://api.github.com/repos/{REPO}/compare/{local_sha}...{remote_sha}",
        timeout=TIMEOUT_SHORT,
    )
    return [
        f["filename"]
        for f in data.get("files", [])
        if f["status"] != "removed" and f["filename"] in TRACKED_FILES
    ]


def _download_file(repo_path: str) -> None:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{repo_path}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "BackgroundRemoverStudio-Updater/1.0"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_DL) as resp:
        content = resp.read()
    dest = ROOT_DIR / repo_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)


# ── SHA local ─────────────────────────────────────────────────

def _read_local_sha() -> str | None:
    # Prioridade 1: arquivo .last_commit salvo pelo updater
    if SHA_FILE.exists():
        sha = SHA_FILE.read_text().strip()
        if sha:
            return sha
    # Prioridade 2: git rev-parse HEAD (se o repo tem git)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True,
            cwd=str(ROOT_DIR), timeout=4,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _save_local_sha(sha: str) -> None:
    try:
        SHA_FILE.write_text(sha)
    except Exception:
        pass


# ── Restart ───────────────────────────────────────────────────

def _restart() -> None:
    """Relança o processo atual e encerra o atual."""
    try:
        subprocess.Popen(
            [sys.executable] + sys.argv,
            cwd=str(Path(__file__).parent),
        )
    except Exception:
        pass
    sys.exit(0)


# ── Diálogo de update ─────────────────────────────────────────

def _show_update_dialog(changed: list[str], remote_sha: str, parent=None) -> None:
    import tkinter as tk
    from tkinter import ttk

    # Cores do app
    BG    = "#0B0F14"
    CARD  = "#111827"
    CARD2 = "#161D28"
    BORDER_C = "#222B38"
    ACCENT = "#3994FF"
    TEXT   = "#F7F9FC"
    DIM    = "#9CA7B5"
    MUTED  = "#6E7888"
    SUCCESS = "#3DD68C"
    ERROR   = "#FF7F7F"

    result = {"update": False}

    dlg = tk.Toplevel(parent) if parent else tk.Tk()
    dlg.title("Update Available")
    dlg.configure(bg=BG)
    dlg.resizable(False, False)
    dlg.grab_set()

    # Centralizar
    dlg.update_idletasks()
    w, h = 420, 320
    sw = dlg.winfo_screenwidth()
    sh = dlg.winfo_screenheight()
    dlg.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # Header
    hdr = tk.Frame(dlg, bg=CARD, padx=20, pady=16)
    hdr.pack(fill="x")
    tk.Label(hdr, text="🔄  Update Available",
             font=("Segoe UI", 13, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
    tk.Label(hdr, text="A new version of Background Remover Studio is ready.",
             font=("Segoe UI", 9), bg=CARD, fg=DIM).pack(anchor="w", pady=(4, 0))

    # Lista de arquivos
    body = tk.Frame(dlg, bg=BG, padx=20, pady=14)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=f"{len(changed)} file(s) will be updated:",
             font=("Segoe UI", 9, "bold"), bg=BG, fg=TEXT).pack(anchor="w")

    box = tk.Frame(body, bg=CARD2, highlightthickness=1,
                   highlightbackground=BORDER_C, pady=8, padx=10)
    box.pack(fill="x", pady=(6, 0))
    for f in changed[:8]:
        tk.Label(box, text=f"  •  {f}", font=("Segoe UI", 8),
                 bg=CARD2, fg=DIM, anchor="w").pack(fill="x")
    if len(changed) > 8:
        tk.Label(box, text=f"  ... and {len(changed) - 8} more",
                 font=("Segoe UI", 8), bg=CARD2, fg=MUTED).pack(anchor="w")

    tk.Label(body, text="The app will restart automatically after updating.",
             font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(anchor="w", pady=(10, 0))

    # Progress bar (hidden initially)
    prog_frame = tk.Frame(body, bg=BG)
    prog_frame.pack(fill="x", pady=(8, 0))
    prog_var = tk.DoubleVar(value=0)
    prog_bar = ttk.Progressbar(prog_frame, variable=prog_var, maximum=len(changed),
                                length=370, mode="determinate")
    prog_lbl = tk.Label(prog_frame, text="", font=("Segoe UI", 8),
                        bg=BG, fg=DIM)
    # (packed only when update starts)

    # Botões
    btn_row = tk.Frame(dlg, bg=BG, padx=20, pady=14)
    btn_row.pack(fill="x", side="bottom")

    status_lbl = tk.Label(btn_row, text="", font=("Segoe UI", 8),
                          bg=BG, fg=DIM)
    status_lbl.pack(anchor="w", pady=(0, 8))

    def _do_update():
        btn_update.config(state="disabled")
        btn_skip.config(state="disabled")
        prog_bar.pack(fill="x")
        prog_lbl.pack(anchor="w", pady=(4, 0))

        def _worker():
            try:
                for i, f in enumerate(changed):
                    dlg.after(0, lambda n=f: prog_lbl.config(text=f"Downloading {n}…"))
                    _download_file(f)
                    dlg.after(0, lambda v=i+1: prog_var.set(v))
                _save_local_sha(remote_sha)
                dlg.after(0, lambda: (
                    status_lbl.config(text="✓ Updated! Restarting…", fg=SUCCESS),
                    dlg.after(900, lambda: (dlg.destroy(), _restart())),
                ))
            except Exception as exc:
                dlg.after(0, lambda e=exc: (
                    status_lbl.config(text=f"Error: {e}", fg=ERROR),
                    btn_update.config(state="normal"),
                    btn_skip.config(state="normal"),
                ))

        threading.Thread(target=_worker, daemon=True).start()

    def _do_skip():
        _save_local_sha(remote_sha)  # não perguntar de novo nesta versão
        dlg.destroy()

    btn_update = tk.Button(
        btn_row, text="Update Now", command=_do_update,
        bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
        relief="flat", padx=18, pady=8, cursor="hand2",
        activebackground="#5AA7FF", activeforeground="white",
    )
    btn_update.pack(side="right", padx=(8, 0))

    btn_skip = tk.Button(
        btn_row, text="Skip", command=_do_skip,
        bg=CARD2, fg=DIM, font=("Segoe UI", 10),
        relief="flat", padx=12, pady=8, cursor="hand2",
        activebackground=CARD, activeforeground=TEXT,
    )
    btn_skip.pack(side="right")

    if parent:
        dlg.wait_window()
    else:
        dlg.mainloop()


# ── Entry point ───────────────────────────────────────────────

def check_and_update(parent=None) -> None:
    """
    Verifica atualizações no GitHub e exibe diálogo se houver.
    Silencioso em caso de erro de rede ou qualquer exceção.
    Deve ser chamado no início do app, antes de criar a janela principal.
    """
    try:
        remote_sha = _get_remote_sha()
        local_sha  = _read_local_sha()

        if local_sha == remote_sha:
            _save_local_sha(remote_sha)
            return  # já está atualizado

        # Descobrir quais arquivos mudaram
        if local_sha:
            changed = _get_changed_files(local_sha, remote_sha)
        else:
            changed = list(TRACKED_FILES)  # SHA desconhecido → baixa tudo

        if not changed:
            _save_local_sha(remote_sha)
            return

        _show_update_dialog(changed, remote_sha, parent=parent)

    except Exception:
        pass  # sem internet, limite de API, etc. — ignora silenciosamente
