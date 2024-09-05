#!/usr/bin/env bash

set -e

DEFAULT_PYTHON_VENV="./wheel_builder_venv"
DEFAULT_BASE_PYTHON="python3"

remove_venv(){
    if [ -d $1 ]; then
        echo "removing $1"
        rm -r $1
    fi
}

generate_venv(){
    base_python=$1
    virtual_env=$2
    trap "remove_venv $virtual_env" ERR SIGINT SIGTERM
    $base_python -m venv $virtual_env
    . $virtual_env/bin/activate
    pip install uv
    UV_INDEX_STRATEGY=unsafe-best-match uv pip install wheel==0.37 build delocate
}

generate_wheel(){
    virtual_env=$1
    . $virtual_env/bin/activate
    python --version

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
    UV_INDEX_STRATEGY=unsafe-best-match _PYTHON_HOST_PLATFORM=$_PYTHON_HOST_PLATFORM MACOSX_DEPLOYMENT_TARGET=$MACOSX_DEPLOYMENT_TARGET ARCHFLAGS=$ARCHFLAGS python -m build --wheel --installer=uv --outdir=$out_temp_wheels_dir
    pattern="$out_temp_wheels_dir/*.whl"
    files=( $pattern )
    undelocate_wheel="${files[0]}"

    echo ""
    echo "================================================================================"
    echo "${undelocate_wheel} is linked to the following:"
    delocate-listdeps --depending "${undelocate_wheel}"
    echo ""
    echo "================================================================================"
    delocate-wheel -w $output_path --require-archs $REQUIRED_ARCH --verbose "$undelocate_wheel"
}

print_usage(){
    echo "Usage: $0 project_root [--venv_path optional_path]"
}

show_help() {
  print_usage
  echo
  echo "Arguments:"
  echo "  project_root          Path to Python project containing pyproject.toml file."
  echo "  --venv_path[=path]    Path used to install build tools. Defaults to '$DEFAULT_PYTHON_VENV'."
  echo "  --help, -h            Display this help message."
}


check_args(){
    if [[ -f "$project_root" ]]; then
        echo "error: project_root should point to a directory not a file"
        print_usage
        exit
    fi
    if [[ ! -f "$project_root/pyproject.toml" ]]; then
        echo "error: $project_root contains no pyproject.toml"
        exit
    fi
}

# Check if the help flag is provided
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0
  fi
done

# Check if the project_root argument is provided
if [ -z "$1" ]; then
  print_usage
  exit 1
fi

# Assign the project_root argument to a variable
project_root=$1

# venv_path value is set to default
venv_path=$DEFAULT_PYTHON_VENV

# base_python_path value is set to default
base_python_path=$DEFAULT_BASE_PYTHON

# Parse optional arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --venv-path=*)
      venv_path="${1#*=}"
      shift
      ;;
    --venv-path)
      venv_path="$2"
      shift 2
      ;;

    --base-python=*)
      base_python_path="${1#*=}"
      shift
      ;;
    --base-python)
      base_python_path="$2"
      shift 2
      ;;

    *)
      shift
      ;;
  esac
done

# Output the values

check_args

build_virtual_env=$venv_path
if [[ ! -f "$build_virtual_env/bin/python" ]]; then
    generate_venv $base_python_path $build_virtual_env
else
    echo "Using existing venv: $build_virtual_env"
fi

generate_wheel $build_virtual_env $project_root
