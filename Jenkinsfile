#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _


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
        buildDiscarder logRotator(artifactDaysToKeepStr: '10', artifactNumToKeepStr: '10', daysToKeepStr: '', numToKeepStr: '')
    }
    environment {
        PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
        PKG_NAME = pythonPackageName(toolName: "CPython-3.6")
        PKG_VERSION = pythonPackageVersion(toolName: "CPython-3.6")
        DOC_ZIP_FILENAME = "${env.PKG_NAME}-${env.PKG_VERSION}.doc.zip"
        DEVPI = credentials("DS_devpi")
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
        PIPENV_CACHE_DIR="${WORKSPACE}\\..\\.virtualenvs\\cache\\"
        WORKON_HOME ="${WORKSPACE}\\pipenv\\"
        PIPENV_NOSPIN="DISABLED"
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
        booleanParam(name: "TEST_UNIT_TESTS", defaultValue: true, description: "Run automated unit tests")
        booleanParam(name: "TEST_RUN_DOCTEST", defaultValue: true, description: "Test documentation")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 static analysis")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy static analysis")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        
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
                    stages{
                        stage("Purge all existing data in workspace"){
                            when{
                                anyOf{
                                    equals expected: true, actual: params.FRESH_WORKSPACE
                                    triggeredBy "TimerTriggerCause"
                                }
                            }
                            steps{
                                deleteDir()
                                dir("source"){
                                    checkout scm
                                }
                            }
                        }
                        stage("Installing required system level dependencies"){
                            steps{
                                lock("system_python_${NODE_NAME}"){
                                    bat "python -m pip install --upgrade pip --quiet"
                                }
                            }
                            post{
                                always{
                                    lock("system_python_${NODE_NAME}"){
                                        bat "(if not exist logs mkdir logs) && python -m pip list > logs\\pippackages_system_${NODE_NAME}.log"
                                    }
                                    archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                                }
                            }
                        }
                        stage("Installing Pipfile"){
                            options{
                                timeout(5)
                            }
                            steps {
                                dir("source"){
                                    bat "python -m pipenv install --dev --deploy && python -m pipenv run pip list > ..\\logs\\pippackages_pipenv_${NODE_NAME}.log && python -m pipenv check"

                                }
                            }
                            post{
                                always{
                                    archiveArtifacts artifacts: "logs/pippackages_pipenv_*.log"
                                }
                                failure {
                                    dir("source"){
                                        bat returnStatus: true, script: "python -m pipenv --rm"
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
                                bat "python -m venv venv\\venv36"
                                script {
                                    try {
                                        bat "call venv\\venv36\\Scripts\\python.exe -m pip install -U pip"
                                    }
                                    catch (exc) {
                                        bat "python -m venv venv36 && venv\\venv36\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                                    }
                                }
                                bat "venv\\venv36\\Scripts\\pip.exe install -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed && venv\\venv36\\scripts\\pip.exe install \"tox>=3.7\""
                            }
                            post{
                                success{
                                    bat "venv\\venv36\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                                    archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
                                    cleanWs patterns: [[pattern: "logs/pippackages_venv_*.log", type: 'INCLUDE']]
                                }
                                failure {
                                    cleanWs deleteDirs: true, patterns: [[pattern: 'venv\\venv36', type: 'INCLUDE']]
                                }
                            }
                        }
                    }
                }
            }
            post{
                success{
                    echo "Configured ${env.PKG_NAME}, version ${env.PKG_VERSION}, for testing."
                }

            }

        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    options{
                        lock("CMakeBuilding")
                        retry 2
                        timeout(10)
                    }
                    environment {
                        PATH = "${tool 'CPython-3.6'};${tool 'cmake3.13'};$PATH"
                        CL = "/MP"
                    }
                    steps {
                        dir("source"){
                            lock("system_pipenv_${NODE_NAME}"){
                                
                                powershell(
                                    script: "& python -m pipenv run python setup.py build -b ..../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib/ --build-temp ../build/36/temp build_ext --inplace | tee ${WORKSPACE}\\logs\\build.log"
                                )
                            }
                        }
                    }
                    post{
                        always{
                            archiveArtifacts artifacts: "logs/build.log"
                            recordIssues(tools: [
                                    pyLint(name: 'Setuptools Build: PyLint', pattern: 'logs/build.log'),
                                    msBuild(name: 'Setuptools Build: MSBuild', pattern: 'logs/build.log')
                                ]
                                )

                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/build.log', type: 'INCLUDE']])
                        }
                        success{
                          stash includes: 'build/36/lib/**', name: "${NODE_NAME}_build"
                          stash includes: 'source/py3exiv2bind/**/*.dll,source/py3exiv2bind/**/*.pyd,source/py3exiv2bind/**/*.exe"', name: "built_source"
                        }
                        failure{
                            archiveArtifacts allowEmptyArchive: true, artifacts: "**/MSBuild_*.failure.txt"

                        }
                    }
                    
                }     
                stage("Building Sphinx Documentation"){
                    steps {
                        echo "Building docs on ${env.NODE_NAME}"
                        dir("source"){
                            lock("system_pipenv_${NODE_NAME}"){
                                powershell "& python -m pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs | Tee-Object -FilePath ${WORKSPACE}\\logs\\build_sphinx.log"
                            }
                        }
                    }
                    post{
                        always {
                            recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                            archiveArtifacts artifacts: 'logs/build_sphinx.log'
                        }
                        success{
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                            zip archive: true, dir: "${WORKSPACE}/build/docs/html", glob: '', zipFile: "dist/${env.DOC_ZIP_FILENAME}"
                            stash includes: "dist/${env.DOC_ZIP_FILENAME},build/docs/html/**", name: 'DOCS_ARCHIVE'

                        }
                        cleanup{
                            cleanWs(patterns: [
                                    [pattern: 'logs/build_sphinx.log', type: 'INCLUDE'],
                                    [pattern: "dist/${env.DOC_ZIP_FILENAME}", type: 'INCLUDE']
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
            parallel {
                stage("Run Tox test") {
                    agent{
                        node {
//                        Runs in own node because tox tests delete the coverage data produced
                            label "Windows && VS2015 && Python3 && longfilenames"
                        }
                    }
                    when {
                       equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    
                    options{
                        timeout(15)
//                        lock("system_python_${env.NODE_NAME}")
                    }
                    stages{                        
                        stage("Install Tox"){
                            environment {
                                PATH = "${tool 'CPython-3.6'};$PATH"
                            }
                            steps{
                                bat "python -m venv venv\\venv36 && venv\\venv36\\scripts\\python.exe -m pip install pip --upgrade --quiet && venv\\venv36\\scripts\\pip.exe install \"tox>=3.7\""
                            }
                        }
                        stage("run tox"){
                            environment {
                                PATH = "${WORKSPACE}\\venv\\venv36\\scripts;${tool 'cmake3.13'};${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                                CL = "/MP"
                            }
                            steps {
                                dir("source"){
                                    script{
                                        try{
                                            bat "tox --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox -vv"

                                        } catch (exc) {
                                            bat "tox --recreate --parallel=auto --parallel-live  --workdir ${WORKSPACE}\\.tox -vv"
                                        }
                                    }
                                }
                                
                            }        
                        }
                    }
                    
                    post {
                        failure {
                            dir("${WORKSPACE}\\.tox"){
                                deleteDir()
                            }
                        }
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                disableDeferredWipeout: true,
                                patterns: [
                                    [pattern: 'dist', type: 'INCLUDE'],
                                    [pattern: 'reports', type: 'INCLUDE'],
                                    [pattern: "source", type: 'INCLUDE'],
                                    [pattern: '*tmp', type: 'INCLUDE'],
                                    ]
                            )
                        }
                    }
                }
                stage("Run Doctest Tests"){
                    when {
                       equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps {
                        dir("source"){
                            bat "python -m pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs\\html -b doctest > ${WORKSPACE}/logs/doctest.log"
                        }
                        bat "move ${WORKSPACE}\\build\\docs\\html\\doctest\\output.txt ${WORKSPACE}\\reports\\doctest.txt"
                    }
                    post{
                        always {
                            archiveArtifacts artifacts: "reports/doctest.txt"
                            recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest.log', id: 'doctest')])

                        }
                    }
                }
                stage("MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    environment {
                        PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;$PATH"
                    }
                    stages{
                        stage("Generate stubs") {
                            steps{
                                dir("source"){
                                  bat "stubgen py3exiv2bind --recursive -o ${WORKSPACE}\\mypy_stubs"
                                }
                            }

                        }
                        stage("Run MyPy") {
                            environment{
                                MYPYPATH = "${WORKSPACE}\\mypy_stubs"
                            }
                            steps{
                                bat "if not exist reports\\mypy\\html mkdir reports\\mypy\\html"
                                dir("source"){
                                    bat returnStatus: true, script: "mypy -p py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log"
                                }
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
                  when {
                      equals expected: true, actual: params.TEST_RUN_FLAKE8
                  }
                  options{
                    timeout(2)
                    lock("${currentBuild.absoluteUrl}")
                  }
                  environment {
                    PATH = "${WORKSPACE}\\venv\\venv36\\Scripts;$PATH"
                  }
                  steps{
                    bat "(if not exist logs mkdir logs) && pip install flake8"
                    unstash "built_source"
                    dir("source"){
                        bat returnStatus: true, script: "flake8 py3exiv2bind --tee --output-file ${WORKSPACE}/logs/flake8.log"
                    }
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
                  when {
                    equals expected: true, actual: params.TEST_UNIT_TESTS
                  }
                  options{
                    timeout(2)
                    lock("${currentBuild.absoluteUrl}")
                  }
                  steps{
                    dir("source"){
                        bat "python -m pipenv run coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=${WORKSPACE}/reports/pytest/${env.junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
                    }
                  }
                  post{
                    always{
                        junit "reports/pytest/${env.junit_filename}"
                    }
                  }
                }
            }
            post{
                success{
                    dir("source"){
                        bat "python -m pipenv run coverage combine && python -m pipenv run coverage xml -o ${WORKSPACE}\\reports\\coverage.xml && python -m pipenv run coverage html -d ${WORKSPACE}\\reports\\coverage"

                    }
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
                            [pattern: 'source/.coverage', type: 'INCLUDE']
                        ]
                    )

                }
            }

        }
        stage("Packaging") {
            environment {
                CMAKE_PATH = "${tool 'cmake3.13'}"
                PATH = "${env.CMAKE_PATH};$PATH"
                CL = "/MP"
            }
            parallel{
                stage("Python 3.6 whl"){
                    stages{
                        stage("Create venv for 3.6"){
                            environment {
                                PATH = "${tool 'CPython-3.6'};$PATH"
                            }

                            steps {
                                bat "python -m venv venv\\venv36 && venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                        stage("Creating bdist wheel for 3.6"){
                            environment {
                                PATH = "${WORKSPACE}\\venv\\venv36\\scripts;${tool 'CPython-3.6'};$PATH"
                            }
                            steps {
                                dir("source"){
                                    bat "python setup.py build -b ../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib --build-temp ../build/36/temp build_ext --cmake-exec=${env.CMAKE_PATH}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                }
                            }
                            post{
                               success{
                                    stash includes: 'dist/*.whl', name: "whl 3.6"
                                }
                            }
                        }
                    }
                }
                stage("Python sdist"){
                    steps {
                        dir("source"){
                            bat "python setup.py sdist -d ${WORKSPACE}\\dist --format zip"
                        }
                    }
                    post{
                        success{
                            stash includes: 'dist/*.zip,dist/*.tar.gz', name: "sdist"
                        }
                    }
                }
                stage("Python 3.7 whl"){
                    agent {
                        node {
                            label "Windows && Python3 && VS2015"
                        }
                    }
                    environment {
                        CMAKE_PATH = "${tool 'cmake3.13'}"
                        PATH = "${env.CMAKE_PATH};${tool 'CPython-3.7'};$PATH"
                        CL = "/MP"
                    }
                    stages{
                        stage("create venv for 3.7"){
                            steps {
                                bat "python -m venv venv\\venv37 && venv\\venv37\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv37\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                    
                        stage("Creating bdist wheel for 3.7"){
                            environment {
                                PATH = "${WORKSPACE}\\venv\\venv37\\scripts;${tool 'CPython-3.6'};$PATH"
                            }
                            steps {
                                dir("source"){
                                    bat "python setup.py build -b ../build/37/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/37/lib/ --build-temp ../build/37/temp build_ext --cmake-exec=${env.CMAKE_PATH}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                }
                            }
                            post{
                                success{
                                    stash includes: 'dist/*.whl', name: "whl 3.7"
                                }
                                cleanup{
                                    cleanWs(
                                        deleteDirs: true,
                                        disableDeferredWipeout: true,
                                        patterns: [
                                            [pattern: 'dist', type: 'INCLUDE'],
                                            [pattern: 'source', type: 'INCLUDE'],
                                            [pattern: '*tmp', type: 'INCLUDE'],
                                            [pattern: 'venv37', type: 'INCLUDE'],
                                            ]
                                        )
                                }
                            }
                        }
                    }
                }
            }
            post{
                success{
                    unstash "whl 3.7"
                    unstash "whl 3.6"
                    unstash "sdist"
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                }
            }
        }
        stage("Deploy to DevPi") {
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
                stage("Test DevPi packages") {
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
                                stage("Creating venv to test sdist"){
                                        steps {
                                            lock("system_python_${NODE_NAME}"){
                                                bat "python -m venv venv\\venv36"
                                            }
                                            bat "venv\\venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\venv36\\Scripts\\pip.exe install setuptools --upgrade && venv\\venv36\\Scripts\\pip.exe install \"tox<3.7\" detox devpi-client"
                                        }

                                }
                                stage("Testing DevPi zip Package"){

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
                                    label "Windows && Python3 && !Docker"
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
                                        lock("system_python_${NODE_NAME}"){
                                            bat "(if not exist venv\\36 mkdir venv\\36) && python -m venv venv\\36"
                                        }
                                        bat "venv\\36\\Scripts\\python.exe -m pip install pip --upgrade && venv\\36\\Scripts\\pip.exe install setuptools --upgrade && venv\\36\\Scripts\\pip.exe install \"tox<3.7\" devpi-client"
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
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "**/MSBuild_*.failure.txt"
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
                                    label "Windows && Python3 && !Docker"
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
//                                            bat "if not exist venv\\37 mkdir venv\\37"
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
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "**/MSBuild_*.failure.txt"
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
                            script {
                                try{
                                    timeout(30) {
                                        input "Release ${env.PKG_NAME} ${env.PKG_VERSION} (https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging/${env.PKG_NAME}/${env.PKG_VERSION}) to DevPi Production? "
                                    }
                                    bat "venv\\venv36\\Scripts\\devpi.exe login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && venv\\venv36\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging && venv\\venv36\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} production/release"
                                } catch(err){
                                    echo "User response timed out. Packages not deployed to DevPi Production."
                                }
                            }
                        }
                }
            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
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
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                    }
                    steps{
                        unstash "DOCS_ARCHIVE"
                        // script {
                        //     if(!params.BUILD_DOCS){
                        //         bat "python -m pipenv run python setup.py build_sphinx"
                        //     }
                        // }
                        
                        dir("build/docs/html/"){
                            script{
                                try{
                                    timeout(30) {
                                        input "Update project documentation to https://www.library.illinois.edu/dccdocs/${env.PKG_NAME}"
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
                                                remoteDirectory: "${env.PKG_NAME}", 
                                                remoteDirectorySDF: false, 
                                                removePrefix: 'build/docs/html', 
                                                sourceFiles: 'build/docs/html/**')], 
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

            }
        }
    }
    post {
        cleanup {
            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [
                    [pattern: 'dist', type: 'INCLUDE'],
//                    [pattern: 'build', type: 'INCLUDE'],
                    [pattern: 'reports', type: 'INCLUDE'],
                    [pattern: 'logs', type: 'INCLUDE'],
                    [pattern: 'certs', type: 'INCLUDE'],
                    [pattern: '*tmp', type: 'INCLUDE'],
                    [pattern: "source/**/*.dll", type: 'INCLUDE'],
                    [pattern: "source/**/*.pyd", type: 'INCLUDE'],
                    [pattern: "source/**/*.exe", type: 'INCLUDE'],
                    [pattern: "source/**/*.exe", type: 'INCLUDE']
                    ]
                )
        }
    }
}
