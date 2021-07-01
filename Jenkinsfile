#!groovy
// @Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
// ============================================================================
//  Groovy helper scripts loaded during start of pipeline
// ============================================================================
// def packaging   = null
// def tox         = null

// ============================================================================
// Configurations loaded at start of pipeline
// ============================================================================
// configurations      = null
// defaultParamValues  = null


def getDevPiStagingIndex(){

    if (env.TAG_NAME?.trim()){
        return 'tag_staging'
    } else{
        return "${env.BRANCH_NAME}_staging"
    }
}

def DEVPI_CONFIG = [
    stagingIndex: getDevPiStagingIndex(),
    server: 'https://devpi.library.illinois.edu',
    credentialsId: 'DS_devpi',
]
PYPI_SERVERS = [
    'https://jenkins.library.illinois.edu/nexus/repository/uiuc_prescon_python/',
    'https://jenkins.library.illinois.edu/nexus/repository/uiuc_prescon_python_public/',
    'https://jenkins.library.illinois.edu/nexus/repository/uiuc_prescon_python_testing/'
    ]
SUPPORTED_MAC_VERSIONS = ['3.8', '3.9']
SUPPORTED_LINUX_VERSIONS = ['3.6', '3.7', '3.8', '3.9']
SUPPORTED_WINDOWS_VERSIONS = ['3.6', '3.7', '3.8', '3.9']
// ============================================================================
//  Dynamic variables. Used to help manage state
wheelStashes = []

// ============================================================================
// Helper functions.
// ============================================================================
// def check_dll_deps(path){
//     if(!isUnix()){
//         findFiles(glob: "${path}/**/*.pyd").each{
//             bat(
//                 label: "Checking Python extension for dependents",
//                 script: "dumpbin /DEPENDENTS ${it.path}"
//             )
//         }
//     }
// }
//

def getMacDevpiName(pythonVersion, format){
    if(format == 'wheel'){
        return "${pythonVersion.replace('.','')}-*macosx*.*whl"
    } else if(format == 'sdist'){
        return 'tar.gz'
    } else{
        error "unknown format ${format}"
    }
}
def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + '/api/issues/search?componentKeys=' + props['projectKey'] + '&resolved=no'
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
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
                remoteDirectory: pkgName,
                remoteDirectorySDF: false,
                removePrefix: prefix,
                sourceFiles: "${prefix}/**")],
            usePromotionTimestamp: false,
            useWorkspaceInPromotion: false,
            verbose: true
            )
        ]
    )
}


def sonarcloudSubmit(outputJson, sonarCredentials){
    unstash 'DIST-INFO'

    def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
    withSonarQubeEnv(installationName:'sonarcloud', credentialsId: sonarCredentials) {
        if (env.CHANGE_ID){
            sh(
                label: 'Running Sonar Scanner',
                script:"sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
                )
        } else {
            sh(
                label: 'Running Sonar Scanner',
                script: "sonar-scanner -Dsonar.projectVersion=${props.Version} -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory"
                )
        }
    }
     timeout(time: 1, unit: 'HOURS') {
         def sonarqube_result = waitForQualityGate(abortPipeline: false)
         if (sonarqube_result.status != 'OK') {
             unstable "SonarQube quality gate: ${sonarqube_result.status}"
         }
         def outstandingIssues = get_sonarqube_unresolved_issues('.scannerwork/report-task.txt')
         writeJSON file: outputJson, json: outstandingIssues
     }
}


def startup(){
    parallel(
        [
            failFast: true,
            'Loading Reference Build Information': {
                node(){
                    checkout scm
                    discoverGitReferenceBuild(latestBuildIfNotFound: true)
                }
            },
            'Loading helper scripts and configs': {
                node(){
                    ws{
                        checkout scm
                        devpi = load('ci/jenkins/scripts/devpi.groovy')
                        echo 'loading configurations'
                        defaultParamValues = readYaml(file: 'ci/jenkins/defaultParameters.yaml').parameters.defaults
//                         configurations = load('ci/jenkins/scripts/configs.groovy').getConfigurations()
                    }
                }
            },
            'Getting Distribution Info': {
                node('linux && docker') {
                    ws{
                        checkout scm
                        try{
                            docker.image('python').inside {
                                timeout(2){
                                    sh(
                                       label: 'Running setup.py with dist_info',
                                       script: '''python --version
                                                  PIP_NO_CACHE_DIR=off python setup.py dist_info
                                               '''
                                    )
                                    stash includes: 'py3exiv2bind.dist-info/**', name: 'DIST-INFO'
                                    archiveArtifacts artifacts: 'py3exiv2bind.dist-info/**'
                                }
                            }
                        } finally{
                            cleanWs()
                        }
                    }
                }
            }
        ]
    )
}



def test_cpp_code(buildPath){
    stage('Build'){
        tee('logs/cmake-build.log'){
            sh(label: 'Building C++ Code',
               script: """conan install . -if ${buildPath}
                          cmake -B ${buildPath} -Wdev -DCMAKE_TOOLCHAIN_FILE=build/conan_paths.cmake -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra"
                          cmake --build ${buildPath} -j \$(grep -c ^processor /proc/cpuinfo)
                          """
            )
        }
    }
    stage('CTest'){
        sh(label: 'Running CTest',
           script: "cd ${buildPath} && ctest --output-on-failure --no-compress-output -T Test"
        )
    }
}
def get_props(){
    stage('Reading Package Metadata'){
        node() {
            try{
                unstash 'DIST-INFO'
                def props = readProperties interpolate: true, file: 'py3exiv2bind.dist-info/METADATA'
                return props
            } finally {
                cleanWs()
            }
        }
    }
}
// *****************************************************************************
startup()
props = get_props()
pipeline {
    agent none
    parameters {
        booleanParam(
                name: 'TEST_RUN_TOX',
                defaultValue: defaultParamValues.TEST_RUN_TOX,
                description: 'Run Tox Tests'
            )
        booleanParam(
                name: 'RUN_CHECKS',
                defaultValue: defaultParamValues.RUN_CHECKS,
                description: 'Run checks on code'
            )
        booleanParam(
                name: 'USE_SONARQUBE',
                defaultValue: defaultParamValues.USE_SONARQUBE,
                description: 'Send data test data to SonarQube'
            )
        booleanParam(
                name: 'BUILD_PACKAGES',
                defaultValue: defaultParamValues.BUILD_PACKAGES,
                description: 'Build Python packages'
            )
        booleanParam(
                name: 'BUILD_MAC_PACKAGES',
                defaultValue: defaultParamValues.BUILD_MAC_PACKAGES,
                description: 'Test Python packages on Mac'
            )
        booleanParam(
                name: 'TEST_PACKAGES',
                defaultValue: defaultParamValues.TEST_PACKAGES,
                description: 'Test Python packages by installing them and running tests on the installed package'
            )
        booleanParam(
                name: 'DEPLOY_DEVPI',
                defaultValue: defaultParamValues.DEPLOY_DEVPI,
                description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}"
            )
        booleanParam(
                name: 'DEPLOY_DEVPI_PRODUCTION',
                defaultValue: defaultParamValues.DEPLOY_DEVPI_PRODUCTION,
                description: 'Deploy to https://devpi.library.illinois.edu/production/release'
            )
        booleanParam(
                name: 'DEPLOY_PYPI',
                defaultValue: false,
                description: 'Deploy to pypi'
            )
        booleanParam(
                name: 'DEPLOY_DOCS',
                defaultValue: defaultParamValues.DEPLOY_DOCS,
                description: 'Update online documentation'
        )
    }
    stages {
        stage('Building Documentation'){
            agent {
                dockerfile {
                    filename 'ci/docker/linux/test/Dockerfile'
                    label 'linux && docker'
                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL'
                }
            }
            steps {
                sh(label: 'Running Sphinx',
                   script: '''mkdir -p logs
                              mkdir -p build/docs/html
                              python setup.py build -b build --build-lib build/lib/ --build-temp build/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace
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
                    zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.Name}-${props.Version}.doc.zip"
                    stash includes: 'dist/*.doc.zip,build/docs/html/**', name: 'DOCS_ARCHIVE'
                }
                cleanup{
                    cleanWs(
                        deleteDirs: true,
                        patterns: [
                            [pattern: 'build/', type: 'INCLUDE'],
                            [pattern: 'logs/', type: 'INCLUDE'],
                            [pattern: 'dist/', type: 'INCLUDE']
                        ]
                    )
                }
            }
        }
        stage('Checks'){
            when{
                equals expected: true, actual: params.RUN_CHECKS
            }
            stages{
                stage('Code Quality'){
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/test/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL'
                            args '--mount source=sonar-cache-py3exiv2bind,target=/opt/sonar/.sonar/cache'
                        }
                    }
                    stages{
                        stage('Testing') {
                            stages{
//                                 stage('Setting up Test Env'){
//                                     steps{
//                                         sh '''mkdir -p build
//                                               mkdir -p logs
//                                               '''
//                                     }
//                                 }
                                stage('Building Project for Testing'){
                                    parallel{
                                        stage('Building Extension for Python with coverage data'){
                                            steps{
                                                sh(label: 'Building debug build with coverage data',
                                                   script: 'mkdir -p build/build_wrapper_output_directory && CFLAGS="--coverage -fprofile-arcs -ftest-coverage" LFLAGS="-lgcov --coverage" build-wrapper-linux-x86-64 --out-dir build/build_wrapper_output_directory python setup.py build -b build/python --build-lib build/python/lib/ --build-temp build/python/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace'
                                               )
                                            }
                                        }
                                        stage('Building Extension code and C++ Tests with coverage data'){
                                            steps{
                                                tee('logs/cmake-build.log'){
                                                    sh(label: 'Building C++ Code',
                                                       script: '''conan install . -if build/cpp/
                                                                  cmake -B build/cpp/ -Wdev -DCMAKE_TOOLCHAIN_FILE=build/cpp/conan_paths.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra"
                                                                  '''
                                                    )
                                                }
                                                sh 'mkdir -p build/build_wrapper_output_directory && build-wrapper-linux-x86-64 --out-dir build/build_wrapper_output_directory cmake --build build/cpp -j $(grep -c ^processor /proc/cpuinfo) --target all '
                                            }
                                            post{
                                                always{
                                                    recordIssues(
                                                        filters: [excludeFile('build/cpp/_deps/*')],
                                                        tools: [gcc(pattern: 'logs/cmake-build.log'), [$class: 'Cmake', pattern: 'logs/cmake-build.log']]
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                                stage('Running Tests'){
                                    parallel {
                                        stage('Clang Tidy Analysis') {
                                            steps{
                                                tee('logs/clang-tidy.log') {
                                                    catchError(buildResult: 'SUCCESS', message: 'Clang-Tidy found issues', stageResult: 'UNSTABLE') {
                                                        sh(label: 'Run Clang Tidy', script: 'run-clang-tidy -clang-tidy-binary clang-tidy -p ./build/cpp/')
                                                    }
                                                }
                                            }
                                            post{
                                                always {
                                                    recordIssues(
                                                        filters: [
                                                            excludeFile('build/cpp/_deps/*'),
                                                            excludeFile('/usr/include/*'),
                                                        ],
                                                        tools: [clangTidy(pattern: 'logs/clang-tidy.log')]
                                                    )
                                                }
                                            }
                                        }
                                        stage('CPP Check'){
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'cppcheck found issues', stageResult: 'UNSTABLE') {
                                                    sh(label: 'Running cppcheck',
//                                                        script: "cppcheck --error-exitcode=1 --project=build/cpp/compile_commands.json -i$WORKSPACE/build/cpp/_deps  --suppress=missingIncludeSystem --suppress=unmatchedSuppression --enable=all  --xml --output-file=logs/cppcheck_debug.xml"
                                                       script: 'cppcheck --error-exitcode=1 --project=build/cpp/compile_commands.json -i$WORKSPACE/build/cpp/_deps --suppress=*:build/cpp/_deps/* --enable=all  --xml --output-file=logs/cppcheck_debug.xml'
                                                       )
                                                }
                                            }
                                            post{
                                                always {
                                                    recordIssues(
                                                        filters: [
//                                                             excludeFile('build/cpp/_deps/*'),
                                                        ],
                                                        tools: [
                                                            cppCheck(pattern: 'logs/cppcheck_debug.xml')
                                                        ]
                                                    )
                                                }
                                            }
                                        }
                                        stage('CTest'){
                                            steps{
                                                sh(label: 'Running CTest',
                                                   script: 'cd build/cpp && ctest --output-on-failure --no-compress-output -T Test'
                                                )
                                            }
                                            post{
                                                always{
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
                                                                pattern: 'build/Testing/**/*.xml',
                                                                skipNoTestFiles: true,
                                                                stopProcessingIfError: true
                                                            )
                                                        ]
                                                   )
                                                }
                                            }
                                        }
                                        stage('Run Doctest Tests'){
                                            steps {
                                                sh 'sphinx-build docs/source reports/doctest -b doctest -d build/docs/.doctrees --no-color -w logs/doctest_warnings.log'
                                            }
                                            post{
                                                always {
                                                    recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest_warnings.log', id: 'doctest')])
                                                }
                                            }
                                        }
                                        stage('MyPy Static Analysis') {
                                            steps{
                                                tee('logs/mypy.log'){
                                                    sh(returnStatus: true,
                                                       script: 'mypy -p py3exiv2bind --html-report reports/mypy/html'
                                                      )
                                                }
                                            }
                                            post {
                                                always {
                                                    recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                }
                                            }
                                        }
                                        stage('Run Pylint Static Analysis') {
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                    sh(
                                                        script: '''mkdir -p logs
                                                                   mkdir -p reports
                                                                   PYLINTHOME=. pylint py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                                   ''',
                                                        label: 'Running pylint'
                                                    )
                                                }
                                                sh(
                                                    script: 'PYLINTHOME=. pylint  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                                    label: 'Running pylint for sonarqube',
                                                    returnStatus: true
                                                )
                                            }
                                            post{
                                                always{
                                                    stash includes: 'reports/pylint_issues.txt,reports/pylint.txt', name: 'PYLINT_REPORT'
                                                    recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                                }
                                            }
                                        }
                                        stage('Flake8') {
                                          steps{
                                            sh returnStatus: true, script: 'flake8 py3exiv2bind --tee --output-file ./logs/flake8.log'
                                          }
                                          post {
                                            always {
                                                stash includes: 'logs/flake8.log', name: 'FLAKE8_REPORT'
                                                recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                            }
                                          }
                                        }
                                        stage('Running Unit Tests'){
                                            steps{
                                                sh 'coverage run --parallel-mode --source=py3exiv2bind -m pytest --junitxml=./reports/pytest/junit-pytest.xml'
                                            }
                                            post{
                                                always{
                                                    stash includes: 'reports/pytest/junit-pytest.xml', name: 'PYTEST_REPORT'
                                                    junit 'reports/pytest/junit-pytest.xml'
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
                                                  gcovr --root . --filter py3exiv2bind --exclude-directories build/python/temp/conan_cache --print-summary --keep --json -o reports/coverage/coverage-c-extension.json
                                                  gcovr --root . --filter py3exiv2bind --print-summary --keep --json -o reports/coverage/coverage_cpp.json
                                                  gcovr --add-tracefile reports/coverage/coverage-c-extension.json --add-tracefile reports/coverage/coverage_cpp.json --keep --print-summary --xml -o reports/coverage/coverage_cpp.xml
                                                  '''
                                          )
                                    stash(includes: 'reports/coverage/*.xml,reports/coverage/*.json', name: 'PYTHON_COVERAGE_REPORT')
                                    unstash 'PYTHON_COVERAGE_REPORT'
                                    publishCoverage(
                                        adapters: [
                                                coberturaAdapter(mergeToOneReport: true, path: 'reports/coverage/*.xml')
                                            ],
                                        sourceFileResolver: sourceFiles('STORE_ALL_BUILD')
                                    )
                                }
                            }
                        }
                        stage('Sonarcloud Analysis'){
                            options{
                                lock('py3exiv2bind-sonarcloud')
                            }
                            when{
                                equals expected: true, actual: params.USE_SONARQUBE
                                beforeAgent true
                                beforeOptions true
                            }
                            steps{
                                sh(
                                    label: 'Preparing c++ coverage data available for SonarQube',
                                    script: """mkdir -p build/coverage
                                    find ./build -name '*.gcno' -exec gcov {} -p --source-prefix=${WORKSPACE}/ \\;
                                    mv *.gcov build/coverage/
                                    """
                                    )

//                                 unstash 'PYTHON_COVERAGE_REPORT'
//                                 unstash 'PYTEST_REPORT'
                //                 unstash 'BANDIT_REPORT'
//                                 unstash 'PYLINT_REPORT'
//                                 unstash 'FLAKE8_REPORT'

                                sonarcloudSubmit('reports/sonar-report.json', 'sonarcloud-py3exiv2bind')
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
                    post{
                        cleanup{
                            cleanWs(
                                patterns: [
                                        [pattern: '.coverage/', type: 'INCLUDE'],
                                        [pattern: '.eggs/', type: 'INCLUDE'],
                                        [pattern: '.mypy_cache/', type: 'INCLUDE'],
                                        [pattern: '.pytest_cache/', type: 'INCLUDE'],
                                        [pattern: 'dist/', type: 'INCLUDE'],
                                        [pattern: 'build/', type: 'INCLUDE'],
                                        [pattern: '*.dist-info/', type: 'INCLUDE'],
                                        [pattern: 'logs/', type: 'INCLUDE'],
                                        [pattern: 'reports/', type: 'INCLUDE'],
                                        [pattern: 'generatedJUnitFiles/', type: 'INCLUDE'],
                                        [pattern: 'py3exiv2bind/*.so', type: 'INCLUDE'],
                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                    ],
                                notFailBuild: true,
                                deleteDirs: true
                            )
                        }
                    }
                }
                stage('Run Tox test') {
                    when {
                       equals expected: true, actual: params.TEST_RUN_TOX
                       beforeAgent true
                    }
                    steps {
                        script{
                            def tox
                            node(){
                                checkout scm
                                tox = load('ci/jenkins/scripts/tox.groovy')
                            }
                            def windowsJobs = [:]
                            def linuxJobs = [:]
                            parallel(
                                'Linux':{
                                    linuxJobs = tox.getToxTestsParallel(
                                                envNamePrefix: 'Tox Linux',
                                                label: 'linux && docker',
                                                dockerfile: 'ci/docker/linux/tox/Dockerfile',
                                                dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                            )
                                },
                                'Windows':{
                                    windowsJobs = tox.getToxTestsParallel(
                                                    envNamePrefix: 'Tox Windows',
                                                    label: 'windows && docker',
                                                    dockerfile: 'ci/docker/windows/tox/Dockerfile',
                                                    dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                                )
                                }
                            )
                            parallel(windowsJobs + linuxJobs)
                        }
                    }
                }
            }
        }
        stage('Python Packaging'){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                }
                beforeAgent true
            }
            stages{
                stage('Building'){
                    steps{
                        script{
                            def packages
                            node(){
                                checkout scm
                                packages = load 'ci/jenkins/scripts/packaging.groovy'
                            }
                            def macBuildStages = [:]
                                SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                                    macBuildStages["MacOS - Python ${pythonVersion}: wheel"] = {
                                        packages.buildPkg(
                                            agent: [
                                                label: "mac && python${pythonVersion}",
                                            ],
                                            buildCmd: {
                                                sh "python${pythonVersion} -m pip wheel -v --no-deps -w ./dist ."
                                            },
                                            post:[
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                    stash includes: 'dist/*.whl', name: "python${pythonVersion} mac wheel"
                                                    wheelStashes << "python${pythonVersion} mac wheel"
                                                }
                                            ]
                                        )
                                    }
                                }
                                def windowsBuildStages = [:]
                                SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                                    windowsBuildStages["Windows - Python ${pythonVersion}: wheel"] = {
                                        packages.buildPkg(
                                            agent: [
                                                dockerfile: [
                                                    label: 'windows && docker',
                                                    filename: 'ci/docker/windows/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                                ]
                                            ],
                                            buildCmd: {
                                                bat "py -${pythonVersion} -m build --wheel"
                                            },
                                            post:[
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                    stash includes: 'dist/*.whl', name: "python${pythonVersion} windows wheel"
                                                    wheelStashes << "python${pythonVersion} windows wheel"
                                                }
                                            ]
                                        )
                                    }
                                }
                                def buildStages =  [
                                   failFast: true,
                                    'Source Distribution': {
                                        packages.buildPkg(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker',
                                                    filename: 'ci/docker/linux/package/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                                ]
                                            ],
                                            buildCmd: {
                                                sh 'python3 -m build --sdist'
                                            },
                                            post:[
                                                success: {
                                                    stash includes: 'dist/*.tar.gz,dist/*.zip', name: 'sdist'
                                                    wheelStashes << 'sdist'
                                                    archiveArtifacts artifacts: 'dist/*.tar.gz,dist/*.zip'
                                                },
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                            ]
                                        )
                                    }
                                ]
                                def linuxBuildStages = [:]
                                SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
                                    linuxBuildStages["Linux - Python ${pythonVersion}: wheel"] = {
                                        packages.buildPkg(
                                            agent: [
                                                dockerfile: [
                                                    label: 'linux && docker',
                                                    filename: 'ci/docker/linux/package/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                                ]
                                            ],
                                            buildCmd: {
                                                sh(label: 'Building python wheel',
                                                   script:"""python${pythonVersion} -m build --wheel
                                                             auditwheel repair ./dist/*.whl -w ./dist
                                                             """
                                                   )
                                            },
                                            post:[
                                                cleanup: {
                                                    cleanWs(
                                                        patterns: [
                                                                [pattern: 'dist/', type: 'INCLUDE'],
                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                            ],
                                                        notFailBuild: true,
                                                        deleteDirs: true
                                                    )
                                                },
                                                success: {
                                                    stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux wheel"
                                                    wheelStashes << "python${pythonVersion} linux wheel"
                                                }
                                            ]
                                        )
                                    }
                                }
                                buildStages = buildStages + windowsBuildStages + linuxBuildStages
                                if(params.BUILD_MAC_PACKAGES == true){
                                    buildStages = buildStages + macBuildStages
                                }
                                parallel(buildStages)
                        }
                    }
                }
                stage('Testing'){
                    when{
                        equals expected: true, actual: params.TEST_PACKAGES
                    }
                    steps{
                        script{
                            def packages
                            node(){
                                checkout scm
                                packages = load 'ci/jenkins/scripts/packaging.groovy'
                            }
                            def macTestStages = [:]
                            SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                                macTestStages["MacOS - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion}",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} mac wheel"
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
                                                )
                                            }
                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: 'venv/', type: 'INCLUDE'],
                                                            [pattern: '.tox/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                            success: {
                                                 archiveArtifacts artifacts: 'dist/*.whl'
                                            }
                                        ]
                                    )
                                }
                                macTestStages["MacOS - Python ${pythonVersion}: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            label: "mac && python${pythonVersion}",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install tox
                                                   ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
                                                )
                                            }

                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: 'venv/', type: 'INCLUDE'],
                                                            [pattern: '.tox/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                        ]
                                    )
                                }
                            }
                            def windowsTestStages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                                windowsTestStages["Windows - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'windows && docker',
                                                filename: 'ci/docker/windows/tox_no_vs/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                            ]
                                        ],
                                        dockerImageName: "${currentBuild.fullProjectName}_test_no_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        testSetup: {
                                             checkout scm
                                             unstash "python${pythonVersion} windows wheel"
                                        },
                                        testCommand: {
                                             findFiles(glob: 'dist/*.whl').each{
                                                timeout(10){
                                                    bat(label: 'Running Tox', script: "tox --installpkg ${it.path} --workdir %TEMP%\\tox  -e py${pythonVersion.replace('.', '')}")
                                                }
                                             }

                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                            success: {
                                                archiveArtifacts artifacts: 'dist/*.whl'
                                            }
                                        ]
                                    )
                                }
                                windowsTestStages["Windows - Python ${pythonVersion}: sdist"] = {

                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'windows && docker',
                                                filename: 'ci/docker/windows/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE'
                                            ]
                                        ],
                                        dockerImageName: "${currentBuild.fullProjectName}_test_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                timeout(60){
                                                    bat(label: 'Running Tox', script: "tox --workdir %TEMP%\\tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}")
                                                }
                                            }
                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                        ]
                                    )
                                }
                            }
                            def linuxTestStages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
                                linuxTestStages["Linux - Python ${pythonVersion}: wheel"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker',
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                            ]
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} linux wheel"
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                timeout(5){
                                                    sh(
                                                        label: 'Running Tox',
                                                        script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                        )
                                                }
                                            }
                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                            success: {
                                                archiveArtifacts artifacts: 'dist/*.whl'
                                            },
                                        ]
                                    )
                                }
                                linuxTestStages["Linux - Python ${pythonVersion}: sdist"] = {
                                    packages.testPkg2(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker',
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                                            ]
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash 'sdist'
                                        },
                                        testCommand: {
                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                sh(
                                                    label: 'Running Tox',
                                                    script: "tox --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}"
                                                    )
                                            }
                                        },
                                        post:[
                                            cleanup: {
                                                cleanWs(
                                                    patterns: [
                                                            [pattern: 'dist/', type: 'INCLUDE'],
                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                        ],
                                                    notFailBuild: true,
                                                    deleteDirs: true
                                                )
                                            },
                                        ]
                                    )
                                }

                            }

                            def testingStages = windowsTestStages + linuxTestStages
                            if(params.BUILD_MAC_PACKAGES == true){
                                testingStages = testingStages + macTestStages
                            }
                            parallel(testingStages)
                        }
                    }
                }
            }
        }
        stage('Deploy to Devpi'){
            when {
                allOf{
                    equals expected: true, actual: params.DEPLOY_DEVPI
                    anyOf {
                        equals expected: 'master', actual: env.BRANCH_NAME
                        equals expected: 'dev', actual: env.BRANCH_NAME
                        tag '*'
                    }
                }
                beforeAgent true
            }
            agent none
            options{
                lock('py3exiv2bind-devpi')
            }
            stages{
                stage('Deploy to Devpi Staging') {
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/tox/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                          }
                    }
                    options{
                        retry(3)
                    }
                    steps {
                        timeout(5){
                            unstash 'DOCS_ARCHIVE'
                            script{
                                wheelStashes.each{
                                    unstash it
                                }
                                devpi.upload(
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,
                                    index: DEVPI_CONFIG.stagingIndex,
                                )
                            }
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE']
                                    ]
                            )
                        }
                    }
                }
                stage('Test DevPi packages') {
                    steps{
                        script{
                            def macPackages = [:]
                            SUPPORTED_MAC_VERSIONS.each{pythonVersion ->
                                macPackages["MacOS - Python ${pythonVersion}: wheel"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            label: "mac && python${pythonVersion}"
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                            devpiExec: 'venv/bin/devpi'
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: getMacDevpiName(pythonVersion, 'wheel'),
                                        ],
                                        test:[
                                            setup: {
                                                sh(
                                                    label:'Installing Devpi client',
                                                    script: '''python3 -m venv venv
                                                                venv/bin/python -m pip install pip --upgrade
                                                                venv/bin/python -m pip install devpi_client
                                                                '''
                                                )
                                            },
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                            teardown: {
                                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                                            }
                                        ]
                                    )
                                }
                                macPackages["MacOS - Python ${pythonVersion}: sdist"]= {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            label: "mac && python${pythonVersion}"
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                            devpiExec: 'venv/bin/devpi'
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            setup: {
                                                sh(
                                                    label:'Installing Devpi client',
                                                    script: '''python3 -m venv venv
                                                                venv/bin/python -m pip install pip --upgrade
                                                                venv/bin/python -m pip install devpi_client
                                                                '''
                                                )
                                            },
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                            teardown: {
                                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                                            }
                                        ]
                                    )
                                }
                            }
                            def windowsPackages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{pythonVersion ->
                                windowsPackages["Windows - Python ${pythonVersion}: sdist"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/windows/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                label: 'windows && docker'
                                            ]
                                        ],
                                        dockerImageName:  "${currentBuild.fullProjectName}_devpi_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                                windowsPackages["Test Python ${pythonVersion}: wheel Windows"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/windows/tox_no_vs/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE',
                                                label: 'windows && docker'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        dockerImageName:  "${currentBuild.fullProjectName}_devpi_without_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: "(${pythonVersion.replace('.','')}).*(win_amd64\\.whl)"
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                            }
                            def linuxPackages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                linuxPackages["Linux - Python ${pythonVersion}: sdist"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                label: 'linux && docker'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: 'tar.gz'
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                                linuxPackages["Linux - Python ${pythonVersion}: wheel"] = {
                                    devpi.testDevpiPackage(
                                        agent: [
                                            dockerfile: [
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                label: 'linux && docker'
                                            ]
                                        ],
                                        devpi: [
                                            index: DEVPI_CONFIG.stagingIndex,
                                            server: DEVPI_CONFIG.server,
                                            credentialsId: DEVPI_CONFIG.credentialsId,
                                        ],
                                        package:[
                                            name: props.Name,
                                            version: props.Version,
                                            selector: "(${pythonVersion.replace('.','')}).*(manylinux).*(\\.whl)"
                                        ],
                                        test:[
                                            toxEnv: "py${pythonVersion}".replace('.',''),
                                        ]
                                    )
                                }
                            }
                            def devpiPackagesTesting = windowsPackages + linuxPackages
                            if (params.BUILD_MAC_PACKAGES){
                                 devpiPackagesTesting = devpiPackagesTesting + macPackages
                            }

                            parallel(devpiPackagesTesting)
                        }
                    }
                }
                stage('Deploy to DevPi Production') {
                    when {
                        allOf{
                            equals expected: true, actual: params.DEPLOY_DEVPI_PRODUCTION
                            anyOf {
                                branch 'master'
                                tag '*'
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
                            filename 'ci/docker/linux/tox/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL'
                        }
                    }
                    steps {
                        script{
//                             echo 'Pushing to production/release index'
                            devpi.pushPackageToIndex(
                                pkgName: props.Name,
                                pkgVersion: props.Version,
                                server: DEVPI_CONFIG.server,
                                indexSource: "DS_Jenkins/${DEVPI_CONFIG.stagingIndex}",
                                indexDestination: 'production/release',
                                credentialsId: DEVPI_CONFIG.credentialsId
                            )
                        }
                    }
                }
            }
            post{
                success{
                    node('linux && docker') {
                        script{
                            if (!env.TAG_NAME?.trim()){
                                docker.build('py3exiv2bind:devpi','-f ./ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                    devpi.pushPackageToIndex(
                                        pkgName: props.Name,
                                        pkgVersion: props.Version,
                                        server: DEVPI_CONFIG.server,
                                        indexSource: "DS_Jenkins/${DEVPI_CONFIG.stagingIndex}",
                                        indexDestination: "DS_Jenkins/${env.BRANCH_NAME}",
                                        credentialsId: DEVPI_CONFIG.credentialsId
                                    )
                                }
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker') {
                        script{
                            docker.build('py3exiv2bind:devpi','-f ./ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .').inside{
                                devpi.removePackage(
                                    pkgName: props.Name,
                                    pkgVersion: props.Version,
                                    index: "DS_Jenkins/${DEVPI_CONFIG.stagingIndex}",
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,

                                )
                            }
                        }
                    }
                }
            }
        }
        stage('Deploy'){
            parallel {
                stage('Deploy to pypi') {
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/test/Dockerfile'
                            label 'linux && docker'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.8  --build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    when{
                        allOf{
                            equals expected: true, actual: params.BUILD_PACKAGES
                            equals expected: true, actual: params.DEPLOY_PYPI
                        }
                        beforeAgent true
                        beforeInput true
                    }
                    options{
                        retry(3)
                    }
                    input {
                        message 'Upload to pypi server?'
                        parameters {
                            choice(
                                choices: PYPI_SERVERS,
                                description: 'Url to the pypi index to upload python packages.',
                                name: 'SERVER_URL'
                            )
                        }
                    }
                    steps{
                        unstash 'sdist'
                        script{
                            wheelStashes.each{
                                unstash it
                            }
                            def pypi = fileLoader.fromGit(
                                    'pypi',
                                    'https://github.com/UIUCLibrary/jenkins_helper_scripts.git',
                                    '1',
                                    null,
                                    ''
                                )
                            pypi.pypiUpload(
                                credentialsId: 'jenkins-nexus',
                                repositoryUrl: SERVER_URL,
                                glob: 'dist/*'
                                )
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                        [pattern: 'dist/', type: 'INCLUDE']
                                    ]
                            )
                        }
                    }

                }
//                 stage('Deploy Online Documentation') {
//                     agent any
//                     when{
//                         equals expected: true, actual: params.DEPLOY_DOCS
//                         beforeAgent true
//                         beforeInput true
//                     }
//                     options{
//                         timeout(30)
//                     }
//                     input{
//                         message 'Update project documentation?'
//                     }
//                     steps{
//                         unstash 'DOCS_ARCHIVE'
//                         deploy_docs(props.Name, 'build/docs/html')
//                     }
//                 }
            }
        }
    }
}
