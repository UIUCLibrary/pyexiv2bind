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
                        test:[
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/windows/build/test/msvc/Dockerfile',
                                    label: 'Windows&&Docker',
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.6-windowsservercore --build-arg CHOCOLATEY_SOURCE',
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
                    pkgRegex: [
                        wheel: "*cp36*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            whl: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.6 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
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
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.7',
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
                    pkgRegex: [
                        wheel: "*cp37*.whl",
                        sdist: "*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.7 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
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
                                    additionalBuildArgs: '--build-arg PYTHON_DOCKER_IMAGE_BASE=python:3.8',
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
                    pkgRegex: [
                        wheel: "*cp38*.whl",
                        sdist: "py3exiv2bind-*.zip"
                    ]
                ],
                linux: [
                    agents: [
                        build: [
                            dockerfile: [
                                filename: 'ci/docker/linux/Dockerfile',
                                label: 'linux&&docker',
                                additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                            ]
                        ],
                        test: [
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ],
                        devpi: [
                            wheel: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ],
                            sdist: [
                                dockerfile: [
                                    filename: 'ci/docker/linux/Dockerfile',
                                    label: 'linux&&docker',
                                    additionalBuildArgs: '--build-arg PYTHON_VERSION=3.8 --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
                                ]
                            ]
                        ]
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


def get_package_version(stashName, metadataFile){
    node {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Version
        }
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


def deploy_docs(pkgName, prefix){
    script{
        try{
            timeout(30) {
                input "Update project documentation to https://www.library.illinois.edu/dccdocs/${pkgName}"
            }
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
        } catch(exc){
            echo "User response timed out. Documentation not published."
        }
    }
}
def remove_from_devpi(pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
        docker.build("devpi", "-f ci/docker/deploy/devpi/deploy/Dockerfile .").inside{
            try {
                sh "devpi login ${devpiUsername} --password ${devpiPassword} --clientdir ${WORKSPACE}/devpi"
                sh "devpi use ${devpiIndex} --clientdir ${WORKSPACE}/devpi"
                sh "devpi remove -y ${pkgName}==${pkgVersion} --clientdir ${WORKSPACE}/devpi"
            } catch (Exception ex) {
                echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
            }

        }
    }

}


def deploy_devpi_production(DEVPI, PKG_NAME, PKG_VERSION, BRANCH_NAME, USR, PSW){
    script {
        try{
            timeout(30) {
                input "Release ${PKG_NAME} ${PKG_VERSION} (https://devpi.library.illinois.edu/DS_Jenkins/${BRANCH_NAME}_staging/${PKG_NAME}/${PKG_VERSION}) to DevPi Production? "
            }
            bat "${DEVPI} login ${DEVPI_USR} --password ${DEVPI_PSW} && ${DEVPI} use /DS_Jenkins/${BRANCH_NAME}_staging && ${DEVPI} push ${PKG_NAME}==${PKG_VERSION} production/release"
        } catch(err){
            echo "User response timed out. Packages not deployed to DevPi Production."
        }
    }

}


pipeline {
    agent none
    triggers {
       parameterizedCron '@daily % DEPLOY_DEVPI=true; TEST_RUN_TOX=true'
    }
    libraries {
      lib('devpi')
      lib('PythonHelpers')
    }
    options {
//         disableConcurrentBuilds()  //each branch has 1 job running at a time
//         timeout(120)  // Timeout after 120 minutes. This shouldn't take this long but it hangs for some reason
        buildDiscarder logRotator(artifactDaysToKeepStr: '10', artifactNumToKeepStr: '10', daysToKeepStr: '', numToKeepStr: '')
    }
    environment {
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
        PIPENV_NOSPIN="DISABLED"
    }
    parameters {
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")
    }
    stages {
        stage("Getting Distribution Info"){
            agent {
                dockerfile {
                    filename 'ci/docker/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs "--build-arg PYTHON_VERSION=3.8"
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
                    filename 'ci/docker/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs "--build-arg PYTHON_VERSION=3.8"
                }
            }
            stages{
                stage("Building Python Package"){
                    options{

                    }
                    steps {
                        timeout(10){
                            sh(lable: "Building python package",
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
                        sh "mkdir -p logs"
                        sh "mkdir -p build/docs/html"
                        sh "python -m sphinx docs/source build/docs/html -b html -d build/docs/.doctrees --no-color -w logs/build_sphinx.log"
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                unstash "DIST-INFO"
                                def props = readProperties(interpolate: true, file: "py3exiv2bind.dist-info/METADATA")
                                def DOC_ZIP_FILENAME = "${props.Name}-${props.Version}.doc.zip"
                                zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
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
            environment{
                junit_filename = "junit-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
            }
            agent {
                dockerfile {
                    filename 'ci/docker/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs "--build-arg PYTHON_VERSION=3.8"
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
                    options{
                        timeout(15)
                    }
                    parallel {
                        stage("Run Tox test") {
                            when {
                               equals expected: true, actual: params.TEST_RUN_TOX
                               beforeAgent true
                            }
                            stages{
                                stage("Running Tox"){
                                    options{
                                        timeout(15)
                                    }
                                    steps {
                                        sh "tox -e py -vv"
                                    }
                                }
                            }
                            post {
                                always{
                                    archiveArtifacts allowEmptyArchive: true, artifacts: '.tox/py*/log/*.log,.tox/log/*.log,logs/tox_report.json'
                                }
                            }
                        }
                        stage("Run Doctest Tests"){
                            steps {
                                sh "sphinx-build docs/source reports/doctest -b doctest -d build/docs/.doctrees --no-color -w logs/doctest_warnings.log"
                            }
                            post{
                                always {
                                    archiveArtifacts artifacts: "reports/doctest/output.txt", allowEmptyArchive: true
                                    recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest_warnings.log', id: 'doctest')])
                                }
                            }
                        }
                        stage("MyPy Static Analysis") {
                            stages{
                                stage("Generate stubs") {
                                    steps{
                                      sh "stubgen -p py3exiv2bind -o ${WORKSPACE}//mypy_stubs"
                                    }
                                }
                                stage("Run MyPy") {
                                    environment{
                                        MYPYPATH = "${WORKSPACE}/mypy_stubs"
                                    }
                                    steps{
                                        sh "mkdir -p reports/mypy/html"
                                        sh returnStatus: true, script: "mypy -p py3exiv2bind --html-report ${WORKSPACE}/reports/mypy/html > ${WORKSPACE}/logs/mypy.log"
                                    }
                                    post {
                                        always {
                                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                        }
                                    }
                                }
                            }
                            post{
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        patterns: [[pattern: 'mypy_stubs', type: 'INCLUDE']]
                                    )
                                }
                            }
                        }
                        stage("Flake8") {
                          options{
                            timeout(2)
                          }
                          steps{
                            sh returnStatus: true, script: "flake8 py3exiv2bind --tee --output-file ${WORKSPACE}/logs/flake8.log"
                          }
                          post {
                            always {
                                recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                            }
                            cleanup{
                                cleanWs patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']]
                            }
                          }
                        }
                        stage("Running Unit Tests"){
                            options{
                                timeout(2)
                            }
                            steps{
                                sh "coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=${WORKSPACE}/reports/pytest/${env.junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
                            }
                            post{
                                always{
                                    junit "reports/pytest/${env.junit_filename}"
                                }
                            }
                        }
                    }
                }
            }
            post{
                success{
                    sh "coverage combine && coverage xml -o ${WORKSPACE}/reports/coverage.xml && coverage html -d ${WORKSPACE}/reports/coverage"
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
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
        stage("Python sdist"){
            agent{
                dockerfile {
                    filename 'ci/docker/linux/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs "--build-arg PYTHON_VERSION=3.8"
                }
            }
           steps {
               sh "python setup.py sdist -d ${WORKSPACE}/dist --format zip"
           }
           post{
               success{
                   stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                   archiveArtifacts artifacts: "dist/*.tar.gz,dist/*.zip", fingerprint: true
               }
           }
       }
        stage('Testing Packages') {
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
                        name 'FORMAT'
                        values(
                            "wheel",
                            "sdist"
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
                excludes{
                    exclude {
                        axis {
                            name 'PLATFORM'
                            values 'linux'
                        }
                        axis {
                            name 'FORMAT'
                            values 'wheel'
                        }
                    }
                }
                stages{
                    stage("Creating bdist wheel"){
                        agent {
                            dockerfile {
                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.build.dockerfile.filename}"
                                label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.build.dockerfile.label}"
                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.build.dockerfile.additionalBuildArgs}"
                             }
                        }
                        when{
                            equals expected: "wheel", actual: FORMAT
                            beforeAgent true
                        }
                        steps{
                            timeout(15){
                                bat(
                                    script: "python setup.py build -b build/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/lib --build-temp build/temp bdist_wheel -d ${WORKSPACE}\\dist",
                                    label: "Building Wheel for Python ${PYTHON_VERSION} for ${PLATFORM}"
                                )
                            }
                        }
                        post{
                            always{
                                script{
                                    findFiles(glob: "build/lib/**/*.pyd").each{
                                        bat(
                                            label: "Checking Python extension for dependents",
                                            script: "dumpbin /DEPENDENTS ${it.path}"
                                        )
                                    }
                                }
                            }
                            success{
                                stash includes: 'dist/*.whl', name: "whl ${PYTHON_VERSION}"
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
                    stage("Testing package"){
                        agent {
                            dockerfile {
                                filename "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test[FORMAT].dockerfile.filename}"
                                label "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test[FORMAT].dockerfile.label}"
                                additionalBuildArgs "${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].agents.test[FORMAT].dockerfile.additionalBuildArgs}"
                             }
                        }
                        steps{
                            script{
                                if(FORMAT == "wheel") {
                                    unstash "whl ${PYTHON_VERSION}"
                                } else {
                                    unstash "sdist"
                                }
                                if(PLATFORM == "windows"){
                                    bat(
                                        label: "Checking Python version",
                                        script: "python --version"
                                        )
                                } else{
                                    sh(
                                        label: "Checking Python version",
                                        script: "python --version"
                                    )
                                }
                            }
                            script{
                                findFiles( glob: "dist/**/${CONFIGURATIONS[PYTHON_VERSION].os[PLATFORM].pkgRegex[FORMAT]}").each{
                                    timeout(15){
                                        if(PLATFORM == "windows"){
                                            bat(
                                                script: "tox --installpkg=${it.path} -e py -vv",
                                                label: "Testing ${it}"
                                            )
                                        } else {
                                            sh(
                                                script: "tox --installpkg=${it.path} -e py -vv",
                                                label: "Testing ${it}"
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        post{
                            cleanup{
                                cleanWs(
                                    deleteDirs: true,
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
                    }
                }
                beforeAgent true
            }
            agent none
            environment{
                DEVPI = credentials("DS_devpi")
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
                    options{
                        timeout(5)
                    }
                    steps {
                        unstash "whl 3.6"
                        unstash "whl 3.7"
                        unstash "whl 3.8"
                        unstash "sdist"
                        unstash "DOCS_ARCHIVE"
                        sh(
                            label: "Connecting to DevPi Server",
                            script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                        )
                        sh(
                            label: "Uploading to DevPi Staging",
                            script: """devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi
devpi upload --from-dir dist --clientdir ${WORKSPACE}/devpi"""
                        )
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
                        excludes{
                             exclude {
                                 axis {
                                     name 'PLATFORM'
                                     values 'linux'
                                 }
                                 axis {
                                     name 'FORMAT'
                                     values 'wheel'
                                 }
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
                                                label: "Checking Python version",
                                                script: "python --version"
                                            )
                                            sh(
                                                label: "Connecting to DevPi index",
                                                script: "devpi use https://devpi.library.illinois.edu --clientdir certs && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir certs && devpi use ${env.BRANCH_NAME}_staging --clientdir certs"
                                            )
                                            sh(
                                                label: "Running tests on Devpi",
                                                script: "devpi test --index ${env.BRANCH_NAME}_staging ${props.Name}==${props.Version} -s ${CONFIGURATIONS[PYTHON_VERSION].devpiSelector[FORMAT]} --clientdir certs -e ${CONFIGURATIONS[PYTHON_VERSION].tox_env} -v"
                                            )
                                        } else {
                                            bat(
                                                label: "Checking Python version",
                                                script: "python --version"
                                            )
                                            bat(
                                                label: "Connecting to DevPi index",
                                                script: "devpi use https://devpi.library.illinois.edu --clientdir certs\\ && devpi login %DEVPI_USR% --password %DEVPI_PSW% --clientdir certs\\ && devpi use ${env.BRANCH_NAME}_staging --clientdir certs\\"
                                            )
                                            bat(
                                                label: "Running tests on Devpi",
                                                script: "devpi test --index ${env.BRANCH_NAME}_staging ${props.Name}==${props.Version} -s ${CONFIGURATIONS[PYTHON_VERSION].devpiSelector[FORMAT]} --clientdir certs\\ -e ${CONFIGURATIONS[PYTHON_VERSION].tox_env} -v"
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
                            branch "master"
                        }
                        beforeAgent true
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
                            try{
                                timeout(30) {
                                    input "Release ${props.Name} ${props.Version} (https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging/${props.Name}/${props.Version}) to DevPi Production? "
                                }
                                sh "devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi  && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi && devpi use /DS_Jenkins/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi && devpi push --index ${env.DEVPI_USR}/${env.BRANCH_NAME}_staging ${props.Name}==${props.Version} production/release --clientdir ${WORKSPACE}/devpi"
                            } catch(err){
                                echo "User response timed out. Packages not deployed to DevPi Production."
                            }
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                        checkout scm
                        script{
                            docker.build("py3exiv2bind:devpi.${env.BUILD_ID}",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
                                sh(
                                    label: "Connecting to DevPi Server",
                                    script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                                )
                                sh "devpi use /DS_Jenkins/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi"
                                sh "devpi push ${props.Name}==${props.Version} DS_Jenkins/${env.BRANCH_NAME} --clientdir ${WORKSPACE}/devpi"
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker') {
                       script{
                            docker.build("py3exiv2bind:devpi.${env.BUILD_ID}",'-f ./ci/docker/deploy/devpi/deploy/Dockerfile --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .').inside{
                                unstash "DIST-INFO"
                                def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
                                sh(
                                    label: "Connecting to DevPi Server",
                                    script: 'devpi use https://devpi.library.illinois.edu --clientdir ${WORKSPACE}/devpi && devpi login $DEVPI_USR --password $DEVPI_PSW --clientdir ${WORKSPACE}/devpi'
                                )
                                sh "devpi use /DS_Jenkins/${env.BRANCH_NAME}_staging --clientdir ${WORKSPACE}/devpi"
                                sh "devpi remove -y ${props.Name}==${props.Version} --clientdir ${WORKSPACE}/devpi"
                            }
                       }
                    }
                }
            }
        }
        stage("Deploy"){
            parallel {
                stage("Deploy Online Documentation") {
                    agent {
                        label "Windows && VS2015 && Python3 && longfilenames"
                    }
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                        beforeAgent true
                    }
                    environment{
                        PKG_NAME = get_package_name("DIST-INFO", "py3exiv2bind.dist-info/METADATA")
                    }
                    steps{
                        unstash "DOCS_ARCHIVE"
                        deploy_docs(env.PKG_NAME, "build/docs/html")
                    }
                }
            }
        }
    }
}
