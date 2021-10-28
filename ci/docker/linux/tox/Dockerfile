FROM ubuntu:20.04 as base
COPY ci/docker/linux/tox/apt-packages.txt /tmp/
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    cat /tmp/apt-packages.txt | xargs apt-get -y install

RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache

FROM base as wheel_builder_base
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt requirements.txt requirements-dev.txt /tmp/

FROM wheel_builder_base as WHEEL_BUILDER_PY36
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel build && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY37
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel build && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY38

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel build && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================#
FROM wheel_builder_base as WHEEL_BUILDER_PY39

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN PYTHON=python3.9 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel build && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM wheel_builder_base as WHEEL_BUILDER_PY310

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN PYTHON=python3.10 && \
    $PYTHON -m ensurepip --upgrade && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel build && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM base as conan_builder
RUN pip3 install conan cmake
COPY --chown=user:user ci/docker/shared/conan/remotes.json  /home/user/.conan/remotes.json
COPY --chown=user:user ci/docker/linux/shared/conan/profile.ini  /home/user/profiles/default
USER user
WORKDIR /home/user
ADD conanfile.py /tmp/conanfile.py
RUN conan config home
RUN conan install /tmp --build outdated --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks

# ==============================================================================
FROM base

COPY --from=WHEEL_BUILDER_PY36 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY37 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY38 /wheels/* /wheels/
COPY --from=WHEEL_BUILDER_PY39 /wheels/* /wheels/
RUN python3.10 -m ensurepip --upgrade
COPY --from=WHEEL_BUILDER_PY310 /wheels/* /wheels/
RUN chmod -R 777 /wheels
ENV PIP_FIND_LINKS=/wheels
RUN pip3 install tox conan cmake devpi_client wheel

#USER user
#WORKDIR /home/user
COPY --from=conan_builder /home/user/.conan/ /conan/.conan/
COPY ci/docker/linux/tox/conan/profile.ini  /conan/.conan/profiles/default
COPY ci/docker/shared/conan/remotes.json  /conan/.conan/remotes.json
ADD conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=/conan
RUN conan config home
RUN conan install /tmp --build  missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan

WORKDIR /src
CMD tox --workdir /tmp/tox --recreate --recreate -p=auto