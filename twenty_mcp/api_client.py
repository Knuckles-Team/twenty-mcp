"""CONCEPT:TWENTY-001 Dynamic client facade orchestration and resource mappings."""

#!/usr/bin/env python
from twenty_mcp.api.api_client_crm import CrmApi
from twenty_mcp.api.api_client_metadata import MetadataApi
from twenty_mcp.api.api_client_oauth import OauthApi

__version__ = "0.15.0"


class Api(CrmApi, MetadataApi, OauthApi):
    pass
