# Databricks notebook source
# MAGIC %md ## Import Experiments
# MAGIC 
# MAGIC Widgets
# MAGIC * `1. Input directory` - directory of exported experiments.
# MAGIC * `2. Import source tags`
# MAGIC * `3. Use threads` - use multi-threaded import
# MAGIC 
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_collection.md#Import-experiments.

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("2. Import source tags","no",["yes","no"])
import_source_tags = dbutils.widgets.get("2. Import source tags") == "yes"

dbutils.widgets.dropdown("3. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("3. Use threads") == "yes"

print("input_dir:", input_dir)
print("import_source_tags:", import_source_tags)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")

# COMMAND ----------

from mlflow_export_import.bulk.import_experiments import import_experiments

import_experiments(
    input_dir = input_dir, 
    import_source_tags = import_source_tags,
    use_threads = use_threads
)
