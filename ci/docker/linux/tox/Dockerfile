FROM ubuntu:20.04 as wheel_builder_py36
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update

RUN cat /tmp/apt-packages.txt | apt install -y python3.6-dev python3.6-venv python3-pip
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt requirements.txt requirements-dev.txt /tmp/
RUN PYTHON=python3.6 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM ubuntu:20.04 as wheel_builder_py37
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update

RUN cat /tmp/apt-packages.txt | apt install -y python3.7-dev python3.7-venv python3-pip
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt requirements.txt requirements-dev.txt /tmp/
RUN PYTHON=python3.7 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM ubuntu:20.04 as wheel_builder_py38
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update

RUN cat /tmp/apt-packages.txt | apt install -y python3.8-dev python3.8-venv python3-pip
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY ci/docker/shared/python/requirements-ci.txt ci/docker/shared/python/requirements-extra.txt requirements.txt requirements-dev.txt /tmp/
RUN PYTHON=python3.8 && \
    $PYTHON -m pip install pip --upgrade pip && \
    $PYTHON -m pip install wheel && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -r /tmp/requirements-ci.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements.txt && \
    $PYTHON -m pip wheel -w /wheels --no-cache-dir -v -r /tmp/requirements-extra.txt

# ==============================================================================
FROM ubuntu:20.04
RUN apt update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update

COPY ci/docker/linux/tox/apt-packages.txt /tmp/apt-packages.txt
RUN cat /tmp/apt-packages.txt | xargs apt install -y
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL

COPY --from=wheel_builder_py36 /wheels/* /wheels/
COPY --from=wheel_builder_py37 /wheels/* /wheels/
COPY --from=wheel_builder_py38 /wheels/* /wheels/
ENV PIP_FIND_LINKS=/wheels
RUN pip3 install tox