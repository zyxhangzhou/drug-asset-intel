"""`intel` command line: snapshot management and the app server."""

import argparse
import sys
from pathlib import Path

from sqlmodel import Session

from intel.config import load_settings
from intel.db import init_db, provenance_gaps, rw_engine


def cmd_init_db(db: Path) -> int:
    init_db(db)
    print(f"snapshot ready: {db}")
    return 0


def cmd_check_provenance(db: Path) -> int:
    with Session(rw_engine(db)) as session:
        gaps = provenance_gaps(session)
    for entity_type, entity_id, field in gaps:
        print(f"{entity_type}#{entity_id}.{field}: value has no supporting claim")
    print(f"{len(gaps)} provenance gap(s)")
    return 1 if gaps else 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run("intel.api:create_app", factory=True, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    settings = load_settings()
    parser = argparse.ArgumentParser(prog="intel")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init-db", "check-provenance"):
        p = sub.add_parser(name)
        p.add_argument("--db", type=Path, default=settings.db_path)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    match args.command:
        case "init-db":
            return cmd_init_db(args.db)
        case "check-provenance":
            return cmd_check_provenance(args.db)
        case "serve":
            return cmd_serve(args.host, args.port)
    return 2


if __name__ == "__main__":
    sys.exit(main())
