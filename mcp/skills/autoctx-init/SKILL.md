---
name: autoctx-init
description: Orchestrates the initialization workflow for the auto context generation for the DB Data Agent.
---

# Auto Context Generation Initialization

This skill guides the user through scaffolding a new environment for the DB Data Agent auto context generation. It relies on the `database-connectivity` skill to seamlessly generate the required database configurations.

## Input

To initialize the environment, you must delegate the collection of database connection details entirely to the `database-connectivity` skill. 
Do not assume which parameters are needed. The required inputs depend entirely on the target database type and the structure defined within the `database-connectivity` skill.
If the user hasn't provided the necessary details, rely on the `database-connectivity` skill to determine exactly what to ask them.

## Workflow

Follow these steps sequentially to complete the initialization:

1.  **Confirm Working Directory:** Explicitly state the current working directory to the user. Explain that the initialization (creating `tools.yaml`, `state.md`, etc.) will occur in this directory. Ask them to confirm if this is the correct location, or if they would prefer to target a different folder before proceeding. Proceed only after obtaining their confirmation.
2.  **Activate Database Connectivity Skill:** Use the `activate_skill` tool to load the `database-connectivity` skill into your context.
3.  **Generate `tools.yaml`:** Follow the directions in the `database-connectivity` skill to determine the required parameters, collect them from the user, and create the `configs/tools.yaml` file.
4.  **Create State Tracker:** Use your file management tools to create a `state.md` file in the approved directory. Include a brief header explaining it tracks dynamic experiment state and active Context Set IDs.
5.  **Initialize Reporting Directory:** Create an empty `reporting_output/` directory in the approved directory to hold all future evaluation logs.
6.  **Validate Connection:** Execute the validation command specified by the `database-connectivity` skill to perform a dry-run and ensure the newly generated `tools.yaml` can successfully connect to the database.

## Output

Upon successful completion, the workspace must contain:
- `configs/tools.yaml`: A structurally sound configuration file for the Toolbox MCP Server.
- `state.md`: The external state tracker for hill-climbing iterations.
- `reporting_output/`: The base directory prepared for evaluation runs.

## Final Summary

Conclude the command by providing a succinct, easy-to-read summary to the user. Ensure your message clearly states:
- The "auto context generation for DB Data Agent" workspace was initialized successfully.
- All folders and files (`tools.yaml`, `state.md`, `reporting_output/`) have been scaffolded.
- The database connectivity dry-run succeeded.
- The user is now ready to proceed to the next phase (e.g., the Bootstrap workflow).
