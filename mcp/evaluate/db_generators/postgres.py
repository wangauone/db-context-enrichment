from typing import Tuple
import textwrap
import google.cloud.geminidataanalytics_v1beta as gda
from .base import BaseDBConfigGenerator

class PostgresGenerator(BaseDBConfigGenerator):
    """
    Dedicated generator mapping properties to explicit Cloud SQL Postgres configuration
    topologies utilized by both EvalBench binaries and GDA Context objects.
    """
    REQUIRED_FIELDS = ["project", "region", "instance", "database", "user", "password"]
    
    def generate_db_config(self) -> Tuple[str, str, str]:
        db_type = "postgres"
        dialect = "postgres"
        db_path = f"{self.project}:{self.region}:{self.instance}"
        
        db_config_yaml = textwrap.dedent(f"""\
            db_type: {db_type}
            dialect: {dialect}
            database_name: {self.database}
            database_path: {db_path}
            max_executions_per_minute: 180
            user_name: {self.user}
            password: {self.password}
        """)
        return db_config_yaml.strip(), db_type, dialect

    def build_datasource_reference(self, context_set_id: str) -> gda.DatasourceReferences:
        datasource_ref = gda.DatasourceReferences()
        
        datasource_ref.cloud_sql_reference = gda.CloudSqlReference(
            database_reference=gda.CloudSqlDatabaseReference(
                engine=gda.CloudSqlDatabaseReference.Engine.POSTGRESQL,
                project_id=self.project,
                region=self.region,
                instance_id=self.instance,
                database_id=self.database
            ),
            agent_context_reference=gda.AgentContextReference(
                context_set_id=context_set_id
            )
        )
        return datasource_ref
