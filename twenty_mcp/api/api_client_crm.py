from twenty_mcp.api.api_client_base import ApiClientBase

class Api(ApiClientBase):
    def get_people(self) -> dict:
        """Get CRM contacts."""
        return self.request("GET", "/api/v1/people")

    def create_person(self, first_name: str, last_name: str, email: str = None) -> dict:
        """Create a person in CRM."""
        return self.request("POST", "/api/v1/people", data={"firstName": first_name, "lastName": last_name, "email": email})

    def get_companies(self) -> dict:
        """Get CRM companies."""
        return self.request("GET", "/api/v1/companies")

    def create_company(self, name: str, domain: str = None) -> dict:
        """Create a company in CRM."""
        return self.request("POST", "/api/v1/companies", data={"name": name, "domain": domain})

    def get_opportunities(self) -> dict:
        """Get opportunities."""
        return self.request("GET", "/api/v1/opportunities")

    def create_opportunity(self, name: str, amount: float = None) -> dict:
        """Create opportunity."""
        return self.request("POST", "/api/v1/opportunities", data={"name": name, "amount": amount})

    def execute_gql(self, query: str, variables: dict = None) -> dict:
        """Execute arbitrary GraphQL queries on custom schemas (guarantees 100% API coverage)."""
        return self.request("POST", "/graphql", data={"query": query, "variables": variables})
