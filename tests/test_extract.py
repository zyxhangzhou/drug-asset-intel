import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from intel.docs.documents import Document
from intel.docs.index import ChunkIndex
from intel.docs.text import normalize
from intel.enums import SourceType
from intel.extract import review
from intel.extract.client import Endpoint, LlmClient
from intel.extract.ledger import Ledger, LlmConfig, PeakRefused
from intel.extract.run import Extractor
from intel.extract.tasks import SYSTEM_PROMPT, TASKS, user_prompt
from intel.extract.validate import check_item

ROOT = Path(__file__).resolve().parents[1]
CFG = LlmConfig.load(ROOT / "config" / "llm.toml")
OFFPEAK = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)  # Wednesday 20:00 Beijing
PEAK = datetime(2026, 11, 4, 2, 0, tzinfo=UTC)

DOC_TEXT = (
    "Viking Therapeutics Announces Topline Results\n"
    "VK2735 is a dual agonist of the GLP-1 and GIP receptors.\n"
    "The VENTURE study (NCT05000000) met its primary endpoint, with mean weight loss of up to "
    "14.7% from baseline at week 13 compared with 1.7% for placebo (p<0.0001).\n"
    "Viking expects to initiate a Phase 3 program in the second half of 2027.\n"
)
DOC_NORM = normalize(DOC_TEXT)
Q_CATALYST = "expects to initiate a Phase 3 program in the second half of 2027"
Q_MOA = "VK2735 is a dual agonist of the GLP-1 and GIP receptors"
Q_RESULT = (
    "met its primary endpoint, with mean weight loss of up to 14.7% from baseline at week 13 "
    "compared with 1.7% for placebo (p<0.0001)"
)


# --- tasks & validation ---------------------------------------------------------------


def test_every_task_requires_quotes_and_forbids_guessing():
    assert "verbatim" in SYSTEM_PROMPT and "Do not guess" in SYSTEM_PROMPT
    for task in TASKS.values():
        prompt = user_prompt(task, "VKTX", ["VK2735"], [])
        assert '"quotes"' in prompt and "VK2735" in prompt


def result_item(**kw) -> dict:
    base = {"asset": "VK2735", "trial": "NCT05000000", "indication": "obesity",
            "endpoint": "mean weight loss from baseline at week 13",
            "result": "up to 14.7% vs 1.7%",
            "analysis": "p<0.0001", "comparator": "placebo", "advantage_vs_soc": "",
            "quotes": [Q_RESULT]}  # fmt: skip
    return base | kw


def test_reformatted_quote_accepted():
    quote = Q_RESULT.replace("14.7% from", "14.7%\n from").replace("met its", "met  its")
    item, reason = check_item(TASKS["clinical_result"], result_item(quotes=[quote]), DOC_NORM)
    assert reason is None and item.spans[0][0] >= 0


def test_curly_quotes_and_dashes_match():
    doc = normalize("The drug “VK-2735” reduced weight — strongly in all arms")
    raw = {"asset": "VK2735", "mechanism": "reduced weight", "modality": "",
           "quotes": ['The drug "VK‑2735" reduced weight - strongly']}  # fmt: skip
    assert check_item(TASKS["program"], raw, doc)[1] is None


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"quotes": ["met its primary endpoint with a 20% weight loss at week 13"]},
         "quote_not_in_text"),
        ({"result": "up to 42% vs 1.7%"}, "number_not_in_quote:result=42"),
        ({"quotes": ["p<0.0001"]}, "quote_too_short"),
        ({"quotes": []}, "no_quote"),
        ({"endpoint": ""}, "missing_field:endpoint"),
        ({"advantage_vs_soc": "better than semaglutide"}, "advantage_without_confidence"),
    ],
)  # fmt: skip
def test_rejections(change, reason):
    assert check_item(TASKS["clinical_result"], result_item(**change), DOC_NORM) == (None, reason)


def test_catalyst_event_type_controlled():
    raw = {"asset": "VK2735", "event": "initiate a Phase 3 program", "event_type": "launch",
           "timing": "second half of 2027",
           "quotes": [Q_CATALYST]}  # fmt: skip
    assert check_item(TASKS["catalyst"], raw, DOC_NORM)[1] == "bad_event_type"
    raw["event_type"] = "trial_start"
    assert check_item(TASKS["catalyst"], raw, DOC_NORM)[1] is None


# --- end to end with mocked providers ---------------------------------------------------

PROGRAM = {"asset": "VK2735", "mechanism": "dual agonist of the GLP-1 and GIP receptors",
           "modality": "", "quotes": [Q_MOA]}  # fmt: skip
CATALYST = {"asset": "VK2735", "event": "initiate a Phase 3 program", "event_type": "trial_start",
            "timing": "second half of 2027",
            "quotes": [Q_CATALYST]}  # fmt: skip


def answers(primary: dict, verify: dict):
    """Route by host; pick the task from the prompt text."""
    sent = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        prompt = body["messages"][1]["content"]
        task = next(n for n, t in TASKS.items() if t.instruction in prompt)
        table = primary if "deepseek" in request.url.host else verify
        sent.append((request.url.host, task))
        return httpx.Response(
            200,
            json={
                "model": body["model"] + "-served",
                "choices": [
                    {
                        "message": {"content": json.dumps({"items": table.get(task, [])})},
                        "finish_reason": "stop",
                    }
                ],  # fmt: skip
                "usage": {"prompt_tokens": 500, "completion_tokens": 100},
            },
        )

    return httpx.Client(transport=httpx.MockTransport(handler)), sent


def setup(tmp_path, primary, verify, with_verify=True, now=OFFPEAK, dry_run=False):
    docs_dir = tmp_path / "docs"
    doc = Document(2, "VKTX", "https://www.sec.gov/x.htm", SourceType.press_release, "PR",
                   "2026-08-01", "DOC-VKTX-aaaa", None)  # fmt: skip
    doc.folder(docs_dir).mkdir(parents=True)
    doc.text_path(docs_dir).write_text(DOC_TEXT)
    doc.meta_path(docs_dir).write_text(json.dumps({"status": "ok", "text_sha256": "h"}))
    http, sent = answers(primary, verify)
    ledger = Ledger(tmp_path / "llm" / "ledger.jsonl")

    def client(ep):
        return LlmClient(ep, CFG, ledger, http, tmp_path / "llm" / "responses",
                         now=lambda: now, sleep=lambda s: None)  # fmt: skip

    p = client(Endpoint("primary", "https://api.deepseek.com", "deepseek-v4-pro", "k"))
    v = client(Endpoint("verify", "https://x.aliyuncs.com/v1", "qwen3.7-plus", "k"))
    ex = Extractor(p, v if with_verify else None, ChunkIndex(":memory:"), docs_dir,
                   tmp_path / "llm" / "validation.jsonl", dry_run=dry_run)  # fmt: skip
    (tmp_path / "llm").mkdir(exist_ok=True)
    return ex, doc, sent


def test_agreed_disputed_and_one_sided(tmp_path):
    primary = {"program": [PROGRAM], "clinical_result": [result_item()], "catalyst": [CATALYST]}
    verify = {
        "program": [PROGRAM | {"mechanism": "GLP-1/GIP dual agonist"}],  # same span -> agreed
        "clinical_result": [result_item(result="up to 14.7%")],  # numbers differ
        "catalyst": [],  # only primary found it
    }
    ex, doc, sent = setup(tmp_path, primary, verify)
    items = ex.run_document(doc, list(TASKS))
    by_type = {i.type: i for i in items}
    assert by_type["program"].check == "agreed" and by_type["program"].decision == "accept"
    assert by_type["clinical_result"].check == "disputed"
    assert by_type["clinical_result"].decision == ""
    assert by_type["clinical_result"].verify["result"] == "up to 14.7%"
    assert by_type["catalyst"].check == "disputed" and by_type["catalyst"].verify is None
    assert by_type["program"].returned_model == "deepseek-v4-pro-served"
    assert len(sent) == 6 and ex.summary.calls == 6


def test_verify_only_item_is_disputed(tmp_path):
    ex, doc, _ = setup(tmp_path, {}, {"catalyst": [CATALYST]})
    items = ex.run_document(doc, ["catalyst"])
    assert [(i.check, i.model) for i in items] == [("disputed", "qwen3.7-plus")]


def test_no_verify_model_marks_single(tmp_path):
    ex, doc, sent = setup(tmp_path, {"program": [PROGRAM]}, {}, with_verify=False)
    items = ex.run_document(doc, ["program"])
    assert [i.check for i in items] == ["single"] and items[0].decision == ""
    assert {h for h, _ in sent} == {"api.deepseek.com"}


def test_rejected_items_logged_not_returned(tmp_path):
    bad = result_item(result="up to 42%")
    ex, doc, _ = setup(tmp_path, {"clinical_result": [bad]}, {}, with_verify=False)
    assert ex.run_document(doc, ["clinical_result"]) == []
    log = [json.loads(x) for x in (tmp_path / "llm" / "validation.jsonl").read_text().splitlines()]
    assert log[0]["ok"] is False and log[0]["reason"].startswith("number_not_in_quote")
    assert ex.summary.rejected["number_not_in_quote"] == 1


def test_dry_run_sends_nothing(tmp_path):
    ex, doc, sent = setup(tmp_path, {}, {}, dry_run=True)
    assert ex.run_document(doc, list(TASKS)) == []
    assert sent == [] and ex.summary.estimate_cny > 0


def test_peak_hours_refused(tmp_path):
    ex, doc, sent = setup(tmp_path, {}, {}, now=PEAK)
    with pytest.raises(PeakRefused):
        ex.run_document(doc, ["program"])
    assert sent == []


# --- review file ----------------------------------------------------------------------


def test_review_file_prefill_and_rerun_keeps_decisions(tmp_path):
    primary = {"program": [PROGRAM], "catalyst": [CATALYST]}
    verify = {"program": [PROGRAM]}
    ex, doc, _ = setup(tmp_path, primary, verify)
    items = ex.run_document(doc, ["program", "catalyst"])
    path = tmp_path / "VKTX.toml"
    assert review.merge_write(path, "VKTX", items) == (2, 0)
    parsed = review.parse(path)
    assert parsed.verified_by == ""
    assert [i.decision for i in parsed.items] == ["accept", ""]
    assert parsed.items[0].quotes == PROGRAM["quotes"]

    text = path.read_text().replace('decision = "accept"', 'decision = "reject"', 1)
    path.write_text(text.replace('note = ""', 'note = "wrong drug"', 1))
    again = ex.run_document(doc, ["program", "catalyst"])
    assert [i.id for i in again] == [i.id for i in items]  # ids are stable
    assert review.merge_write(path, "VKTX", again) == (0, 2)
    kept = review.parse(path).items[0]
    assert (kept.decision, kept.note) == ("reject", "wrong drug")


def test_review_rejects_bad_decision(tmp_path):
    path = tmp_path / "X.toml"
    path.write_text('ticker = "X"\nverified_by = ""\n[[items]]\nid = "p-1"\ntype = "program"\n'
                    'source_id = "S"\ndecision = "maybe"\n')  # fmt: skip
    with pytest.raises(review.ExtractionReviewError, match="decision"):
        review.parse(path)


def test_report_counts_checks_cost_and_agreement(tmp_path):
    from intel.extract.report import report

    primary = {"program": [PROGRAM], "clinical_result": [result_item(result="up to 42%")]}
    ex, doc, _ = setup(tmp_path, primary, {"program": [PROGRAM]})
    items = ex.run_document(doc, ["program", "clinical_result"])
    review.merge_write(tmp_path / "ext" / "VKTX.toml", "VKTX", items)
    text = "\n".join(report(tmp_path / "llm", tmp_path / "ext"))
    assert "deepseek: 2 calls" in text and "qwen: 2 calls" in text
    assert "VKTX deepseek: 2 items, 1 kept; quote check 2/2 (100%); number check 1/2 (50%)" in text
    assert "rejection reasons: number_not_in_quote 1" in text
    assert "VKTX: agreed 1/1 (100%)" in text


def test_agreement_is_field_by_field():
    from intel.extract.run import agree

    task = TASKS["program"]
    quote = ["VK2735 is a dual agonist of the GLP-1 and GIP receptors"]
    a = check_item(task, PROGRAM | {"modality": ""}, DOC_NORM)[0]
    b = check_item(task, PROGRAM | {"mechanism": "GLP-1/GIP dual agonist"}, DOC_NORM)[0]
    c = check_item(task, PROGRAM | {"modality": "dual agonist", "quotes": quote}, DOC_NORM)[0]
    assert agree(a, b)  # same quote span, wording differs
    assert not agree(a, c)  # one side has a modality, the other none


def test_timing_without_year_rejected():
    raw = CATALYST | {"timing": "upcoming"}
    assert check_item(TASKS["catalyst"], raw, DOC_NORM)[1] == "timing_without_year"


def test_asset_code_digits_exempt_from_number_check():
    raw = result_item(result="VK2735 up to 14.7% vs 1.7%")
    assert check_item(TASKS["clinical_result"], raw, DOC_NORM)[1] is None


def test_differently_worded_endpoints_pair_by_passage(tmp_path):
    a = result_item(endpoint="mean weight loss from baseline at week 13")
    b = result_item(endpoint="Mean body weight reduction vs baseline (week 13)", trial="VENTURE")
    ex, doc, _ = setup(tmp_path, {"clinical_result": [a]}, {"clinical_result": [b]})
    items = ex.run_document(doc, ["clinical_result"])
    assert [i.check for i in items] == ["agreed"]


def test_program_without_values_rejected():
    raw = PROGRAM | {"mechanism": "", "modality": ""}
    assert check_item(TASKS["program"], raw, DOC_NORM)[1] == "no_value"
