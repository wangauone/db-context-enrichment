import json
import textwrap
from typing import Dict, Any, Union

from .db_generators.base import BaseDBConfigGenerator
from .db_generators.alloydb import AlloyDBGenerator
from .db_generators.spanner import SpannerGenerator
from .db_generators.postgres import PostgresGenerator
from .db_generators.mysql import MySQLGenerator

# Dependencies resolved externally


def generate_evalbench_configs(
    experiment_name: str,
    dataset_path: str,
    context_set_id: str,
    toolbox_db_info: Union[str, Dict[str, Any]]
) -> Dict[str, str]:
    """
    Main entrypoint: Generates Evalbench-compatible YAML configurations natively using 
    private DB format converters and the google-cloud-geminidataanalytics API validations.
    """
    params = _extract_toolbox_params(toolbox_db_info)
    generator: BaseDBConfigGenerator = _get_db_generator(params)
    
    db_config_yaml, _, evalbench_dialect = generator.generate_db_config()
    model_config_yaml = generator.generate_model_config(context_set_id)
    run_config_yaml = _generate_run_config(experiment_name, dataset_path, evalbench_dialect)

    return {
        "db_config.yaml": db_config_yaml,
        "model_config.yaml": model_config_yaml,
        "run_config.yaml": run_config_yaml
    }


def _extract_toolbox_params(toolbox_db_info: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Safely extracts and standardizes the database connection dictionary."""
    if isinstance(toolbox_db_info, str):
        try:
            toolbox_db_info = json.loads(toolbox_db_info)
        except json.JSONDecodeError as e:
            raise ValueError(f"toolbox_db_info must be a valid JSON dictionary: {e}") from e
    
    toolbox_source_type = toolbox_db_info.get("type", "").lower()
    if not toolbox_source_type:
        raise ValueError("Missing required field 'type' in the parsed tools.yaml 'kind: source' block")

    # We still ensure toolbox_source_type is injected if they fetched it cleanly
    toolbox_db_info["toolbox_source_type"] = toolbox_source_type
    return toolbox_db_info


def _get_db_generator(params: Dict[str, Any]) -> BaseDBConfigGenerator:
    """Factory function to build the correct Evaluation Generator."""
    toolbox_source_type = params["toolbox_source_type"]
    
    if "alloydb" in toolbox_source_type:
        return AlloyDBGenerator(params)
    elif "spanner" in toolbox_source_type:
        return SpannerGenerator(params)
    elif "mysql" in toolbox_source_type:
        return MySQLGenerator(params)
    else:
        return PostgresGenerator(params)


def _generate_run_config(experiment_name: str, dataset_path: str, dialect: str) -> str:
    """Generates the main EvalBench Run Experiment scaffolding."""
    return textwrap.dedent(f"""\
        ############################################################
        ### Dataset / Eval Items
        ############################################################
        dataset_config: {dataset_path}
        database_configs:
         - experiments/{experiment_name}/eval_configs/db_config.yaml
        dialects:
         - {dialect}
        query_types:
         - dql

        ############################################################
        ### Prompt and Generation Modules
        ############################################################
        model_config: experiments/{experiment_name}/eval_configs/model_config.yaml
        prompt_generator: 'SQLGenBasePromptGenerator'

        ############################################################
        ### Scorer Related Configs
        ############################################################
        scorers:
          exact_match: null
          executable_sql: null

        {_generate_reporting(experiment_name)}
    """).strip()


def _generate_reporting(experiment_name: str) -> str:
    """Returns the reporting configuration isolated."""
    return textwrap.dedent(f"""\
        ############################################################
        ### Reporting Related Configs
        ############################################################
        reporting:
          csv:
            output_directory: 'experiments/{experiment_name}/eval_reports/'
    """).strip()
