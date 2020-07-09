FROM quay.io/pypa/manylinux2014_x86_64

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh
RUN curl -L --output  /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL && \
    chmod +x /tmp/install_cmake.sh  && \
    /tmp/install_cmake.sh  --skip-license --prefix=/usr && \
    cmake --version

ARG PYTHON_VERSION=3.8
RUN declare -A python_versions && \
    python_versions=( \
        ["3.5"]="/opt/python/cp35-cp35m" \
        ["3.6"]="/opt/python/cp36-cp36m" \
        ["3.7"]="/opt/python/cp37-cp37m" \
        ["3.8"]="/opt/python/cp38-cp38" \
        ["3.9"]="/opt/python/cp39-cp39" \
        ) && \
    if [ ${python_versions[$PYTHON_VERSION]} ] ; \
        then \
            ln -sf ${python_versions[$PYTHON_VERSION]}/bin/python /usr/bin/python ; \
            export PATH="${python_versions[$PYTHON_VERSION]}/bin:${PATH}" ; \
        else exit 1; \
    fi
