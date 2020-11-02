#!groovy
// @Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils

def CONFIGURATIONS = [
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
    ]
def check_dll_deps(path){
    if(!isUnix()){
        findFiles(glob: "${path}/**/*.pyd").each{
            bat(
                label: "Checking Python extension for dependents",
                script: "dumpbin /DEPENDENTS ${it.path}"
            )
        }
    }
}

def test_deps(glob){
    findFiles(glob: glob).each{
        if(!isUnix()){
            bat "tox --installpkg ${it} -e dumpbin"
        }
    }
}


def getToxEnvs(){
    def envs
    if(isUnix()){
        envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
    } else{
        envs = bat(returnStdout: true, script: "@tox -l").trim().split('\n')
    }
    envs.collect{
        it.trim()
    }
    return envs
}

def getToxTestsParallel(envNamePrefix, label, dockerfile, dockerArgs){
    script{
        def envs
        def originalNodeLabel
        node(label){
            originalNodeLabel = env.NODE_NAME
            checkout scm
            def dockerImageName = "tox${currentBuild.projectName}"
            def dockerImage = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} .")
            echo "dockerImage.id = ${dockerImage.id}"
            dockerImage.inside{
                envs = getToxEnvs()
            }
            if(isUnix()){
                sh(
                    label: "Removing Docker Image used to run tox",
                    script: "docker image ls ${dockerImageName}"
                )
            } else {
                bat(
                    label: "Removing Docker Image used to run tox",
                    script: """docker image ls ${dockerImageName}
                               """
                )
            }
        }
        echo "Found tox environments for ${envs.join(', ')}"
        def dockerImageForTesting
        node(originalNodeLabel){
            def dockerImageName = "tox"
            checkout scm
            dockerImageForTesting = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} . ")

        }
        echo "Adding jobs to ${originalNodeLabel} with ${dockerImageForTesting}"
        def jobs = envs.collectEntries({ tox_env ->
            def tox_result
            def githubChecksName = "Tox: ${tox_env} ${envNamePrefix}"
            def jenkinsStageName = "${envNamePrefix} ${tox_env}"

            [jenkinsStageName,{
                node(originalNodeLabel){
                    checkout scm
                    dockerImageForTesting.inside{
                        try{
                            publishChecks(
                                conclusion: 'NONE',
                                name: githubChecksName,
                                status: 'IN_PROGRESS',
                                summary: 'Use Tox to test installed package',
                                title: 'Running Tox'
                            )
                            if(isUnix()){
                                sh(
                                    label: "Running Tox with ${tox_env} environment",
                                    script: "tox  -vv --parallel--safe-build --result-json=tox_result.json -e $tox_env"
                                )
                            } else {
                                bat(
                                    label: "Running Tox with ${tox_env} environment",
                                    script: "tox  -vv --parallel--safe-build --result-json=tox_result.json -e $tox_env "
                                )
                            }
                        } catch (e){
                            publishChecks(
                                name: githubChecksName,
                                summary: 'Use Tox to test installed package',
                                text: "${tox_result}",
                                conclusion: 'FAILURE',
                                title: 'Failed'
                            )
                            throw e
                        }
                        tox_result = readJSON(file: 'tox_result.json')
                        echo "${readFile('tox_result.json')}"
                        def checksReportText = """toxversion: ${tox_result['toxversion']}
                                                  platform:   ${tox_result['platform']}
                        """
                        publishChecks(
                                name: githubChecksName,
                                summary: 'Use Tox to test installed package',
                                text: "${tox_result}",
                                title: 'Passed'
                            )
                    }
                }
            }]
        })
        return jobs
    }
}

def run_tox_envs(){
    script {
        def cmds
        def envs
        if(isUnix()){
            envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
            cmds = envs.collectEntries({ tox_env ->
                ["Unix ${tox_env}", {
                    sh( label:"Running Tox", script: "tox  -vvve $tox_env")
                }]
            })
        } else{
            envs = bat(returnStdout: true, script: "@tox -l").trim().split('\n')
            cmds = envs.collectEntries({ tox_env ->
                ["Windows ${tox_env}", {
                    bat( label:"Running Tox", script: "tox  -vvve $tox_env")
                }]
            })
        }
        echo "Setting up tox tests for ${envs.join(', ')}"
        parallel(cmds)
    }
}

def test_package_on_mac(glob){
    cleanWs(
        notFailBuild: true,
        deleteDirs: true,
        disableDeferredWipeout: true,
        patterns: [
                [pattern: '.git/**', type: 'EXCLUDE'],
                [pattern: 'tests/**', type: 'EXCLUDE'],
                [pattern: 'tox.ini', type: 'EXCLUDE'],
                [pattern: 'dist/', type: 'EXCLUDE'],
                [pattern: 'pyproject.toml', type: 'EXCLUDE'],
                [pattern: 'setup.cfg', type: 'EXCLUDE'],
                [pattern: glob, type: 'EXCLUDE'],
            ]
    )
    script{
        def pkgs = findFiles(glob: glob)
//         todo here
        if(pkgs.size() == 0){
            error "No packages found for ${glob}"
        }
        pkgs.each{
            sh(
                label: "Testing ${it}",
                script: """python3 -m venv venv
                           venv/bin/python -m pip install pip --upgrade
                           venv/bin/python -m pip install wheel
                           venv/bin/python -m pip install --upgrade setuptools
                           venv/bin/python -m pip install tox
                           venv/bin/tox --installpkg=${it.path} -e py -vv --recreate
                           """
            )
        }
    }
}
// def devpiRunTest3(devpiClient, pkgName, pkgVersion, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
//         if (isUnix()){
//             sh(
//                 label: "Running test",
//                 script: """${devpiClient} use https://devpi.library.illinois.edu --clientdir certs/
//                            ${devpiClient} login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
//                            ${devpiClient} use ${devpiIndex} --clientdir certs/
//                            ${devpiClient} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
//                 """
//             )
//         } else {
//             bat(
//                 label: "Running tests on Devpi",
//                 script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
//                            devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
//                            devpi use ${devpiIndex} --clientdir certs\\
//                            devpi test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
//                            """
//             )
//         }
//     }
// }
// def devpiRunTest2(devpiClient, pkgPropertiesFile, devpiIndex, devpiSelector, devpiUsername, devpiPassword, toxEnv){
//     script{
//         if(!fileExists(pkgPropertiesFile)){
//             error "${pkgPropertiesFile} does not exist"
//         }
//         def props = readProperties interpolate: false, file: pkgPropertiesFile
//         if (isUnix()){
//             sh(
//                 label: "Running test",
//                 script: """${devpiClient} use https://devpi.library.illinois.edu --clientdir certs/
//                            ${devpiClient} login ${devpiUsername} --password ${devpiPassword} --clientdir certs/
//                            ${devpiClient} use ${devpiIndex} --clientdir certs/
//                            ${devpiClient} test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs/ -e ${toxEnv} --tox-args=\"-vv\"
//                 """
//             )
//         } else {
//             bat(
//                 label: "Running tests on Devpi",
//                 script: """devpi use https://devpi.library.illinois.edu --clientdir certs\\
//                            devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
//                            devpi use ${devpiIndex} --clientdir certs\\
//                            devpi test --index ${devpiIndex} ${props.Name}==${props.Version} -s ${devpiSelector} --clientdir certs\\ -e ${toxEnv} --tox-args=\"-vv\"
//                            """
//             )
//         }
//     }
// }

def testDevpiPackage(devpiIndex, devpiUsername, devpiPassword,  pkgName, pkgVersion, pkgSelector, toxEnv){
    if(isUnix()){
        sh(
            label: "Running tests on Packages on DevPi",
            script: """python --version
                       devpi use https://devpi.library.illinois.edu --clientdir certs
                       devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs
                       devpi use ${devpiIndex} --clientdir certs
                       devpi test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector} --clientdir certs -e ${toxEnv} -v
                       """
        )
    } else {
        bat(
            label: "Running tests on Packages on DevPi",
            script: """python --version
                       devpi use https://devpi.library.illinois.edu --clientdir certs\\
                       devpi login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                       devpi use ${devpiIndex} --clientdir certs\\
                       devpi test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector}  --clientdir certs\\ -e ${toxEnv} -v
                       """
        )
    }
}

def testDevpiPackage2(devpiExec, devpiIndex, devpiUsername, devpiPassword,  pkgName, pkgVersion, pkgSelector, toxEnv){
    if(isUnix()){
        sh(
            label: "Running tests on Packages on DevPi",
            script: """${devpiExec} use https://devpi.library.illinois.edu --clientdir certs
                       ${devpiExec} login ${devpiUsername} --password ${devpiPassword} --clientdir certs
                       ${devpiExec} use ${devpiIndex} --clientdir certs
                       ${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector} --clientdir certs -e ${toxEnv} -v
                       """
        )
    } else {
        bat(
            label: "Running tests on Packages on DevPi",
            script: """${devpiExec} use https://devpi.library.illinois.edu --clientdir certs\\
                       ${devpiExec} login ${devpiUsername} --password ${devpiPassword} --clientdir certs\\
                       ${devpiExec} use ${devpiIndex} --clientdir certs\\
                       ${devpiExec} test --index ${devpiIndex} ${pkgName}==${pkgVersion} -s ${pkgSelector}  --clientdir certs\\ -e ${toxEnv} -v
                       """
        )
    }
}

def test_pkg(glob, timeout_time){

    def pkgFiles = findFiles( glob: glob)
    if( pkgFiles.size() == 0){
        error "Unable to check package. No files found with ${glob}"
    }

    pkgFiles.each{
        timeout(timeout_time){
            if(isUnix()){
                sh(label: "Testing ${it}",
                   script: """python --version
                              tox --installpkg=${it.path} -e py -vv
                              """
                )
            } else {
                bat(label: "Testing ${it}",
                    script: """python --version
                               tox --installpkg=${it.path} -e py -vv
                               """
                )
            }
        }
    }
}

def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + "/api/issues/search?componentKeys=" + props['projectKey'] + "&resolved=no"
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

def get_package_name(stashName, metadataFile){
    node {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Name
        }
    }
}

def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return "tag_staging"
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

def deploy_docs(pkgName, prefix){
    sshPublisher(
        publishers: [
            sshPublisherDesc(
                configName: 'apache-ns - lib-dccuser-updater',
                sshLabel: [label: 'Linux'],
                transfers: [sshTransfer(excludes: '',
                execCommand: '',
                execTimeout: 120000,
                flatten: false,
                makeEmptyDirs: false,
                noDefaultExcludes: false,
                patternSeparator: '[, ]+',
                remoteDirectory: "${pkgName}",
                remoteDirectorySDF: false,
                removePrefix: "${prefix}",
                sourceFiles: "${prefix}/**")],
            usePromotionTimestamp: false,
            useWorkspaceInPromotion: false,
            verbose: true
            )
        ]
    )
}

def build_wheel(){

    if(isUnix()){
        sh(label: "Building Python Wheel",
            script: "python -m pip wheel -w dist/ --no-deps ."
        )
    } else{
        bat(label: "Building Python Wheel",
            script: "python -m pip wheel -w dist/ -v --no-deps ."
        )
    }
}

def sonarcloudSubmit(metadataFile, outputJson, sonarCredentials){
    def props = readProperties interpolate: true, file: metadataFile
    withSonarQubeEnv(installationName:"sonarcloud", credentialsId: sonarCredentials) {
        if (env.CHANGE_ID){
            sh(
                label: "Running Sonar Scanner",
                script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
                )
        } else {
            sh(
                label: "Running Sonar Scanner",
                script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
                )
        }
    }
     timeout(time: 1, unit: 'HOURS') {
         def sonarqube_result = waitForQualityGate(abortPipeline: false)
         if (sonarqube_result.status != 'OK') {
             unstable "SonarQube quality gate: ${sonarqube_result.status}"
         }
         def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
         writeJSON file: outputJson, json: outstandingIssues
     }
}
def startup(){
    stage("Getting Distribution Info"){
        node('linux && docker') {
            docker.image('python:3.8').inside {
                timeout(2){
                    try{
                        checkout scm
                        sh(
                           label: "Running setup.py with dist_info",
                           script: """python --version
                                      python setup.py dist_info
                                   """
                        )
                        stash includes: "py3exiv2bind.dist-info/**", name: 'DIST-INFO'
                        archiveArtifacts artifacts: "py3exiv2bind.dist-info/**"
                    } finally{
                        deleteDir()
                    }
                }
            }
        }
    }
}



def test_cpp_code(buildPath){
    stage("Build"){
        tee("logs/cmake-build.log"){
            sh(label: "Building C++ Code",
               script: """conan install . -if ${buildPath}
                          cmake -B ${buildPath} -Wdev -DCMAKE_TOOLCHAIN_FILE=build/conan_paths.cmake -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra"
                          cmake --build ${buildPath} -j \$(grep -c ^processor /proc/cpuinfo)
                          """
            )
        }
    }
    stage("CTest"){
        sh(label: "Running CTest",
           script: "cd ${buildPath} && ctest --output-on-failure --no-compress-output -T Test"
        )
    }
}
def get_props(){
    stage("Reading Package Metadata"){
        node() {
            try{
                unstash "DIST-INFO"
                def props = readProperties interpolate: true, file: "py3exiv2bind.dist-info/METADATA"
                return props
            } finally {
                deleteDir()
            }
        }
    }
}
startup()
def props = get_props()

pipeline {
    agent none
    parameters {
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "RUN_CHECKS", defaultValue: true, description: "Run checks on code")
        booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")
        booleanParam(name: "BUILD_PACKAGES", defaultValue: false, description: "Build Python packages")
        booleanParam(name: "BUILD_MAC_PACKAGES", defaultValue: false, description: "Test Python packages on Mac")
        booleanParam(name: "TEST_PACKAGES", defaultValue: true, description: "Test Python packages by installing them and running tests on the installed package")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")
    }
    stages {
//     todo turn this back on
//         stage("Building Documentation"){
//             agent {
//                 dockerfile {
//                     filename 'ci/docker/linux/test/Dockerfile'
//                     label 'linux && docker'
//                     additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
//                 }
//             }
//             steps {
//                 sh(label: "Running Sphinx",
//                    script: '''mkdir -p logs
//                               mkdir -p build/docs/html
//                               python setup.py build -b build --build-lib build/lib/ --build-temp build/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace
//                               python -m sphinx docs/source build/docs/html -b html -d build/docs/.doctrees --no-color -w logs/build_sphinx.log
//                               '''
//                   )
//             }
//             post{
//                 always {
//                     recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
//                 }
//                 success{
//                     publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
//                     script{
//                         def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
//                         zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
//                     }
//                     stash includes: "dist/*.doc.zip,build/docs/html/**", name: 'DOCS_ARCHIVE'
//                 }
//                 cleanup{
//                     cleanWs(patterns: [
//                             [pattern: 'logs/build_sphinx.log', type: 'INCLUDE'],
//                             [pattern: "dist/*doc.zip,", type: 'INCLUDE']
//                         ]
//                     )
//                 }
//             }
//         }
        stage("Checks"){
            when{
                equals expected: true, actual: params.RUN_CHECKS
            }
            stages{
                stage("Run Tox test") {
//                                     when {
//                                        equals expected: true, actual: params.TEST_RUN_TOX
//                                        beforeAgent true
//                                     }
                    steps {
                        script{
                            def linux_jobs = getToxTestsParallel("Linux", "linux && docker", "ci/docker/linux/tox/Dockerfile", "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL")
                            def windows_jobs = getToxTestsParallel("Windows", "windows && docker", "ci/docker/windows/tox/Dockerfile", "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE")
                            def jobs = windows_jobs + linux_jobs
                            parallel(jobs)
                        }
                    }
                }
                stage("Testing"){
                    stages{
                        stage("Python Testing"){
                            stages{
                                stage("Testing") {
                                    agent {
                                        dockerfile {
                                            filename 'ci/docker/linux/test/Dockerfile'
                                            label 'linux && docker'
                                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                        }
                                    }
                                    stages{
                                        stage("Setting up Test Env"){
                                            steps{
                                                sh(label: "Building debug build with coverage data",
                                                   script: '''CFLAGS="--coverage" python setup.py build -b build --build-lib build/lib/ --build-temp build/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace
                                                              mkdir -p logs
                                                              '''
                                               )
                                            }
                                        }
                                        stage("Running Tests"){
                                            parallel {
                                                stage("Run Doctest Tests"){
                                                    steps {
                                                        sh "sphinx-build docs/source reports/doctest -b doctest -d build/docs/.doctrees --no-color -w logs/doctest_warnings.log"
                                                    }
                                                    post{
                                                        always {
                                                            recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest_warnings.log', id: 'doctest')])
                                                        }
                                                    }
                                                }
                                                stage("MyPy Static Analysis") {
                                                    steps{
                                                        sh(returnStatus: true,
                                                           script: '''stubgen -p py3exiv2bind -o ./mypy_stubs
                                                                      mkdir -p reports/mypy/html
                                                                      MYPYPATH="$WORKSPACE/mypy_stubs" mypy -p py3exiv2bind --html-report reports/mypy/html > logs/mypy.log
                                                                      '''
                                                          )
                                                    }
                                                    post {
                                                        always {
                                                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                        }
                                                        cleanup{
                                                            cleanWs(
                                                                deleteDirs: true,
                                                                patterns: [[pattern: 'mypy_stubs', type: 'INCLUDE']]
                                                            )
                                                        }
                                                    }
                                                }
                                                stage("Run Pylint Static Analysis") {
                                                    steps{
                                                        catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                            sh(
                                                                script: '''mkdir -p logs
                                                                           mkdir -p reports
                                                                           PYLINTHOME=. pylint py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                                           ''',
                                                                label: "Running pylint"
                                                            )
                                                        }
                                                        sh(
                                                            script: 'PYLINTHOME=. pylint  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                                            label: "Running pylint for sonarqube",
                                                            returnStatus: true
                                                        )
                                                    }
                                                    post{
                                                        always{
                                                            stash includes: "reports/pylint_issues.txt,reports/pylint.txt", name: 'PYLINT_REPORT'
                                                            recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                                        }
                                                    }
                                                }
                                                stage("Flake8") {
                                                  steps{
                                                    timeout(2){
                                                        sh returnStatus: true, script: "flake8 py3exiv2bind --tee --output-file ./logs/flake8.log"
                                                    }
                                                  }
                                                  post {
                                                    always {
                                                        stash includes: "logs/flake8.log", name: 'FLAKE8_REPORT'
                                                        recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                    }
                                                  }
                                                }
                                                stage("Running Unit Tests"){
                                                    steps{
                                                        timeout(2){
                                                            sh "coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=./reports/pytest/junit-pytest.xml"
                                                        }
                                                    }
                                                    post{
                                                        always{
                                                            stash includes: "reports/pytest/junit-pytest.xml", name: 'PYTEST_REPORT'
                                                            junit "reports/pytest/junit-pytest.xml"
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    post{
                                        always{
                                            sh(label: 'combining coverage data',
                                               script: '''mkdir -p reports/coverage
                                                          coverage combine
                                                          coverage xml -o ./reports/coverage/coverage-python.xml
                                                          gcovr --root . --filter py3exiv2bind --exclude-directories build/temp/conan_cache --print-summary --json -o reports/coverage/coverage-c-extension.json
                                                          '''
                                            )
                                            stash(includes: 'reports/coverage/*.xml,reports/coverage/*.json', name: 'PYTHON_COVERAGE_REPORT')
                                        }
                                        cleanup{
                                            cleanWs(
                                                deleteDirs: true,
                                                patterns: [
                                                    [pattern: 'reports/coverage/', type: 'INCLUDE'],
                                                ]
                                            )
                                        }
                                    }
                                }

                            }
                        }
                        stage("C++ Testing"){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/cpp/Dockerfile'
                                    label 'linux && docker'
                                    additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                }
                            }
                            steps{
                                test_cpp_code('build')
                            }
                            post{
                                always{
                                    recordIssues(
                                        filters: [excludeFile('build/_deps/*')],
                                        tools: [gcc(pattern: 'logs/cmake-build.log'), [$class: 'Cmake', pattern: 'logs/cmake-build.log']]
                                        )

                                    sh "mkdir -p reports/coverage && gcovr --root . --filter py3exiv2bind --print-summary  --json -o reports/coverage/coverage_cpp.json"
                                    stash(includes: "reports/coverage/*.json", name: "CPP_COVERAGE_TRACEFILE")
                                    xunit(
                                        testTimeMargin: '3000',
                                        thresholdMode: 1,
                                        thresholds: [
                                            failed(),
                                            skipped()
                                        ],
                                        tools: [
                                            CTest(
                                                deleteOutputFiles: true,
                                                failIfNotNew: true,
                                                pattern: "build/Testing/**/*.xml",
                                                skipNoTestFiles: true,
                                                stopProcessingIfError: true
                                            )
                                        ]
                                   )
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'build/', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
                        stage("Report Coverage"){
                            agent {
                                dockerfile {
                                    filename 'ci/docker/linux/test/Dockerfile'
                                    label 'linux && docker'
                                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                }
                            }
                            steps{
                                unstash "PYTHON_COVERAGE_REPORT"
                                unstash "CPP_COVERAGE_TRACEFILE"
                                sh "gcovr --add-tracefile reports/coverage/coverage-c-extension.json --add-tracefile reports/coverage/coverage_cpp.json --print-summary --xml -o reports/coverage/coverage_cpp.xml"
                                publishCoverage(
                                    adapters: [
                                            coberturaAdapter(mergeToOneReport: true, path: 'reports/coverage/*.xml')
                                        ],
                                    sourceFileResolver: sourceFiles('NEVER_STORE')
                                )
                            }
                        }
                    }
//                     post{
//                         always{
//                             node("linux && docker"){
//                                 script{
//                                     docker.build("py3exiv2bind:util",'-f ci/docker/linux/test/Dockerfile --build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
//                                         checkout scm
//                                         unstash "PYTHON_COVERAGE_REPORT"
//                                         unstash "CPP_COVERAGE_TRACEFILE"
//                                         sh "gcovr --add-tracefile reports/coverage/coverage-c-extension.json --add-tracefile reports/coverage/coverage_cpp.json --print-summary --xml -o reports/coverage/coverage_cpp.xml"
//                                         publishCoverage(
//                                             adapters: [
//                                                     coberturaAdapter(mergeToOneReport: true, path: 'reports/coverage/*.xml')
//                                                 ],
//                                             sourceFileResolver: sourceFiles('NEVER_STORE')
//                                         )
//                                     }
//                                 }
//                             }
//                         }
//                     }
                }

                stage("Sonarcloud Analysis"){
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/test/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            args '--mount source=sonar-cache-py3exiv2bind,target=/home/user/.sonar/cache'
                        }
                    }
                    options{
                        lock("py3exiv2bind-sonarcloud")
                    }
                    when{
                        equals expected: true, actual: params.USE_SONARQUBE
                        beforeAgent true
                        beforeOptions true
                    }
                    steps{
                        unstash "PYTHON_COVERAGE_REPORT"
                        unstash "PYTEST_REPORT"
        //                 unstash "BANDIT_REPORT"
                        unstash "PYLINT_REPORT"
                        unstash "FLAKE8_REPORT"
                        unstash "DIST-INFO"
                        sonarcloudSubmit("py3exiv2bind.dist-info/METADATA", "reports/sonar-report.json", 'sonarcloud-py3exiv2bind')
                    }
                    post {
                        always{
                            script{
                                if(fileExists('reports/sonar-report.json')){
                                    recordIssues(tools: [sonarQube(pattern: 'reports/sonar-report.json')])
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Distribution Packages') {
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            stages{
                stage("Python sdist"){
                    agent{
                        dockerfile {
                            filename 'ci/docker/linux/test/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                        }
                    }
                    steps {
                       sh "python -m pep517.build --source --out-dir dist/ ."
                    }
                    post{
                       success{
                           stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                           archiveArtifacts artifacts: "dist/*.tar.gz,dist/*.zip", fingerprint: true
                       }
                   }
                }
                stage("macOS 10.14"){
                    when{
                        equals expected: true, actual: params.BUILD_MAC_PACKAGES
                    }
                    stages{
                        stage('Building Wheel') {
                            agent {
                                label 'mac && 10.14 && python3.8'
                            }
                            steps{
                                sh(
                                    label: "Building wheel for macOS 10.14",
                                    script: 'python3 -m pip wheel --no-deps -w dist .'
                                )
                            }
                            post{
                                always{
                                    stash includes: 'dist/*.whl', name: "MacOS 10.14 py38 wheel"
                                }
                                success{
                                    archiveArtifacts artifacts: "dist/*.whl"
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [
                                            [pattern: 'build/', type: 'INCLUDE'],
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                        ]
                                    )
                                }
                            }
                        }
                        stage("Testing Packages"){
                            when{
                                equals expected: true, actual: params.TEST_PACKAGES
                            }
                            parallel{
                                stage('Testing Wheel Package') {
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        unstash "MacOS 10.14 py38 wheel"
                                        test_package_on_mac("dist/*.whl")
                                    }
                                    post{
                                        cleanup{
                                            deleteDir()
                                        }
                                    }
                                }
                                stage('Testing sdist Package') {
                                    when{
                                        anyOf{
                                            equals expected: true, actual: params.TEST_PACKAGES
                                        }
                                        beforeAgent true
                                    }
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        unstash "sdist"
                                        test_package_on_mac("dist/*.tar.gz,dist/*.zip")
                                    }
                                    post{
                                        cleanup{
                                            deleteDir()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Windows and Linux"){
                    matrix{
                        agent none
                        axes{
                            axis {
                                name 'PLATFORM'
                                values(
                                    "linux",
                                    "windows"
                                )
                            }
                            axis {
                                name "PYTHON_VERSION"
                                values(
        //                             "3.6",
                                    "3.7",
                                    "3.8"
                                )
                            }
                        }
                        stages{
                            stage("Creating bdist wheel"){
                                agent {
                                    dockerfile {
                                        filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.package.dockerfile.filename}"
                                        label "${PLATFORM} && docker"
                                        additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.package.dockerfile.additionalBuildArgs}"
                                     }
                                }
                                options {
                                    warnError('Wheel Building Failed')
                                }
                                steps{
                                    timeout(15){
                                        build_wheel()
                                        script{
                                            if(PLATFORM == "linux"){
                                                sh(
                                                    label: "Converting linux wheel to manylinux",
                                                    script:"auditwheel repair ./dist/*.whl -w ./dist"
                                                )
                                            }
                                        }
                                    }
                                }
                                post{
                                    always{
                                        script{
                                            if(PLATFORM == "linux"){
                                                stash includes: 'dist/*manylinux*.whl', name: "whl ${PYTHON_VERSION} ${PLATFORM}"
                                            } else{
                                                stash includes: 'dist/*.whl', name: "whl ${PYTHON_VERSION} ${PLATFORM}"
                                            }
                                        }
//                                         check_dll_deps("build/lib")
                                    }
                                    success{
                                        archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
                                    }
                                    cleanup{
                                        cleanWs(
                                            deleteDirs: true,
                                            patterns: [
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                [pattern: '.tox/', type: 'INCLUDE'],
                                                [pattern: '**/__pycache__', type: 'INCLUDE'],
                                            ]
                                        )
                                    }
                                }
                            }
                        stage("Testing Python Packages"){
                                when{
                                    equals expected: true, actual: params.TEST_PACKAGES
                                }
                                stages{
                                    stage("Testing Wheel Package"){
                                        agent {
                                            dockerfile {
                                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['wheel'].dockerfile.filename}"
                                                label "${PLATFORM} && docker"
                                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['wheel'].dockerfile.additionalBuildArgs}"
                                             }
                                        }
                                        options {
                                            warnError('Testing Wheel Failed')
                                        }
                                        steps{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                disableDeferredWipeout: true,
                                                patterns: [
                                                        [pattern: '.git/**', type: 'EXCLUDE'],
                                                        [pattern: 'tests/**', type: 'EXCLUDE'],
                                                        [pattern: 'tox.ini', type: 'EXCLUDE'],
                                                    ]
                                            )
                                            unstash "whl ${PYTHON_VERSION} ${platform}"
                                            catchError(stageResult: 'FAILURE') {
                                                test_pkg("dist/**/${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].pkgRegex['wheel']}", 15)
                                            }
                                        }
                                        post{
                                            cleanup{
                                                cleanWs(
                                                    deleteDirs: true,
                                                    notFailBuild: true,
                                                    patterns: [
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: '**/__pycache__', type: 'INCLUDE'],
                                                        [pattern: '.tox/', type: 'INCLUDE'],
                                                    ]
                                                )
                                            }
                                        }
                                    }
                                    stage("Testing sdist Package"){
                                        agent {
                                            dockerfile {
                                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].dockerfile.filename}"
                                                label "${PLATFORM} && docker"
                                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].dockerfile.additionalBuildArgs}"
                                             }
                                        }
                                        options {
                                            warnError('Testing sdist Failed')
                                        }
                                        steps{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                disableDeferredWipeout: true,
                                                patterns: [
                                                        [pattern: '.git/**', type: 'EXCLUDE'],
                                                        [pattern: 'tests/**', type: 'EXCLUDE'],
                                                        [pattern: 'tox.ini', type: 'EXCLUDE'],
                                                    ]
                                            )
                                            catchError(stageResult: 'FAILURE') {
                                                unstash "sdist"
                                                test_pkg("dist/*.zip,dist/*.tar.gz", 20)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        stage("Deploy to Devpi"){
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                        tag "*"
                    }
                }
                beforeAgent true
            }
            agent none
            environment{
                DEVPI = credentials("DS_devpi")
                devpiStagingIndex = getDevPiStagingIndex()
            }
            options{
                lock("py3exiv2bind-devpi")
            }
            stages{
                stage("Deploy to Devpi Staging") {
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                          }
                    }
                    steps {
                        timeout(5){
                            script{
                                if(params.BUILD_MAC_PACKAGES){
                                    unstash "MacOS 10.14 py38 wheel"
                                }
                            }
//                             unstash "whl 3.6 windows"
//                             unstash "whl 3.6 linux"
                            unstash "whl 3.7 windows"
                            unstash "whl 3.7 linux"
                            unstash "whl 3.8 windows"
                            unstash "whl 3.8 linux"
                            unstash "sdist"
                            unstash "DOCS_ARCHIVE"
                            sh(
                                label: "Uploading to DevPi Staging",
                                script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                           devpi use /${env.DEVPI_USR}/${env.devpiStagingIndex} --clientdir ./devpi
                                           devpi upload --from-dir dist --clientdir ./devpi
                                           """
                            )
                        }
                    }
                }
                stage("Test DevPi Packages") {
                    stages{
                        stage("macOS 10.14") {
                            when{
                                equals expected: true, actual: params.BUILD_MAC_PACKAGES
                            }
                            parallel{
                                stage("Wheel"){
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        timeout(10){
                                            sh(
                                                label: "Installing devpi client",
                                                script: '''python3 -m venv venv
                                                           venv/bin/python -m pip install --upgrade pip
                                                           venv/bin/pip install devpi-client
                                                           venv/bin/devpi --version
                                                '''
                                            )
                                            testDevpiPackage2("venv/bin/devpi", env.devpiStagingIndex, DEVPI_USR, DEVPI_PSW, props.Name, props.Version, "38-macosx_10_14_x86_64*.*whl",  "py38")
                                        }
                                    }
                                    post{
                                        cleanup{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                patterns: [
                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                ]
                                            )
                                        }
                                    }
                                }
                                stage("sdist"){
                                    agent {
                                        label 'mac && 10.14 && python3.8'
                                    }
                                    steps{
                                        timeout(10){
                                            sh(
                                                label: "Installing devpi client",
                                                script: '''python3 -m venv venv
                                                           venv/bin/python -m pip install --upgrade pip
                                                           venv/bin/pip install devpi-client
                                                           venv/bin/devpi --version
                                                '''
                                            )
                                            testDevpiPackage2(
                                                "venv/bin/devpi",
                                                env.devpiStagingIndex,
                                                DEVPI_USR, DEVPI_PSW,
                                                props.Name, props.Version,
                                                "tar.gz",
                                                "py38"
                                            )
                                        }
                                    }
                                    post{
                                        cleanup{
                                            cleanWs(
                                                notFailBuild: true,
                                                deleteDirs: true,
                                                patterns: [
                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                ]
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        stage("Windows and Linux"){
                            matrix {
                                axes {
                                    axis {
                                        name 'PYTHON_VERSION'
                                        values  '3.7', '3.8'
                                    }
                                    axis {
                                        name 'PLATFORM'
                                        values(
                                            "windows",
                                            "linux"
                                        )
                                    }
                                }
                                agent none
                                stages{
                                    stage("DevPi Wheel Package"){
                                        agent {
                                          dockerfile {
                                            filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['wheel'].dockerfile.filename}"
                                            additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['wheel'].dockerfile.additionalBuildArgs}"
                                            label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['wheel'].dockerfile.label}"
                                          }
                                        }
                                        steps{
                                            script{
                                                testDevpiPackage(
                                                    env.devpiStagingIndex,
                                                    DEVPI_USR, DEVPI_PSW,
                                                    props.Name, props.Version,
                                                    CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].devpiSelector['wheel'],
                                                    CONFIGURATIONS[PYTHON_VERSION].tox_env
                                                )
                                            }
                                        }
                                    }
                                    stage("DevPi sdist Package"){
                                        agent {
                                          dockerfile {
                                            filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.filename}"
                                            additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.additionalBuildArgs}"
                                            label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi['sdist'].dockerfile.label}"
                                          }
                                        }
                                        steps{
                                            script{
                                                testDevpiPackage(
                                                    env.devpiStagingIndex,
                                                    DEVPI_USR, DEVPI_PSW,
                                                    props.Name, props.Version,
                                                    "tar.gz",
                                                    CONFIGURATIONS[PYTHON_VERSION].tox_env
                                                    )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf {
                                branch "master"
                                tag "*"
                            }
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    options{
                      timeout(time: 1, unit: 'DAYS')
                    }
                    input {
                      message 'Release to DevPi Production?'
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/deploy/devpi/deploy/Dockerfile'
                            label 'linux&&docker'
                            additionalBuildArgs '--build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                        }
                    }
                    steps {
                        script {
                            sh(
                                label: "Pushing to DS_Jenkins/${env.BRANCH_NAME} index",
                                script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                           devpi push --index DS_Jenkins/${env.devpiStagingIndex} ${props.Name}==${props.Version} production/release --clientdir ./devpi
                                           """
                            )
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                        script{
                            docker.build("py3exiv2bind:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                if (!env.TAG_NAME?.trim()){
                                    sh(
                                        label: "Pushing ${props.Name} ${props.Version} to DS_Jenkins/${env.BRANCH_NAME} index on DevPi Server",
                                        script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                                   devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                                   devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                                   devpi push ${props.Name}==${props.Version} DS_Jenkins/${env.BRANCH_NAME} --clientdir ./devpi
                                                   """
                                    )
                                }
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker') {
                       script{
                            docker.build("py3exiv2bind:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                sh(
                                label: "Removing ${props.Name} ${props.Version} from staging index on DevPi Server",
                                script: """devpi use https://devpi.library.illinois.edu --clientdir ./devpi
                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ./devpi
                                           devpi use /DS_Jenkins/${env.devpiStagingIndex} --clientdir ./devpi
                                           devpi remove -y ${props.Name}==${props.Version} --clientdir ./devpi
                                           """
                               )
                            }
                       }
                    }
                }
            }
        }
        stage("Deploy"){
            parallel {
                stage("Deploy Online Documentation") {
                    agent any
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                        beforeAgent true
                        beforeInput true
                        beforeInput true
                    }
                    options{
                        timeout(30)
                    }
                    input{
                        message 'Update project documentation?'
                    }
                    steps{
                        unstash "DOCS_ARCHIVE"
                        deploy_docs(get_package_name("DIST-INFO", "py3exiv2bind.dist-info/METADATA"), "build/docs/html")
                    }
                }
            }
        }
    }
}
