"""Controlled vocabularies. Members are lowercase so the stored name equals the value."""

from enum import StrEnum


class Stage(StrEnum):
    preclinical = "preclinical"
    phase1 = "phase1"
    phase1_2 = "phase1_2"
    phase2 = "phase2"
    phase2_3 = "phase2_3"
    phase3 = "phase3"
    filed = "filed"
    approved = "approved"
    unknown = "unknown"


class Confidence(StrEnum):
    high = "high"
    medium_high = "medium_high"
    medium = "medium"
    low = "low"


class ClaimKind(StrEnum):
    fact = "fact"
    inference = "inference"


class ProducedBy(StrEnum):
    manual = "manual"
    api = "api"
    llm = "llm"


class CatalystType(StrEnum):
    data_readout = "data_readout"
    regulatory_filing = "regulatory_filing"
    regulatory_decision = "regulatory_decision"
    trial_start = "trial_start"
    other = "other"


class PreferenceDimension(StrEnum):
    therapeutic_area = "therapeutic_area"
    modality = "modality"


class SourceType(StrEnum):
    mnc_material = "mnc_material"
    sec_filing = "sec_filing"
    sec_xbrl = "sec_xbrl"
    ctgov = "ctgov"
    openfda = "openfda"
    fda_web = "fda_web"
    company_ir = "company_ir"
    press_release = "press_release"
    publication = "publication"
    market_data = "market_data"
    other = "other"
