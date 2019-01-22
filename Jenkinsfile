#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

@Library(["devpi", "PythonHelpers"]) _


def junit_filename = "junit.xml"
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
                stage("Cleanup"){
                    steps {
                        
                        bat "dir"                        
                        dir("logs"){
                            deleteDir()
                            bat "dir > nul"
                        }

//                        dir("build"){
//                            deleteDir()
//                            echo "Cleaned out build directory"
//                            bat "dir > nul"
//                        }
                        
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
                            bat "python -m pip install --upgrade pip --quiet"
                        }
                    }
                    post{
                        always{
                            lock("system_python_${NODE_NAME}"){
                                bat "python -m pip list > logs\\pippackages_system_${NODE_NAME}.log"
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
                            bat "python -m pipenv install --dev --deploy && python -m pipenv run pip list > ..\\logs\\pippackages_pipenv_${NODE_NAME}.log"
                            bat "python -m pipenv check"

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
//                    TODO: Put venv36 inside subdirectory of venv
                        bat "python -m venv venv36"
                        script {
                            try {
                                bat "call venv36\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "python -m venv venv36"
                                bat "call venv36\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv36\\Scripts\\pip.exe install devpi-client -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"
                    }
                    post{
                        success{                            
                            bat "venv36\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                            archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"  
                            cleanWs patterns: [[pattern: "logs/pippackages_venv_*.log", type: 'INCLUDE']]                          
                        }
                        failure {
                            cleanWs deleteDirs: true, patterns: [[pattern: 'venv36', type: 'INCLUDE']]
                        }
                    }
                }
                stage("Setting variables used by the rest of the build"){
                    steps{
                        script{
                            junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                        }
//                        bat "venv36\\Scripts\\devpi use https://devpi.library.illinois.edu"
//                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
//                            bat "venv36\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
//                        }
//                        bat "dir"
                    }
                }
            }
        }
        stage("Building") {
            stages{
                stage("Building Python Package"){
                    options{
                        lock("CMakeBuilding")
                    }
                    environment {
                        PATH = "${tool 'CPython-3.6'};${tool 'cmake3.13'};$PATH"
                        CL = "/MP"
                    }
                    steps {
                        dir("source"){
                            lock("system_pipenv_${NODE_NAME}"){
                            script{
                                powershell(
                                    script: "& python -m pipenv run python setup.py build -b ..../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib/ --build-temp ../build/36/temp build_ext --inplace | tee ${WORKSPACE}\\logs\\build.log"
//                                        """Invoke-Expression -Command \"${tool 'CPython-3.6'}\\python.exe -m pipenv run python setup.py build -b ..../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib/ --build-temp ../build/36/temp build_ext --inplace\" -OutVariable build_output
//                                        echo \"\$build_output\"

//                                """
//                                \$build_output > ${WORKSPACE}\\logs\\build.log
                                )

                            }
//                                Tee-Object -FilePath ${WORKSPACE}\\logs\\build.log
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
                          stash includes: 'source/py3exiv2bind/**/*.dll,source/py3exiv2bind/**/*.pyd,source/py3exiv2bind/**/*.exe"', name: "${NODE_NAME}_built_source"
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
//                                 bat "${tool 'CPython-3.6'}\\python -m pipenv run python setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs 2> ${WORKSPACE}\\logs\\build_sphinx.log & type ${WORKSPACE}\\logs\\build_sphinx.log"
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
                        PATH = "${tool 'cmake3.13'};${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                        CL = "/MP"
                    }
                    options{
                        lock("system_python_${env.NODE_NAME}")
                    }
                    steps {
                        bat "${tool 'CPython-3.6'}\\python -m venv venv36"
                        bat "venv36\\scripts\\python.exe -m pip install pip --upgrade --quiet"
                        bat "venv36\\scripts\\pip.exe install tox>=3.7"
                        dir("source"){
                            script{
                                try{
                                    bat "${WORKSPACE}\\venv36\\scripts\\tox.exe --parallel=auto --parallel-live --workdir ${WORKSPACE}\\.tox -vv -- --junitxml=${WORKSPACE}\\reports\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"

                                } catch (exc) {
                                    bat "${WORKSPACE}\\venv36\\scripts\\tox.exe --recreate --parallel=auto --parallel-live  --workdir ${WORKSPACE}\\.tox -vv -- --junitxml=${WORKSPACE}\\reports\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
                                }
                            }
                        }
                        
                    }
                    post {
                        failure {
                            echo "Tox test failed. Removing ${WORKSPACE}\\.tox"
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
                stage("Run MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    environment {
                        PATH = "${WORKSPACE}\\venv36\\Scripts;$PATH"
                    }
                    steps{
                        dir("reports/mypy/html"){
                            deleteDir()
                            bat "dir"
                        }

                        script{
                            try{
                                dir("source"){
                                    bat "mypy -p py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html > ${WORKSPACE}\\logs\\mypy.log"
                                }
                            } catch (exc) {
                                echo "MyPy found some warnings"
                            }
                        }
                    }
                    post {
                        always {
                            recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                        }
                    }
                }
                stage("Flake8") {
                  when {
                      equals expected: true, actual: params.TEST_RUN_FLAKE8
                  }
                  options{
                    timeout(2)
                  }
                  environment {
                    PATH = "${WORKSPACE}\\venv36\\Scripts;$PATH"
                  }
                  steps{
                    unstash "${NODE_NAME}_built_source"
                    script{
                      try{
                        dir("source"){
                            bat returnStatus: true, script: "mkdir ${WORKSPACE}\\logs"
                            bat "flake8 py3exiv2bind --tee --output-file ${WORKSPACE}/logs/flake8.log"
                        }
                      } catch (exc) {
                        echo "Flake8 found some warnings."
                        // currentBuild.result = 'UNSTABLE'
                      }
                    }
                    stash includes: "logs/flake8.log", name: "FLAKE8_LOG"
                  }
                  post {
                    always {
                        node('master') {
                            unstash "FLAKE8_LOG"
                            recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                            deleteDir()
                        }
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
                  steps{
                    // unstash "${NODE_NAME}_built_source"
                    dir("source"){
                        bat "python -m pipenv run coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=${WORKSPACE}/reports/pytest/${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest"
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
                        bat "python -m pipenv run coverage combine"
                        bat "python -m pipenv run coverage xml -o ${WORKSPACE}\\reports\\coverage.xml"
                        bat "python -m pipenv run coverage html -d ${WORKSPACE}\\reports\\coverage"

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
                                bat "python -m venv venv36"
                                bat "venv36\\Scripts\\python.exe -m pip install pip --upgrade && venv36\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                        stage("Creating bdist wheel for 3.6"){
                            environment {
                                PATH = "${WORKSPACE}\\venv36\\scripts;${tool 'CPython-3.6'};$PATH"
                            }
                            steps {
                                dir("source"){
                                    bat "python.exe setup.py build -b ../build/36/ -j${env.NUMBER_OF_PROCESSORS} --build-lib ../build/36/lib --build-temp ../build/36/temp build_ext --cmake-exec=${env.CMAKE_PATH}\\cmake.exe bdist_wheel -d ${WORKSPACE}\\dist"
                                }
                            }
                        }
                    }
                }
                stage("Python sdist"){
                    steps {
                        dir("source"){
                            bat "python setup.py sdist -d ${WORKSPACE}\\dist"
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
                                bat "python -m venv venv37"
                                bat "venv37\\Scripts\\python.exe -m pip install pip --upgrade && venv37\\Scripts\\pip.exe install wheel setuptools --upgrade"
                            }
                        }
                    
                        stage("Creating bdist wheel for 3.7"){
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
//                                    deleteDir()
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
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                }
            }
        }
        stage("Deploy to DevPi Staging") {
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
            options{
                timestamps()
            }
            stages{
                stage("Upload to DevPi Staging"){
                    steps {
                        unstash "DOCS_ARCHIVE"
                        bat "venv36\\Scripts\\devpi.exe use https://devpi.library.illinois.edu"
                        bat "devpi use https://devpi.library.illinois.edu && devpi login ${env.DEVPI_USR} --password ${env.DEVPI_PSW} && devpi use /${env.DEVPI_USR}/${env.BRANCH_NAME}_staging && devpi upload --from-dir dist"
                    }
                }
                stage("Test DevPi packages") {
                    parallel {
                        stage("Testing Submitted Source Distribution") {
                            environment {
                                PATH = "${tool 'cmake3.13'};${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
                            }
                            steps {
                                echo "Testing Source tar.gz package in devpi"

                                timeout(20){
                                    devpiTest(
                                        devpiExecutable: "venv36\\Scripts\\devpi.exe",
                                        url: "https://devpi.library.illinois.edu",
                                        index: "${env.BRANCH_NAME}_staging",
                                        pkgName: "${env.PKG_NAME}",
                                        pkgVersion: "${env.PKG_VERSION}",
                                        pkgRegex: "tar.gz",
                                        detox: false
                                    )
                                }
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
                                PATH = "${tool 'CPython-3.6'};$PATH"
                            }
                            options {
                                skipDefaultCheckout(true)
                            }

                            steps {
                                bat "${tool 'CPython-3.6'}\\python -m venv venv36"
                                bat "venv36\\Scripts\\python.exe -m pip install pip --upgrade"
                                bat "venv36\\Scripts\\pip.exe install devpi --upgrade"
                                echo "Testing Whl package in devpi"
                                devpiTest(
                                        devpiExecutable: "venv36\\Scripts\\devpi.exe",
                                        url: "https://devpi.library.illinois.edu",
                                        index: "${env.BRANCH_NAME}_staging",
                                        pkgName: "${env.PKG_NAME}",
                                        pkgVersion: "${env.PKG_VERSION}",
                                        pkgRegex: "36.*whl",
                                        detox: false,
                                        toxEnvironment: "py36"
                                    )

                                echo "Finished testing Built Distribution: .whl"
                            }
                            post {
                                failure {
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "**/MSBuild_*.failure.txt"
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
                        stage("Built Distribution: py37 .whl") {
                            agent {
                                node {
                                    label "Windows && Python3"
                                }}
                            environment {
                                PATH = "${tool 'CPython-3.7'};$PATH"
                            }
                            options {
                                skipDefaultCheckout(true)
                            }

                            steps {
                                echo "Testing Whl package in devpi"
                                bat "\"${tool 'CPython-3.7'}\\python.exe\" -m venv venv37"
                                bat "venv37\\Scripts\\python.exe -m pip install pip --upgrade"
                                bat "venv37\\Scripts\\pip.exe install devpi --upgrade"
                                devpiTest(
                                        devpiExecutable: "venv37\\Scripts\\devpi.exe",
                                        url: "https://devpi.library.illinois.edu",
                                        index: "${env.BRANCH_NAME}_staging",
                                        pkgName: "${env.PKG_NAME}",
                                        pkgVersion: "${env.PKG_VERSION}",
                                        pkgRegex: "37.*whl",
                                        detox: false,
                                        toxEnvironment: "py37"
                                    )
                                echo "Finished testing Built Distribution: .whl"
                            }
                            post {
                                failure {
                                    archiveArtifacts allowEmptyArchive: true, artifacts: "**/MSBuild_*.failure.txt"
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
                                    bat "venv36\\Scripts\\devpi.exe login ${env.DEVPI_USR} --password ${env.DEVPI_PSW}"

                                    bat "venv36\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                                    bat "venv36\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} production/release"
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
                    script {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv36\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv36\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv36\\Scripts\\devpi.exe push ${env.PKG_NAME}==${env.PKG_VERSION} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
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
                                bat "python -m pipenv run python setup.py build_sphinx"
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

            }
        }
    }
    post {
        cleanup {
            script {
//                if(fileExists('source/setup.py')){
//                    dir("source"){
//                        try{
//                            if(fileExists('venv36\\Scripts\\python.exe')){
//                                retry(3) {
//                                    bat "venv36\\Scripts\\python.exe setup.py clean --all"
//                                }
//                            }
//                        } catch (Exception ex) {
//                            echo "Unable to successfully run clean. Purging source directory."
//                            deleteDir()
//                        }
//                    }
//
//            }
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv36\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv36\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    def devpi_remove_return_code = bat(returnStatus: true, script:"venv36\\Scripts\\devpi.exe remove -y ${env.PKG_NAME}==${env.PKG_VERSION}")
                    echo "Devpi remove exited with code ${devpi_remove_return_code}."
                }
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
}
