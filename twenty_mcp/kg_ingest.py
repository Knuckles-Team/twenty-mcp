"""Native epistemic-graph ingestion for Twenty CRM records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The package natively pushes its CRM
data into the ONE epistemic-graph knowledge graph as **typed OWL nodes** (`:Person`,
`:Company`, `:Opportunity`, …) + links, using the lightweight engine client
(``GraphComputeEngine()._client`` + ``txn``) — the same fast client the blob
``MediaStore`` uses, NOT the heavy in-process ingestion engine.

Everything is dependency-/engine-guarded: with no agent-utilities KG stack or no
reachable engine, every entry point **no-ops** (returns ``None``), so the connector
keeps working with zero KG infrastructure. Nodes carry the shared provenance
(``domain``/``source``) and their ``type`` matches the classes federated by
``twenty_mcp.ontology`` (``twenty.ttl``). Node ids follow ``twenty:<class>:<uuid>``.

This is a thin mapper: it prefers the shared ``agent_utilities.knowledge_graph.memory.
native_ingest`` primitive when installed, and falls back to a self-contained txn write
path (identical semantics) otherwise, since the primitive is not yet in the installed
agent_utilities.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("twenty_mcp.kg")

_SOURCE = "twenty-mcp"
_DOMAIN = "twenty"
_DEFAULT_GRAPH = "__commons__"


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed nodes (+ edges) into epistemic-graph via the fast engine client.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":rel}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    Prefers the shared ``native_ingest`` primitive; falls back to a local txn path.
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None

    # Preferred path: shared primitive (only when we are NOT given a test client).
    if client is None:
        try:
            from agent_utilities.knowledge_graph.memory.native_ingest import (
                ingest_entities as _shared_ingest,
            )

            return _shared_ingest(
                entities,
                relationships,
                source=source,
                domain=domain,
                graph=graph,
            )
        except Exception as e:  # noqa: BLE001 — primitive absent; use local fallback
            logger.debug("KG ingest: shared primitive unavailable: %s", e)

    # Self-contained fallback (identical semantics to the shared primitive).
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH

    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", source)
            props.setdefault("domain", domain)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


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
) -> dict[str, int] | None:
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
                "type": "Person",
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
                    "type": "worksAt",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_companies(
    companies: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map Twenty company records → ``:Company`` nodes."""
    entities: list[dict[str, Any]] = []
    for rec in companies or []:
        cid = rec.get("id")
        if not cid:
            continue
        entities.append(
            {
                "id": f"twenty:company:{cid}",
                "type": "Company",
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
) -> dict[str, int] | None:
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
                "type": "Opportunity",
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
                    "type": "opportunityFor",
                }
            )
        poc = rec.get("pointOfContactId")
        if poc:
            relationships.append(
                {
                    "source": f"twenty:opportunity:{oid}",
                    "target": f"twenty:person:{poc}",
                    "type": "pointOfContact",
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
