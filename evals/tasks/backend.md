# Backend Golden Tasks

## Task: multi-tenant-schema
- **Skill:** @postgresql
- **Prompt:** Design a PostgreSQL schema for a multi-tenant SaaS invoicing product: tenants, users, invoices, line items. Show the DDL and explain your tenancy isolation choice.
- **Rubric:**
  - Names a tenancy model (shared schema with tenant_id, schema-per-tenant, or database-per-tenant) and justifies the choice
  - Every tenant-scoped table carries and indexes the tenant key
  - Mentions row-level security or an equivalent enforcement mechanism
  - DDL is valid PostgreSQL with sensible types and constraints

## Task: idempotent-webhook
- **Skill:** @api-design-principles
- **Prompt:** Design the endpoint contract and processing flow for receiving payment webhooks that may be delivered more than once. Show the endpoint spec and the idempotency approach.
- **Rubric:**
  - Uses an idempotency key or event id with a persisted dedupe record
  - Returns 2xx for duplicates without re-processing side effects
  - Handles out-of-order delivery explicitly
  - Specifies retry/backoff expectations for the sender

## Task: n-plus-one
- **Skill:** @postgresql
- **Prompt:** This ORM code lists 50 orders and then fetches each order's customer and items in a loop. Explain the failure mode and rewrite the data access to fix it.
- **Rubric:**
  - Names the N+1 query problem explicitly
  - Fix uses joins, batched IN queries, or the ORM's eager loading
  - Quantifies the query count before and after
  - Notes when the fix should NOT be applied (small N, cold paths)
