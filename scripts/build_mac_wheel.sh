#!/usr/bin/env bash

set -e
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
PROJECT_ROOT=$(realpath "$scriptDir/..")
DEFAULT_PYTHON_VENV="./wheel_builder_venv"
DEFAULT_BASE_PYTHON="python3"
DEFAULT_PYTHON_VERSION=3.10
remove_venv(){
    if [ -d $1 ]; then
        echo "removing $1"
        rm -r $1
    fi
}

generate_venv_with_venv(){
    base_python=$1
    virtual_env=$2
    trap "remove_venv $virtual_env" ERR SIGINT SIGTERM
    $base_python -m venv $virtual_env
    $virtual_env/bin/pip install --disable-pip-version-check uv
}

generate_wheel(){
    uv_exec=$1
    project_root=$2
    python_version=$3

    # Get the processor type
    processor_type=$(uname -m)

    # Set the compiling variables based on the processor results
    #
    # The values are taken from cibuildwheel source code
    # https://github.com/pypa/cibuildwheel/blob/main/cibuildwheel/macos.py
    #
    # macOS 11 is the first OS with arm64 support, so the wheels
    # have that as a minimum.

    if [ "$processor_type" == "arm64" ]; then
        _PYTHON_HOST_PLATFORM='macosx-11.0-arm64'
        MACOSX_DEPLOYMENT_TARGET='11.0'
        ARCHFLAGS='-arch arm64'
        REQUIRED_ARCH='arm64'
    elif [ "$processor_type" == "x86_64" ]; then
        _PYTHON_HOST_PLATFORM='macosx-10.15-x86_64'
        MACOSX_DEPLOYMENT_TARGET='10.15'
        ARCHFLAGS='-arch x86_64'
        REQUIRED_ARCH='x86_64'
    else
      echo "Unknown processor type: $processor_type"
    fi

    out_temp_wheels_dir=$(mktemp -d /tmp/python_wheels.XXXXXX)
    output_path="./dist"
    trap "rm -rf $out_temp_wheels_dir" ERR SIGINT SIGTERM RETURN
    UV_INDEX_STRATEGY=unsafe-best-match _PYTHON_HOST_PLATFORM=$_PYTHON_HOST_PLATFORM MACOSX_DEPLOYMENT_TARGET=$MACOSX_DEPLOYMENT_TARGET ARCHFLAGS=$ARCHFLAGS $uv_exec build --wheel --out-dir=$out_temp_wheels_dir --python=$python_version $project_root
    pattern="$out_temp_wheels_dir/*.whl"
    files=( $pattern )
    undelocate_wheel="${files[0]}"

    echo ""
    echo "================================================================================"
    echo "${undelocate_wheel} is linked to the following:"
    $uv_path run --only-group package delocate-listdeps --depending "${undelocate_wheel}"
    echo ""
    echo "================================================================================"
    $uv_path run --only-group package delocate-wheel -w $output_path --require-archs $REQUIRED_ARCH --verbose "$undelocate_wheel"
}


print_usage(){
     echo "Usage: $0 [--uv path] [--python-version version]"
}


show_help() {
  print_usage
  echo
  echo "Arguments:"
  echo "  --uv[=path]           Path to uv executable. If not provided, defaults to 'uv' and if that is missing, a copy will be downloaded."
  echo "  --python-version[=version]      Python version to generate wheel for. Default is $DEFAULT_PYTHON_VERSION."
  echo "  --help, -h            Display this help message."
}


# Check if the help flag is provided
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0
  fi
done

python_version=$DEFAULT_PYTHON_VERSION
## Parse optional arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --python-version=*)
      python_version="${1#*=}"
      shift
      ;;
    --python-version)
      python_version="$2"
      shift 2
      ;;

    --uv=*)
      uv_path="${1#*=}"
      shift
      ;;
    --uv)
      uv_path="$2"
      shift 2
      ;;

    *)
      shift
      ;;
  esac
done
if [ -z "{uv_path+x}" ]; then
  uv_path=uv
fi
if [[ ! -f "$uv_path" ]]; then
    if [[ ! -f "/tmp/uv/bin/uv" ]]; then
      generate_venv_with_venv python3 /tmp/uv
    fi
    uv_path=/tmp/uv/bin/uv
    echo "installed uv: $uv_path"
else
    echo "Using existing venv: $build_virtual_env"
fi

generate_wheel $uv_path $PROJECT_ROOT $python_version
