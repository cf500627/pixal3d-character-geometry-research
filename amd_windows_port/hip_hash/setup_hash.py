"""Portable packaging adapter; original HIP hash mathematics remain unchanged.
The API header is included with its original author notice.
ROCm dependency headers are obtained separately under their own licenses.
"""
import os
from pathlib import Path
from setuptools import setup
from torch.utils.cpp_extension import CUDAExtension, BuildExtension, IS_HIP_EXTENSION
if not IS_HIP_EXTENSION:
    raise RuntimeError("Use the validated Windows ROCm Torch runtime")
base = Path(__file__).resolve().parent
sdk = Path(os.environ['HIP_PATH'])
headers = Path(os.environ['HIP_HASH_DEPENDENCIES'])
setup(name='native-hip-hash', ext_modules=[CUDAExtension(
    name='_stage7e_hash', sources=[str(base/'bindings.cpp'),str(base/'src/hash.cu')],
    include_dirs=[str(base/'src'),str(headers/'generated_include'),str(headers/'generated_include/rocprim'),
                  str(headers/'rocThrust'),str(headers/'rocPRIM/rocprim/include')],
    extra_compile_args={'cxx':['/O2','/std:c++17','/EHsc','/bigobj','/DNOMINMAX'],
                        'nvcc':['-O2','-std=c++17','--rocm-device-lib-path='+str(sdk/'lib/llvm/amdgcn/bitcode')]}
)], cmdclass={'build_ext':BuildExtension.with_options(use_ninja=True)})
