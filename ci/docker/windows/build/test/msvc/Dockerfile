# escape=`
ARG CERTS_GENERATOR_IMAGE=mcr.microsoft.com/dotnet/framework/sdk:4.8
ARG PYTHON_DOCKER_IMAGE_BASE=python:3.7

FROM ${CERTS_GENERATOR_IMAGE} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM ${PYTHON_DOCKER_IMAGE_BASE} as wheel_builder

COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

ARG PIP_EXTRA_INDEX_URL
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt c:/temp/
RUN python -m pip install pip --upgrade ; `
    pip wheel --wheel-dir=c:\wheels `
        -r c:/temp/requirements.txt `
        -r c:/temp/requirements-ci.txt


FROM ${PYTHON_DOCKER_IMAGE_BASE}

COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst
COPY --from=wheel_builder c:/wheels/ c:/wheels/
ARG PIP_EXTRA_INDEX_URL
ADD requirements.txt ci/docker/shared/python/requirements-ci.txt c:/temp/
RUN python -m pip install pip --upgrade ; `
    pip install --no-index --find-links c:\wheels\ `
         -r c:/temp/requirements.txt `
         -r c:/temp/requirements-ci.txt
ENV PIP_FIND_LINKS=c:\wheels\