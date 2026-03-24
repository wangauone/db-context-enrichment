---
name: autoctx-init
description: Orchestrates the initialization workflow for the auto context generation for the DB Data Agent. This skill also handles setting up and validating database connections (AlloyDB, Cloud SQL, Spanner).
---

# Auto Context Generation Initialization

This skill creates a new environment for the DB Data Agent auto context generation. It handles creating necessary tracker tracking files, output directories, and directly assists users in creating a valid `tools.yaml` connection file for the GenAI Toolbox.

## Environment Variable Support

The `tools.yaml` file supports environment variable substitution using the `${VARIABLE_NAME}` syntax. This is recommended for sensitive information such as database users and passwords.

When collecting information from the user, you should offer the option to use environment variables for sensitive fields. For example:
-   Instead of a hardcoded password, the user can provide `${DB_PASSWORD}`.
-   Ensure the user understands they must set the corresponding environment variable in their shell or environment before running the tools.

## Input

To initialize the environment, perform the step-by-step workflow below. You must handle the collection of database connection details internally. Do not load any external skills.

## Workflow

Follow these steps sequentially to complete the initialization:

1.  **Confirm Working Directory:** Explicitly state the current working directory to the user. Explain that the initialization (creating `tools.yaml`, `state.md`, etc.) will occur in this directory. Ask them to confirm if this is the correct location, or if they would prefer to target a different folder before proceeding. Proceed only after obtaining their confirmation.
2.  **Check Existing Configuration:** Use your file reading tools to check if a `tools.yaml` file already exists in the approved directory. 
    - **If it exists:** Inform the user that an existing database configuration was found, and skip directly to **Step 6**.
    - **If it does NOT exist:** Proceed to **Step 3** to configure a new database connection.
3.  **Identify Database Type:** Ask the user which target database they want to configure. The supported types are:
    - Cloud SQL Postgres
    - Cloud SQL MySQL
    - AlloyDB Postgres
    - Spanner
4.  **Collect Database Parameters:** Based on the user's selection, request all **Required Information** as detailed in `references/` folder. Remember to recommend environment variables for passwords.
5.  **Generate `tools.yaml`:** Select the matching template from the references folder, replace all placeholders with the user's provided values, and write the complete `tools.yaml` file to the approved directory.
6.  **Create State Tracker:** Use your file management tools to create a `state.md` file in the approved directory. Include a brief header explaining it tracks dynamic experiment state and active Context Set IDs.
7.  **Initialize Reporting Directory:** Create an empty `reporting_output/` directory in the approved directory to hold all future evaluation logs.
8.  **Validate Connection:** Execute the validation command specified below to perform a dry-run and ensure the `tools.yaml` can successfully connect to the database (if no data source name is known because the file already existed, try parsing it or ask the user to confirm it works):
    `<skill_dir>/scripts/toolbox --tools-file tools.yaml invoke <data_source_name>-list-schemas`
9.  **Apply Changes:** Upon successful validation, return a message to the user instructing them to run `/mcp refresh` to apply the database connections.

## Templates & Reference

For the specific fields required for each database type and the exact YAML structure to use, refer to the `references/` directory included in this skill's folder.

## Output

Upon successful completion, the workspace must contain:
- `tools.yaml`: A structurally sound configuration file for the Toolbox MCP Server.
- `state.md`: The external state tracker for hill-climbing iterations.
- `reporting_output/`: The base directory prepared for evaluation runs.

## Final Summary

Conclude the command by providing a succinct, easy-to-read summary to the user. Ensure your message clearly states:
- The "auto context generation for DB Data Agent" workspace was initialized successfully.
- All folders and files (`tools.yaml`, `state.md`, `reporting_output/`) have been scaffolded.
- The database connectivity dry-run succeeded.
- Instruct the user to run `/mcp refresh` to apply the changes.
- The user is now ready to proceed to the next phase (e.g., the Bootstrap workflow).
