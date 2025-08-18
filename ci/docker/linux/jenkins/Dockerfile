ARG CONAN_USER_HOME=/conan
ARG CONAN_HOME=${CONAN_USER_HOME}/.conan2

ARG PYTHON_VERSION=latest

ARG CONAN_CENTER_PROXY_V2_URL=https://center2.conan.io
# If you want to use a diffrent remote for Conan, such as a proxy. Set the CONAN_CENTER_PROXY_V2_URL
# Not this is only for building the image. The actual conan center proxy URL is set in the remotes.json file.

ARG PIP_DOWNLOAD_CACHE=/.cache/pip
# PIP Cache directory. Change this only if you need to override the default location.

ARG UV_CACHE_DIR=/.cache/uv
# UV Cache directory. Change this only if you need to override the default location.


ARG SONAR_USER_HOME=/opt/sonar/.sonar
FROM python:${PYTHON_VERSION} AS base_image
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt_cache \
    apt-get update && \
    apt-get install -y --no-install-recommends unzip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /.cache/pip &&  \
    chmod -R 777 /.cache

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
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt_cache \
    apt-get update && \
    apt-get install -y --no-install-recommends jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ARG CONAN_USER_HOME
ARG CONAN_DOWNLOAD_CACHE=/tmp/conan_download_cache
ARG CONAN_CENTER_PROXY_V2_URL
COPY conanfile.py /tmp/conanfile.py
ARG UV_CACHE_DIR
ARG PIP_DOWNLOAD_CACHE
COPY requirements-dev.txt /tmp/requirements-dev.txt

ARG CONAN_HOME
COPY ci/docker/shared/conan/remotes.json ${CONAN_HOME}/remotes.json
ENV UV_CONSTRAINT=/tmp/requirements-dev.txt
RUN --mount=type=cache,target=${PIP_DOWNLOAD_CACHE} \
    --mount=type=cache,target=${UV_CACHE_DIR} \
    --mount=type=cache,target=${CONAN_DOWNLOAD_CACHE} \
    python3 -m venv venv && \
    ./venv/bin/pip --disable-pip-version-check install uv && \
    ./venv/bin/uvx --with cmake conan profile detect --exist-ok &&  \
    cp ${CONAN_HOME}/global.conf /tmp/global.conf.original && \
    echo "core.sources:download_cache = $CONAN_DOWNLOAD_CACHE" >> ${CONAN_HOME}/global.conf && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
        echo "Setting the conan center url for building cache: ${CONAN_CENTER_PROXY_V2_URL}" && \
        cp ${CONAN_HOME}/remotes.json /tmp/remotes.json && \
        ./venv/bin/uvx --with cmake conan remote update conan-center --url ${CONAN_CENTER_PROXY_V2_URL}; \
    fi && \
    ./venv/bin/uvx --with cmake conan install /tmp -pr:b=default --build missing -pr:b=default && \
    ./venv/bin/uvx --with cmake conan cache clean "*" -b --source --build --temp && \
    rm -rf venv && \
    if [ "$(jq -r '.remotes[0].url' ${CONAN_HOME}/remotes.json )" != "${CONAN_CENTER_PROXY_V2_URL}" ]; then \
      mv -f /tmp/remotes.json ${CONAN_HOME}/remotes.json; \
    fi && \
    mv -f /tmp/global.conf.original ${CONAN_HOME}/global.conf

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
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update &&  \
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

ARG UV_CACHE_DIR
run mkdir -p "${UV_CACHE_DIR}" && \
    chmod -R 777 "${UV_CACHE_DIR}"
ENV UV_CACHE_DIR=${UV_CACHE_DIR}

ARG PIP_DOWNLOAD_CACHE
run mkdir -p "${PIP_DOWNLOAD_CACHE}" && \
    chmod -R 777 "${PIP_DOWNLOAD_CACHE}"
ENV PIP_DOWNLOAD_CACHE=${PIP_DOWNLOAD_CACHE}

COPY --from=DR_MEMORY_BUILDER /opt/drmemory /opt/drmemory/
RUN ln -s /opt/drmemory/bin64/drmemory /usr/local/bin/drmemory && \
    drmemory -version

ARG CONAN_USER_HOME
ARG CONAN_HOME
COPY --from=conan_builder ${CONAN_HOME} ${CONAN_HOME}
ENV CONAN_USER_HOME=${CONAN_USER_HOME}\
    CONAN_HOME=${CONAN_HOME}
RUN chmod -R 777 ${CONAN_HOME}/
