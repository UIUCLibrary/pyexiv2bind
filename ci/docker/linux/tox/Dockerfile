ARG TARGETARCH=amd64
ARG COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES=9.4
ARG CONAN_USER_HOME=/conan
ARG PIP_FIND_LINKS=/wheels
FROM ubuntu:20.04 as base
COPY ci/docker/linux/tox/apt-packages.txt /tmp/
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common=0.99.9.10 && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM base as wheel_builder_base
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt requirements.txt requirements-dev.txt /tmp/
COPY requirements /tmp/requirements

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY37
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
ENV PYTHON=python3.7
RUN $PYTHON -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS}  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-dev.txt  \
        -r /tmp/requirements-ci.txt  \
        -r /tmp/requirements-extra.txt && \
    rm -rf venv
# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY38

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
ENV PYTHON=python3.8
RUN $PYTHON -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS}  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-dev.txt  \
        -r /tmp/requirements-ci.txt  \
        -r /tmp/requirements-extra.txt && \
    rm -rf venv

# ==============================================================================#
FROM wheel_builder_base as WHEEL_BUILDER_PY39

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
ENV PYTHON=python3.9
RUN $PYTHON -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS}  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-dev.txt  \
        -r /tmp/requirements-ci.txt  \
        -r /tmp/requirements-extra.txt && \
    rm -rf venv

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY310

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
ENV PYTHON=python3.10
RUN $PYTHON -m ensurepip --upgrade && \
    $PYTHON -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS}  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-dev.txt  \
        -r /tmp/requirements-ci.txt  \
        -r /tmp/requirements-extra.txt && \
    rm -rf venv

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY311

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
ENV PYTHON=python3.11
RUN $PYTHON -m ensurepip --upgrade && \
    $PYTHON -m venv venv && \
    . ./venv/bin/activate && \
    python -m pip install --no-cache-dir wheel==0.37.1 && \
    python -m pip wheel --no-cache-dir -w ${PIP_FIND_LINKS}  \
        -r /tmp/requirements.txt \
        -r /tmp/requirements-dev.txt  \
        -r /tmp/requirements-ci.txt  \
        -r /tmp/requirements-extra.txt && \
    rm -rf venv

# ==============================================================================

FROM wheel_builder_base as conan_builder
ARG CONAN_USER_HOME
COPY ci/docker/linux/tox/requirements-conan-build.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements-conan-build.txt
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
ARG TARGETARCH
COPY ci/docker/linux/tox/conan/$TARGETARCH/profile.ini  ${CONAN_USER_HOME}/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config init && \
    conan config set general.revisions_enabled=1

COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
ARG COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES
RUN python3 /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES
COPY conanfile.py /tmp/conanfile.py
RUN conan install /tmp -pr:b=default --build outdated --no-import -s compiler.version=$COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES  && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================
FROM base
ARG PIP_FIND_LINKS
COPY --from=WHEEL_BUILDER_PY37 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY38 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY39 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
RUN python3.10 -m ensurepip --upgrade
COPY --from=WHEEL_BUILDER_PY310 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=WHEEL_BUILDER_PY311 ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
RUN chmod -R 777 ${PIP_FIND_LINKS}
ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}
COPY requirements/ /tmp/requirements
RUN pip3 install --no-cache-dir -r /tmp/requirements/requirements_tox.txt conan cmake "devpi-client<6.0" build twine
ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
ARG TARGETARCH


RUN conan config init && \
    conan config set general.revisions_enabled=1 && \
    conan profile update settings.compiler.libcxx=libstdc++11 default

ARG COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES
COPY conanfile.py /tmp/conanfile.py
RUN conan install /tmp --build  missing --no-import -pr:b=default -s compiler.version=$COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 ${CONAN_USER_HOME}

ENV CONAN_USER_HOME=${CONAN_USER_HOME}

WORKDIR /src
CMD ["tox", "--workdir", "/tmp/tox", "--recreate", "-p=auto"]
