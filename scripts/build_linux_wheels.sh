#!/usr/bin/env bash

set -e
scriptDir=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
PROJECT_ROOT=$(realpath "$scriptDir/..")
DEFAULT_PYTHON_VERSION="3.10"
DOCKERFILE=$(realpath "$scriptDir/resources/package_for_linux/Dockerfile")
DEFAULT_DOCKER_IMAGE_NAME="pyexiv2bind_builder"
OUTPUT_PATH="$PROJECT_ROOT/dist"
DEFAULT_BUILD_CONSTRAINTS="requirements-dev.txt"
REMOVE_DIRS_FIRST=( \
  'py3exiv2bind.egg-info' \
  'build' \
  )

REMOVE_FILES_FIRST=(
  'CMakeUserPresets.json'
  )

arch=$(uname -m)

case "$arch" in
  x86_64|amd64)
    DEFAULT_PLATFORM="linux/amd64"
    ;;
  aarch64|arm64)
    DEFAULT_PLATFORM="linux/arm64"
    ;;
  *)
    echo "Architecture: Unknown ($arch)"
    ;;
esac


generate_wheel(){
    platform=$1
    local docker_image_name_to_use=$2
    local constraints_file=$3
    local python_versions_to_use=("${@:4}")

    case $platform in
        linux/amd64)
            manylinux_image=quay.io/pypa/manylinux_2_28_x86_64
            ;;
        linux/arm64)
            manylinux_image=quay.io/pypa/manylinux_2_28_aarch64
            ;;
        *)
            echo "Unsupported platform: $platform"
            exit 1
    esac

    docker build \
        -t $docker_image_name_to_use \
        --platform=$platform \
        -f "$DOCKERFILE" \
        --build-arg CONAN_CENTER_PROXY_V1_URL \
        --build-arg PIP_EXTRA_INDEX_URL \
        --build-arg PIP_INDEX_URL \
        --build-arg UV_EXTRA_INDEX_URL \
        --build-arg UV_INDEX_URL \
        --build-arg UV_CONSTRAINT=$constraints_file \
        --build-arg manylinux_image=$manylinux_image \
        "$PROJECT_ROOT"

    mkdir -p "$OUTPUT_PATH"
    echo "Building wheels for Python versions: ${python_versions_to_use[*]}"
    CONTAINER_WORKSPACE=/tmp/workspace
    COMMAND="echo 'Making a shadow copy to prevent modifying local files' && \
            mkdir -p ${CONTAINER_WORKSPACE} && \
            lndir -silent /project/ ${CONTAINER_WORKSPACE} && \
            for d in "${REMOVE_DIRS_FIRST[@]}"; do
                OFFENDING_PATH=${CONTAINER_WORKSPACE}/\$d
                if [ -d \"\$OFFENDING_PATH\" ]; then
                  echo \"Removing copy from temporary working path to avoid issues: \$OFFENDING_PATH\";
                  rm -rf \$OFFENDING_PATH;
                fi; \
            done && \
            for f in "${REMOVE_FILES_FIRST[@]}"; do
                OFFENDING_FILE=${CONTAINER_WORKSPACE}/\$f
                if [ -f \"\$OFFENDING_FILE\" ]; then
                  echo \"Removing copy from temporary working path to avoid issues: \$OFFENDING_FILE\";
                  rm \$OFFENDING_FILE;
                fi; \
            done && \
            echo 'Removing Python cache files' && \
            find ${CONTAINER_WORKSPACE} -type d -name '__pycache__' -exec rm -rf {} + && \
            find ${CONTAINER_WORKSPACE} -type f -name '*.pyc' -exec rm -f {} + && \
            for i in "${python_versions_to_use[@]}"; do
                echo \"Creating wheel for Python version: \$i\";
                uv build --python=\$i --python-preference=system --build-constraints=/project/$constraints_file --wheel --out-dir=/tmp/dist ${CONTAINER_WORKSPACE};
                if [ \$? -ne 0 ]; then
                  echo \"Failed to build wheel for Python \$i\";
                  exit 1;
                fi; \
            done && \
            echo 'Fixing up wheels' && \
            auditwheel -v repair /tmp/dist/*.whl -w /dist/;
            for file in /dist/*manylinux*.whl; do
                auditwheel show \$file
            done && \
            echo 'Done'
            "
    docker run --rm \
        --platform=$platform \
        -v "$PROJECT_ROOT":/project:ro \
        -v $OUTPUT_PATH:/dist \
        --entrypoint="/bin/bash" \
        $docker_image_name_to_use \
        -c "$COMMAND"
    echo "Built wheel can be found in '$OUTPUT_PATH'"
}
print_usage(){
    echo "Usage: $0 [--project-root[=PROJECT_ROOT]] [--python-version[=PYTHON_VERSION]] [--help]"
}
#
show_help() {
  print_usage
  echo
  echo "Arguments:                                                                      "
  echo "  --project-root   : Path to Python project containing pyproject.toml file.     "
  echo "                   Defaults to current directory.                               "
  echo "  --python-version : Version of Python wheel to build. This can be specified    "
  echo "                   multiple times to build for multiple versions.               "
  echo "                   Defaults to \"$DEFAULT_PYTHON_VERSION\".                     "
  echo "  --platform       : Platform to build the wheel for.                           "
  echo "                   Defaults to \"$DEFAULT_PLATFORM\".                           "
  echo "  --docker-image-name                                                           "
  echo "                   : Name of the Docker image to use for building the wheel.    "
  echo "                   Defaults to \"$DEFAULT_DOCKER_IMAGE_NAME\".                  "
  echo "  --build-constraints-file                                                      "
  echo "                   : File to use for build constraints. This must be within the "
  echo "                   root of the repository.                                      "
  echo "                   Defaults to \"$DEFAULT_BUILD_CONSTRAINTS\"                   "
  echo "  --help, -h       : Display this help message.                                 "
}


check_args(){
    if [[ -f "$PROJECT_ROOT" ]]; then
        echo "error: PROJECT_ROOT should point to a directory not a file"
        print_usage
        exit 1
    fi
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        echo "error: $PROJECT_ROOT contains no pyproject.toml"
        exit 1
    fi

    if [[ "$build_constraints_file" = /* ]]; then
      echo "The build constraints file '$build_constraints_file' cannot be an absolute path."
      exit 1
    fi

    if [[ ! -f "$build_constraints_file" ]]; then
      echo "No valid file found at $build_constraints_file"
      exit 1
    fi

  # Check if the resolved path is within the source repository
  if [[ ! $(realpath "$build_constraints_file") == "$PROJECT_ROOT"* ]]; then
    echo "Error: The path '$build_constraints_file' is not within the source repository."
    exit 1
  fi


}
# === Main script starts here ===


python_versions=()
# Check if the help flag is provided
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0
  fi
done

# Parse optional arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --project-root=*)
      PROJECT_ROOT="${1#*=}"
      shift
      ;;
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --build-constraints-file=*)
      build_constraints_file="${1#*=}"
      shift
      ;;
    --build-constraints-file)
      build_constraints_file="${2}"
      shift 2
      ;;
    --docker-image-name=*)
      docker_image_name="${1#*=}"
      shift
      ;;
    --docker-image-name)
      docker_image_name="$2"
      shift 2
      ;;
    --python-version=*)
        if [[ -n "${1#*=}" && "${1#*=}" != --* ]]; then
            version="${1#*=}"
            python_versions+=("$version")
            shift
        else
          echo "Error: --python-version requires a value"
          exit 1
        fi
      ;;
    --python-version)
      shift
      if [[ -n "$1" && "$1" != --* ]]; then
        python_versions+=("$1")
        shift
      else
        echo "Error: --python-version requires a value"
        exit 1
      fi
      ;;
    --platform=*)
      PLATFORM="${1#*=}"
      shift
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      show_help
      exit 1
      shift
      ;;
  esac
done

if [[ -z "$PLATFORM" ]]; then
  PLATFORM="$DEFAULT_PLATFORM"
fi

# Set default if no versions were specified
if [[ ${#python_versions[@]} -eq 0 ]]; then
    python_versions=($DEFAULT_PYTHON_VERSION)
fi

if [[ ! -v docker_image_name ]]; then
    docker_image_name=$DEFAULT_DOCKER_IMAGE_NAME
else
  echo "Using '$docker_image_name' for the name of the Docker Image generated to build."
fi
if [[ -z "$build_constraints_file" ]]; then
    build_constraints_file=$DEFAULT_BUILD_CONSTRAINTS
else
  echo "Using '$build_constraints_file' for constraints file."
fi
check_args
generate_wheel $PLATFORM $docker_image_name $build_constraints_file ${python_versions[@]}
