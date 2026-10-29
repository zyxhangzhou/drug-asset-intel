"""Domain and provenance tables.

Business values live in typed columns; their provenance lives in Claim rows that point at
(entity_type, entity_id, field). `BUSINESS_FIELDS` on each domain table names the columns
that must be backed by at least one claim whenever they hold a value.
"""

from datetime import date, datetime
from typing import ClassVar

from sqlmodel import Field, Relationship, SQLModel

from intel.enums import (
    CatalystType,
    ClaimKind,
    Confidence,
    ExclusionCategory,
    LinkStatus,
    PreferenceDimension,
    ProducedBy,
    SourceType,
    Stage,
)


class Source(SQLModel, table=True):
    source_id: str = Field(primary_key=True)
    url: str | None = None
    source_type: SourceType
    title: str | None = None
    publisher: str | None = None
    doc_kind: str | None = None
    note: str | None = None
    published_date: date | None = None
    published_date_text: str | None = None
    fetched_at: datetime
    local_path: str | None = None
    content_hash: str | None = None
    link_status: LinkStatus = LinkStatus.unchecked
    link_checked_at: datetime | None = None


class Claim(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    entity_type: str = Field(index=True)
    entity_id: str = Field(index=True)
    field: str
    value: str | None = None
    kind: ClaimKind
    confidence: Confidence | None = None
    source_id: str = Field(foreign_key="source.source_id", index=True)
    quote: str | None = None
    as_of: date | None = None
    produced_by: ProducedBy
    model: str | None = None
    note: str | None = None


class MethodNote(SQLModel, table=True):
    """Methodology notes shipped with the MNC material; documentation, not business data."""

    __tablename__ = "method_note"
    id: int | None = Field(default=None, primary_key=True)
    source_id: str = Field(foreign_key="source.source_id")
    item: str
    text: str


class SnapshotMeta(SQLModel, table=True):
    __tablename__ = "snapshot_meta"
    id: int = Field(default=1, primary_key=True)
    generated_at: datetime
    generator: str
    snapshot_date: date | None = None


class Buyer(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "financial_signals",
        "therapeutic_priorities",
        "modality_priorities",
        "deal_preference",
        "buy_rationale",
        "key_evidence",
    )
    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(unique=True)
    name: str
    name_zh: str | None = None
    financial_signals: str | None = None
    therapeutic_priorities: str | None = None
    modality_priorities: str | None = None
    deal_preference: str | None = None
    buy_rationale: str | None = None
    key_evidence: str | None = None
    confidence: Confidence | None = None

    preferences: list["BuyerPreference"] = Relationship(back_populates="buyer")
    financials: list["BuyerFinancial"] = Relationship(back_populates="buyer")
    products: list["BuyerProductLoe"] = Relationship(back_populates="buyer")
    matches: list["Match"] = Relationship(back_populates="buyer")


class BuyerPreference(SQLModel, table=True):
    __tablename__ = "buyer_preference"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "label",
        "need_type",
        "target_profile",
        "evidence",
        "analysis",
        "ideal_stage",
        "deal_form",
    )
    id: int | None = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="buyer.id", index=True)
    dimension: PreferenceDimension
    rank: int
    label: str | None = None
    need_type: str | None = None
    target_profile: str | None = None
    evidence: str | None = None
    analysis: str | None = None
    ideal_stage: str | None = None
    deal_form: str | None = None
    confidence: Confidence | None = None

    buyer: Buyer = Relationship(back_populates="preferences")


class BuyerFinancial(SQLModel, table=True):
    """Buyer capacity row from the MNC overview sheet; amounts in billions, local currency."""

    __tablename__ = "buyer_financial"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "revenue_total",
        "revenue_us",
        "cash_and_short_term_investments",
        "total_debt",
        "net_debt",
        "free_cash_flow",
        "capital_allocation_note",
        "recent_deals",
        "focus_areas",
    )
    id: int | None = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="buyer.id", index=True)
    fiscal_year: str
    currency: str
    revenue_total: float | None = None
    revenue_us: float | None = None
    cash_and_short_term_investments: float | None = None
    total_debt: float | None = None
    net_debt: float | None = None
    free_cash_flow: float | None = None
    capital_allocation_note: str | None = None
    recent_deals: str | None = None
    focus_areas: str | None = None

    buyer: Buyer = Relationship(back_populates="financials")


class BuyerProductLoe(SQLModel, table=True):
    """A buyer product facing US loss of exclusivity; revenue in billions, local currency."""

    __tablename__ = "buyer_product_loe"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "revenue_global",
        "revenue_us",
        "us_loe",
        "generic_status",
        "defense",
        "basis_note",
    )
    id: int | None = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="buyer.id", index=True)
    product: str
    revenue_global: float | None = None
    revenue_us: float | None = None
    us_loe: str | None = None
    generic_status: str | None = None
    defense: str | None = None
    basis_note: str | None = None

    buyer: Buyer = Relationship(back_populates="products")


class Target(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = ("cik", "exclusion_reason", "selection_rationale")
    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(unique=True)
    name: str
    cik: str | None = None
    excluded: bool = False
    exclusion_category: ExclusionCategory | None = None
    exclusion_reason: str | None = None
    shortlisted: bool = False
    deep_dive: bool = False
    selection_rationale: str | None = None

    programs: list["Program"] = Relationship(back_populates="target")
    trials: list["Trial"] = Relationship(back_populates="target")
    approvals: list["ApprovedProduct"] = Relationship(back_populates="target")
    catalysts: list["Catalyst"] = Relationship(back_populates="target")
    financials: list["FinancialSnapshot"] = Relationship(back_populates="target")
    matches: list["Match"] = Relationship(back_populates="target")


class Program(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = ("mechanism", "modality")
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    name: str
    mechanism: str | None = None
    modality: str | None = None

    target: Target = Relationship(back_populates="programs")
    indications: list["ProgramIndication"] = Relationship(back_populates="program")


class ProgramIndication(SQLModel, table=True):
    __tablename__ = "program_indication"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = ("indication", "therapeutic_area", "stage")
    id: int | None = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="program.id", index=True)
    indication: str | None = None
    therapeutic_area: str | None = None
    stage: Stage = Stage.unknown

    program: Program = Relationship(back_populates="indications")
    trials: list["Trial"] = Relationship(back_populates="indication")


class Trial(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "title",
        "phase",
        "status",
        "design",
        "conditions",
        "interventions",
        "enrollment",
        "start_date",
        "primary_completion_date",
        "completion_date",
        "expected_readout",
    )
    id: int | None = Field(default=None, primary_key=True)
    nct_id: str = Field(unique=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    indication_id: int | None = Field(default=None, foreign_key="program_indication.id", index=True)
    title: str | None = None
    phase: Stage | None = None
    status: str | None = None
    design: str | None = None
    conditions: str | None = None
    interventions: str | None = None
    enrollment: int | None = None
    enrollment_type: str | None = None  # ESTIMATED / ACTUAL, as registered
    # Registry dates are kept as registered (YYYY-MM-DD or YYYY-MM); a month is never padded.
    start_date: str | None = None
    primary_completion_date: str | None = None
    primary_completion_type: str | None = None  # ESTIMATED / ACTUAL, as registered
    completion_date: str | None = None
    expected_readout: str | None = None

    target: Target = Relationship(back_populates="trials")
    indication: ProgramIndication | None = Relationship(back_populates="trials")
    results: list["TrialResult"] = Relationship(back_populates="trial")


class TrialResult(SQLModel, table=True):
    __tablename__ = "trial_result"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "endpoint",
        "result",
        "analysis",
        "comparator",
        "advantage_vs_soc",
    )
    id: int | None = Field(default=None, primary_key=True)
    trial_id: int = Field(foreign_key="trial.id", index=True)
    endpoint: str | None = None
    result: str | None = None
    analysis: str | None = None
    comparator: str | None = None
    advantage_vs_soc: str | None = None

    trial: Trial = Relationship(back_populates="results")


class Catalyst(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = ("event", "window_start", "window_end")
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    program_id: int | None = Field(default=None, foreign_key="program.id")
    event: str | None = None
    event_type: CatalystType = CatalystType.other
    window_start: date | None = None
    window_end: date | None = None

    target: Target = Relationship(back_populates="catalysts")


class FinancialSnapshot(SQLModel, table=True):
    __tablename__ = "financial_snapshot"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "cash_and_investments",
        "total_debt",
        "operating_cash_flow_ytd",
        "runway_months",
        "shares_outstanding",
        "share_price",
        "market_cap",
        "acquisition_cost_low",
        "acquisition_cost_high",
    )
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    as_of: date
    currency: str = "USD"
    cash_and_investments: float | None = None
    total_debt: float | None = None
    operating_cash_flow_ytd: float | None = None  # as filed: fiscal year to date
    operating_cash_flow_months: int | None = None  # length of that period
    runway_months: float | None = None
    shares_outstanding: float | None = None
    share_price: float | None = None
    market_cap: float | None = None
    acquisition_cost_low: float | None = None
    acquisition_cost_high: float | None = None

    target: Target = Relationship(back_populates="financials")


class ApprovedProduct(SQLModel, table=True):
    __tablename__ = "approved_product"
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = (
        "application_number",
        "brand_name",
        "active_ingredients",
        "first_approval_date",
    )
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    application_number: str | None = None
    brand_name: str | None = None
    active_ingredients: str | None = None
    first_approval_date: date | None = None

    target: Target = Relationship(back_populates="approvals")


class Match(SQLModel, table=True):
    BUSINESS_FIELDS: ClassVar[tuple[str, ...]] = ("score", "rationale")
    id: int | None = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="buyer.id", index=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    score: float | None = None
    rationale: str | None = None
    confidence: Confidence | None = None

    buyer: Buyer = Relationship(back_populates="matches")
    target: Target = Relationship(back_populates="matches")


DOMAIN_TABLES: tuple[type[SQLModel], ...] = (
    Buyer,
    BuyerPreference,
    BuyerFinancial,
    BuyerProductLoe,
    Target,
    Program,
    ProgramIndication,
    Trial,
    TrialResult,
    Catalyst,
    FinancialSnapshot,
    ApprovedProduct,
    Match,
)
