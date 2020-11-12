FROM ubuntu:20.04
RUN apt update && apt install -y python3 python3-pip build-essential git
RUN python3 -m pip install conan cmake gcovr

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user
RUN mkdir -p /home/user/.conan/data && \
    chown user:user -R /home/user/.conan/
# FIXME: this should be removed as soon when the CMakeLists.txt no longer creates a python venv
RUN apt-get install -y python3-venv

USER user
WORKDIR /home/user
COPY --chown=user:user ci/docker/linux/shared/remotes.json /home/user/.conan/remotes.json
COPY conanfile.py /tmp/conanfile.py
ENV CONAN_USER_HOME=/home/user/
RUN conan config home
RUN conan install /tmp --build  missing --no-import
