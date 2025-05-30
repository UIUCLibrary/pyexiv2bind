# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V1_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.
ARG CONAN_CENTER_PROXY_V1_URL

# PIP Cache directory. Change this only if you need to override the default location.
ARG PIP_DOWNLOAD_CACHE=/.cache/pip

# UV Cache directory. Change this only if you need to override the default location.
ARG UV_CACHE_DIR=/.cache/uv

ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64

FROM ${manylinux_image} AS base_python
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp36-cp36m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV CONAN_USER_HOME=/conan
COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY requirements-dev.txt /tmp/requirements-dev.txt
COPY conanfile.py /tmp/conanfile.py
COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
ARG CONAN_CENTER_PROXY_V1_URL

RUN --mount=type=cache,target=${PIP_DOWNLOAD_CACHE} \
    --mount=type=cache,target=${UV_CACHE_DIR} \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config init && \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config set general.revisions_enabled=1 && \
    uv run  /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") && \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
      echo 'Using a proxy for conan center' && \
      cp ${CONAN_USER_HOME}/.conan/remotes.json /tmp/remotes.json && \
      uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote remove conan-center && \
      uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remote add conan-center ${CONAN_CENTER_PROXY_V1_URL}; \
    fi && \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan install /tmp --build  missing --no-import  && \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove "*" -b --src -f && \
    uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove --locks && \
    uv cache prune && \
    if [ -n "${CONAN_CENTER_PROXY_V1_URL}" ]; then \
      mv -f /tmp/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json; \
    fi && \
    chmod -R 777 /conan

