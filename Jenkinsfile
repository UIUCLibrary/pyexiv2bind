#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

@Library("devpi") _

def PKG_NAME = "unknown"
def PKG_VERSION = "unknown"
def DOC_ZIP_FILENAME = "doc.zip"
def junit_filename = "junit.xml"
def VENV_ROOT = ""
def VENV_PYTHON = ""
def VENV_PIP = ""
pipeline {
    agent {
        label "Windows && VS2015 && Python3 && longfilenames"
    }
    
    triggers {
        cron('@daily')
    }

    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    environment {
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
        PIPENV_CACHE_DIR="${WORKSPACE}\\..\\.virtualenvs\\cache\\"
        WORKON_HOME ="${WORKSPACE}\\pipenv\\"
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
        booleanParam(name: "TEST_UNIT_TESTS", defaultValue: true, description: "Run automated unit tests")
        booleanParam(name: "TEST_RUN_DOCTEST", defaultValue: true, description: "Test documentation")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 static analysis")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy static analysis")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: "DEPLOY_DEVPI_PRODUCTION", defaultValue: false, description: "Deploy to https://devpi.library.illinois.edu/production/release")
        // choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
        booleanParam(name: "DEPLOY_DOCS", defaultValue: false, description: "Update online documentation")
    }
    stages {
        stage("Configure") {
            stages{
                stage("Purge all existing data in workspace"){
                    when{
                        equals expected: true, actual: params.FRESH_WORKSPACE
                    }
                    steps{
                        deleteDir()
                        dir("source"){
                            checkout scm
                        }
                    }
                }
                stage("Cleanup"){
                    steps {
                        
                        bat "dir"                        
                        dir("logs"){
                            deleteDir()
                            bat "dir > nul"
                        }

                        dir("build"){
                            deleteDir()
                            echo "Cleaned out build directory"
                            bat "dir > nul"
                        }
                        
                        dir("reports"){
                            deleteDir()
                            echo "Cleaned out reports directory"
                            bat "dir > nul"
                        }
                    }
                    post{
                        failure {
                            deleteDir()
                        }
                    }
                }
                stage("Installing required system level dependencies"){
                    steps{
                        lock("system_python_${NODE_NAME}"){
                            bat "${tool 'CPython-3.6'} -m pip install --upgrade pip --quiet"
                        }
                    }
                    post{
                        always{
                            lock("system_python_${NODE_NAME}"){
                                bat "${tool 'CPython-3.6'} -m pip list > logs\\pippackages_system_${NODE_NAME}.log"
                            }
                            archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                        }
                    }
                }
//                 stage("Installing required system level dependencies"){
//                     steps{
//                         lock("system_python_${env.NODE_NAME}"){
//                             bat "${tool 'CPython-3.6'} -m pip install pip --upgrade --quiet"
//                             bat "${tool 'CPython-3.6'} -m pip install scikit-build --quiet"
//                             bat "${tool 'CPython-3.6'} -m pip install --upgrade pipenv --quiet"
//                             tee("logs/pippackages_system_${NODE_NAME}.log") {
//                                 bat "${tool 'CPython-3.6'} -m pip list"
//                             }
//                         }

//                     }
//                     post{
//                         always{
//                             archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
// //                            dir(){
// //                            script{
// //                                def log_files = findFiles glob: 'logs/pippackages_system_*.log'
// //                                log_files.each { log_file ->
// //                                    echo "Found ${log_file}"
// //                                    archiveArtifacts artifacts: "${log_file}"
// //                                    bat "del ${log_file}"
// //                                }
// //                            }
// //                            }
//                         }
//                         failure {
//                             deleteDir()
//                         }
//                     }

//                 }
//                 stage("Installing Pipfile"){
//                     options{
//                         timeout(5)
//                     }
//                     steps {
//                         dir("source"){
//                             bat "${tool 'CPython-3.6'} -m pipenv install --dev --deploy"
                            
//                         }
//                         tee("logs/pippackages_pipenv_${NODE_NAME}.log") {
//                             bat "${tool 'CPython-3.6'} -m pipenv run pip list"
//                         }  
                        
//                     }
//                     post{
//                         always{
//                             archiveArtifacts artifacts: "logs/pippackages_pipenv_${NODE_NAME}.log"
// //                                }
// //                            }
//                         }
//                     }
//                 }
                stage("Installing Pipfile"){
                    options{
                        timeout(5)
                    }
                    steps {
                        dir("source"){
                            bat "pipenv install --dev --deploy && pipenv run pip list > ..\\logs\\pippackages_pipenv_${NODE_NAME}.log"
                            bat "pipenv check"

                        }
                    }
                    post{
                        always{
                            archiveArtifacts artifacts: "logs/pippackages_pipenv_*.log"
                        }
                        failure {
                            dir("source"){
                                bat returnStatus: true, script: "pipenv --rm"
                            }

                            deleteDir()
                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: "logs/pippackages_pipenv_*.log", type: 'INCLUDE']])
                        }
                    }
                }
                stage("Creating virtualenv for building"){
                    steps{
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "${tool 'CPython-3.6'} -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv\\Scripts\\pip.exe install devpi-client -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"
                    }
                    post{
                        success{                            
                            bat "venv\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                            archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"  
                            cleanWs patterns: [[pattern: "logs/pippackages_venv_*.log", type: 'INCLUDE']]                          
                        }
                        failure {
                            cleanWs deleteDirs: true, patterns: [[pattern: 'venv', type: 'INCLUDE']]
                        }
                    }
                }
                // stage("Creating virtualenv for building"){
                //     steps {
                //         bat "${tool 'CPython-3.6'} -m venv venv"
                        
                //         script {
                //             try {
                //                 bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                //             }
                //             catch (exc) {
                //                 bat "${tool 'CPython-3.6'} -m venv venv"
                //                 bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                //             }                           
                //         }
                        
                //         bat "venv\\Scripts\\pip.exe install devpi-client flake8 pytest pytest-cov --upgrade-strategy only-if-needed --quiet"
                        
           
                //         tee("logs/pippackages_venv_${NODE_NAME}.log") {
                //             bat "venv\\Scripts\\pip.exe list"
                //         }
                //     }
                //     post{
                //         always{
                //             script{
                //                 def log_files = findFiles glob: '**/pippackages_venv_*.log'
                //                 log_files.each { log_file ->
                //                     echo "Found ${log_file}"
                //                     archiveArtifacts artifacts: "${log_file}"
                //                     bat "del ${log_file}"
                //                 }
                //             }
                //         }
                //         failure {
                //             deleteDir()
                //         }
                //     }
                // }
                stage("Setting variables used by the rest of the build"){
                    steps{
                        
                        script {
                            // Set up the reports directory variable 
                            dir("source"){
                                PKG_NAME = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                                PKG_VERSION = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                            }
                        }

                        script{
                            DOC_ZIP_FILENAME = "${PKG_NAME}-${PKG_VERSION}.doc.zip"
                            junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                        }


                        
                        
                        script{
                            VENV_ROOT = "${WORKSPACE}\\venv\\"

                            VENV_PYTHON = "${WORKSPACE}\\venv\\Scripts\\python.exe"
                            bat "${VENV_PYTHON} --version"

                            VENV_PIP = "${WORKSPACE}\\venv\\Scripts\\pip.exe"
                            bat "${VENV_PIP} --version"
                        }

                        
                        bat "venv\\Scripts\\devpi use https://devpi.library.illinois.edu"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {    
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "dir"
                    }
                }
            }
            post{
                always{
                    echo """Name                            = ${PKG_NAME}
Version                         = ${PKG_VERSION}
documentation zip file          = ${DOC_ZIP_FILENAME}
Python virtual environment path = ${VENV_ROOT}
VirtualEnv Python executable    = ${VENV_PYTHON}
VirtualEnv Pip executable       = ${VENV_PIP}
junit_filename                  = ${junit_filename}
"""           

                }
                
            }

        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    environment {
                        CL = "/MP"
                    }
                    steps {
                        dir("source"){
                            lock("system_pipenv_${NODE_NAME}"){
                                powershell "& pipenv run python setup.py build -b ..../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib/ --build-temp ../build/36/temp build_ext --inplace --cmake-exec=${tool 'cmake3.12'}\\cmake.exe | Tee-Object -FilePath ${WORKSPACE}\\logs\\build.log"
                            }
                        }
                    }
                    post{
                        always{
                            archiveArtifacts artifacts: "logs/build.log"
                            // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build.log']]
                            recordIssues enabledForFailure: true, tools: [
                                [name: 'Setuptools Build: PyLint', pattern: 'logs/build.log', tool: pyLint()],
                                [name: 'Setuptools Build: MSBuild', pattern: 'logs/build.log', tool: msBuild()]
                                ]
                            // bat "dir build"
                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/build.log', type: 'INCLUDE']])
                        }
                        success{
                          stash includes: 'build/36/lib/**', name: "${NODE_NAME}_build"
                          stash includes: 'source/py3exiv2bind/**/*.dll,source/py3exiv2bind/**/*.pyd,source/py3exiv2bind/**/*.exe"', name: "${NODE_NAME}_built_source"
                        }
                    }
                    
                }     
//                 stage("Building Python Package"){
// //                    environment {
// //                        PATH = "${tool 'cmake3.12'}\\;$PATH"
// //                    }
//                     steps {
//                         tee("logs/setuptools_build_${env.NODE_NAME}.log") {
//                             dir("source"){
//                                 bat script: "pipenv run python setup.py build -b ../build -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/lib --build-temp ../build/temp build_ext --inplace --cmake-exec=${tool 'cmake3.12'}\\cmake.exe"
//                             }
                        
//                         }
//                     }
//                     post{
//                         always{
//                            archiveArtifacts artifacts: "logs/setuptools_build_${env.NODE_NAME}.log"
//                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MSBuild', pattern: "logs/setuptools_build_${env.NODE_NAME}.log"]]
//                         }
//                         success{
//                           stash includes: 'build/lib/**', name: "${NODE_NAME}_build"
//                           stash includes: 'source/py3exiv2bind/**/*.dll,source/py3exiv2bind/**/*.pyd,source/py3exiv2bind/**/*.exe"', name: "${NODE_NAME}_built_source"
//                         }
//                     }
//                 }
//                 stage("Building Sphinx Documentation"){
//                     when {
//                         equals expected: true, actual: params.BUILD_DOCS
//                     }
//                     environment {
//                         PATH = "${tool 'cmake3.12'}\\;$PATH"
//                     }
//                     steps {
//                         dir("build/docs/html"){
//                             deleteDir()
//                             echo "Cleaned out build/docs/html dirctory"

//                         }
// //
//                         echo "Building docs on ${env.NODE_NAME}"
//                         tee("logs/build_sphinx_${env.NODE_NAME}.log") {
//                             dir("source"){
//                                 bat "pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs"
//                             }
//                         }
//                     }
//                     post{
//                         always {
//                             archiveArtifacts artifacts: "logs/build_sphinx_${env.NODE_NAME}.log"
//                         }
//                         success{
//                             publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
//                             zip archive: true, dir: "build/docs/html/", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
//                         }
//                     }
                
//                 }
                stage("Building Sphinx Documentation"){
                    steps {
                        echo "Building docs on ${env.NODE_NAME}"
                        dir("source"){
                            lock("system_pipenv_${NODE_NAME}"){
                                powershell "& ${tool 'CPython-3.6'} -m pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs |  Tee-Object -FilePath ${WORKSPACE}\\logs\\build_sphinx.log"
                            }
                        }
                    }
                    post{
                        always {
                            recordIssues enabledForFailure: true, tools: [[name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', tool: pep8()]]
                            // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build_sphinx.log']]
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "dist/${DOC_ZIP_FILENAME}"
                            stash includes: "dist/${DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'

                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/build_sphinx.log', type: 'INCLUDE']])
                            cleanWs(patterns: [[pattern: "dist/${DOC_ZIP_FILENAME}", type: 'INCLUDE']])
                        }
                    }
                }
            }
        }
        
        stage("Testing") {
            parallel {
                stage("Run Tox test") {
                    agent{
                        node {
                            label "Windows && VS2015 && Python3 && longfilenames"
                            customWorkspace "c:/Jenkins/temp/${JOB_NAME}/tox/"
                        }
                    }
                    when {
                       equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    environment {
                        PATH = "${tool 'cmake3.12'}\\;${tool 'CPython-3.6'}\\..\\;${tool 'CPython-3.7'}\\..\\;$PATH"
                    }
                    options{
                        lock("system_python_${env.NODE_NAME}")
                    }
                    steps {
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        bat "venv\\scripts\\python.exe -m pip install pip --upgrade --quiet"
                        bat "venv\\scripts\\pip.exe install tox detox --upgrade"
                        dir("source"){
                            // bat "${tool 'CPython-3.6'} -m pipenv install --dev --deploy"
                            script{
                                try{
                                    bat "${WORKSPACE}\\venv\\scripts\\detox.exe --workdir ${WORKSPACE}\\.tox -vv -- --junitxml=${WORKSPACE}\\reports\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"

                                } catch (exc) {
                                    bat "${WORKSPACE}\\venv\\scripts\\detox.exe --recreate --workdir ${WORKSPACE}\\.tox -vv -- --junitxml=${WORKSPACE}\\reports\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
                                }
                            }
                        }
                        
                    }
                    post {
                        // success{
                        //     script {
                        //         try{
                        //             publishCoverage adapters: [
                        //                     coberturaAdapter('reports/tox_coverage.xml')
                        //                     ],
                        //                 tag: 'coverage'
                        //                 sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                        //         } catch(exc){
                        //             echo "cobertura With Coverage API failed. Falling back to cobertura plugin"
                        //             cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: "reports/tox_coverage.xml", conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                        //         }
                        //         archiveArtifacts artifacts: "reports/tox_coverage.xml"
                        //         bat "del reports\\tox_coverage.xml"
                        //     }
                        //     dir("reports}"){
                        //         bat "dir"

                        //         script {
                        //             def xml_files = findFiles glob: "**/*.xml"
                        //             xml_files.each { junit_xml_file ->
                        //                 echo "Found ${junit_xml_file}"
                        //                 junit "${junit_xml_file}"
                        //             }
                        //         }
                        //     }              
                        //     publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        // }
                        failure {
                            echo "Tox test failed. Removing ${WORKSPACE}\\.tox"
                            dir("${WORKSPACE}\\.tox"){
                                deleteDir()
                            }
                        }
                    }
                }
                stage("Run Doctest Tests"){
                    when {
                       equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps {
                        dir("source"){
                            bat "pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs\\html -b doctest"
                        }
                        bat "move ${WORKSPACE}\\build\\docs\\html\\doctest\\output.txt ${WORKSPACE}\\reports\\doctest.txt"
                    }
                    post{
                        always {
                            archiveArtifacts artifacts: "reports/doctest.txt"
                        }
                    }
                }
                stage("Run MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    steps{
                        dir("reports/mypy/html"){
                            deleteDir()
                            bat "dir"
                        }
                        script{
                            try{
                                dir("source"){
                                    bat "dir"
                                    bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log"
                                }
                            } catch (exc) {
                                echo "MyPy found some warnings"
                            }
                        }
                    }
                    post {
                        always {
                            recordIssues enabledForFailure: true, tools: [[name: 'MyPy', pattern: "logs/mypy.log", tool: myPy()]]
                            // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                        }
                    }
                }
                // stage("Run MyPy Static Analysis") {
                //     when {
                //         equals expected: true, actual: params.TEST_RUN_MYPY
                //     }
                //     steps{
                //         dir("reports/mypy/html"){
                //             deleteDir()
                //             bat "dir"
                //         }
                //         script{
                //             tee("logs/mypy.log") {
                //                 try{
                //                     dir("source"){
                //                         bat "dir"
                //                         bat "pipenv run mypy ${WORKSPACE}\\build\\lib\\py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html"
                //                     }
                //                 } catch (exc) {
                //                     echo "MyPy found some warnings"
                //                 }
                //             }
                //         }
                //     }
                //     post {
                //         always {
                //             warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                //             publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                //         }
                //     }
                // }
                stage("Flake8") {
                  when {
                      equals expected: true, actual: params.TEST_RUN_FLAKE8
                  }
                  options{
                    timeout(2)
                  }
                  steps{
                    unstash "${NODE_NAME}_built_source"
                    script{
                      try{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\flake8.exe py3exiv2bind --tee --output-file ${WORKSPACE}/logs/flake8.log"
                        }
                      } catch (exc) {
                        echo "Flake8 found some warnings."
                        // currentBuild.result = 'UNSTABLE'
                      }
                    }
                  }
                  post {
                    always {
                        recordIssues enabledForFailure: true, tools: [[name: 'Flake8', pattern: 'logs/flake8.log', tool: flake8()]]
                    //   warnings parserConfigurations: [[parserName: 'PyLint', pattern: 'reports/flake8.txt']], unHealthy: ''
                    }
                  }
                }
                stage("Running Unit Tests"){
                  when {
                    equals expected: true, actual: params.TEST_UNIT_TESTS
                  }
                  steps{
                    // unstash "${NODE_NAME}_built_source"
                    dir("source"){
                        bat "pipenv run coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=${WORKSPACE}/reports/pytest/${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
                    //   bat "${WORKSPACE}\\venv\\Scripts\\python.exe -m pytest --junitxml=${WORKSPACE}\\reports\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/pytest/ --cov-report xml:${WORKSPACE}/reports/coverage.xml"
                    }
                  }
                  post{
                    always{
                        junit "reports/pytest/${junit_filename}"                      
                    }
                  }
                }
            }
            post{
                always{
                    dir("source"){
                        bat "pipenv run coverage combine"
                        bat "pipenv run coverage xml -o ${WORKSPACE}\\reports\\coverage.xml"
                        bat "pipenv run coverage html -d ${WORKSPACE}\\reports\\coverage"

                    }
                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "reports/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                    publishCoverage adapters: [
                                    coberturaAdapter('reports/coverage.xml')
                                    ],
                                sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                }
                cleanup{
                    cleanWs(patterns: [[pattern: 'reports/coverage.xml', type: 'INCLUDE']])
                    cleanWs(patterns: [[pattern: 'reports/coverage', type: 'INCLUDE']])
                    cleanWs(patterns: [[pattern: 'source/.coverage', type: 'INCLUDE']])

                }
            }

        }
        stage("Packaging") {
            environment {
                PATH = "${tool 'cmake3.12'};$PATH"
            }
            parallel{
                stage("Python 3.6 whl"){
                    stages{
                        
                        stage("Create venv for 3.6"){
                            environment {
                                PATH = "${tool 'cmake3.12'}\\;${tool 'CPython-3.6'}\\..\\;$PATH"
                                CL = "/MP"
                            }
                            steps {
                                bat "${tool 'CPython-3.6'} -m venv venv36"
                                bat "venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv36\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                        stage("Creating bdist wheel for 3.6"){
                            steps {
                                dir("source"){
                                    // bat "pipenv run python setup.py build -b ../build -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/lib --build-temp ../build/temp build_ext --cmake-exec=${tool 'cmake3.12'}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                    bat "${WORKSPACE}\\venv36\\scripts\\python.exe setup.py build -b ../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib --build-temp ../build/36/temp build_ext --cmake-exec=${tool 'cmake3.12'}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                }
                            }
                        }
                    }
                }
                stage("Python sdist"){
                    steps {
                        dir("source"){
                            bat "${tool 'CPython-3.6'} setup.py sdist -d ${WORKSPACE}\\dist"
                        }
                    }
                }
                stage("Python 3.7 whl"){
                    agent {
                            node {
                                label "Windows && Python3"
                            }
                        }
                    stages{
                        stage("create venv for 3.7"){
                            environment {
                                PATH = "${tool 'cmake3.12'}\\;${tool 'CPython-3.7'}\\..\\;$PATH"
                                CL = "/MP"
                            }
                            steps {
                                bat "${tool 'CPython-3.7'} -m venv venv37"
                                bat "venv37\\Scripts\\python.exe -m pip install pip --upgrade && venv37\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                    
                        stage("Creating bdist wheel for 3.7"){
                            steps {
                                dir("source"){
                                    bat "${WORKSPACE}\\venv37\\scripts\\python.exe setup.py build -b ../build/37/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/37/lib/ --build-temp ../build/37/temp build_ext --cmake-exec=${tool 'cmake3.12'}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                }
                            }
                            post{
                                success{
                                    stash includes: 'dist/*.whl', name: "whl 3.7"
                                }
                            }
                        }
                    }
                }
            }
            post{
                success{
                    unstash "whl 3.7"
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                }
            }
        }
        stage("Deploy to DevPi Staging") {

            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }
            steps {
                bat "venv\\Scripts\\devpi.exe use https://devpi.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    
                }
                bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
                            bat "venv\\Scripts\\devpi.exe upload --only-docs ${WORKSPACE}\\dist\\${DOC_ZIP_FILENAME}"
                        } catch (exc) {
                            echo "Unable to upload to devpi with docs."
                        }
                    }

            }
        }
        stage("Test DevPi packages") {
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: "master", actual: env.BRANCH_NAME
                        equals expected: "dev", actual: env.BRANCH_NAME
                    }
                }
            }


            parallel {
                stage("Testing Submitted Source Distribution") {
                    environment {
                        PATH = "${tool 'cmake3.12'}\\;${tool 'CPython-3.6'}\\..\\;${tool 'CPython-3.7'}\\..\\;$PATH"
                    }
                    steps {
                        echo "Testing Source tar.gz package in devpi"
                        
                        timeout(10){
                            // bat "venv\\Scripts\\devpi.exe use https://devpi.library.illinois.edu/${env.BRANCH_NAME}_staging"
                            devpiTest(
                                devpiExecutable: "venv\\Scripts\\devpi.exe",
                                url: "https://devpi.library.illinois.edu",
                                index: "${env.BRANCH_NAME}_staging",
                                pkgName: "${PKG_NAME}",
                                pkgVersion: "${PKG_VERSION}",
                                pkgRegex: "tar.gz",
                                detox: false
                            )
                        }
                        
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    
                        // }
                        // bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"

                        // script {                          
                        //     def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME}==${PKG_VERSION} -s tar.gz  --verbose"
                        //     if(devpi_test_return_code != 0){   
                        //         error "Devpi exit code for tar.gz was ${devpi_test_return_code}"
                        //     }
                        // }
                        echo "Finished testing Source Distribution: .tar.gz"
                    }
                    post {
                        failure {
                            echo "Tests for .tar.gz source on DevPi failed."
                        }
                    }

                }
                stage("Built Distribution: py36 .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }
                    }
                    environment {
                        PATH = "${tool 'CPython-3.6'}\\..\\;${tool 'CPython-3.7'}\\..\\;$PATH"
                    }
                    options {
                        skipDefaultCheckout(true)
                    }
                    
                    steps {
                        bat "${tool 'CPython-3.6'} -m venv venv36"
                        bat "venv36\\Scripts\\python.exe -m pip install pip --upgrade"
                        bat "venv36\\Scripts\\pip.exe install devpi --upgrade"
                        echo "Testing Whl package in devpi"
                        devpiTest(
                                devpiExecutable: "venv36\\Scripts\\devpi.exe",
                                url: "https://devpi.library.illinois.edu",
                                index: "${env.BRANCH_NAME}_staging",
                                pkgName: "${PKG_NAME}",
                                pkgVersion: "${PKG_VERSION}",
                                pkgRegex: "36.*whl",
                                detox: false,
                                toxEnvironment: "py36"
                            )
                        // bat "${tool 'CPython-3.6'} -m venv venv"
                        // bat "venv\\Scripts\\pip.exe install tox devpi-client"
                        // bat "where python"
                        // bat "set"
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"                        
                        // }
                        // bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        // script{
                        //     def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME}==${PKG_VERSION} -s \"36.*whl\" -e py36  --verbose"
                        //     if(devpi_test_return_code != 0){   
                        //         error "Devpi exit code for whl was ${devpi_test_return_code}"
                        //     }
                        // }
                        echo "Finished testing Built Distribution: .whl"
                    }
                    post {
                        failure {
                            echo "Tests for whl on DevPi failed."
                        }
                    }
                }
                stage("Built Distribution: py37 .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }}
                    environment {
                        PATH = "${tool 'CPython-3.7'}\\..\\;$PATH"
                    }
                    options {
                        skipDefaultCheckout(true)
                    }
                    
                    steps {
                        echo "Testing Whl package in devpi"
                        bat "${tool 'CPython-3.7'} -m venv venv37"
                        bat "venv37\\Scripts\\python.exe -m pip install pip --upgrade"
                        bat "venv37\\Scripts\\pip.exe install devpi --upgrade"
                        devpiTest(
                                devpiExecutable: "venv37\\Scripts\\devpi.exe",
                                url: "https://devpi.library.illinois.edu",
                                index: "${env.BRANCH_NAME}_staging",
                                pkgName: "${PKG_NAME}",
                                pkgVersion: "${PKG_VERSION}",
                                pkgRegex: "37.*whl",
                                detox: false,
                                toxEnvironment: "py37"
                            )
                        // bat "${tool 'CPython-3.6'} -m venv venv"
                        // bat "venv\\Scripts\\pip.exe install tox devpi-client"
                        // bat "where python"
                        // bat "set"
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"                        
                        // }
                        // bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        // script{
                        //     def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME}==${PKG_VERSION} -s \"36.*whl\" -e py36  --verbose"
                        //     if(devpi_test_return_code != 0){   
                        //         error "Devpi exit code for whl was ${devpi_test_return_code}"
                        //     }
                        // }
                        echo "Finished testing Built Distribution: .whl"
                    }
                    post {
                        failure {
                            echo "Tests for whl on DevPi failed."
                        }
                    }
                }
            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }

                    }
                }
                failure {
                    echo "At least one package format on DevPi failed."
                }
            }
        }
        stage("Deploy"){
            parallel {
                stage("Deploy Online Documentation") {
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                    steps{
                        script {
                            if(!params.BUILD_DOCS){
                                bat "pipenv run python setup.py build_sphinx"
                            }
                        }
                        
                        dir("build/docs/html/"){
                            script{
                                try{
                                    timeout(30) {
                                        input 'Update project documentation?'
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
                                                remoteDirectory: "${params.DEPLOY_DOCS_URL_SUBFOLDER}", 
                                                remoteDirectorySDF: false, 
                                                removePrefix: '', 
                                                sourceFiles: '**')], 
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
                    }
                }
                stage("Deploy to DevPi Production") {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            equals expected: true, actual: params.DEPLOY_DEVPI
                            branch "master"
                        }
                    }
                    steps {
                        script {
                            try{
                                timeout(30) {
                                    input "Release ${PKG_NAME} ${PKG_VERSION} (https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging/${PKG_NAME}/${PKG_VERSION}) to DevPi Production? "
                                }
                                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"         
                                }

                                bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                                bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} production/release"
                            } catch(err){
                                echo "User response timed out. Packages not deployed to DevPi Production."
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        cleanup {
            dir('dist') {
                deleteDir()
            }

            dir('build') {
                deleteDir()
            }
            dir("reports") {
                deleteDir()
            }
            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            if(fileExists('venv\\Scripts\\python.exe')){
                                retry(3) {
                                    bat "venv\\Scripts\\python.exe setup.py clean --all"
                                }
                            }
                        } catch (Exception ex) {
                            echo "Unable to successfully run clean. Purging source directory."
                            deleteDir()
                        }
                        bat "dir"
                    }
                dir("source"){
                    def binary_files = findFiles glob: "**/*.dll,**/*.pyd,**/*.exe"
                    binary_files.each { binary_file ->
                        bat "del ${binary_file}"
                    }
                  }
                }

                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${PKG_NAME}==${PKG_VERSION}"
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
            }
            bat "dir"
        }
    }
    // post {
    //     cleanup{
    //         echo "Cleaning up."
    //         script {
    //             if(fileExists('source/setup.py')){
    //                 dir("source"){
    //                     try{
    //                         bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py clean --all"
    //                     } catch (Exception ex) {
    //                         echo "Unable to succesfully run clean. Purging source directory."
    //                         deleteDir()
    //                     }   
    //                 }
    //             }                
    //             if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
    //                 withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
    //                     bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
    //                     bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
    //                 }

    //                 def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${PKG_NAME}==${PKG_VERSION}"
    //                 echo "Devpi remove exited with code ${devpi_remove_return_code}."
    //             }
    //         }
    //     } 
    // }
}
