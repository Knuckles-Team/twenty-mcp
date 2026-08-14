"""Native epistemic-graph ingestion for Twenty CRM records.

All writes use the required ``agent_utilities.knowledge_graph.memory.native_ingest``
primitive. Nodes use canonical ``node_type`` and edges use canonical ``relationship``;
nodes and edges commit in one native transaction. Missing engine dependencies, rejected
records, conflicts, and transaction failures propagate as ``NativeIngestError``.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

logger = logging.getLogger("twenty_mcp.kg")

_SOURCE = "twenty-mcp"
_DOMAIN = "twenty"


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships in one native transaction."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


# --- record → node field extraction helpers ---------------------------------


def _s(value: Any) -> str | None:
    """Coerce a scalar-ish value to a trimmed string, or None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _full_name(record: dict[str, Any]) -> str | None:
    """Twenty stores names as ``{"firstName": ..., "lastName": ...}`` (or flat)."""
    name = record.get("name")
    if isinstance(name, dict):
        parts = [name.get("firstName"), name.get("lastName")]
        joined = " ".join(p for p in parts if p)
        return joined.strip() or None
    return _s(name)


def _primary_email(record: dict[str, Any]) -> str | None:
    emails = record.get("emails")
    if isinstance(emails, dict):
        return _s(emails.get("primaryEmail"))
    return _s(record.get("email"))


def _domain_name(record: dict[str, Any]) -> str | None:
    dn = record.get("domainName")
    if isinstance(dn, dict):
        return _s(dn.get("primaryLinkUrl") or dn.get("primaryLinkLabel"))
    return _s(dn or record.get("domain"))


def _amount(record: dict[str, Any]) -> tuple[float | None, str | None]:
    amt = record.get("amount")
    if isinstance(amt, dict):
        micros = amt.get("amountMicros")
        currency = _s(amt.get("currencyCode"))
        if micros is not None:
            try:
                return float(micros) / 1_000_000.0, currency
            except (TypeError, ValueError):
                return None, currency
        return None, currency
    if isinstance(amt, (int, float)):
        return float(amt), _s(record.get("currencyCode"))
    return None, _s(record.get("currencyCode"))


# --- typed mappers -----------------------------------------------------------


def ingest_people(
    people: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map Twenty people records → ``:Person`` (+ ``:Company`` / ``:worksAt``) nodes."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for rec in people or []:
        pid = rec.get("id")
        if not pid:
            continue
        entities.append(
            {
                "id": f"twenty:person:{pid}",
                "node_type": "Person",
                "name": _full_name(rec),
                "primaryEmail": _primary_email(rec),
                "jobTitle": _s(rec.get("jobTitle")),
                "city": _s(rec.get("city")),
                "createdAt": _s(rec.get("createdAt")),
                "updatedAt": _s(rec.get("updatedAt")),
                "externalToolId": str(pid),
            }
        )
        cid = rec.get("companyId")
        if cid:
            relationships.append(
                {
                    "source": f"twenty:person:{pid}",
                    "target": f"twenty:company:{cid}",
                    "relationship": "worksAt",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_companies(
    companies: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map Twenty company records → ``:Company`` nodes."""
    entities: list[dict[str, Any]] = []
    for rec in companies or []:
        cid = rec.get("id")
        if not cid:
            continue
        entities.append(
            {
                "id": f"twenty:company:{cid}",
                "node_type": "Company",
                "name": _s(rec.get("name")),
                "domainName": _domain_name(rec),
                "employees": rec.get("employees"),
                "createdAt": _s(rec.get("createdAt")),
                "updatedAt": _s(rec.get("updatedAt")),
                "externalToolId": str(cid),
            }
        )
    return ingest_entities(entities, None, client=client, graph=graph)


def ingest_opportunities(
    opportunities: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map Twenty opportunity records → ``:Opportunity`` (+ company / contact links)."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for rec in opportunities or []:
        oid = rec.get("id")
        if not oid:
            continue
        amount, currency = _amount(rec)
        entities.append(
            {
                "id": f"twenty:opportunity:{oid}",
                "node_type": "Opportunity",
                "name": _s(rec.get("name")),
                "amount": amount,
                "currencyCode": currency,
                "stage": _s(rec.get("stage")),
                "closeDate": _s(rec.get("closeDate")),
                "createdAt": _s(rec.get("createdAt")),
                "updatedAt": _s(rec.get("updatedAt")),
                "externalToolId": str(oid),
            }
        )
        cid = rec.get("companyId")
        if cid:
            relationships.append(
                {
                    "source": f"twenty:opportunity:{oid}",
                    "target": f"twenty:company:{cid}",
                    "relationship": "opportunityFor",
                }
            )
        poc = rec.get("pointOfContactId")
        if poc:
            relationships.append(
                {
                    "source": f"twenty:opportunity:{oid}",
                    "target": f"twenty:person:{poc}",
                    "relationship": "pointOfContact",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


# --- response unwrap ---------------------------------------------------------


def extract_records(response: Any, object_name: str) -> list[dict[str, Any]]:
    """Pull the record list out of a Twenty REST response.

    Twenty returns ``{"data": {"<object>": [ ... ]}}`` for list endpoints. Also
    tolerates a bare list or a ``{"data": [ ... ]}`` shape. Coerces pydantic
    models via ``model_dump``.
    """
    data: Any = response
    if isinstance(response, dict):
        data = response.get("data", response)
    if isinstance(data, dict):
        data = data.get(object_name, data)
    if data is None:
        return []
    records = data if isinstance(data, list) else [data]
    out: list[dict[str, Any]] = []
    for r in records:
        if r is None:
            continue
        out.append(r.model_dump() if hasattr(r, "model_dump") else r)
    return out
