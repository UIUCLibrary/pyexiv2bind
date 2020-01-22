#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _

def CONFIGURATIONS = [
    "3.6": [
            pkgRegex: "*cp36*.whl",
            python_install_url:"https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe",
            test_docker_image: "python:3.6-windowsservercore"
        ],
    "3.7": [
            pkgRegex: "*cp37*.whl",
            python_install_url:"https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe",
            test_docker_image: "python:3.7"
        ]
]

def test_wheel(pkgRegex, python_version){
    script{

        bat "python -m venv venv\\${NODE_NAME}\\${python_version} && venv\\${NODE_NAME}\\${python_version}\\Scripts\\python.exe -m pip install pip --upgrade && venv\\${NODE_NAME}\\${python_version}\\Scripts\\pip.exe install tox --upgrade"

        def python_wheel = findFiles glob: "**/${pkgRegex}"
        python_wheel.each{
            echo "Testing ${it}"
            bat "${WORKSPACE}\\venv\\${NODE_NAME}\\${python_version}\\Scripts\\tox.exe --installpkg=${WORKSPACE}\\${it} -e py${python_version}"
        }
    }
}

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


def rebuild_workspace(sourceDir){
    script{
        deleteDir()
        dir("${sourceDir}"){
            checkout scm
            bat "dir"
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

def remove_from_devpi(devpiExecutable, pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
            try {
                bat "${devpiExecutable} login ${devpiUsername} --password ${devpiPassword}"
                bat "${devpiExecutable} use ${devpiIndex}"
                bat "${devpiExecutable} remove -y ${pkgName}==${pkgVersion}"
            } catch (Exception ex) {
                echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
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

def runTox(tox_exec){
    script{
        try{
            bat "where python"
            bat "if not exist ${WORKSPACE}\\logs mkdir ${WORKSPACE}\\logs"
            bat  (
                label: "Run Tox",
                script: "${tox_exec} --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox -vv --result-json=${WORKSPACE}\\logs\\tox_report.json"
            )

        } catch (exc) {
            bat (
                label: "Run Tox with new environments",
                script: "${tox_exec} --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox --recreate -vv --result-json=${WORKSPACE}\\logs\\tox_report.json"
            )
        }
    }
}

pipeline {
    agent none
    //agent {
    //    label "Windows && VS2015 && Python3 && longfilenames"
    //}
    
    triggers {
       parameterizedCron '@daily % DEPLOY_DEVPI=true; TEST_RUN_TOX=true'
    }

    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(120)  // Timeout after 120 minutes. This shouldn't take this long but it hangs for some reason
        buildDiscarder logRotator(artifactDaysToKeepStr: '10', artifactNumToKeepStr: '10', daysToKeepStr: '', numToKeepStr: '')
    }
    environment {

        DEVPI = credentials("DS_devpi")
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
        //WORKON_HOME ="${WORKSPACE}\\pipenv\\"
        PIPENV_NOSPIN="DISABLED"
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: false, description: "Run Tox Tests")
        
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        // choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")
    }
    stages {
        stage("Configure") {
            parallel{
                stage("Setting up Workspace"){
                    agent {
                        label "Windows && VS2015 && Python3 && longfilenames"
                    }
                    environment{
                        PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                    }
                    stages{
                        //stage("Purge all Existing Data in Workspace"){
                        //    when{
                        //        anyOf{
                        //            equals expected: true, actual: params.FRESH_WORKSPACE
                        //            triggeredBy "TimerTriggerCause"
                        //        }
                        //    }
                        //    steps{
                        //        rebuild_workspace("source")
                        //    }
                        //}
                        stage("Getting Distribution Info"){
                            environment{
                                PATH = "${tool 'CPython-3.7'};${tool 'cmake3.13'};$PATH"
                            }
                            steps{
                                bat "python setup.py dist_info"
                            }
                            post{
                                success{
                                    stash includes: "py3exiv2bind.dist-info/**", name: 'DIST-INFO'
                                    archiveArtifacts artifacts: "py3exiv2bind.dist-info/**"
                                }
                            }
                        }
                        //stage("Installing Required System Level Dependencies"){
                        //    steps{
                        //        lock("system_python_${NODE_NAME}"){
                        //            bat "python -m pip install --upgrade pip --quiet"
                        //        }
                        //    }
                        //    post{
                        //        always{
                        //            lock("system_python_${NODE_NAME}"){
                        //                bat "(if not exist logs mkdir logs) && python -m pip list > logs\\pippackages_system_${NODE_NAME}.log"
                        //            }
                        //            archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                        //        }
                        //    }
                        //}
//                         stage("Installing Pipfile"){
//                             options{
//                                 timeout(5)
//                                 retry 2
//                             }
//                             steps {
//
//                                 bat "(if not exist logs mkdir logs) && python -m pipenv install --dev --deploy && python -m pipenv run pip list > logs\\pippackages_pipenv_${NODE_NAME}.log && python -m pipenv check"
//                             }
//                             post{
//                                 always{
//                                     archiveArtifacts artifacts: "logs/pippackages_pipenv_*.log"
//                                 }
//                                 cleanup{
//                                     cleanWs(patterns: [[pattern: "logs/pippackages_pipenv_*.log", type: 'INCLUDE']])
//                                 }
//                             }
//                         }
//                         stage("Creating Virtualenv for Building"){
//                             steps{
//                                 bat "python -m venv venv\\venv36"
//                                 script {
//                                     try {
//                                         bat "call venv\\venv36\\Scripts\\python.exe -m pip install -U pip"
//                                     }
//                                     catch (exc) {
//                                         bat "python -m venv venv36 && venv\\venv36\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
//                                     }
//                                 }
//                                 bat "venv\\venv36\\Scripts\\pip.exe install -r requirements.txt -r requirements-dev.txt --upgrade-strategy only-if-needed && venv\\venv36\\scripts\\pip.exe install \"tox>=3.8.2,<3.10\""
//                             }
//                             post{
//                                 success{
//                                     bat "venv\\venv36\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
//                                     archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
//                                     cleanWs patterns: [[pattern: "logs/pippackages_venv_*.log", type: 'INCLUDE']]
//                                 }
//
//                             }
//                         }
                    }
                }
            }
            post{
                failure {
                    bat returnStatus: true, script: "python -m pipenv --rm"

                    deleteDir()
                }

            }

        }
        stage("Building") {
            agent {
                dockerfile {
                    filename 'ci/docker/windows/build/msvc/Dockerfile'
                    label 'windows && Docker'
                    additionalBuildArgs "${(env.CHOCOLATEY_SOURCE != null) ? "--build-arg CHOCOLATEY_SOURCE=${env.CHOCOLATEY_SOURCE}": ''}"
                }
            }
            //    label "Windows && VS2015 && Python3 && longfilenames"
            //}
            //environment{
            //    PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
            //}
            stages{
                stage("Building Python Package"){
                    options{
                        timeout(10)
                    }
                    //environment {
                    //    PATH = "${tool 'CPython-3.6'};${tool 'cmake3.13'};$PATH"
                    //    CL = "/MP"
                    //}
                    steps {
                        bat "if not exist logs mkdir logs"
                        bat "python setup.py build -b build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/36/lib/ --build-temp build/36/temp build_ext --inplace"
                        //powershell(
                        //    script: "& python -m pipenv run python setup.py build -b build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/36/lib/ --build-temp build/36/temp build_ext --inplace | tee ${WORKSPACE}\\logs\\build.log"
                        //)
                    }
                    post{
                        //always{
                        //    recordIssues(tools: [
                        //            pyLint(name: 'Setuptools Build: PyLint', pattern: 'logs/build.log'),
                        //            msBuild(name: 'Setuptools Build: MSBuild', pattern: 'logs/build.log')
                        //        ]
                        //        )
                        //}
                        //cleanup{
                        //    cleanWs(patterns: [[pattern: 'logs/build.log', type: 'INCLUDE']])
                        //}
                        success{
                          stash includes: 'py3exiv2bind/**/*.dll,py3exiv2bind/**/*.pyd,py3exiv2bind/**/*.exe"', name: "built_source"
                        }
                    }
                    
                }     
                stage("Building Sphinx Documentation"){
                    environment{
                        PKG_NAME = get_package_name("DIST-INFO", "py3exiv2bind.dist-info/METADATA")
                        PKG_VERSION = get_package_version("DIST-INFO", "py3exiv2bind.dist-info/METADATA")
                    }
                    steps {
                        bat "if not exist logs mkdir logs"
                        bat "if not exist build\\docs\\html mkdir build\\docs\\html"
                        bat "python -m sphinx docs/source build/docs/html -b html -d build\\docs\\.doctrees --no-color -w logs\\build_sphinx.log"
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            script{
                                def DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
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
//                 PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
            }
            agent {
                dockerfile {
                    filename 'ci/docker/windows/build/msvc/Dockerfile'
                    label 'windows && Docker'
                    additionalBuildArgs "${(env.CHOCOLATEY_SOURCE != null) ? "--build-arg CHOCOLATEY_SOURCE=${env.CHOCOLATEY_SOURCE}": ''}"
                }
            }
//             agent {
//                 label "Windows && VS2015 && Python3 && longfilenames"
//             }
            stages{
                stage("Setting up Test Env"){
                    steps{
                        unstash "built_source"
                        bat "if not exist logs mkdir logs"
//                         bat "python -m venv venv\\venv36 && venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install --upgrade setuptools && venv\\venv36\\Scripts\\pip.exe install -r requirements-dev.txt"
                    }
                }

                stage("Running Tests"){

//                     failFast true
                    parallel {
                        stage("Run Tox test") {
//                             agent{
//                                 node {
//         //                        Runs in own node because tox tests delete the coverage data produced
//                                     label "Windows && VS2015 && Python3 && longfilenames"
//                                 }
//                             }
                            when {
                               equals expected: true, actual: params.TEST_RUN_TOX
                            }


                            stages{
//                                 stage("Purge all Existing Data in Node"){
//                                     when{
//                                         anyOf{
//                                             equals expected: true, actual: params.FRESH_WORKSPACE
//                                             triggeredBy "TimerTriggerCause"
//                                         }
//                                     }
//                                     steps{
//                                         deleteDir()
//                                         checkout scm
//                                     }
//                                 }
//                                 stage("Install Tox"){
// //                                     environment {
// //                                         PATH = "${tool 'CPython-3.6'};$PATH"
// //                                     }
//                                     steps{
//                                         bat 'python -m venv venv\\venv36 && venv\\venv36\\scripts\\python.exe -m pip install pip --upgrade --quiet && venv\\venv36\\scripts\\pip.exe install "tox>=3.8.2,<3.10" --upgrade'
//                                     }
//                                 }
                                stage("Running Tox"){
//                                     environment {
//                                         PATH = "${WORKSPACE}\\venv\\venv36\\scripts;${tool 'cmake3.13'};${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
//                                         CL = "/MP"
//                                     }
                                    options{
                                        timeout(15)
                                    }
                                    steps {
                                        bat "tox -e py -vv"
//                                         runTox("${WORKSPACE}\\venv\\venv36\\Scripts\\tox.exe")

                                    }
                                }
                            }

                            post {
                                always{
                                    archiveArtifacts allowEmptyArchive: true, artifacts: '.tox/py*/log/*.log,.tox/log/*.log,logs/tox_report.json'
                                }
//                                 failure {
//                                     dir("${WORKSPACE}\\.tox"){
//                                         deleteDir()
//                                     }
//                                 }
//                                 cleanup{
//                                     cleanWs(
//                                         deleteDirs: true,
//                                         disableDeferredWipeout: true,
//                                         patterns: [
//                                             [pattern: 'dist', type: 'INCLUDE'],
//                                             [pattern: 'build', type: 'INCLUDE'],
//                                             [pattern: 'reports', type: 'INCLUDE'],
//                                             [pattern: '*tmp', type: 'INCLUDE'],
//                                             ]
//                                     )
//                                 }
                            }
                        }
                        stage("Run Doctest Tests"){
//                             environment{
//                                 PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;${PATH}"
//                             }
                            steps {
                                bat "sphinx-build docs/source reports\\doctest -b doctest -d build\\docs\\.doctrees --no-color -w logs\\doctest_warnings.log"
                            }
                            post{
                                always {
                                    archiveArtifacts artifacts: "reports/doctest/output.txt", allowEmptyArchive: true
                                    recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest_warnings.log', id: 'doctest')])

                                }
                            }
                        }
                        stage("MyPy Static Analysis") {
//                             environment {
//                                 PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;$PATH"
//                             }
                            stages{
                                stage("Generate stubs") {
                                    steps{
                                      bat "stubgen -p py3exiv2bind -o ${WORKSPACE}\\mypy_stubs"
                                    }

                                }
                                stage("Run MyPy") {
                                    environment{
                                        MYPYPATH = "${WORKSPACE}\\mypy_stubs"
                                    }
                                    steps{
                                        bat "if not exist reports\\mypy\\html mkdir reports\\mypy\\html"
                                        bat returnStatus: true, script: "mypy -p py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log"
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
//                           environment {
//                             PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;$PATH"
//                           }
                          steps{
//                             bat "(if not exist logs mkdir logs) && pip install flake8"
                            bat returnStatus: true, script: "flake8 py3exiv2bind --tee --output-file ${WORKSPACE}/logs/flake8.log"
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
                                bat "coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=${WORKSPACE}/reports/pytest/${env.junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
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
                    bat "python -m pipenv run coverage combine && python -m pipenv run coverage xml -o ${WORKSPACE}\\reports\\coverage.xml && python -m pipenv run coverage html -d ${WORKSPACE}\\reports\\coverage"
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                    publishCoverage adapters: [
                                    coberturaAdapter('reports/coverage.xml')
                                    ],
                                sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
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
        stage('Creating Binary Packages') {
            matrix{
                agent none
                axes{
                    axis {
                        name "PYTHON_VERSION"
                        values(
                            "3.6",
                            "3.7"
                        )
                    }
                }
                stages{
                    stage("Creating bdist wheel"){
                        agent{
                            dockerfile {
                                filename 'ci/docker/windows/build/msvc/Dockerfile'
                                label 'windows && Docker'
                                additionalBuildArgs "--build-arg PYTHON_INSTALLER_URL=${CONFIGURATIONS[PYTHON_VERSION].python_install_url} ${(env.CHOCOLATEY_SOURCE != null) ? "--build-arg CHOCOLATEY_SOURCE=${env.CHOCOLATEY_SOURCE}": ''}"
                            }
                        }

                        steps{
                            bat "python setup.py build -b build/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/lib --build-temp build/temp bdist_wheel -d ${WORKSPACE}\\dist"
                        }
                        post{
                            success{
                                stash includes: 'dist/*.whl', name: "whl ${PYTHON_VERSION}"
                                archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
                            }
                        }
                    }
                    stage("Testing wheel"){
                        agent{
                            dockerfile {
                                filename 'ci/docker/windows/build/test/msvc/Dockerfile'
                                label 'windows && docker'
                                additionalBuildArgs "--build-arg PYTHON_DOCKER_IMAGE_BASE=${CONFIGURATIONS[PYTHON_VERSION].test_docker_image}"
                            }
                        }

                    steps{
                        unstash "whl ${PYTHON_VERSION}"
                        bat "python --version"

                            script{
                                findFiles(glob: "**/${CONFIGURATIONS[PYTHON_VERSION].pkgRegex}").each{
                                    bat(
                                        script: "tox --installpkg=${WORKSPACE}\\${it} -e py",
                                        label: "Testing ${it}"
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
        //stage("Packaging") {
        //    parallel{
        //        stage("Python 3.6 whl"){
        //            agent {
        //                label "Windows && VS2015 && Python3 && longfilenames"
        //            }
        //            environment {
        //                CMAKE_PATH = "${tool 'cmake3.13'}"
        //                //PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};${env.CMAKE_PATH};$PATH"
        //                CL = "/MP"
        //            }
        //            stages{
        //                stage("Create venv for 3.6"){
        //                    environment {
        //                        PATH = "${tool 'CPython-3.6'};$PATH"
        //                    }
        //                    steps {
        //                        bat "python -m venv venv\\venv36 && venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install wheel setuptools --upgrade"
        //                    }
        //                }
        //                stage("Creating bdist Wheel for 3.6"){
        //                    environment {
        //                        PATH = "${WORKSPACE}\\venv\\venv36\\scripts;${tool 'CPython-3.6'};${env.CMAKE_PATH};$PATH"
        //                    }
        //                    steps {
        //                        bat "python setup.py build -b build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/36/lib --build-temp build/36/temp build_ext --cmake-exec=${env.CMAKE_PATH}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
        //                    }
        //                    post{
        //                       success{
        //                            stash includes: 'dist/*.whl', name: "whl 3.6"
        //                        }
        //                    }
        //                }
        //                stage("Testing 3.6 Wheel"){
        //                    agent { label 'Windows && Python3' }
        //                    environment {
        //                        PATH = "${tool 'CPython-3.6'};$PATH"
        //                    }
        //                    steps{
        //                        unstash "whl 3.6"
        //                        test_wheel("*cp36*.whl", "36")
        //                    }
        //                    post{
        //                        cleanup{
        //                            deleteDir()
        //                        }
        //                    }
        //                }
        //            }
        //        }
               stage("Python sdist"){
                    agent{
                        dockerfile {
                            filename 'ci/docker/windows/build/msvc/Dockerfile'
                            label 'windows && Docker'
                            additionalBuildArgs "--build-arg PYTHON_INSTALLER_URL=${CONFIGURATIONS[PYTHON_VERSION].python_install_url} ${(env.CHOCOLATEY_SOURCE != null) ? "--build-arg CHOCOLATEY_SOURCE=${env.CHOCOLATEY_SOURCE}": ''}"
                        }
                    }
//                    agent {
//                        label "Windows && VS2015 && Python3 && longfilenames"
//                    }
//                    environment {
//                        CMAKE_PATH = "${tool 'cmake3.13'}"
//                        PATH = "${tool 'CPython-3.7'};${env.CMAKE_PATH};$PATH"
//                    }
                   steps {
                       bat "python setup.py sdist -d ${WORKSPACE}\\dist --format zip"
                   }
                   post{
                       success{
                           stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                           archiveArtifacts artifacts: "dist/*.tar.gz,dist/*.zip", fingerprint: true
                       }
                   }
               }
        //        stage("Python 3.7 whl"){
        //            agent {
        //                node {
        //                    label "Windows && Python3 && VS2015"
        //                }
        //            }
        //            options{
        //                retry 2
        //                timeout(10)
        //            }
        //            environment {
        //                CMAKE_PATH = "${tool 'cmake3.13'}"
        //                //PATH = "${env.CMAKE_PATH};${tool 'CPython-3.7'};$PATH"
        //                CL = "/MP"
        //            }
        //            stages{
        //                stage("Create venv for 3.7"){
        //                    environment {
        //                        PATH = "${tool 'CPython-3.7'};${env.CMAKE_PATH};$PATH"
        //                    }
        //                    steps {
        //                        bat "python -m venv venv\\venv37 && venv\\venv37\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv37\\Scripts\\pip.exe install wheel setuptools --upgrade"
        //                    }
        //                }
        //                stage("Creating bdist Wheel for 3.7"){
        //                    environment {
        //                        PATH = "${WORKSPACE}\\venv\\venv37\\scripts;${tool 'CPython-3.7'};${env.CMAKE_PATH};$PATH"
        //                    }
        //                    steps {
        //                        bat "python setup.py build -b build/37/ -j${env.NUMBER_OF_PROCESSORS} --build-lib build/37/lib/ --build-temp build/37/temp build_ext --cmake-exec=${env.CMAKE_PATH}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
        //                    }
        //                    post{
        //                        success{
        //                            stash includes: 'dist/*.whl', name: "whl 3.7"
        //                            archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
        //                        }
        //                        cleanup{
        //                            cleanWs(
        //                                deleteDirs: true,
        //                                patterns: [
        //                                    [pattern: 'dist', type: 'INCLUDE'],
        //                                    [pattern: '*tmp', type: 'INCLUDE'],
        //                                    [pattern: '.eggs/', type: 'INCLUDE'],
        //                                    [pattern: 'build/', type: 'INCLUDE'],
        //                                    [pattern: 'venv/venv37.', type: 'INCLUDE'],
        //                                    [pattern: '*.egg-info/', type: 'INCLUDE'],
        //                                    ]
        //                                )
        //                        }
        //                    }
        //                }
        //                stage("Testing 3.7 Wheel"){
        //                    agent { label 'Windows && Python3' }
        //                    environment {
        //                        PATH = "${tool 'CPython-3.7'};$PATH"
        //                    }
        //                    steps{
        //                        unstash "whl 3.7"
        //                        test_wheel("*cp37*.whl", "37")
        //                    }
        //                    post{
        //                        cleanup{
        //                            deleteDir()
        //                        }
        //                        success{
        //                            archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
        //                        }
        //                    }
        //                }
        //            }
        //        }
        //    }
        //}
        stage("Deploy to DevPi") {
            agent {
                label "Windows && VS2015 && Python3 && longfilenames"
            }
            when {
                allOf{
                    anyOf{
                        equals expected: true, actual: params.DEPLOY_DEVPI
                        triggeredBy "TimerTriggerCause"
                    }
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }

            environment{
                PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;$PATH"
                PKG_NAME = get_package_name("DIST-INFO", "py3exiv2bind.dist-info/METADATA")
                PKG_VERSION = get_package_version("DIST-INFO", "py3exiv2bind.dist-info/METADATA")
            }
            stages{
                stage("Upload to DevPi Staging"){
                    steps {
                        unstash "DOCS_ARCHIVE"
                        unstash "whl 3.6"
                        unstash "whl 3.7"
                        unstash "sdist"
                        bat "pip install devpi-client && devpi use https://devpi.library.illinois.edu && devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && devpi upload --from-dir dist"
                    }
                }
                stage("Test DevPi Packages") {
                    options{
                        timestamps()
                    }
                    parallel {
                        stage("Testing DevPi .zip Package with Python 3.6 and 3.7"){
                            environment {
                                PATH = "${tool 'CPython-3.7'};${tool 'CPython-3.6'};$PATH"
                            }
                            agent {
                                node {
                                    label "Windows && Python3 && VS2015"
                                }
                            }
                            options {
                                skipDefaultCheckout(true)

                            }
                            stages{
                                stage("Creating venv to Test Sdist"){
                                        steps {
                                            bat "python -m venv venv\\venv36 && venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install setuptools --upgrade && venv\\venv36\\Scripts\\pip.exe install \"tox<3.7\" detox devpi-client"
                                        }

                                }
                                stage("Testing DevPi Zip Package"){

                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;${tool 'cmake3.13'};${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                                    }
                                    steps {
                                        timeout(20){
                                            devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "zip",
                                                detox: false
                                            )
                                        }
                                    }
                                }
                            }
                            post {
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                                failure{
                                    deleteDir()
                                }
                            }

                        }

                        stage("Testing DevPi .whl Package with Python 3.6"){
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }

                            options {
                                skipDefaultCheckout(true)
                            }
                            stages{
                                stage("Creating venv to Test py36 .whl"){
                                    environment {
                                        PATH = "${tool 'CPython-3.6'};$PATH"
                                    }
                                    steps {
                                        bat "(if not exist venv\\36 mkdir venv\\36) && python -m venv venv\\36 && venv\\36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\36\\Scripts\\pip.exe install setuptools --upgrade && venv\\36\\Scripts\\pip.exe install \"tox<3.7\" devpi-client"
                                    }

                                }
                                stage("Testing DevPi .whl Package with Python 3.6"){
                                    options{
                                        timeout(20)
                                    }
                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\36\\Scripts;$PATH"
                                    }

                                    steps {

                                        devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "36.*whl",
                                                detox: false,
                                                toxEnvironment: "py36"
                                            )

                                    }
                                }
                            }
                            post {
                                failure {
                                    deleteDir()
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
                                }
                            }
                        }
                        stage("Testing DevPi .whl Package with Python 3.7"){
                            agent {
                                node {
                                    label "Windows && Python3"
                                }
                            }

                            options {
                                skipDefaultCheckout(true)
                            }
                            stages{
                                stage("Creating venv to Test py37 .whl"){
                                    environment {
                                        PATH = "${tool 'CPython-3.7'};$PATH"
                                    }
                                    steps {
                                        lock("system_python_${NODE_NAME}"){
                                            bat "python -m venv venv\\37"
                                        }
                                        bat "venv\\37\\Scripts\\python.exe -m pip install pip --upgrade && venv\\37\\Scripts\\pip.exe install setuptools --upgrade && venv\\37\\Scripts\\pip.exe install \"tox<3.7\" devpi-client"
                                    }

                                }
                                stage("Testing DevPi .whl Package with Python 3.7"){
                                    options{
                                        timeout(20)
                                    }
                                    environment {
                                        PATH = "${WORKSPACE}\\venv\\37\\Scripts;$PATH"
                                    }

                                    steps {

                                        devpiTest(
                                                devpiExecutable: "${powershell(script: '(Get-Command devpi).path', returnStdout: true).trim()}",
                                                url: "https://devpi.library.illinois.edu",
                                                index: "${env.BRANCH_NAME}_staging",
                                                pkgName: "${env.PKG_NAME}",
                                                pkgVersion: "${env.PKG_VERSION}",
                                                pkgRegex: "37.*whl",
                                                detox: false,
                                                toxEnvironment: "py37"
                                            )

                                    }
                                }
                            }
                            post {
                                failure {
                                    deleteDir()
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'certs', type: 'INCLUDE']
                                            ]
                                    )
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
                        }
                        steps {
                            deploy_devpi_production("venv\\venv36\\Scripts\\devpi.exe", env.PKG_NAME, env.PKG_VERSION, env.BRANCH_NAME, env.DEVPI_USR, env.DEVPI_PSW)
                        }
                }
            }
            post {
                success {
                    bat "venv\\venv36\\Scripts\\devpi.exe login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && venv\\venv36\\Scripts\\devpi.exe use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && venv\\venv36\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} ${env.DEVPI_USR}/${env.BRANCH_NAME}"

                }
                cleanup{
                    remove_from_devpi("venv\\venv36\\Scripts\\devpi.exe", "${env.PKG_NAME}", "${env.PKG_VERSION}", "/${env.DEVPI_USR}/${env.BRANCH_NAME}_staging", "${env.DEVPI_USR}", "${env.DEVPI_PSW}")
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
    //post {
    //    cleanup {
    //        cleanWs(
    //            deleteDirs: true,
    //            patterns: [
    //                [pattern: 'dist/', type: 'INCLUDE'],
    //                [pattern: 'build/', type: 'INCLUDE'],
    //                [pattern: 'reports', type: 'INCLUDE'],
    //                [pattern: 'logs', type: 'INCLUDE'],
    //                [pattern: 'certs', type: 'INCLUDE'],
    //                [pattern: '*.dist-info/', type: 'INCLUDE'],
    //                [pattern: '*.egg-info/', type: 'INCLUDE'],
    //                [pattern: 'venv/', type: 'INCLUDE'],
    //                [pattern: '*tmp', type: 'INCLUDE'],
//  //                  [pattern: "source/**/*.dll", type: 'INCLUDE'],
//  //                  [pattern: "source/**/*.pyd", type: 'INCLUDE'],
//  //                  [pattern: "source/**/*.exe", type: 'INCLUDE'],
//  //                  [pattern: "source/**/*.exe", type: 'INCLUDE']
    //                ]
    //            )
    //    }
    //}
}
