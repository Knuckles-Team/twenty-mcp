"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_people`` / ``ingest_companies`` /
``ingest_opportunities`` seams with a fake engine client (no engine required),
asserting the txn add_node/commit + edge calls and the Twenty record → typed-node
mapping, plus the ``extract_records`` response unwrap.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

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
        self.committed = False
        self.graph = None

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "Person", "name": "p"},
            {"id": "b", "type": "Company"},
        ],
        [{"source": "a", "target": "b", "type": "worksAt"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "twenty-mcp"
    assert c.txn.nodes["a"]["domain"] == "twenty"
    assert c.edges.edges == [("a", "b", {"type": "worksAt"})]


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
    assert node["type"] == "Person"
    assert node["name"] == "Jane Doe"
    assert node["primaryEmail"] == "jane@acme.com"
    assert node["jobTitle"] == "VP Sales"
    assert node["externalToolId"] == "p-1"
    assert c.edges.edges == [
        ("twenty:person:p-1", "twenty:company:co-9", {"type": "worksAt"})
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
    assert node["type"] == "Company"
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
    assert node["type"] == "Opportunity"
    assert node["amount"] == 48000.0
    assert node["currencyCode"] == "USD"
    assert node["stage"] == "PROPOSAL"
    assert (
        "twenty:opportunity:op-3",
        "twenty:company:co-9",
        {"type": "opportunityFor"},
    ) in c.edges.edges
    assert (
        "twenty:opportunity:op-3",
        "twenty:person:p-1",
        {"type": "pointOfContact"},
    ) in c.edges.edges


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


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_people([{"id": "p-1"}]) is None


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_people([], client=_FakeClient()) is None
    assert ingest_companies([], client=_FakeClient()) is None
    assert ingest_opportunities([], client=_FakeClient()) is None
