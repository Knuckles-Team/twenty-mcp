"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        "twenty-find-contact",
        (
            ToolStep(
                "twenty_find_records",
                params=(
                    "object_name",
                    "filter",
                    "order_by",
                    "limit",
                    "depth",
                ),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_people",
                params=("params",),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_person",
                params=("person_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Search contacts by name or email, then read the chosen person.",
    ),
    ToolUseContract(
        "twenty-create-contact",
        (
            ToolStep(
                "twenty_find_duplicates",
                params=(
                    "object_name",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_person",
                params=(
                    "first_name",
                    "last_name",
                    "email",
                    "params_json",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_person",
                params=("person_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Check for a duplicate person, create the contact and read it back.",
    ),
    ToolUseContract(
        "twenty-update-contact",
        (
            ToolStep(
                "twenty_get_person",
                params=("person_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_person",
                params=(
                    "person_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Read a contact, then change its fields.",
    ),
    ToolUseContract(
        "twenty-remove-contact",
        (
            ToolStep(
                "twenty_get_person",
                params=("person_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_person",
                params=("person_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Confirm a contact is the right one, then delete it.",
    ),
    ToolUseContract(
        "twenty-find-company",
        (
            ToolStep(
                "twenty_get_companies",
                params=("params",),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="List companies and read one account.",
    ),
    ToolUseContract(
        "twenty-create-company",
        (
            ToolStep(
                "twenty_find_duplicates",
                params=(
                    "object_name",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_company",
                params=(
                    "name",
                    "domain",
                    "params_json",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Check for a duplicate account, create the company and read it back.",
    ),
    ToolUseContract(
        "twenty-update-company",
        (
            ToolStep(
                "twenty_get_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_company",
                params=(
                    "company_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Read a company, then change its fields.",
    ),
    ToolUseContract(
        "twenty-remove-company",
        (
            ToolStep(
                "twenty_get_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Confirm a company is the right one, then delete it.",
    ),
    ToolUseContract(
        "twenty-review-pipeline",
        (
            ToolStep(
                "twenty_get_opportunities",
                params=("params",),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_opportunity",
                params=("opportunity_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="List the deals, then read one for its stage, amount and close date.",
    ),
    ToolUseContract(
        "twenty-open-opportunity",
        (
            ToolStep(
                "twenty_get_company",
                params=("company_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_opportunity",
                params=(
                    "name",
                    "amount",
                    "params_json",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_opportunity",
                params=("opportunity_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Open a deal for an existing company and read it back.",
    ),
    ToolUseContract(
        "twenty-advance-opportunity",
        (
            ToolStep(
                "twenty_get_opportunity",
                params=("opportunity_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_opportunity",
                params=(
                    "opportunity_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Read a deal, then set its stage, amount or close date.",
    ),
    ToolUseContract(
        "twenty-remove-opportunity",
        (
            ToolStep(
                "twenty_get_opportunity",
                params=("opportunity_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_opportunity",
                params=("opportunity_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Confirm a deal is the right one, then delete it.",
    ),
    ToolUseContract(
        "twenty-read-record",
        (
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_records",
                params=(
                    "object_name",
                    "params",
                ),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_record",
                params=(
                    "object_name",
                    "record_id",
                    "params",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Resolve a built-in or custom object, list its records and read one.",
    ),
    ToolUseContract(
        "twenty-write-record",
        (
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_record",
                params=(
                    "object_name",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_record",
                params=(
                    "object_name",
                    "record_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Check the object schema, create a record of any object and amend it.",
    ),
    ToolUseContract(
        "twenty-remove-record",
        (
            ToolStep(
                "twenty_get_record",
                params=(
                    "object_name",
                    "record_id",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_record",
                params=(
                    "object_name",
                    "record_id",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Read a record of any object, then delete it.",
    ),
    ToolUseContract(
        "twenty-bulk-create",
        (
            ToolStep(
                "twenty_find_duplicates",
                params=(
                    "object_name",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_batch_create_records",
                params=(
                    "object_name",
                    "records",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Screen a batch for duplicates, then create up to 60 records at once.",
    ),
    ToolUseContract(
        "twenty-bulk-update",
        (
            ToolStep(
                "twenty_find_records",
                params=(
                    "object_name",
                    "filter",
                    "limit",
                    "starting_after",
                ),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_batch_update_records",
                params=(
                    "object_name",
                    "records",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Select records with a filter, then update up to 60 of them at once.",
    ),
    ToolUseContract(
        "twenty-bulk-remove",
        (
            ToolStep(
                "twenty_find_records",
                params=(
                    "object_name",
                    "filter",
                    "limit",
                ),
                result=(
                    "data",
                    "pageInfo",
                    "totalCount",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_batch_delete_records",
                params=(
                    "object_name",
                    "record_ids",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Select records with a filter, then delete up to 60 by id.",
    ),
    ToolUseContract(
        "twenty-run-graphql",
        (
            ToolStep(
                "twenty_discover_graphql_schema",
                params=("type_name",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_graphql",
                params=(
                    "query",
                    "variables",
                    "operation_name",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
        description="Look up a GraphQL type, then run a query or mutation.",
    ),
    ToolUseContract(
        "twenty-run-gql",
        (
            ToolStep(
                "twenty_get_metadata",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_execute_gql",
                params=(
                    "query",
                    "variables",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
        description="Read the workspace schema, then run a GraphQL call on the core API.",
    ),
    ToolUseContract(
        "twenty-inspect-schema",
        (
            ToolStep(
                "twenty_get_metadata",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_objects",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_fields",
                params=("params",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_field",
                params=("field_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_relations",
                params=("params",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_relation",
                params=("relation_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Walk the workspace meta-model from the whole schema to one object, field or relation.",
    ),
    ToolUseContract(
        "twenty-raw-metadata-request",
        (
            ToolStep(
                "twenty_get_metadata",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_request_metadata",
                params=(
                    "method",
                    "endpoint",
                    "data",
                    "params",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Reach a metadata endpoint no typed tool covers.",
    ),
    ToolUseContract(
        "twenty-define-object",
        (
            ToolStep(
                "twenty_get_metadata_objects",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_metadata_object",
                params=("data",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_metadata_field",
                params=("data",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_create_metadata_relation",
                params=("data",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Add a custom object with its fields and relations, then read the result.",
    ),
    ToolUseContract(
        "twenty-update-schema",
        (
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_metadata_object",
                params=(
                    "object_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_field",
                params=("field_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_metadata_field",
                params=(
                    "field_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_get_metadata_relation",
                params=("relation_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_update_metadata_relation",
                params=(
                    "relation_id",
                    "data",
                ),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Change an object, a field or a relation after reading its current definition.",
    ),
    ToolUseContract(
        "twenty-drop-schema",
        (
            ToolStep(
                "twenty_get_metadata_object",
                params=("object_name_or_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_metadata_relation",
                params=("relation_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_metadata_field",
                params=("field_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                "twenty_delete_metadata_object",
                params=("object_id",),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
        description="Remove relations, then fields, then the custom object itself.",
    ),
    ToolUseContract(
        "twenty-register-oauth-client",
        (
            ToolStep(
                "twenty_get_oauth_discovery",
                params=(),
                result=(
                    "issuer",
                    "token_endpoint",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_register_oauth_client",
                params=(
                    "client_name",
                    "redirect_uris",
                    "grant_types",
                    "token_endpoint_auth_method",
                ),
                result=(
                    "client_id",
                    "client_secret",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Read the OAuth server metadata and register a client dynamically.",
    ),
    ToolUseContract(
        "twenty-oauth-code-flow",
        (
            ToolStep(
                "twenty_get_oauth_discovery",
                params=(),
                result=(
                    "issuer",
                    "token_endpoint",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_exchange_oauth_token",
                params=(
                    "code",
                    "redirect_uri",
                    "client_id",
                    "client_secret",
                    "code_verifier",
                ),
                result=(
                    "access_token",
                    "refresh_token",
                    "expires_in",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
            ToolStep(
                "twenty_refresh_oauth_token",
                params=(
                    "refresh_token",
                    "client_id",
                    "client_secret",
                ),
                result=(
                    "access_token",
                    "refresh_token",
                    "expires_in",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Exchange an authorization code for tokens and refresh them before they expire.",
    ),
    ToolUseContract(
        "twenty-service-token",
        (
            ToolStep(
                "twenty_get_oauth_discovery",
                params=(),
                result=(
                    "issuer",
                    "token_endpoint",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_client_credentials_oauth_token",
                params=(
                    "client_id",
                    "client_secret",
                    "scope",
                ),
                result=(
                    "access_token",
                    "expires_in",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "NOT_FOUND", "no record, object or schema element has the id"
                    ),
                ),
            ),
        ),
        description="Obtain a workspace-scoped server-to-server token.",
    ),
    ToolUseContract(
        "twenty-verify-webhook",
        (
            ToolStep(
                "twenty_validate_webhook_signature",
                params=(
                    "payload",
                    "signature",
                    "timestamp",
                    "secret",
                ),
                result=("valid",),
                refusals=(
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
        description="Check the HMAC signature of an incoming webhook before trusting it.",
    ),
    ToolUseContract(
        "twenty-provision-api-key",
        (
            ToolStep(
                "twenty_provision_api_key",
                params=(
                    "email",
                    "password",
                    "name",
                    "expires_at",
                ),
                result=(
                    "api_key",
                    "expires_at",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
        description="Mint a long-lived API key from workspace admin credentials on a new install.",
    ),
    ToolUseContract(
        "twenty-ingest-to-graph",
        (
            ToolStep(
                "twenty_get_metadata_objects",
                params=(),
                result=("data",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                "twenty_ingest_records",
                params=(
                    "object_name",
                    "params_json",
                ),
                result=(
                    "ingested",
                    "object_name",
                ),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
        description="Pick an object and ingest its records into the knowledge graph.",
    ),
)

LINKS = (
    SurfaceLink(
        "twenty-find-contact",
        tools=(
            "twenty_find_records",
            "twenty_get_people",
            "twenty_get_person",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
            "twenty-data-steward",
        ),
        skills=(
            "twenty-contacts",
            "twenty-mcp-operations",
        ),
    ),
    SurfaceLink(
        "twenty-create-contact",
        tools=(
            "twenty_find_duplicates",
            "twenty_create_person",
            "twenty_get_person",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-update-contact",
        tools=(
            "twenty_get_person",
            "twenty_update_person",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-remove-contact",
        tools=(
            "twenty_get_person",
            "twenty_delete_person",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-find-company",
        tools=(
            "twenty_get_companies",
            "twenty_get_company",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-create-company",
        tools=(
            "twenty_find_duplicates",
            "twenty_create_company",
            "twenty_get_company",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-update-company",
        tools=(
            "twenty_get_company",
            "twenty_update_company",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-remove-company",
        tools=(
            "twenty_get_company",
            "twenty_delete_company",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-contacts",),
    ),
    SurfaceLink(
        "twenty-review-pipeline",
        tools=(
            "twenty_get_opportunities",
            "twenty_get_opportunity",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-pipeline",),
    ),
    SurfaceLink(
        "twenty-open-opportunity",
        tools=(
            "twenty_get_company",
            "twenty_create_opportunity",
            "twenty_get_opportunity",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-pipeline",),
    ),
    SurfaceLink(
        "twenty-advance-opportunity",
        tools=(
            "twenty_get_opportunity",
            "twenty_update_opportunity",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-pipeline",),
    ),
    SurfaceLink(
        "twenty-remove-opportunity",
        tools=(
            "twenty_get_opportunity",
            "twenty_delete_opportunity",
        ),
        prompts=(
            "twenty-operator",
            "twenty-sales-representative",
        ),
        skills=("twenty-pipeline",),
    ),
    SurfaceLink(
        "twenty-read-record",
        tools=(
            "twenty_get_metadata_object",
            "twenty_get_records",
            "twenty_get_record",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-write-record",
        tools=(
            "twenty_get_metadata_object",
            "twenty_create_record",
            "twenty_update_record",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-remove-record",
        tools=(
            "twenty_get_record",
            "twenty_delete_record",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-bulk-create",
        tools=(
            "twenty_find_duplicates",
            "twenty_batch_create_records",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-bulk-update",
        tools=(
            "twenty_find_records",
            "twenty_batch_update_records",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-bulk-remove",
        tools=(
            "twenty_find_records",
            "twenty_batch_delete_records",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-records",),
    ),
    SurfaceLink(
        "twenty-run-graphql",
        tools=(
            "twenty_discover_graphql_schema",
            "twenty_graphql",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=(
            "twenty-graphql",
            "twenty-mcp-operations",
        ),
    ),
    SurfaceLink(
        "twenty-run-gql",
        tools=(
            "twenty_get_metadata",
            "twenty_execute_gql",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-graphql",),
    ),
    SurfaceLink(
        "twenty-inspect-schema",
        tools=(
            "twenty_get_metadata",
            "twenty_get_metadata_objects",
            "twenty_get_metadata_object",
            "twenty_get_metadata_fields",
            "twenty_get_metadata_field",
            "twenty_get_metadata_relations",
            "twenty_get_metadata_relation",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=(
            "twenty-metadata",
            "twenty-mcp-operations",
        ),
    ),
    SurfaceLink(
        "twenty-raw-metadata-request",
        tools=(
            "twenty_get_metadata",
            "twenty_request_metadata",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-metadata",),
    ),
    SurfaceLink(
        "twenty-define-object",
        tools=(
            "twenty_get_metadata_objects",
            "twenty_create_metadata_object",
            "twenty_create_metadata_field",
            "twenty_create_metadata_relation",
            "twenty_get_metadata_object",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-metadata",),
    ),
    SurfaceLink(
        "twenty-update-schema",
        tools=(
            "twenty_get_metadata_object",
            "twenty_update_metadata_object",
            "twenty_get_metadata_field",
            "twenty_update_metadata_field",
            "twenty_get_metadata_relation",
            "twenty_update_metadata_relation",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-metadata",),
    ),
    SurfaceLink(
        "twenty-drop-schema",
        tools=(
            "twenty_get_metadata_object",
            "twenty_delete_metadata_relation",
            "twenty_delete_metadata_field",
            "twenty_delete_metadata_object",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-metadata",),
    ),
    SurfaceLink(
        "twenty-register-oauth-client",
        tools=(
            "twenty_get_oauth_discovery",
            "twenty_register_oauth_client",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-oauth",),
    ),
    SurfaceLink(
        "twenty-oauth-code-flow",
        tools=(
            "twenty_get_oauth_discovery",
            "twenty_exchange_oauth_token",
            "twenty_refresh_oauth_token",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-oauth",),
    ),
    SurfaceLink(
        "twenty-service-token",
        tools=(
            "twenty_get_oauth_discovery",
            "twenty_client_credentials_oauth_token",
        ),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-oauth",),
    ),
    SurfaceLink(
        "twenty-verify-webhook",
        tools=("twenty_validate_webhook_signature",),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-oauth",),
    ),
    SurfaceLink(
        "twenty-provision-api-key",
        tools=("twenty_provision_api_key",),
        prompts=(
            "twenty-operator",
            "twenty-crm-administrator",
        ),
        skills=("twenty-provisioner",),
    ),
    SurfaceLink(
        "twenty-ingest-to-graph",
        tools=(
            "twenty_get_metadata_objects",
            "twenty_ingest_records",
        ),
        prompts=(
            "twenty-operator",
            "twenty-data-steward",
        ),
        skills=("twenty-kg-sync",),
    ),
)

LOCATIONS = (
    DataLocation(
        "twenty-people",
        ("Person",),
        "TWENTY_URL",
        "twenty_get_people",
        store="",
        route_param="",
        federation_key="id",
    ),
    DataLocation(
        "twenty-companies",
        ("Company",),
        "TWENTY_URL",
        "twenty_get_companies",
        store="",
        route_param="",
        federation_key="id",
    ),
    DataLocation(
        "twenty-opportunities",
        (
            "Opportunity",
            "PipelineStage",
        ),
        "TWENTY_URL",
        "twenty_get_opportunities",
        store="",
        route_param="",
        federation_key="id",
    ),
    DataLocation(
        "twenty-records",
        (
            "CrmNote",
            "CrmTask",
        ),
        "TWENTY_URL",
        "twenty_get_records",
        store="",
        route_param="object_name",
        federation_key="id",
    ),
    DataLocation(
        "twenty-schema",
        ("Concept",),
        "TWENTY_URL",
        "twenty_get_metadata",
        store="",
        route_param="",
        federation_key="",
    ),
)

ROLES = (
    BusinessRole(
        "sales representative",
        tasks=(
            "twenty-find-contact",
            "twenty-create-contact",
            "twenty-update-contact",
            "twenty-remove-contact",
            "twenty-find-company",
            "twenty-create-company",
            "twenty-update-company",
            "twenty-remove-company",
            "twenty-review-pipeline",
            "twenty-open-opportunity",
            "twenty-advance-opportunity",
            "twenty-remove-opportunity",
        ),
    ),
    BusinessRole(
        "CRM administrator",
        tasks=(
            "twenty-run-graphql",
            "twenty-run-gql",
            "twenty-inspect-schema",
            "twenty-raw-metadata-request",
            "twenty-define-object",
            "twenty-update-schema",
            "twenty-drop-schema",
            "twenty-register-oauth-client",
            "twenty-oauth-code-flow",
            "twenty-service-token",
            "twenty-verify-webhook",
            "twenty-provision-api-key",
        ),
    ),
    BusinessRole(
        "data steward",
        tasks=(
            "twenty-read-record",
            "twenty-write-record",
            "twenty-remove-record",
            "twenty-bulk-create",
            "twenty-bulk-update",
            "twenty-bulk-remove",
            "twenty-ingest-to-graph",
        ),
    ),
)
