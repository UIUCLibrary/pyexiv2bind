ARG CONAN_USER_HOME=/conan
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
COPY requirements-dev.txt /tmp/requirements-dev.txt
COPY ci/docker/shared/conan/remotes.json  ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py

COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
COPY conanfile.py /tmp/conanfile.py
RUN python3 -m venv venv && \
    ./venv/bin/pip install --disable-pip-version-check --no-cache-dir uv && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config init && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan config set general.revisions_enabled=1 && \
    ./venv/bin/uv run /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default  && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan install /tmp -pr:b=default --build outdated --no-import && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove "*" -b --src -f && \
    ./venv/bin/uvx --constraint=/tmp/requirements-dev.txt --with cmake conan remove --locks && \
    rm -rf venv
# ==============================================================================
FROM base
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG CONAN_USER_HOME
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
RUN chmod -R 777 ${CONAN_USER_HOME}
ENV CONAN_USER_HOME=${CONAN_USER_HOME}

WORKDIR /src

CMD ["tox", "--workdir", "/tmp/tox", "--recreate", "-p=auto"]
