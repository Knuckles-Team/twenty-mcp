from typing import Any

from twenty_mcp.api.api_client_base import ApiClientBase


class CrmApi(ApiClientBase):
    # --- Generic/Dynamic Record API ---

    def get_records(
        self, object_name: str, params: dict[str, Any] | None = None
    ) -> dict:
        """Fetch a list of records for any custom or built-in object."""
        return self.request("GET", f"{self.api_prefix}/{object_name}", params=params)

    def get_record(
        self, object_name: str, record_id: str, params: dict[str, Any] | None = None
    ) -> dict:
        """Fetch a specific record by ID for any custom or built-in object."""
        return self.request(
            "GET", f"{self.api_prefix}/{object_name}/{record_id}", params=params
        )

    def create_record(self, object_name: str, data: dict[str, Any]) -> dict:
        """Create a new record for any custom or built-in object."""
        return self.request("POST", f"{self.api_prefix}/{object_name}", data=data)

    def update_record(
        self, object_name: str, record_id: str, data: dict[str, Any]
    ) -> dict:
        """Update an existing record by ID for any custom or built-in object."""
        return self.request(
            "PATCH", f"{self.api_prefix}/{object_name}/{record_id}", data=data
        )

    def delete_record(self, object_name: str, record_id: str) -> dict:
        """Delete a record by ID for any custom or built-in object."""
        return self.request("DELETE", f"{self.api_prefix}/{object_name}/{record_id}")

    # --- Batch REST Operations (Max 60 records) ---

    def batch_create_records(
        self, object_name: str, records: list[dict[str, Any]]
    ) -> dict:
        """Batch create up to 60 records for any object."""
        if len(records) > 60:
            raise ValueError("Batch size cannot exceed 60 records.")
        return self.request("POST", f"{self.api_prefix}/{object_name}", data=records)

    def batch_update_records(
        self, object_name: str, records: list[dict[str, Any]]
    ) -> dict:
        """Batch update up to 60 records for any object."""
        if len(records) > 60:
            raise ValueError("Batch size cannot exceed 60 records.")
        return self.request("PATCH", f"{self.api_prefix}/{object_name}", data=records)

    def batch_delete_records(self, object_name: str, record_ids: list[str]) -> dict:
        """Batch delete up to 60 records by ID for any object."""
        if len(record_ids) > 60:
            raise ValueError("Batch size cannot exceed 60 records.")
        return self.request(
            "DELETE", f"{self.api_prefix}/{object_name}", data={"ids": record_ids}
        )

    # --- People (Contacts) API ---

    def get_people(self, params: dict[str, Any] | None = None) -> dict:
        """Get CRM contacts."""
        return self.get_records("people", params=params)

    def get_person(self, person_id: str) -> dict:
        """Get a specific contact by ID."""
        return self.get_record("people", person_id)

    def create_person(
        self, first_name: str, last_name: str, email: str | None = None, **kwargs
    ) -> dict:
        """Create a person in CRM."""
        data: dict[str, Any] = {"firstName": first_name, "lastName": last_name}
        if email:
            data["email"] = email
        data.update(kwargs)
        return self.create_record("people", data)

    def update_person(self, person_id: str, data: dict[str, Any]) -> dict:
        """Update a contact's fields."""
        return self.update_record("people", person_id, data)

    def delete_person(self, person_id: str) -> dict:
        """Delete a contact by ID."""
        return self.delete_record("people", person_id)

    # --- Companies API ---

    def get_companies(self, params: dict[str, Any] | None = None) -> dict:
        """Get CRM companies."""
        return self.get_records("companies", params=params)

    def get_company(self, company_id: str) -> dict:
        """Get a specific company by ID."""
        return self.get_record("companies", company_id)

    def create_company(self, name: str, domain: str | None = None, **kwargs) -> dict:
        """Create a company in CRM."""
        data: dict[str, Any] = {"name": name}
        if domain:
            data["domain"] = domain
        data.update(kwargs)
        return self.create_record("companies", data)

    def update_company(self, company_id: str, data: dict[str, Any]) -> dict:
        """Update a company's fields by ID."""
        return self.update_record("companies", company_id, data)

    def delete_company(self, company_id: str) -> dict:
        """Delete a company by ID."""
        return self.delete_record("companies", company_id)

    # --- Opportunities API ---

    def get_opportunities(self, params: dict[str, Any] | None = None) -> dict:
        """Get opportunities."""
        return self.get_records("opportunities", params=params)

    def get_opportunity(self, opportunity_id: str) -> dict:
        """Get a specific opportunity by ID."""
        return self.get_record("opportunities", opportunity_id)

    def create_opportunity(
        self, name: str, amount: float | None = None, **kwargs
    ) -> dict:
        """Create opportunity."""
        data: dict[str, Any] = {"name": name}
        if amount is not None:
            data["amount"] = amount
        data.update(kwargs)
        return self.create_record("opportunities", data)

    def update_opportunity(self, opportunity_id: str, data: dict[str, Any]) -> dict:
        """Update an opportunity's fields by ID."""
        return self.update_record("opportunities", opportunity_id, data)

    def delete_opportunity(self, opportunity_id: str) -> dict:
        """Delete an opportunity by ID."""
        return self.delete_record("opportunities", opportunity_id)

    # --- GraphQL Core API ---

    def execute_gql(self, query: str, variables: dict[str, Any] | None = None) -> dict:
        """Execute arbitrary GraphQL queries on core and custom schemas."""
        return self.request(
            "POST", "/graphql", data={"query": query, "variables": variables}
        )
