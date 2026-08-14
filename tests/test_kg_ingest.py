"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_people`` / ``ingest_companies`` /
``ingest_opportunities`` seams with a fake engine client (no engine required),
asserting the txn add_node/commit + edge calls and the Twenty record → typed-node
mapping, plus the ``extract_records`` response unwrap.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

from twenty_mcp.kg_ingest import (
    extract_records,
    ingest_companies,
    ingest_entities,
    ingest_opportunities,
    ingest_people,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Person", "name": "p"},
            {"id": "b", "node_type": "Company"},
        ],
        [{"source": "a", "target": "b", "relationship": "worksAt"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "twenty-mcp"
    assert c.nodes.values["a"]["domain"] == "twenty"
    assert c.changes.edges == [("a", "b", {"relationship": "worksAt"})]


def test_ingest_people_maps_person_and_worksat():
    c = _FakeClient()
    res = ingest_people(
        [
            {
                "id": "p-1",
                "name": {"firstName": "Jane", "lastName": "Doe"},
                "emails": {"primaryEmail": "jane@acme.com"},
                "jobTitle": "VP Sales",
                "companyId": "co-9",
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 1}
    node = c.nodes.values["twenty:person:p-1"]
    assert node["node_type"] == "Person"
    assert node["name"] == "Jane Doe"
    # native_ingest's governed PII scrubber redacts email-shaped values.
    assert node["primaryEmail"] == "[REDACTED_EMAIL]"
    assert node["jobTitle"] == "VP Sales"
    assert node["externalToolId"] == "p-1"
    assert c.changes.edges == [
        ("twenty:person:p-1", "twenty:company:co-9", {"relationship": "worksAt"})
    ]


def test_ingest_companies_maps_company():
    c = _FakeClient()
    res = ingest_companies(
        [
            {
                "id": "co-9",
                "name": "Acme Corp",
                "domainName": {"primaryLinkUrl": "acme.com"},
                "employees": 250,
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["twenty:company:co-9"]
    assert node["node_type"] == "Company"
    assert node["name"] == "Acme Corp"
    assert node["domainName"] == "acme.com"
    assert node["employees"] == 250
    assert node["externalToolId"] == "co-9"


def test_ingest_opportunities_maps_amount_and_links():
    c = _FakeClient()
    res = ingest_opportunities(
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
        client=c,
    )
    assert res == {"nodes": 1, "edges": 2}
    node = c.nodes.values["twenty:opportunity:op-3"]
    assert node["node_type"] == "Opportunity"
    assert node["amount"] == 48000.0
    assert node["currencyCode"] == "USD"
    assert node["stage"] == "PROPOSAL"
    assert (
        "twenty:opportunity:op-3",
        "twenty:company:co-9",
        {"relationship": "opportunityFor"},
    ) in c.changes.edges
    assert (
        "twenty:opportunity:op-3",
        "twenty:person:p-1",
        {"relationship": "pointOfContact"},
    ) in c.changes.edges


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


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Person"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
