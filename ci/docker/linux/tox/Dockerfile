ARG PIPX_HOME=/pipx
ARG PIP_DOWNLOAD_CACHE=/.cache/pip
ARG TARGETARCH=amd64
ARG COMPILER_VERSION_FOR_PREBUILD_CONAN_PACKAGES=11.4
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
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/ /tmp/python_requirements/requirements/
COPY requirements-dev.txt /tmp/python_requirements
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/python_requirements/requirements-dev.txt

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
