---
name: skill-autoctx-bootstrap
description: Guides the agent to bootstrap an initial context set (templates & facets) by deducing key information from the database schema and generating a ContextSet file.
---

# Auto Context Generation - Bootstrap Workflow

This skill guides the process of bootstrapping an initial ContextSet (baseline context) from the target database schema.

## Workflow

Follow these steps exactly in order:

1. **Schema Retrieval:**
   - Use the available Toolbox MCP tools (e.g., `list_schema` or equivalent) configured in the active `tools.yaml` to fetch the schemas for the target database.
   - If the schema is large, ask the user if they want to filter or focus on specific tables before fetching everything.

2. **Deduce Key Info for Context:**
   - **Analyze** the retrieved schema to identify important concepts, relationships, or likely query patterns.
   - **Templates**: Deduce key information for a set of query templates. For each, you need the natural language question (`question`), the corresponding `sql`, and the overall `intent`.
   - **Facets**: Deduce key information for a set of SQL facets (reusable filters, conditions, expressions). For each, you need the `sql_snippet` and the `intent`.
   - *Review Check:* Briefly display the deduced key info (templates and facets) to the user for approval or modifications before proceeding.

3. **Context Generation:**
   - Once the user approves the key information, use the `generate_bootstrap_context` tool.
   - You must provide the exact `output_file_path` indicating where the `.json` file should be saved in the local workspace.
   - Pass the deduced key info as JSON parameters (`templates_json`, `facets_json`) matching the tool's expected schema.

4. **Final Summary:**
   - Confirm to the user that the bootstrap context file has been successfully generated and saved.
   - Mention the final file path and suggest any next steps (e.g., triggering an evaluation).
