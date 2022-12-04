from mlflow_export_import.source_tags import ImportTags
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.model.import_model import ModelImporter
from mlflow_export_import.model.import_model import _extract_model_path

import oss_utils_test 
from compare_utils import compare_models_with_versions, _compare_models, _compare_versions
from init_tests import mlflow_context


# Test stages

def test_export_import_model_1_stage(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=["Production"] )
    assert len(model_dst.latest_versions) == 1
    compare_models_with_versions(mlflow_context.client_src, mlflow_context.client_dst,  model_src, model_dst, mlflow_context.output_dir)


def test_export_import_model_2_stages(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=["Production","Staging"])
    assert len(model_dst.latest_versions) == 2
    compare_models_with_versions(mlflow_context.client_src, mlflow_context.client_dst,  model_src, model_dst, mlflow_context.output_dir)


def test_export_import_model_all_stages(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=None)
    assert len(model_dst.latest_versions) == 4
    compare_models_with_versions(mlflow_context.client_src, mlflow_context.client_dst,  model_src, model_dst, mlflow_context.output_dir)


# Test stages and versions

def test_export_import_model_both_stages(mlflow_context):
    try:
        _run_test_export_import_model_stages(mlflow_context,  stages=["Production"], versions=[1])
    except MlflowExportImportException:
        # "Both stages {self.stages} and versions {self.versions} cannot be set")
        pass


# Test versions

def _get_version_ids(model):
    return [vr.version for vr in model.latest_versions ]


def _get_version_ids_2(model):
    return [vr.tags[ImportTags.TAG_VERSION] for vr in model.latest_versions ]


def test_export_import_model_first_two_versions(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, versions=["1","2"])
    assert len(model_dst.latest_versions) == 2
    compare_models_with_versions(mlflow_context.client_src, mlflow_context.client_dst,  model_src, model_dst, mlflow_context.output_dir)
    ids_src = _get_version_ids(model_src)
    ids_dst = _get_version_ids(model_dst)
    for j, id in enumerate(ids_dst):
        assert(id == ids_src[j])


def _compare_models_with_versions(mlflow_client_src, mlflow_client_dst, model_src, model_dst, output_dir):
    _compare_models(model_src, model_dst, mlflow_client_src!=mlflow_client_dst)
    for (vr_src, vr_dst) in zip(model_src.latest_versions, model_dst.latest_versions):
        _compare_versions(mlflow_client_src, mlflow_client_dst, vr_src, vr_dst, output_dir)


def test_export_import_model_two_from_middle_versions(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, versions=["2","3","4"])
    assert len(model_dst.latest_versions) == 3
    ids_src = _get_version_ids(model_src)
    ids_dst = _get_version_ids_2(model_dst)
    assert set(ids_dst).issubset(set(ids_src))

    _compare_models(model_src, model_dst, mlflow_context.client_src!=mlflow_context.client_dst)
    for vr_dst in model_dst.latest_versions:
        vr_src_id = vr_dst.tags[ImportTags.TAG_VERSION]
        vr_src = [vr for vr in model_src.latest_versions if vr.version == vr_src_id ]
        assert(len(vr_src)) == 1
        vr_src = vr_src[0]
        assert(vr_src.version == vr_src_id)
        _compare_versions(mlflow_context.client_src, mlflow_context.client_dst, vr_src, vr_dst, mlflow_context.output_dir)


# Internal

def _run_test_export_import_model_stages(mlflow_context, stages=None, versions=None):
    exporter = ModelExporter(mlflow_context.client_src, stages=stages, versions=versions)
    model_name_src = oss_utils_test.mk_test_object_name_default()
    desc = "Hello decription"
    tags = { "city": "franconia" }
    model_src = mlflow_context.client_src.create_registered_model(model_name_src, tags, desc)

    _create_version(mlflow_context.client_src, model_name_src, "Production")
    _create_version(mlflow_context.client_src, model_name_src, "Staging")
    _create_version(mlflow_context.client_src, model_name_src, "Archived")
    _create_version(mlflow_context.client_src, model_name_src, "None")
    model_src = mlflow_context.client_src.get_registered_model(model_name_src)
    exporter.export_model(model_name_src, mlflow_context.output_dir)

    model_name_dst = oss_utils_test.create_dst_model_name(model_name_src)
    experiment_name =  model_name_dst
    importer = ModelImporter(mlflow_context.client_dst, import_source_tags=True)
    importer.import_model(model_name_dst, 
        mlflow_context.output_dir, 
        experiment_name, delete_model=True, 
        verbose=False, 
        sleep_time=10)

    model_dst = mlflow_context.client_dst.get_registered_model(model_name_dst)
    return model_src, model_dst


def _create_version(client, model_name, stage=None):
    run = _create_run(client)
    source = f"{run.info.artifact_uri}/model"
    desc = "My version desc"
    tags = { "city": "franconia" }
    vr = client.create_model_version(model_name, source, run.info.run_id, description=desc, tags=tags)
    if stage:
        vr = client.transition_model_version_stage(model_name, vr.version, stage)
    return vr


def _create_run(client):
    _, run = oss_utils_test.create_simple_run(client)
    return client.get_run(run.info.run_id)


# Simple tests for parsing

_run_id = "48cf29167ddb4e098da780f0959fb4cf"
_model_path = "models:/my_model"


def test_extract_model_path_databricks(mlflow_context):
    source = f"dbfs:/databricks/mlflow-tracking/4072937019901104/{_run_id}/artifacts/{_model_path}"
    _run_test_extract_model_path(source)


def test_extract_model_path_oss(mlflow_context):
    source = f"/opt/mlflow_context/local_mlrun/mlruns/3/{_run_id}/artifacts/{_model_path}"
    _run_test_extract_model_path(source)


def _run_test_extract_model_path(source):
    model_path2 = _extract_model_path(source, _run_id)
    assert _model_path == model_path2
