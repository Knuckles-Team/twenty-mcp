from typing import Any

from twenty_mcp.api.api_client_base import ApiClientBase


class MetadataApi(ApiClientBase):
    """Metadata API for managing Twenty CRM schema (objects, fields, and relations)."""

    def request_metadata(
        self,
        method: str,
        endpoint: str,
        data: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict:
        """Internal helper for Routing Metadata requests under /rest/metadata or /metadata."""
        endpoint = endpoint.lstrip("/")
        prefix = "/metadata"
        if hasattr(self, "api_prefix") and self.api_prefix.startswith("/rest"):
            prefix = "/rest/metadata"

        path = f"{prefix}/{endpoint}" if endpoint else prefix
        return self.request(method, path, params=params, data=data)

    def get_metadata(self) -> dict:
        """Fetch complete workspace metadata schema."""
        return self.request_metadata("GET", "")

    def get_metadata_objects(self) -> dict:
        """Fetch all object schemas."""
        return self.request_metadata("GET", "objects")

    def get_metadata_object(self, object_name_or_id: str) -> dict:
        """Fetch a specific object schema by name or ID."""
        return self.request_metadata("GET", f"objects/{object_name_or_id}")

    def create_metadata_object(self, data: dict[str, Any]) -> dict:
        """Create a new custom object schema (e.g. Invoice)."""
        return self.request_metadata("POST", "objects", data=data)

    def update_metadata_object(self, object_id: str, data: dict[str, Any]) -> dict:
        """Update a custom object schema."""
        return self.request_metadata("PATCH", f"objects/{object_id}", data=data)

    def delete_metadata_object(self, object_id: str) -> dict:
        """Delete a custom object schema."""
        return self.request_metadata("DELETE", f"objects/{object_id}")

    def create_metadata_field(self, data: dict[str, Any]) -> dict:
        """Create a custom field on a standard or custom object."""
        return self.request_metadata("POST", "fields", data=data)

    def update_metadata_field(self, field_id: str, data: dict[str, Any]) -> dict:
        """Update an existing field's metadata configuration."""
        return self.request_metadata("PATCH", f"fields/{field_id}", data=data)

    def delete_metadata_field(self, field_id: str) -> dict:
        """Delete a custom field from an object schema."""
        return self.request_metadata("DELETE", f"fields/{field_id}")

    def create_metadata_relation(self, data: dict[str, Any]) -> dict:
        """Create a bidirectional relation between objects."""
        return self.request_metadata("POST", "relations", data=data)

    def delete_metadata_relation(self, relation_id: str) -> dict:
        """Delete an existing relation by relation ID."""
        return self.request_metadata("DELETE", f"relations/{relation_id}")
