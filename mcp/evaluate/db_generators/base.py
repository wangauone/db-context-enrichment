from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import yaml
import google.cloud.geminidataanalytics_v1beta as gda
from google.protobuf.json_format import MessageToDict

class BaseDBConfigGenerator(ABC):
    """
    Abstract Base Class enforcing the construction contract for Evalbench database topologies.
    Each distinct DB type (Spanner, Postgres, AlloyDB, MySQL) must inherit and implement 
    the mappings required by both the standard EvalBench framework and the GDA SDK model.
    """
    
    REQUIRED_FIELDS = []
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.validate()
        self.project = params.get("project")
        self.region = params.get("region")
        self.instance = params.get("instance")
        self.database = params.get("database")
        self.user = params.get("user")
        self.password = params.get("password")
        self.cluster = params.get("cluster")

    @abstractmethod
    def generate_db_config(self) -> Tuple[str, str, str]:
        """
        Generates the Evalbench db_config.yaml payload natively.
        Returns:
            db_config_yaml (str): The raw string contents of the configuration.
            db_type (str): The underlying dialect type for EvalBench config (e.g. spanner).
            evalbench_dialect (str): The specific dialect format (e.g. spanner_gsql).
        """
        pass

    @abstractmethod
    def build_datasource_reference(self, context_set_id: str) -> gda.DatasourceReferences:
        """
        Constructs the strict Protocol Buffer DatasourceReference required by the QueryDataAPI 
        context generation flow.
        """
        pass

    def validate(self) -> None:
        """
        Validates that the provided tools.yaml source configuration block contains all 
        the mandatory fields required by the specific Evalbench topology.
        """
        toolbox_source_type = self.params.get("toolbox_source_type", "unknown")
        missing = [f for f in self.REQUIRED_FIELDS if f not in self.params]
        if missing:
            raise ValueError(
                f"Missing required fields in tools.yaml config for '{toolbox_source_type}': "
                f"{', '.join(missing)}"
            )

    def generate_model_config(self, context_set_id: str) -> str:
        """
        Standardized Model Builder converting the strictly typed GDA object into an EvalBench model dict.
        """
        datasource_ref = self.build_datasource_reference(context_set_id)
        
        query_context = gda.QueryDataContext(
            datasource_references=datasource_ref
        )

        query_context_dict = MessageToDict(
            query_context._pb, 
            preserving_proto_field_name=True
        )

        model_config = {
            "generator": "query_data_api",
            "project_id": self.project,
            "location": self.region or "global",
            "context": query_context_dict
        }
        
        return yaml.dump(model_config, sort_keys=False, default_flow_style=False).strip()
