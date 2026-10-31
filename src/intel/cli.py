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


def cmd_check_scoring(db: Path) -> int:
    from intel.scoring import ScoringConfig, checks

    weights = ScoringConfig.load().weights
    with Session(rw_engine(db)) as session:
        recs = checks.primaries(session)
        unsupported = checks.unsupported_high_scores(session, recs)
        bias = checks.coverage_bias(checks.rank(recs, weights))
        moves = checks.sensitivity(recs, weights)
    for line in unsupported:
        print(f"unsupported: {line}")
    for line in bias:
        print(f"low coverage in top 10: {line}")
    for dim, delta, moved in moves:
        print(f"sensitivity: {dim} {delta:+.0%}: {moved} leave the top 20")
    print(
        f"{len(unsupported)} unsupported high score(s); {len(bias)} low-coverage top company(ies)"
    )
    return 1 if unsupported or bias else 0


BATCH_SOURCES = ("ctgov", "xbrl", "prices")
SINGLE_SOURCES = ("openfda", "labels", "docs")


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
            if what == "docs":
                return _fetch_docs(inputs, client, refresh, only)
            if what == "labels":
                from intel.ingest import openfda

                result = openfda.fetch_labels(inputs, fetch.Throttled(client), refresh)
                print(
                    f"labels: fetched {len(result.fetched)}, cached {len(result.skipped)}, "
                    f"failed {len(result.failed)}"
                )
                for number, reason in result.failed.items():
                    print(f"  failed {number}: {reason}")
                return 0
            return _fetch_batch(what, inputs, client, refresh, only)
    except fetch.MissingConfig as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _fetch_docs(inputs, client, refresh, only) -> int:
    from intel.docs.documents import read_documents
    from intel.docs.fetch import fetch_documents

    docs, errors = read_documents(inputs.documents)
    for line, reason in errors:
        print(f"  skipped {inputs.documents}:{line}: {reason}")
    docs = [d for d in docs if not only or d.ticker in only]
    result = fetch_documents(docs, client, load_settings(), inputs.docs_dir, refresh)
    print(
        f"docs: fetched {len(result.fetched)}, cached {len(result.skipped)}, "
        f"problems {len(result.failed)} (log: {inputs.docs_dir / 'fetch_log.jsonl'})"
    )
    for source_id, reason in result.failed.items():
        print(f"  {source_id}: {reason}")
    return 0


def cmd_filings(ticker: str, forms: list[str], limit: int) -> int:
    from intel import fetch
    from intel.docs.fetch import cik_for, list_filings
    from intel.ingest import Inputs

    try:
        cik = cik_for(ticker, Inputs().sec_tickers)
        with fetch.http_client() as client:
            filings = list_filings(cik, set(forms), client, load_settings(), limit)
    except (fetch.MissingConfig, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for f in filings:
        print(f"{f.filed} {f.form} {f.accession} {f.primary_url}")
        for ex in f.exhibits:
            print(f"    {ex.kind:<10} {ex.description[:50]:<50} {ex.url}")
    return 0


def _snapshot_programs(db: Path):
    import sqlite3

    def programs(ticker: str) -> list[str]:
        if not db.exists():
            return []
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as con:
            rows = con.execute(
                "SELECT p.name FROM program p JOIN target t ON t.id = p.target_id "
                "WHERE t.ticker = ? ORDER BY p.name",
                (ticker,),
            ).fetchall()
        return [r[0] for r in rows]

    return programs


def cmd_extract(args) -> int:
    from intel import fetch
    from intel.docs.documents import read_documents
    from intel.docs.index import ChunkIndex
    from intel.extract import review
    from intel.extract.client import LlmClient, LlmError, endpoints
    from intel.extract.ledger import BudgetExceeded, Ledger, LlmConfig, NoPrice, PeakRefused
    from intel.extract.run import Extractor
    from intel.extract.tasks import TASKS
    from intel.ingest import Inputs

    inputs = Inputs()
    if args.action == "report":
        from intel.extract.report import report

        print("\n".join(report(inputs.llm_dir, inputs.extractions_dir)))
        return 0
    settings = load_settings()
    primary_ep, verify_ep = endpoints(settings)
    if primary_ep is None:
        print("error: LLM_BASE_URL, LLM_MODEL and LLM_API_KEY must be set", file=sys.stderr)
        return 1
    if args.no_verify:
        verify_ep = None
    elif verify_ep is None:
        print("note: no cross-check model configured; every item will be marked single")
    tasks = args.tasks or list(TASKS)
    unknown = set(tasks) - set(TASKS)
    if unknown:
        print(f"error: unknown task(s) {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    docs, errors = read_documents(inputs.documents)
    for line, reason in errors:
        print(f"  skipped {inputs.documents}:{line}: {reason}")
    docs = [d for d in docs if (not args.only or d.ticker in args.only)
            and (not args.source or d.source_id in args.source)]  # fmt: skip
    cfg = LlmConfig.load(inputs.llm_config)
    ledger = Ledger(inputs.llm_dir / "ledger.jsonl")
    inputs.llm_dir.mkdir(parents=True, exist_ok=True)
    with fetch.http_client() as http:

        def client(ep):
            return LlmClient(ep, cfg, ledger, http, inputs.llm_dir / "responses",
                             allow_peak=args.allow_peak, replay=args.replay)  # fmt: skip

        index = ChunkIndex(inputs.docs_dir / "index.sqlite")
        extractor = Extractor(
            client(primary_ep),
            client(verify_ep) if verify_ep else None,
            index,
            inputs.docs_dir,
            inputs.llm_dir / "validation.jsonl",
            programs=_snapshot_programs(args.db),
            dry_run=args.dry_run,
        )
        status = 0
        for doc in docs:
            try:
                items = extractor.run_document(doc, tasks)
            except (BudgetExceeded, PeakRefused, NoPrice, LlmError) as exc:
                print(f"stopped at {doc.source_id}: {exc}", file=sys.stderr)
                status = 1
                break
            if items:
                path = inputs.extractions_dir / f"{doc.ticker}.toml"
                added, kept = review.merge_write(path, doc.ticker, items)
                print(f"{doc.source_id}: {added} new item(s), {kept} kept -> {path}")
        index.close()
    s = extractor.summary
    for line in s.skipped_docs:
        print(f"  skipped {line}")
    if args.dry_run:
        print(f"dry run: {len(docs)} document(s), worst-case cost {s.estimate_cny:.4f} CNY")
        return status
    print(
        f"calls {s.calls}, cost {s.cost_cny:.4f} CNY; items {dict(s.items)}; "
        f"rejected {dict(s.rejected)}"
    )
    return status


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
    for name in ("init-db", "check-provenance", "check-scoring", "build"):
        p = sub.add_parser(name)
        p.add_argument("--db", type=Path, default=settings.db_path)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("what", choices=["sec-tickers", "links", *SINGLE_SOURCES, *BATCH_SOURCES])
    fetch.add_argument("--refresh", action="store_true", help="re-fetch cached companies")
    fetch.add_argument("--only", type=lambda s: s.split(","), help="comma-separated tickers")
    docs = sub.add_parser("docs")
    docs_sub = docs.add_subparsers(dest="docs_command", required=True)
    filings = docs_sub.add_parser("filings", help="list recent EDGAR filings and exhibits")
    filings.add_argument("ticker")
    filings.add_argument("--forms", type=lambda s: s.split(","), default=["10-K", "10-Q", "8-K"])
    filings.add_argument("--limit", type=int, default=15)
    extract = sub.add_parser("extract", help="LLM extraction from listed documents")
    extract.add_argument("action", nargs="?", choices=["run", "report"], default="run")
    extract.add_argument("--only", type=lambda s: s.split(","), help="comma-separated tickers")
    extract.add_argument("--source", type=lambda s: s.split(","), help="source ids")
    extract.add_argument(
        "--tasks", type=lambda s: s.split(","), help="program,clinical_result,catalyst"
    )
    extract.add_argument("--no-verify", action="store_true", help="skip the cross-check model")
    extract.add_argument("--allow-peak", action="store_true", help="run in peak price hours")
    extract.add_argument("--dry-run", action="store_true", help="estimate cost, call nothing")
    extract.add_argument(
        "--replay", action="store_true", help="re-pair saved replies of the same prompts, no calls"
    )
    extract.add_argument("--db", type=Path, default=settings.db_path)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    match args.command:
        case "init-db":
            return cmd_init_db(args.db)
        case "check-provenance":
            return cmd_check_provenance(args.db)
        case "check-scoring":
            return cmd_check_scoring(args.db)
        case "build":
            return cmd_build(args.db)
        case "fetch":
            return cmd_fetch(args.what, args.refresh, args.only)
        case "docs":
            return cmd_filings(args.ticker, args.forms, args.limit)
        case "extract":
            return cmd_extract(args)
        case "serve":
            return cmd_serve(args.host, args.port)
    return 2


if __name__ == "__main__":
    sys.exit(main())
