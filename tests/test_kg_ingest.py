"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_people`` / ``ingest_companies`` /
``ingest_opportunities`` seams with a fake engine client (no engine required),
asserting the txn add_node/commit + edge calls and the Twenty record → typed-node
mapping, plus the ``extract_records`` response unwrap.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from twenty_mcp.kg_ingest import (
    extract_records,
    ingest_companies,
    ingest_entities,
    ingest_opportunities,
    ingest_people,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False
        self.graph = None

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, source, target, props):
        self.edges.append((source, target, props))

    def commit(self, txn):
        self.committed = True
        return True


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Person", "name": "p"},
            {"id": "b", "node_type": "Company"},
        ],
        [{"source": "a", "target": "b", "relationship": "worksAt"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "twenty-mcp"
    assert c.txn.nodes["a"]["domain"] == "twenty"
    assert c.txn.edges == [("a", "b", {"relationship": "worksAt"})]


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
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 1}
    node = c.txn.nodes["twenty:person:p-1"]
    assert node["node_type"] == "Person"
    assert node["name"] == "Jane Doe"
    assert node["primaryEmail"] == "jane@acme.com"
    assert node["jobTitle"] == "VP Sales"
    assert node["externalToolId"] == "p-1"
    assert c.txn.edges == [
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
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["twenty:company:co-9"]
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
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 2}
    node = c.txn.nodes["twenty:opportunity:op-3"]
    assert node["node_type"] == "Opportunity"
    assert node["amount"] == 48000.0
    assert node["currencyCode"] == "USD"
    assert node["stage"] == "PROPOSAL"
    assert (
        "twenty:opportunity:op-3",
        "twenty:company:co-9",
        {"relationship": "opportunityFor"},
    ) in c.txn.edges
    assert (
        "twenty:opportunity:op-3",
        "twenty:person:p-1",
        {"relationship": "pointOfContact"},
    ) in c.txn.edges


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
