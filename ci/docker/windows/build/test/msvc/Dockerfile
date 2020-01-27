# escape=`
ARG PYTHON_DOCKER_IMAGE_BASE=python:3.7
FROM ${PYTHON_DOCKER_IMAGE_BASE}

ADD https://download.visualstudio.microsoft.com/download/pr/9565895b-35a6-434b-a881-11a6f4beec76/EE84FED2552E018E854D4CD2496DF4DD516F30733A27901167B8A9882119E57C/VC_redist.x64.exe c:/VC_redist.x64.exe

RUN c:/VC_redist.x64.exe /quiet /install /norestart

RUN certutil -generateSSTFromWU roots.sst ; `
    certutil -addstore -f root roots.sst ; `
    del roots.sst

RUN python -m pip install tox