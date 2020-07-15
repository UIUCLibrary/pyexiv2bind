#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils

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
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe --build-arg CHOCOLATEY_SOURCE'
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
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        package: [
                            dockerfile: [
                                filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                label: 'Windows&&Docker',
                                additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg CHOCOLATEY_SOURCE'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg CHOCOLATEY_SOURCE'
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
                                    additionalBuildArgs: '--build-arg PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe --build-arg CHOCOLATEY_SOURCE'
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

def test_pkg(glob, timeout_time){

    findFiles( glob: glob).each{
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
            script: 'python setup.py build -b build/ -j $(grep -c ^processor /proc/cpuinfo) --build-lib build/lib --build-temp build/temp bdist_wheel -d ./dist'
        )
    } else{
        bat(label: "Building Python Wheel",
            script: "python setup.py build -b build/ -j ${env.NUMBER_OF_PROCESSORS} --build-lib build/lib --build-temp build/temp bdist_wheel -d ./dist"
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

pipeline {
    agent none
    options {
        buildDiscarder logRotator(artifactDaysToKeepStr: '10', artifactNumToKeepStr: '10', daysToKeepStr: '', numToKeepStr: '')
    }
    parameters {
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "USE_SONARQUBE", defaultValue: true, description: "Send data test data to SonarQube")
        booleanParam(name: "BUILD_PACKAGES", defaultValue: false, description: "Build Python packages")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")
    }
    stages {
        stage("Getting Distribution Info"){
            agent {
                dockerfile {
                    filename 'ci/docker/linux/test/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                }
            }
            steps{
                timeout(3){
                    sh "python setup.py dist_info"
                }
            }
            post{
                success{
                    stash includes: "py3exiv2bind.dist-info/**", name: 'DIST-INFO'
                    archiveArtifacts artifacts: "py3exiv2bind.dist-info/**"
                }
            }
        }
        stage("Building") {
            agent {
                dockerfile {
                    filename 'ci/docker/linux/test/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                }
            }
            stages{
                stage("Building Python Package"){
                    steps {
                        timeout(10){
                            sh(label: "Building python package",
                               script: '''mkdir -p logs
                                          python setup.py build -b build --build-lib build/lib/ --build-temp build/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace
                                          '''
                            )
                        }
                    }
                    post{
                        success{
                          stash includes: 'py3exiv2bind/**/*.dll,py3exiv2bind/**/*.pyd,py3exiv2bind/**/*.exe,py3exiv2bind/**/*.so,', name: "built_source"
                        }
                        failure{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: 'dist/', type: 'INCLUDE'],
                                    [pattern: 'build/', type: 'INCLUDE'],
                                    [pattern: '.eggs/', type: 'INCLUDE'],
                                    [pattern: 'logs/', type: 'INCLUDE'],
                                    ]
                            )
                        }
                    }
                }
                stage("Building Sphinx Documentation"){
                    steps {
                        sh(label: "Running Sphinx",
                           script: '''mkdir -p logs
                                      mkdir -p build/docs/html
                                      python -m sphinx docs/source build/docs/html -b html -d build/docs/.doctrees --no-color -w logs/build_sphinx.log
                                      '''
                          )
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                unstash "DIST-INFO"
                                def props = readProperties(interpolate: true, file: "py3exiv2bind.dist-info/METADATA")
                                def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
                                zip archive: true, dir: "build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                                stash includes: "dist/${DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'
                            }
                        }
                        cleanup{
                            cleanWs(patterns: [
                                    [pattern: 'logs/build_sphinx.log', type: 'INCLUDE'],
                                    [pattern: "dist/*doc.zip,", type: 'INCLUDE']
                                ]
                            )
                        }
                    }
                }
            }
        }
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
                        unstash "built_source"
                        sh "mkdir -p logs"
                    }
                }
                stage("Running Tests"){
                    parallel {
                        stage("Run Tox test") {
                            when {
                               equals expected: true, actual: params.TEST_RUN_TOX
                               beforeAgent true
                            }
                            stages{
                                stage("Running Tox"){
                                    steps {
                                        timeout(15){
                                            sh "tox -e py -vv"
                                        }
                                    }
                                }
                            }
                        }
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
                                withEnv(['PYLINTHOME=.']) {
                                    catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                        sh(
                                            script: '''mkdir -p logs
                                                       mkdir -p reports
                                                       pylint py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                       ''',
                                            label: "Running pylint"
                                        )
                                    }
                                    sh(
                                        script: 'pylint   -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                        label: "Running pylint for sonarqube",
                                        returnStatus: true
                                    )
                                }
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
                    sh "coverage combine && coverage xml -o ./reports/coverage.xml && coverage html -d ./reports/coverage"
                    stash includes: "reports/coverage.xml", name: 'COVERAGE_REPORT'
                    publishCoverage(
                        adapters: [
                            coberturaAdapter('reports/coverage.xml')
                        ],
                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                    )
                }
                cleanup{
                    cleanWs(patterns: [
                            [pattern: 'reports/coverage.xml', type: 'INCLUDE'],
                            [pattern: 'reports/coverage', type: 'INCLUDE'],
                        ]
                    )
                }
            }
        }
        stage("Sonarcloud Analysis"){
            agent {
              dockerfile {
                filename 'ci/docker/sonarcloud/Dockerfile'
                label 'linux && docker'
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
                checkout scm
                sh "git fetch --all"
                unstash "COVERAGE_REPORT"
                unstash "PYTEST_REPORT"
//                 unstash "BANDIT_REPORT"
                unstash "PYLINT_REPORT"
                unstash "FLAKE8_REPORT"
                unstash "DIST-INFO"
                sonarcloudSubmit("py3exiv2bind.dist-info/METADATA", "reports/sonar-report.json", 'sonarcloud-py3exiv2bind')
//                 script{
//                     withSonarQubeEnv(installationName:"sonarcloud", credentialsId: 'sonarcloud-py3exiv2bind') {
//                         unstash "DIST-INFO"
//                         def props = readProperties(interpolate: true, file: "py3exiv2bind.dist-info/METADATA")
//                         if (env.CHANGE_ID){
//                             sh(
//                                 label: "Running Sonar Scanner",
//                                 script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
//                                 )
//                         } else {
//                             sh(
//                                 label: "Running Sonar Scanner",
//                                 script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME}"
//                                 )
//                         }
//                     }
//                     timeout(time: 1, unit: 'HOURS') {
//                         def sonarqube_result = waitForQualityGate(abortPipeline: false)
//                         if (sonarqube_result.status != 'OK') {
//                             unstable "SonarQube quality gate: ${sonarqube_result.status}"
//                         }
//                         def outstandingIssues = get_sonarqube_unresolved_issues(".scannerwork/report-task.txt")
//                         writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
//                     }
//                 }
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
        stage("Python sdist"){
            agent{
                dockerfile {
                    filename 'ci/docker/linux/test/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                }
            }
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            steps {
               sh "python setup.py sdist -d ./dist --format zip"
            }
            post{
               success{
                   stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                   archiveArtifacts artifacts: "dist/*.tar.gz,dist/*.zip", fingerprint: true
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
                            "3.6",
                            "3.7",
                            "3.8"
                        )
                    }
                }
                stages{
                    stage("Testing sdist package"){
                        agent {
                            dockerfile {
                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].dockerfile.filename}"
                                label "${PLATFORM} && docker"
                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['sdist'].dockerfile.additionalBuildArgs}"
                             }
                        }
                        steps{
                            catchError(stageResult: 'FAILURE') {
                                unstash "sdist"
                                test_pkg("dist/**/${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].pkgRegex['sdist']}", 20)
                            }
                        }
                    }
                    stage("Creating bdist wheel"){
                        agent {
                            dockerfile {
                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.package.dockerfile.filename}"
                                label "${PLATFORM} && docker"
                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.package.dockerfile.additionalBuildArgs}"
                             }
                        }
                        steps{
                            timeout(15){
                                build_wheel()
                            }
                        }
                        post{
                            always{
                                stash includes: 'dist/*.whl', name: "whl ${PYTHON_VERSION} ${PLATFORM}"
                                script{
                                    if(!isUnix()){
                                        findFiles(glob: "build/lib/**/*.pyd").each{
                                            bat(
                                                label: "Checking Python extension for dependents",
                                                script: "dumpbin /DEPENDENTS ${it.path}"
                                            )
                                        }
                                    }
                                }
                            }
                            success{
                                archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
                            }
                            cleanup{
                                cleanWs(
                                    deleteDirs: true,
                                    patterns: [[pattern: 'dist/', type: 'INCLUDE']]
                                )
                            }
                        }
                    }
                    stage("Create manylinux wheel"){
                        agent {
                          docker {
                            image 'quay.io/pypa/manylinux2014_x86_64'
                            label 'linux && docker'
                          }
                        }
                        when{
                            equals expected: "linux", actual: PLATFORM
                            beforeAgent true
                        }
                        steps{
                            unstash "whl ${PYTHON_VERSION} ${PLATFORM}"
                            sh "auditwheel repair ./dist/*.whl -w ./dist"
                        }
                        post{
                            always{
                                stash includes: 'dist/*manylinux*.whl', name: "whl ${PYTHON_VERSION} manylinux"
                            }
                            success{
                                archiveArtifacts(
                                    artifacts: "dist/*manylinux*.whl",
                                    fingerprint: true
                                )
                            }
                        }
                    }
                    stage("Testing Wheel Package"){
                        agent {
                            dockerfile {
                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['wheel'].dockerfile.filename}"
                                label "${PLATFORM} && docker"
                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test['wheel'].dockerfile.additionalBuildArgs}"
                             }
                        }
                        steps{
                            script{
                                if( platform == "linux"){
                                    unstash "whl ${PYTHON_VERSION} manylinux"
                                } else{
                                    unstash "whl ${PYTHON_VERSION} ${platform}"
                                }
                                catchError(stageResult: 'FAILURE') {
                                    test_pkg("dist/**/${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].pkgRegex['wheel']}", 15)
                                }
                            }
                        }
                        post{
                            cleanup{
                                cleanWs(
                                    deleteDirs: true,
                                    notFailBuild: true,
                                    patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: '.tox/', type: 'INCLUDE'],
                                    ]
                                )
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
                            unstash "whl 3.6 windows"
                            unstash "whl 3.6 manylinux"
                            unstash "whl 3.7 windows"
                            unstash "whl 3.7 manylinux"
                            unstash "whl 3.8 windows"
                            unstash "whl 3.8 manylinux"
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
                stage("Test DevPi packages") {
                    matrix {
                        axes {
                            axis {
                                name 'PYTHON_VERSION'
                                values '3.6', '3.7', '3.8'
                            }
                            axis {
                                name 'FORMAT'
                                values "wheel", 'sdist'
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
                            stage("Testing DevPi Package"){
                                agent {
                                  dockerfile {
                                    filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi[FORMAT].dockerfile.filename}"
                                    additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi[FORMAT].dockerfile.additionalBuildArgs}"
                                    label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.devpi[FORMAT].dockerfile.label}"
                                  }
                                }
                                steps{
                                    unstash "DIST-INFO"
                                    script{
                                        def props = readProperties interpolate: true, file: "py3exiv2bind.dist-info/METADATA"

                                        if(isUnix()){
                                            sh(
                                                label: "Running tests on Packages on DevPi",
                                                script: """python --version
                                                           devpi use https://devpi.library.illinois.edu --clientdir certs
                                                           devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir certs
                                                           devpi use ${env.devpiStagingIndex} --clientdir certs
                                                           devpi test --index ${env.devpiStagingIndex} ${props.Name}==${props.Version} -s ${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].devpiSelector[FORMAT]} --clientdir certs -e ${CONFIGURATIONS[PYTHON_VERSION].tox_env} -v
                                                           """
                                            )
                                        } else {
                                            bat(
                                                label: "Running tests on Packages on DevPi",
                                                script: """python --version
                                                           devpi use https://devpi.library.illinois.edu --clientdir certs\\
                                                           devpi login %DEVPI_USR% --password %DEVPI_PSW% --clientdir certs\\
                                                           devpi use ${env.devpiStagingIndex} --clientdir certs\\
                                                           devpi test --index ${env.devpiStagingIndex} ${props.Name}==${props.Version} -s ${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].devpiSelector[FORMAT]} --clientdir certs\\ -e ${CONFIGURATIONS[PYTHON_VERSION].tox_env} -v
                                                           """
                                            )
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
                            unstash "DIST-INFO"
                            def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
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
                        checkout scm
                        script{
                            docker.build("py3exiv2bind:devpi",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                if (!env.TAG_NAME?.trim()){
                                    unstash "DIST-INFO"
                                    def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
                                    sh(
                                        label: "Connecting to DevPi Server",
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
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
                                sh(
                                label: "Connecting to DevPi Server",
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
