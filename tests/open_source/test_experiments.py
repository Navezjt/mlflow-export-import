from mlflow_export_import.experiment.export_experiment import ExperimentExporter
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from oss_utils_test import create_simple_run, init_output_dirs, create_dst_experiment_name
from compare_utils import compare_runs
from compare_utils import dump_runs
from init_tests import mlflow_context

_use_source_tags = True

# == Setup

def _init_exp_test(mlflow_context, exporter, importer, verbose=False):
    init_output_dirs(mlflow_context.output_dir)
    exp1, run1 = create_simple_run(mlflow_context.client_src)
    run1 = mlflow_context.client_src.get_run(run1.info.run_id)
    exporter.export_experiment(exp1.name, mlflow_context.output_dir)

    experiment_name = create_dst_experiment_name(exp1.name)
    importer.import_experiment(experiment_name, mlflow_context.output_dir)
    exp2 = mlflow_context.client_dst.get_experiment_by_name(experiment_name)
    runs = mlflow_context.client_dst.search_runs(exp2.experiment_id)
    run2 = mlflow_context.client_dst.get_run(runs[0].info.run_id)

    if verbose: dump_runs(run1, run2)
    return exp1, exp2, run1, run2


def _compare_experiments(exp1, exp2):
    assert exp1.name == exp2.name
    assert exp1.lifecycle_stage == exp2.lifecycle_stage
    assert exp1.tags == exp2.tags
    assert exp1.tags == exp2.tags
    assert exp1.tags == exp2.tags
    assert exp1.artifact_location != exp2.artifact_location


def test_exp_basic(mlflow_context):
    exp1, exp2, run1, run2 = _init_exp_test(mlflow_context,
        ExperimentExporter(mlflow_context.client_src),
        ExperimentImporter(mlflow_context.client_dst), 
        True)
    _compare_experiments(exp1, exp2)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)


def test_exp_with_source_tags(mlflow_context):
    exp1, exp2, run1, run2 = _init_exp_test(mlflow_context,
       ExperimentExporter(mlflow_context.client_src, export_source_tags=True), 
       ExperimentImporter(mlflow_context.client_dst), verbose=False)
    _compare_experiments(exp1, exp2)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir, _use_source_tags)
