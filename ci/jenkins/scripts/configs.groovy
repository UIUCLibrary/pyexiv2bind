def getConfigurations(){
    def configs = [
        "3.6" : [
            os: [
                windows:[
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        test:[
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/test/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.6-windowsservercore --build-arg PIP_EXTRA_INDEX_URL',
                                    baseImage: "python:3.6-windowsservercore"
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/whl/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.6-windowsservercore'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/source/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "36m-win*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp36*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/test/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/linux/package/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "36m-manylinux*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp36*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ]
            ],
            tox_env: "py36",
            devpiSelector: [
                sdist: "zip",
                wheel: "36.*whl",
            ],
            pkgRegex: [
                wheel: "*cp36*.whl",
                sdist: "*.zip"
            ]
        ],
        "3.7" : [
            os: [
                windows: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/test/msvc/Dockerfile',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.7 --build-arg PIP_EXTRA_INDEX_URL',
                                    label: 'windows && docker',
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/whl/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.7'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/source/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "37m-win*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp37*.whl",
                        sdist: "*.zip"
                    ],
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/test/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/linux/package/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "37m-manylinux*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp37*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ]
            ],
            tox_env: "py37",
            devpiSelector: [
                sdist: "zip",
                wheel: "37.*whl",
            ],
            pkgRegex: [
                wheel: "*cp37*.whl",
                sdist: "*.zip"
            ]
        ],
        "3.8" : [
            os: [
                windows: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/test/msvc/Dockerfile',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.8 --build-arg PIP_EXTRA_INDEX_URL',
                                    label: 'windows && docker',
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/whl/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.8'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/source/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ]
                        ]

                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "38-win*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp38*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/test/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/linux/package/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "38-manylinux*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp38*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ]
            ],
            tox_env: "py38",
            devpiSelector: [
                sdist: "zip",
                wheel: "38.*whl",
            ],
            pkgRegex: [
                wheel: "*cp38*.whl",
                sdist: "*.zip"
            ]
        ],
        "3.9" : [
            os: [
                windows: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/test/msvc/Dockerfile',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.9 --build-arg PIP_EXTRA_INDEX_URL',
                                    label: 'windows && docker',
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/whl/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.9'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/deploy/devpi/test/windows/source/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe --build-arg PIP_EXTRA_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                ]
                            ]
                        ]

                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "39-win*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp39*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/test/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/linux/package/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/test/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.9 --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
                    ],
                    devpiSelector: [
                        sdist: "zip",
                        wheel: "39-manylinux*.*whl",
                    ],
                    pkgRegex: [
                        wheel: "*cp39*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ]
            ],
            tox_env: "py39",
            devpiSelector: [
                sdist: "zip",
                wheel: "39.*whl",
            ],
            pkgRegex: [
                wheel: "*cp39*.whl",
                sdist: "*.zip"
            ]
        ],
    ]
    return configs
}
return this