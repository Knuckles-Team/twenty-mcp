"""MCP tools for native epistemic-graph ingestion of Twenty CRM records.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Wire-First tools that list Twenty
records via the real CRM client and push them into the knowledge graph as typed
:Person / :Company / :Opportunity nodes. Best-effort: ``{"ingested": None}`` when no
engine is reachable.
"""

import json

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from twenty_mcp.auth import get_client
from twenty_mcp.kg_ingest import (
    extract_records,
    ingest_companies,
    ingest_opportunities,
    ingest_people,
)

_OBJECTS = {
    "people": ("get_people", ingest_people),
    "companies": ("get_companies", ingest_companies),
    "opportunities": ("get_opportunities", ingest_opportunities),
}


def register_ingest_tools(mcp: FastMCP):
    """Register Twenty MCP native ingestion tools.
    CONCEPT:AU-KG.ingest.enterprise-source-extractor
    """

    @mcp.tool(tags={"kg", "ingest"})
    async def twenty_ingest_records(
        object_name: str = Field(
            default="people",
            description="Twenty object to ingest: 'people', 'companies', or 'opportunities'.",
        ),
        params_json: str = Field(
            default="{}",
            description='JSON string of list filters (e.g. {"limit": 60}) passed to the CRM client.',
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """List a Twenty CRM object and natively ingest it into epistemic-graph.

        Maps records to typed :Person / :Company / :Opportunity nodes (+ :worksAt /
        :opportunityFor / :pointOfContact links) and pushes them via the fast engine
        client. Returns ``{"object": ..., "listed": n, "ingested": {...}|None}``.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        obj = (object_name or "people").strip().lower()
        entry = _OBJECTS.get(obj)
        if entry is None:
            return {
                "error": f"Unknown object '{object_name}'. Use one of {sorted(_OBJECTS)}."
            }
        list_method_name, mapper = entry

        if ctx:
            await ctx.info(f"Ingesting Twenty {obj} into the knowledge graph...")

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:  # noqa: BLE001
            return {"error": f"Invalid params_json: {e}"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        method = getattr(client, list_method_name, None)
        if method is None:
            return {"error": f"Client has no method '{list_method_name}'."}
        try:
            params = kwargs or None
            response = method(params=params) if params is not None else method()
        except Exception as e:  # noqa: BLE001
            return {"error": f"Failed to list Twenty {obj}: {e}"}

        records = extract_records(response, obj)
        result = mapper(records)
        return {"object": obj, "listed": len(records), "ingested": result}

    return None
