# NOTICE: This Dockerfile needs to be built from the root of the repository. If you build it from the same location as
#         this file, it will not work because it needs access to files not in this directory. If you need to build this
#         Dockerfile directly, use the "docker build" command with the
#         "-f scripts/resources/package_for_linux/Dockerfile" argument.

ARG CONAN_USER_HOME=/conan

ARG CONAN_CENTER_PROXY_V1_URL
# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.

ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
# Base image to use, this should be of the manylinux family. More info at: https://github.com/pypa/manylinux

ARG UV_CACHE_DIR=/.cache/uv
# UV Cache directory. Change this only if you need to override the default location.

ARG PIP_DOWNLOAD_CACHE=/.cache/pip
# PIP Cache directory. Change this only if you need to override the default location.

ARG UV_CONSTRAINT=requirements-dev.txt
# Python contraint file used when acquiring conan to prebuild the native dependencies

# ==============================================================================
FROM ${manylinux_image} AS base

RUN --mount=type=cache,target=/var/cache/yum \
    yum install -y lndir

# This needed to use uvx with --constraint option
RUN --mount=type=cache,target=/path/to/pipx/cache \
    pipx install "uv>=0.6.5" --force

# ==============================================================================
FROM base AS conan_builder
ARG CONAN_USER_HOME
ARG TARGETARCH
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG UV_EXTRA_INDEX_URL
ARG UV_INDEX_URL

COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
ARG CONAN_CENTER_PROXY_V1_URL
ARG UV_CONSTRAINT
COPY ${UV_CONSTRAINT} /tmp/${UV_CONSTRAINT}
ENV UV_CONSTRAINT=/tmp/${UV_CONSTRAINT}
RUN --mount=type=cache,target=${PIP_DOWNLOAD_CACHE} \
    --mount=type=cache,target=${UV_CACHE_DIR} \
    uvx --with cmake conan config init && \
    uvx --with cmake conan config set general.revisions_enabled=1 && \
    uv run  /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") && \
    uvx --with cmake conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
      echo 'Using a proxy for conan center' && \
      cp ${CONAN_USER_HOME}/.conan/remotes.json /tmp/remotes.json && \
      uvx --with cmake conan remote remove conan-center && \
      uvx --with cmake conan remote add conan-center ${CONAN_CENTER_PROXY_V1_URL}; \
    fi && \
    uvx --with cmake conan install /tmp --build missing --no-import  && \
    uvx --with cmake conan remove "*" -b --src -f && \
    uvx --with cmake conan remove --locks && \
    uv cache prune && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
      mv -f /tmp/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json; \
    fi
# ==============================================================================

FROM base

ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/ ${CONAN_USER_HOME}/
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
RUN chmod -R 777 ${CONAN_USER_HOME} && \
    mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE} && \
    mkdir -p ${UV_CACHE_DIR} && \
    chmod -R 777 ${UV_CACHE_DIR}
