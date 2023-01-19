# MLflow Export Import - Governance and Lineage

MLflow provides rudimentary capabilities for tracking lineage regarding the original source objects.

There are two types of MLflow object attributes:
* **Object fields (properties)**: Standard object fields such as [RunInfo.run_id](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.RunInfo.run_id). The MLflow objects that are exported are:
  * [Experiment](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.Experiment)
  * [Run](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.RunInfo)
  * [RunInfo](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.RunInfo)
  * [Registered Model](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.model_registry.RegisteredModel)
  * [Registered Model Version](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.model_registry.ModelVersion)
* **System tags**: Key/value pairs represented as a dictionary whose keys start with *mlflow.* such as *mlflow.runId*.
  * Every object (such as Experiment or Run) can have system tags. 
  * Databricks system tags start with *mlflow.databricks* or sometimes just *mlflow* and are not publicly documented.
  * For details see: [What are the MLflow system run tags?](https://github.com/amesar/mlflow-resources/blob/master/MLflow_FAQ.md#what-are-the-mlflow-system-run-tags). 

Another dimension is how the attribute values are set. 
* **System attributes:** Auto-generated by the system such as *experiment.experiment_id* or *experiment.creation_time*.
* **User attributes:** Set by the user such as *experiment.name*.

When importing, all user attributes will be preserved "as is".
System attributes by definition cannot be preserved since MLflow will set their values when creating the new imported object.

For example, if your source *creation_time* was *2022-12-08 04:45:38*, the imported target *creation_time* value will be different such as *2023-01-14 18:14:54*.

For lineage purposes, there is an option *--import-source-tags* to preserve the original values of system attributes as tags starting with the prefix *mlflow_exim*.
When using this option, all source object fields and system tags will be imported under the *mlflow_exim* prefix.

These preserved attributes are called *source tags*.
There are two types of source tags:
* **Object field tags** - preserve the original object fields. Starts with *mlflow_exim.field* or for *mlflow_exim.run_info* for RunInfo.
* **System tags** - preserve original system tags. Starts with *mlflow_exim.mlflow_tag.*

**Experiment source tags example**
```
"experiment": {
  "creation_time": 1673720094,
  "tags": {
    "mlflow.experiment.sourceName": "/Users/andre@mycompany.com/mlflow/imported/My_Experiment_Imported",
    "mlflow_exim.mlflow_tag.experiment.sourceName": "/Users/andre@mycompany.com/mlflow/My_Experiment",
    "mlflow_exim.field.creation_time": "1670474737597"
  }
```

**Run source tags example**
```
  "mlflow": {
    "info": {
      "start_time": 1673365293970
    },
    "tags": {
      "mlflow_exim.run_info.start_time": "1670836055960",
      "mlflow.user": "admin@mycompany.com",
      "mlflow_exim.mlflow_tag.user": "andre@company.com"
  }
```