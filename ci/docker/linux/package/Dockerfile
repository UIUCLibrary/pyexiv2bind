ARG manylinux_image=quay.io/pypa/manylinux2014_x86_64
FROM ${manylinux_image} AS base_python
ENV PATH=/opt/python/cp39-cp39/bin:/opt/python/cp38-cp38/bin:/opt/python/cp37-cp37m/bin:/opt/python/cp36-cp36m/bin:/opt/python/cp35-cp35m/bin:$PATH
RUN mkdir -p /.cache/pip && \
    chmod -R 777 /.cache
ARG PIP_EXTRA_INDEX_URL
ARG PIP_INDEX_URL
COPY requirements/requirements_conan.txt /tmp/requirements_conan.txt
RUN python3 --version && python3 -m pip install --no-cache-dir -r /tmp/requirements_conan.txt
ARG TARGETARCH
COPY conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=/conan
RUN conan config init && \
    conan config set general.revisions_enabled=1 && \
    conan profile update settings.compiler.version=$(cc -dumpfullversion -dumpversion | grep -oE  "^([0-9]+(\.)?)([0-9]+?)") default && \
    conan install /tmp --build  missing --no-import  && \
    conan remove "*" -b --src -f && \
    conan remove --locks && \
    chmod -R 777 /conan


RUN /opt/python/cp38-cp38/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/python/cp38-cp38/bin/python -m pip install --no-cache-dir --upgrade wheel && \
    /opt/python/cp38-cp38/bin/python -m pip install --no-cache-dir --upgrade build &&  \
    python3.8 -m build --version && \
    /opt/python/cp39-cp39/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/python/cp39-cp39/bin/python -m pip install --no-cache-dir --upgrade wheel && \
    /opt/python/cp39-cp39/bin/python -m pip install --no-cache-dir --upgrade build &&  \
    python3.9 -m build --version && \
    /opt/python/cp310-cp310/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/python/cp310-cp310/bin/python -m pip install --no-cache-dir --upgrade wheel && \
    /opt/python/cp310-cp310/bin/python -m pip install --no-cache-dir --upgrade build &&  \
    python3.10 -m build --version && \
    /opt/python/cp311-cp311/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/python/cp311-cp311/bin/python -m pip install --no-cache-dir --upgrade wheel && \
    /opt/python/cp311-cp311/bin/python -m pip install --no-cache-dir --upgrade build &&  \
    python3.11 -m build --version && \
    /opt/python/cp312-cp312/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/python/cp312-cp312/bin/python -m pip install --no-cache-dir --upgrade wheel && \
    /opt/python/cp312-cp312/bin/python -m pip install --no-cache-dir --upgrade build &&  \
    python3.12 -m build --version
