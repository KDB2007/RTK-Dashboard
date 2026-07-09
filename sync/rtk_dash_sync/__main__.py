import argparse
import json
import os
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx


def get_config_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / "rtk-dash"


def get_rtk_db_path() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/rtk/history.db"
    elif sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "")) / "rtk/history.db"
    else:
        return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "rtk/history.db"


def load_config() -> dict:
    config_dir = get_config_dir()
    config_file = config_dir / "config.json"
    if not config_file.exists():
        return {}
    return json.loads(config_file.read_text())


def save_config(cfg: dict):
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    config_file.write_text(json.dumps(cfg, indent=2))
    config_file.chmod(0o600)


def read_cursor() -> int:
    cursor_file = get_config_dir() / "cursor.txt"
    if cursor_file.exists():
        return int(cursor_file.read_text().strip())
    return 0


def write_cursor(cursor: int):
    cursor_file = get_config_dir() / "cursor.txt"
    cursor_file.parent.mkdir(parents=True, exist_ok=True)
    cursor_file.write_text(str(cursor))


def read_commands(db_path: Path, cursor: int, limit: int = 500):
    if not db_path.exists():
        print(f"RTK database not found at {db_path}")
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, original_cmd, rtk_cmd, input_tokens, output_tokens,
               saved_tokens, savings_pct, exec_time_ms, project_path, timestamp
        FROM commands
        WHERE id > ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (cursor, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cmd_init(api_url: str, api_key: str | None):
    if not api_url:
        api_url = input("Cloud API URL (e.g. https://rtk-dash.example.com): ").strip()
        api_url = api_url.rstrip("/")

    name = platform.node()
    os_name = f"{platform.system()} {platform.release()}"

    payload = {"name": name, "os": os_name, "rtk_version": "unknown"}
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"Registering machine '{name}' with {api_url}...")
    try:
        resp = httpx.post(f"{api_url}/agents/register", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        save_config({
            "api_url": api_url,
            "api_key": data["api_key"],
            "agent_id": data["agent_id"],
            "machine_name": name,
        })
        print(f"Registered! Agent ID: {data['agent_id']}")
        print(f"API Key: {data['api_key']}")
        print("Save this key — it won't be shown again.")
    except httpx.HTTPStatusError as e:
        print(f"Registration failed: {e.response.status_code} {e.response.text}")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


def cmd_sync(watch: bool = False):
    cfg = load_config()
    if not cfg.get("api_key"):
        print("Not configured. Run 'rtk-dash-sync init' first.")
        sys.exit(1)

    db_path = get_rtk_db_path()
    api_url = cfg["api_url"].rstrip("/")

    while True:
        cursor = read_cursor()
        commands = read_commands(db_path, cursor)
        if commands:
            total = 0
            while commands:
                batch = [
                    {
                        "original_cmd": c["original_cmd"],
                        "rtk_cmd": c["rtk_cmd"],
                        "input_tokens": c["input_tokens"],
                        "output_tokens": c["output_tokens"],
                        "saved_tokens": c["saved_tokens"],
                        "savings_pct": c["savings_pct"],
                        "exec_time_ms": c["exec_time_ms"],
                        "project_path": c["project_path"] or "",
                        "ran_at": c["timestamp"],
                    }
                    for c in commands
                ]

                try:
                    resp = httpx.post(
                        f"{api_url}/sync/batch",
                        json={"commands": batch},
                        headers={"Authorization": f"Bearer {cfg['api_key']}"},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    write_cursor(data["cursor"])
                    total += data["synced_count"]
                    print(f"Synced {data['synced_count']} commands (cursor: {data['cursor']})")
                except httpx.HTTPStatusError as e:
                    print(f"Sync failed: {e.response.status_code} {e.response.text}")
                    if not watch:
                        sys.exit(1)
                    break
                except httpx.RequestError as e:
                    print(f"Network error: {e}")
                    if not watch:
                        sys.exit(1)
                    break

                cursor = data["cursor"]
                commands = read_commands(db_path, cursor)

            print(f"Done. {total} commands synced.")

        if not watch:
            break
        import time
        time.sleep(15)


def cmd_status():
    cfg = load_config()
    if not cfg.get("api_key"):
        print("Not configured.")
        return

    db_path = get_rtk_db_path()
    cursor = read_cursor()

    conn = sqlite3.connect(str(db_path))
    total = conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM commands WHERE id > ?", (cursor,)).fetchone()[0]
    conn.close()

    print(f"API URL:     {cfg.get('api_url')}")
    print(f"Agent ID:    {cfg.get('agent_id')}")
    print(f"Machine:     {cfg.get('machine_name')}")
    print(f"Last cursor: {cursor}")
    print(f"Total cmds:  {total}")
    print(f"Pending:     {pending}")


def main():
    parser = argparse.ArgumentParser(description="RTK Dashboard Sync Agent")
    sub = parser.add_subparsers(dest="command")

    init_parser = sub.add_parser("init", help="Register this machine")
    init_parser.add_argument("--api-url", default="")
    init_parser.add_argument("--api-key", default="")

    sync_parser = sub.add_parser("sync", help="Sync pending commands")
    sync_parser.add_argument("--watch", "-w", action="store_true", help="Watch for new commands continuously")

    sub.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.api_url, args.api_key)
    elif args.command == "sync":
        cmd_sync(watch=args.watch)
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
