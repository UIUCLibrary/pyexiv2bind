ARG PIPX_HOME=/pipx
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG CONAN_USER_HOME=/conan
ARG PIP_FIND_LINKS=/wheels
FROM ubuntu:22.04 AS base
COPY ci/docker/linux/tox/apt-packages.txt /tmp/
RUN apt-get update && \
    apt-get install -y software-properties-common gpg-agent --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata && \
    apt-get update && \
     < /tmp/apt-packages.txt xargs apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# ==============================================================================

FROM base AS conan_builder
ARG CONAN_USER_HOME
COPY requirements/requirements_conan.txt /tmp/python_requirements/
RUN pip3 install --no-cache-dir -r /tmp/python_requirements/requirements_conan.txt
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py

COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
COPY conanfile.py /tmp/conanfile.py
RUN conan config init && \
    conan config set general.revisions_enabled=1 && \
    python3 /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") && \
    conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default  && \
    conan install /tmp -pr:b=default --build outdated --no-import && \
    conan remove "*" -b --src -f && \
    conan remove --locks
# ==============================================================================
FROM base
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/ /tmp/python_requirements/requirements/
COPY requirements-dev.txt /tmp/python_requirements
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/python_requirements/requirements-dev.txt

ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/


RUN conan config init && \
    conan config set general.revisions_enabled=1 && \
    conan profile update settings.compiler.libcxx=libstdc++11 default

COPY conanfile.py /tmp/conanfile.py
RUN conan install /tmp --build  missing --no-import -pr:b=default && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 ${CONAN_USER_HOME}

ENV CONAN_USER_HOME=${CONAN_USER_HOME}
ARG PIP_DOWNLOAD_CACHE
RUN mkdir -p ${PIP_DOWNLOAD_CACHE} && \
    chmod -R 777 ${PIP_DOWNLOAD_CACHE}
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

ARG PIPX_HOME
ENV PIPX_HOME=${PIPX_HOME}
ENV PIPX_BIN_DIR=${PIPX_HOME}/bin
RUN pip3 install --no-cache-dir pipx && \
    pipx ensurepath && \
    mkdir -p $PIPX_HOME  && chmod -R 777 $PIPX_HOME
RUN PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install 'devpi-client<7.0' &&  \
    PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install pip-audit



WORKDIR /src

CMD ["tox", "--workdir", "/tmp/tox", "--recreate", "-p=auto"]
