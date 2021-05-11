ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION} as base_image
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
#==============================================================================

FROM base_image as wheel_builder
ARG PIP_EXTRA_INDEX_URL
RUN python -m pip install pip --upgrade && \
    pip install wheel && \
    pip install setuptools --upgrade

ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/

RUN pip wheel --wheel-dir=/wheels \
    -r /requirements/requirements-ci.txt \
    -r /requirements/requirements.txt && \
    rm -rf  /root/.cache
#==============================================================================

FROM base_image as SONAR_BUILDER
RUN apt-get update && \
    apt-get install -y unzip

ENV SONAR_SCANNER_VERSION=4.4.0.2170
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
ENV SONAR_USER_HOME=/opt/sonar/.sonar

RUN curl --create-dirs -sSLo /tmp/sonar-scanner.zip \
        https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip && \
    unzip -o /tmp/sonar-scanner.zip -d /opt/sonar/ && \
    rm /tmp/sonar-scanner.zip && \
    mkdir -p $SONAR_USER_HOME/cache && \
    chmod -R 777 "${SONAR_USER_HOME}" &&\
    ln -s /opt/sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner
# ==============================================================================
FROM base_image as conan_builder
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN pip3 install conan
ENV CONAN_USER_HOME=/conan
COPY ci/docker/shared/conan/remotes.json /conan/.conan/remotes.json
COPY ci/docker/linux/test/conan/profile.ini  /conan/.conan/profiles/default
COPY conanfile.py /tmp/conanfile.py
RUN conan config init
RUN conan install /tmp --build outdated --no-import  && \
    conan install /tmp --build outdated --no-import  -s build_type=Debug && \
    conan remove "*" -b --src -f && \
    conan remove --locks
#==============================================================================

FROM base_image

RUN apt update && apt install -y ninja-build
COPY --from=SONAR_BUILDER /opt/sonar /opt/sonar/
ENV SONAR_SCANNER_VERSION=4.4.0.2170
ARG SONAR_SCANNER_HOME=/opt/sonar/${SONAR_SCANNER_VERSION}-linux
RUN ln -s /opt/sonar/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    which sonar-scanner
RUN mkdir -p /.sonar/cache && \
    chmod -R 777 /.sonar/cache
ENV SONAR_SCANNER_OPTS="-server"


COPY --from=wheel_builder /wheels /wheels/
RUN chmod -R 777 /wheels
ARG PIP_EXTRA_INDEX_URL
ENV PIP_NO_CACHE_DIR=1
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt /requirements/
RUN python -m pip install pip --upgrade && \
    pip install wheel && \
    pip install setuptools --upgrade && \
    pip install --no-index --find-links=/wheels/ \
         -r /requirements/requirements.txt \
         -r /requirements/requirements-ci.txt

ENV CONAN_USER_HOME=/conan
COPY --from=conan_builder /conan/.conan/ /conan/.conan/
COPY ci/docker/shared/conan/remotes.json /conan/.conan/remotes.json
COPY ci/docker/linux/test/conan/profile.ini  /conan/.conan/profiles/default
ADD conanfile.py /tmp/conanfile.py
RUN conan config init
RUN conan install /tmp --build  missing --no-import && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan

ENV PIP_FIND_LINKS=/wheels/
