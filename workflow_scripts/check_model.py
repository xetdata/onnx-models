# SPDX-License-Identifier: Apache-2.0

from cpuinfo import get_cpu_info
import ort_test_dir_utils
import onnxruntime
import onnx
import os
from shutil import rmtree
import tarfile
import test_utils


def has_vnni_support():
    return "avx512vnni" in set(get_cpu_info()["flags"])


def run_onnx_checker(model_path):
    model = onnx.load(model_path)
    onnx.checker.check_model(model)


def ort_skip_reason(model_path):
    if (model_path.endswith("-int8.onnx") or model_path.endswith("-qdq.onnx")) and not has_vnni_support():
        # At least run InferenceSession to test shape inference
        onnxruntime.InferenceSession(model_path)
        return f"Skip ORT test for {model_path} because this machine lacks avx512vnni support and the output.pb was produced with avx512vnni support."
    model = onnx.load(model_path)
    if model.opset_import[0].version < 7:
        return f"Skip ORT test for {model_path} because ORT only supports opset version >= 7"
    return None


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz", format=tarfile.GNU_FORMAT) as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def run_backend_ort(model_path, test_data_set=None, tar_gz_path=None):
    skip_reason = ort_skip_reason(model_path)
    if skip_reason:
        print(skip_reason)
        return
    # if "test_data_set_N" doesn't exist, create test_dir
    if not test_data_set:
        # Start from ORT 1.10, ORT requires explicitly setting the providers parameter if you want to use execution providers
        # other than the default CPU provider (as opposed to the previous behavior of providers getting set/registered by default
        # based on the build flags) when instantiating InferenceSession.
        # For example, if NVIDIA GPU is available and ORT Python package is built with CUDA, then call API as following:
        # onnxruntime.InferenceSession(path/to/model, providers=["CUDAExecutionProvider"])
        onnxruntime.InferenceSession(model_path)
        # Get model name without .onnx
        model_name = os.path.basename(os.path.splitext(model_path)[0])
        if model_name is None:
            print(f"The model path {model_path} is invalid")
            return
        ort_test_dir_utils.create_test_dir(model_path, "./", test_utils.TEST_ORT_DIR)
        ort_test_dir_utils.run_test_dir(test_utils.TEST_ORT_DIR)
        if os.path.exists(model_name) and os.path.isdir(model_name):
            rmtree(model_name)
        os.rename(test_utils.TEST_ORT_DIR, model_name)
        make_tarfile(tar_gz_path, model_name)
        rmtree(model_name)
    # otherwise use the existing "test_data_set_N" as test data
    else:
        test_dir_from_tar = test_utils.get_model_directory(model_path)
        ort_test_dir_utils.run_test_dir(test_dir_from_tar)
    # remove the produced test_dir from ORT
    test_utils.remove_onnxruntime_test_dir()
