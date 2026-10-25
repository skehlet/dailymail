"""
Decide what in today's Google Alert articles is genuinely new to the reader,
by comparing against the topic's ledger of previously reported facts.
"""
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dailymail_shared.my_llm import call_llm_structured, get_context_window_size
from .ledger import Ledger, LedgerFact

KINDS = ("NEW", "CHANGED", "CONFIRMED", "CONTRADICTED")
MAX_LEDGER_FACTS = 40


class NewDevelopment(BaseModel):
    kind: str = Field(
        description="NEW (not covered by any known fact), CHANGED (supersedes a known fact, e.g. a date moved), "
        "CONFIRMED (a known rumor is now officially confirmed), or CONTRADICTED (a credible source disputes a known fact)."
    )
    statement: str = Field(
        description="One self-contained sentence stating the development, understandable without the article. "
        "Include specifics: names, dates, numbers."
    )
    status: str = Field(description="CONFIRMED (official/verified) or RUMOR (leak, speculation, unnamed sources).")
    source_urls: List[str] = Field(description="URLs of the articles that report this development.")


class AlertNewsCheck(BaseModel):
    new_developments: List[NewDevelopment] = Field(
        description="Only developments the reader has not already been told. Empty if there is nothing new."
    )
    summary: str = Field(
        description="1-2 sentences telling the reader what is new, written directly (no 'the articles say'). "
        "Empty string if there are no new developments."
    )


class CompactedLedger(BaseModel):
    facts: List[LedgerFact]


class AlertSource(BaseModel):
    title: str
    url: str


class AlertDevelopment(BaseModel):
    kind: str
    statement: str
    status: str
    sources: List[AlertSource]


class AlertUpdate(BaseModel):
    """What to show the reader for one topic, and the ledger to save once they've been sent it."""
    topic: str
    summary: str
    developments: List[AlertDevelopment]
    updated_ledger: Ledger


CHECK_SYSTEM_PROMPT = """\
You keep track of what a reader already knows about a topic they follow, so they are only told genuinely new information.

You are given KNOWN_FACTS (everything the reader has already been told, with the date they were told) and TODAYS_ARTICLES.
Report only developments that are not already covered by KNOWN_FACTS.

These are NOT new, and must be left out:
- Restatements, rephrasings, recaps, or background of known facts, even from a different outlet or with a fresh headline.
- Commentary, opinion, or speculation about known facts ("fans are frustrated", "why it hasn't been announced yet").
- A rumor that is already known, repeated by another outlet.
- Anything unrelated to the topic.

These ARE new:
- NEW: a fact or claim not covered by any known fact.
- CHANGED: something that supersedes a known fact (a date moved, a price changed, a plan was cancelled).
- CONFIRMED: a known rumor is now officially confirmed.
- CONTRADICTED: a credible source disputes a known fact.

If several articles report the same development, list it once with all their URLs.
Be strict: most days, most articles contain nothing new, and an empty list is the correct answer."""


COMPACT_SYSTEM_PROMPT = """\
You maintain a list of facts a reader has been told about a topic. Rewrite it to be shorter without losing information:
- Merge facts that say the same thing, keeping the earliest date.
- Where a newer fact supersedes an older one (a date moved, a rumor was confirmed), keep only the current state, \
noting the change if it matters (e.g. "Release delayed from May 2026 to Nov 19, 2026").
- Keep every distinct fact that is still current. Do not invent anything."""


def check_alert_for_news(topic: str, records: list, ledger: Ledger, today: str, interest: Optional[str] = None) -> AlertUpdate:
    articles = [
        {
            "title": record.get("title"),
            "url": record.get("url"),
            "published": record.get("published"),
            "summary": record.get("summary"),
            "notable_aspects": record.get("notable_aspects"),
        }
        for record in records
    ]
    known_facts = [fact.model_dump() for fact in ledger.facts]

    contents = f"TOPIC: {topic}\n\n"
    if interest:
        contents += f"WHAT THE READER WANTS TO KNOW: {interest}\n\n"
    contents += f"KNOWN_FACTS:\n{json.dumps(known_facts, indent=2)}\n\nTODAYS_ARTICLES:\n{json.dumps(articles, indent=2)}\n"
    contents = contents[:get_context_window_size() - 100]

    result: AlertNewsCheck = call_llm_structured(contents, AlertNewsCheck, system_prompt=CHECK_SYSTEM_PROMPT)
    print(f"Alert news check for {topic!r}: {result.model_dump_json(indent=2)}")

    titles_by_url = {article["url"]: article["title"] or article["url"] for article in articles}
    developments = []
    for dev in result.new_developments:
        kind = dev.kind.strip().upper()
        if kind not in KINDS:
            kind = "NEW"
        status = "RUMOR" if dev.status.strip().upper() == "RUMOR" else "CONFIRMED"
        # only keep URLs we actually gave the model
        sources = [AlertSource(title=titles_by_url[url], url=url) for url in dev.source_urls if url in titles_by_url]
        developments.append(AlertDevelopment(kind=kind, statement=dev.statement, status=status, sources=sources))

    facts = ledger.facts + [LedgerFact(date=today, fact=dev.statement, status=dev.status) for dev in developments]
    updated_ledger = Ledger(topic=ledger.topic, facts=facts)
    if developments and len(updated_ledger.facts) > MAX_LEDGER_FACTS:
        updated_ledger = compact_ledger(updated_ledger)

    return AlertUpdate(
        topic=topic,
        summary=result.summary if developments else "",
        developments=developments,
        updated_ledger=updated_ledger,
    )


def compact_ledger(ledger: Ledger) -> Ledger:
    contents = f"TOPIC: {ledger.topic}\n\nFACTS:\n{json.dumps([fact.model_dump() for fact in ledger.facts], indent=2)}\n"
    try:
        result: CompactedLedger = call_llm_structured(contents, CompactedLedger, system_prompt=COMPACT_SYSTEM_PROMPT)
    except Exception as e:
        print(f"Error compacting ledger for {ledger.topic!r}: {e}, keeping it uncompacted")
        return ledger
    # guard against the model throwing most of the memory away
    if not result.facts or len(result.facts) < len(ledger.facts) // 4:
        print(f"Compaction of {ledger.topic!r} returned {len(result.facts)} of {len(ledger.facts)} facts, keeping it uncompacted")
        return ledger
    print(f"Compacted ledger for {ledger.topic!r} from {len(ledger.facts)} to {len(result.facts)} facts")
    return Ledger(topic=ledger.topic, facts=result.facts)
