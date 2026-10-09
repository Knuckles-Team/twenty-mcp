"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_people`` / ``ingest_companies`` /
``ingest_opportunities`` seams against a fake transport boundary (no engine
required), letting the SDK's own ``agent_connector_sdk.ingest`` request builder run
on top of it, plus the ``extract_records`` response unwrap.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from twenty_mcp.kg_ingest import (
    extract_records,
    ingest_companies,
    ingest_entities,
    ingest_opportunities,
    ingest_people,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
            raw_admissions=[],
        )

    async def store_blob(self, data: bytes) -> str:
        raise AssertionError("this test does not exercise blob storage")


@pytest.fixture
def ingest():
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "Person", "name": "p"},
            {"id": "b", "node_type": "Company"},
        ],
        [{"source": "a", "target": "b", "relationship": "worksAt"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert {r.record_id for r in transport.requests[0].records} == {"a", "b"}
    assert transport.requests[0].relationships[0].relation_reference.endswith(
        "/relations/worksAt"
    )


@pytest.mark.asyncio
async def test_ingest_people_maps_person_and_worksat(ingest):
    service, transport = ingest
    res = await ingest_people(
        [
            {
                "id": "p-1",
                "name": {"firstName": "Jane", "lastName": "Doe"},
                "emails": {"primaryEmail": "jane@acme.com"},
                "jobTitle": "VP Sales",
                "companyId": "co-9",
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 1}
    records = {r.record_id: r for r in transport.requests[0].records}
    node = records["twenty:person:p-1"]
    assert node.payload["name"] == "Jane Doe"
    # the SDK's PersistencePrivacyGuard redacts email-shaped values.
    assert node.payload["primaryEmail"] == "[REDACTED_EMAIL]"
    assert node.payload["jobTitle"] == "VP Sales"
    assert node.payload["externalToolId"] == "p-1"
    rel = transport.requests[0].relationships[0]
    assert rel.source.record_id == "twenty:person:p-1"
    assert rel.target.record_id == "twenty:company:co-9"


@pytest.mark.asyncio
async def test_ingest_companies_maps_company(ingest):
    service, transport = ingest
    res = await ingest_companies(
        [
            {
                "id": "co-9",
                "name": "Acme Corp",
                "domainName": {"primaryLinkUrl": "acme.com"},
                "employees": 250,
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    record = transport.requests[0].records[0]
    assert record.record_id == "twenty:company:co-9"
    assert record.payload["name"] == "Acme Corp"
    assert record.payload["domainName"] == "acme.com"
    assert record.payload["employees"] == 250
    assert record.payload["externalToolId"] == "co-9"


@pytest.mark.asyncio
async def test_ingest_opportunities_maps_amount_and_links(ingest):
    service, transport = ingest
    res = await ingest_opportunities(
        [
            {
                "id": "op-3",
                "name": "Acme expansion",
                "amount": {"amountMicros": 48000000000, "currencyCode": "USD"},
                "stage": "PROPOSAL",
                "closeDate": "2026-09-30T00:00:00Z",
                "companyId": "co-9",
                "pointOfContactId": "p-1",
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 2}
    record = transport.requests[0].records[0]
    assert record.record_id == "twenty:opportunity:op-3"
    assert record.payload["amount"] == 48000.0
    assert record.payload["currencyCode"] == "USD"
    assert record.payload["stage"] == "PROPOSAL"
    rel_pairs = {
        (r.source.record_id, r.target.record_id, r.relation_reference.rsplit("/", 1)[-1])
        for r in transport.requests[0].relationships
    }
    assert ("twenty:opportunity:op-3", "twenty:company:co-9", "opportunityFor") in rel_pairs
    assert ("twenty:opportunity:op-3", "twenty:person:p-1", "pointOfContact") in rel_pairs


def test_extract_records_unwraps_twenty_response():
    resp = {"data": {"people": [{"id": "p-1"}, {"id": "p-2"}]}}
    recs = extract_records(resp, "people")
    assert [r["id"] for r in recs] == ["p-1", "p-2"]
    # bare list tolerated
    assert extract_records([{"id": "x"}], "companies") == [{"id": "x"}]
    # single-dict record tolerated
    assert extract_records({"data": {"id": "solo"}}, "opportunities") == [
        {"id": "solo"}
    ]


@pytest.mark.asyncio
async def test_retired_structural_alias_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="id and a node_type"):
        await ingest_entities([{"id": "a", "type": "Person"}], ingest=service)


@pytest.mark.asyncio
async def test_empty_native_ingest_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
