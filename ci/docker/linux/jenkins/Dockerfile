ARG PIP_FIND_LINKS=/wheels/
ARG CONAN_USER_HOME=/conan
ARG PYTHON_VERSION=3.11
ARG SONAR_USER_HOME=/opt/sonar/.sonar
FROM python:${PYTHON_VERSION} AS base_image
RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt /requirements/requirements-dev.txt
RUN python -m pip install --no-cache-dir pip --upgrade && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir setuptools --upgrade && \
    pip install --no-cache-dir -r /requirements/requirements-dev.txt

RUN mkdir -p /.cache/pip &&  \
    chmod -R 777 /.cache

#==============================================================================

FROM base_image AS wheel_builder
ARG PIP_EXTRA_INDEX_URL

COPY requirements-dev.txt /requirements/requirements-dev.txt
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG PIP_FIND_LINKS
RUN mkdir -p ${PIP_FIND_LINKS} &&  \
    pip wheel --wheel-dir=${PIP_FIND_LINKS} --no-cache-dir -r /requirements/requirements-dev.txt
#==============================================================================

FROM base_image AS SONAR_BUILDER
ARG SONAR_USER_HOME

RUN case $(uname -m) in \
    x86_64) URL=https://sonarcloud.io/static/cpp/build-wrapper-linux-x86.zip ;; \
    aarch64) URL=https://sonarcloud.io/static/cpp/build-wrapper-linux-aarch64.zip ;; \
    esac; \
    curl --create-dirs -sSLo /tmp/build-wrapper-linux.zip $URL && \
    unzip -o /tmp/build-wrapper-linux.zip -d /opt/build-wrapper-linux/ && \
    case $(uname -m) in \
        x86_64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux ;; \
        aarch64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-aarch64/build-wrapper-linux-aarch64 /usr/local/bin/build-wrapper-linux ;; \
    esac; \
    which build-wrapper-linux

# ==============================================================================
FROM base_image AS conan_builder
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG CONAN_USER_HOME
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt
COPY ci/docker/shared/conan/remotes.json ${CONAN_USER_HOME}/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
RUN conan config init && \
    conan config set general.revisions_enabled=1 && \
    conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default && \
    conan install /tmp -pr:b=default --build outdated --no-import -pr:b=default && \
    conan install /tmp -pr:b=default --build outdated --no-import -pr:b=default -s build_type=Debug && \
    conan remove "*" -b --src -f && \
    conan remove --locks
#==============================================================================
FROM base_image AS DR_MEMORY_BUILDER
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /drmemory
RUN wget --no-verbose https://github.com/DynamoRIO/drmemory/releases/download/release_2.3.0/DrMemory-Linux-2.3.0-1.tar.gz && \
    mkdir -p /opt/drmemory && tar xzf DrMemory-Linux-2.3.0-1.tar.gz -C /opt/drmemory --strip-components=1 && \
    ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version
#==============================================================================
FROM base_image

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends ninja-build clang-tidy cppcheck && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=SONAR_BUILDER /opt/build-wrapper-linux /opt/build-wrapper-linux/
ARG SONAR_USER_HOME
ENV SONAR_USER_HOME=${SONAR_USER_HOME}

RUN case $(uname -m) in \
        x86_64) ln -s /opt/build-wrapper-linux/build-wrapper-linux-x86/build-wrapper-linux-x86-64 /usr/local/bin/build-wrapper-linux  ;; \
        aarch64) ln ln -s /opt/build-wrapper-linux/build-wrapper-linux-aarch64/build-wrapper-linux-aarch64 /usr/local/bin/build-wrapper-linux  ;; \
    esac; \
    which build-wrapper-linux

RUN mkdir -p /.sonar/cache && \
    chmod -R 777 /.sonar/cache

RUN mkdir -p "$SONAR_USER_HOME" && \
    chmod -R 777 "$SONAR_USER_HOME"

ENV SONAR_SCANNER_OPTS="-server"

COPY --from=DR_MEMORY_BUILDER /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ENV PIP_NO_CACHE_DIR=1
ARG PIP_FIND_LINKS
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST
COPY --from=wheel_builder ${PIP_FIND_LINKS}/* ${PIP_FIND_LINKS}/
COPY --from=wheel_builder requirements/ /requirements
RUN pip install --no-index --no-cache-dir --find-links=${PIP_FIND_LINKS} \
    -r /requirements/requirements-dev.txt

ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}

ARG CONAN_USER_HOME
ENV CONAN_USER_HOME=${CONAN_USER_HOME}
COPY --from=conan_builder ${CONAN_USER_HOME}/.conan/ ${CONAN_USER_HOME}/.conan/
COPY conanfile.py /tmp/conanfile.py
RUN conan install /tmp -pr:b=default --build  missing --no-import && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 ${CONAN_USER_HOME}

ENV PIP_FIND_LINKS=${PIP_FIND_LINKS}
