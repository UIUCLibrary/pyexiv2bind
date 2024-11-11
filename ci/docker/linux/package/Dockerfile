ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
FROM ${manylinux_image} AS base_python
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp36-cp36m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
ENV CONAN_USER_HOME=/conan
COPY requirements-dev.txt /tmp/requirements-dev.txt
COPY conanfile.py /tmp/conanfile.py
COPY ci/docker/linux/tox/update_conan_compiler.py  /tmp/update_conan_compiler.py
RUN python3 -m venv venv && \
    . ./venv/bin/activate && \
    pip install --no-cache-dir uv && \
    uv pip install --no-cache -r /tmp/requirements-dev.txt && \
    conan config init && \
    conan config set general.revisions_enabled=1 && \
    python /tmp/update_conan_compiler.py ${CONAN_USER_HOME}/.conan/settings.yml gcc $(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") && \
    conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default && \
    conan install /tmp --build  missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan &&  \
    rm -rf venv

