ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
FROM ${manylinux_image} as base_python
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp36-cp36m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
RUN python3 --version && python3 -m pip install conan
ARG TARGETARCH
COPY ci/docker/linux/package/conan/$TARGETARCH/profile.ini  /conan/.conan/profiles/default
COPY ci/docker/shared/conan/remotes.json  /conan/.conan/remotes.json
ADD conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=/conan
RUN conan config home
RUN conan install /tmp --build  missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan

RUN python3 -m pip install build