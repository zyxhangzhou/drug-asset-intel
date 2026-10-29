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


def cmd_build(db: Path) -> int:
    from intel.build import build_snapshot

    try:
        report = build_snapshot(db)
    except Exception as exc:  # report and keep the previous snapshot
        print(f"build failed, snapshot unchanged: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    for note in report.notes:
        print(f"note: {note}")
    summary = report.gap_summary()
    for reason, count in sorted(summary.items()):
        print(f"gap: {reason}: {count}")
    print(f"snapshot built: {db} ({len(report.gaps)} gap(s), see {db.with_name('gaps.csv')})")
    return 0


BATCH_SOURCES = ("ctgov", "xbrl", "prices")
SINGLE_SOURCES = ("openfda",)


def cmd_fetch(what: str, refresh: bool, only: list[str] | None) -> int:
    from intel import fetch
    from intel.ingest import Inputs

    inputs = Inputs()
    try:
        with fetch.http_client() as client:
            if what == "sec-tickers":
                print(f"saved: {fetch.fetch_sec_tickers(load_settings(), inputs, client)}")
                return 0
            if what == "links":
                print(f"saved: {fetch.fetch_links(inputs, client)}")
                return 0
            if what == "openfda":
                from intel.ingest import openfda

                print(f"saved: {openfda.fetch(inputs, fetch.Throttled(client))}")
                return 0
            return _fetch_batch(what, inputs, client, refresh, only)
    except fetch.MissingConfig as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _fetch_batch(what, inputs, client, refresh, only) -> int:
    from intel.fetch import CTGOV_DELAY, Throttled
    from intel.ingest import ctgov, financials
    from intel.ingest.pool import candidate_pool

    companies = [c for c in candidate_pool(inputs) if not only or c.ticker in only]
    match what:
        case "ctgov":
            result = ctgov.fetch(inputs, Throttled(client, delay=CTGOV_DELAY), companies, refresh)
        case "xbrl":
            result = financials.fetch_xbrl(
                inputs, Throttled(client), companies, load_settings(), refresh
            )
        case "prices":
            result = financials.fetch_prices(inputs, Throttled(client), companies, refresh)
    log = result.write_log(inputs.raw_dir / {"xbrl": "sec", "prices": "nasdaq"}.get(what, what))
    print(
        f"{what}: fetched {len(result.fetched)}, cached {len(result.skipped)}, "
        f"failed {len(result.failed)} (log: {log})"
    )
    for ticker, reason in result.failed.items():
        print(f"  failed {ticker}: {reason}")
    return 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run("intel.api:create_app", factory=True, host=host, port=port)
    return 0


def main(argv: list[str] | None = None) -> int:
    settings = load_settings()
    parser = argparse.ArgumentParser(prog="intel")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init-db", "check-provenance", "build"):
        p = sub.add_parser(name)
        p.add_argument("--db", type=Path, default=settings.db_path)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("what", choices=["sec-tickers", "links", *SINGLE_SOURCES, *BATCH_SOURCES])
    fetch.add_argument("--refresh", action="store_true", help="re-fetch cached companies")
    fetch.add_argument("--only", type=lambda s: s.split(","), help="comma-separated tickers")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    match args.command:
        case "init-db":
            return cmd_init_db(args.db)
        case "check-provenance":
            return cmd_check_provenance(args.db)
        case "build":
            return cmd_build(args.db)
        case "fetch":
            return cmd_fetch(args.what, args.refresh, args.only)
        case "serve":
            return cmd_serve(args.host, args.port)
    return 2


if __name__ == "__main__":
    sys.exit(main())
