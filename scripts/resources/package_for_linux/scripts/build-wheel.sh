#!/usr/bin/env bash

set -e

WORKSPACE="/workspace"

SKIP_DIRS_NAMED=(\
    'venv' \
    '.venv' \
    '.tox' \
    '.git' \
    '.idea' \
    'reports' \
    '.mypy_cache' \
    '__pycache__' \
    'wheelhouse' \
    '.pytest_cache' \
    'py3exiv2bind.egg-info'\
    'build' \
)

REMOVE_FILES_FIRST=(\
  'CMakeUserPresets.json'
  )

print_usage(){
    echo "Usage: $0 SOURCE_DIRECTORY OUTPUT_DIRECTORY PYTHON_VERSION [PYTHON_VERSION...] [--build-constraints=PATH] [--help]"
}

show_help() {
  print_usage
  echo "  SOURCE_DIRECTORY   : path to project source code.                             "
  echo "  OUTPUT_DIRECTORY   : path to create wheel files.                              "
  echo "  PYTHON_VERSION     : Python version to generate wheel file for.               "
  echo "  --build-constraints: Optional path to a constraints file used building wheel. "
  echo "                                                                                "
  echo "  --help, -h       : Display this help message.                                 "
}

verify_package_with_twine() {
  local dist_directory=$1
  local path=$2
  echo 'Verifying package with twine'

  if ! uv run --frozen --isolated --project="${path}" --only-group=publish twine check --strict "${dist_directory}"/*.whl
  then
    echo "Twine check failed. Please fix the issues and try again."
    exit 1
  fi
}

make_shadow_copy() {
  local source_directory=$1
  local container_workspace=$2
  echo 'Making a shadow copy to prevent modifying local files'
  prune_expr=()
  for name in "${SKIP_DIRS_NAMED[@]}"; do
      prune_expr+=(-name "$name" -type d -prune -o);
  done

  mkdir -p "${container_workspace}"
  (cd /project/ && \
  find . "${prune_expr[@]}" -type d -print | while read -r dir; do
      mkdir -p "${container_workspace}/$dir"
  done &&
  find . "${prune_expr[@]}" \( -type f -o -type l \) -print | while read -r file; do
      echo "$file"
      ln -sf "/project/$file" "${container_workspace}/$file"
  done)
  for f in "${REMOVE_FILES_FIRST[@]}"; do
      OFFENDING_FILE="${container_workspace}/$f"
      if [ -f "$OFFENDING_FILE" ]; then
        echo "Removing copy from temporary working path to avoid issues: $OFFENDING_FILE";
        rm "$OFFENDING_FILE";
      fi;
  done
  echo 'Removing Python cache files'
  find "${container_workspace}" -type d -name '__pycache__' -exec rm -rf {} +
  find "${container_workspace}" -type f -name '*.pyc' -exec rm -f {} +
}

make_wheels() {
  local project_directory=$1
  local dist_directory=$2
  local build_constraints=$3
  local python_versions=("${@:4}")
  local output_manifest
  echo "project_directory = $project_directory"
#  exit 1
  output_manifest="$(mktemp)"
  touch output_manifest
  mkdir -p "$dist_directory"
  for python_version in "${python_versions[@]}"; do
      echo "Creating wheel for Python version: $python_version";
      local temp_dir
      temp_dir="$(mktemp -d -t py3exiv2bind_wheel_XXXXXX)"
      if ! uv build --python="$python_version" --python-preference=system --wheel --build-constraints="$build_constraints" --out-dir="${temp_dir}" "${project_directory}"
      then
        echo "Failed to build wheel for Python $python_version";
        exit 1;
      fi;
      glob_search="${temp_dir}/*.whl"
      echo "searching with ${glob_search}"
      for wheel in $glob_search; do
        echo "Adding $wheel ${dist_directory}/"
        printf "%s\t%s\n" "$(basename "$wheel")" "$python_version" >> "$output_manifest"
      done
      mv "${temp_dir}"/*.whl "${dist_directory}/"
  done
  echo "reading $output_manifest"
  cat "$output_manifest"
  cp "$output_manifest" "${dist_directory}/build_output.tsv"
}

fix_up_wheels(){
  local source_directory=$1
  local output_directory=$2
  echo 'Fixing up wheels'
  auditwheel -v repair /tmp/dist/*.whl -w /dist/;
  for file in /dist/*manylinux*.whl; do
      auditwheel show "$file"
  done
}
for arg in "$@"; do
  if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0
  fi
done

if [[ $# -lt 2 ]]; then
  echo "Error: SOURCE_DIRECTORY and OUTPUT_DIRECTORY are required."
  print_usage
  exit 1
fi

source_directory="$1"
output_directory="$2"
shift 2

build_constraints=""
python_versions_to_use=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --build-constraints=*)
      build_constraints="${1#*=}"
      shift
      ;;
    --build-constraints)
      build_constraints="$2"
      shift 2
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      python_versions_to_use+=("$1")
      shift
      ;;
  esac
done

if [[ ${#python_versions_to_use[@]} -eq 0 ]]; then
  echo "Error: at least one Python version is required."
  print_usage
  exit 1
fi

echo "Building wheels for Python versions: ${python_versions_to_use[*]}"
make_shadow_copy "$source_directory" "$WORKSPACE"
if [[ -z "$build_constraints" ]]; then
  build_constraints=/tmp/constraints.txt
  uv export --frozen --only-group dev --no-hashes --format requirements.txt --no-emit-project --no-annotate --directory "${WORKSPACE}" > "$build_constraints"
fi
make_wheels "$WORKSPACE" "/tmp/dist" "${WORKSPACE}/${build_constraints}" "${python_versions_to_use[@]}"
verify_package_with_twine "/tmp/dist" "${source_directory}"
fix_up_wheels "/tmp/dist" "${output_directory}"
echo 'Done'
