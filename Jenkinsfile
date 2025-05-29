import org.jenkinsci.plugins.pipeline.modeldefinition.Utils
library identifier: 'JenkinsPythonHelperLibrary@2024.1.2', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git',
   ])

def generate_ctest_memtest_script(scriptName){
    writeFile( file: 'suppression.txt',
               text: '''UNINITIALIZED READ: reading register rcx
                        libpthread.so.0!__pthread_initialize_minimal_internal
                        ''')
    writeFile(file: scriptName,
              text: '''set(CTEST_SOURCE_DIRECTORY "$ENV{WORKSPACE}")
                       set(CTEST_BINARY_DIRECTORY build/cpp)
                       set(CTEST_MEMORYCHECK_COMMAND /usr/local/bin/drmemory)
                       set(CTEST_MEMORYCHECK_SUPPRESSIONS_FILE "$ENV{WORKSPACE}/suppression.txt")
                       ctest_start("Experimental")
                       ctest_memcheck()
                       ''')
}
def getPypiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'pypi_config', variable: 'CONFIG_FILE')]) {
            def config = readJSON( file: CONFIG_FILE)
            return config['deployment']['indexes']
        }
    }
}

def installMSVCRuntime(cacheLocation){
    def cachedFile = "${cacheLocation}\\vc_redist.x64.exe".replaceAll(/\\\\+/, '\\\\')
    withEnv(
        [
            "CACHED_FILE=${cachedFile}",
            "RUNTIME_DOWNLOAD_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe"
        ]
    ){
        lock("${cachedFile}-${env.NODE_NAME}"){
            powershell(
                label: 'Ensuring vc_redist runtime installer is available',
                script: '''if ([System.IO.File]::Exists("$Env:CACHED_FILE"))
                           {
                                Write-Host 'Found installer'
                           } else {
                                Write-Host 'No installer found'
                                Write-Host 'Downloading runtime'
                                [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;Invoke-WebRequest "$Env:RUNTIME_DOWNLOAD_URL" -OutFile "$Env:CACHED_FILE"
                           }
                        '''
            )
        }
        powershell(label: 'Install VC Runtime', script: 'Start-Process -filepath "$Env:CACHED_FILE" -ArgumentList "/install", "/passive", "/norestart" -Passthru | Wait-Process;')
    }
}
def SUPPORTED_MAC_VERSIONS = ['3.9', '3.10', '3.11', '3.12', '3.13']
def SUPPORTED_LINUX_VERSIONS = ['3.9', '3.10', '3.11', '3.12', '3.13']
def SUPPORTED_WINDOWS_VERSIONS = ['3.9', '3.10', '3.11', '3.12', '3.13']
// ============================================================================
//  Dynamic variables. Used to help manage state
def wheelStashes = []


def startup(){
    node(){
        parallel(
            [
                failFast: true,
                'Loading Reference Build Information': {
                    stage('Loading Reference Build Information'){
                        discoverGitReferenceBuild(latestBuildIfNotFound: true)
                    }
                },
                'Enable Git Forensics': {
                    stage('Enable Git Forensics'){
                        mineRepository()
                    }
                },
            ]
        )
    }
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

def windows_wheels(pythonVersions, testPackages, params, wheelStashes){
    def wheelStages = [:]
    pythonVersions.each{ pythonVersion ->
        if(params.INCLUDE_WINDOWS_X86_64 == true){
            wheelStages["Python ${pythonVersion} - Windows"] = {
                stage("Python ${pythonVersion} - Windows"){
                    stage("Build Wheel (${pythonVersion} Windows)"){
                        node('windows && docker'){
                            def dockerImageName = "${currentBuild.fullProjectName}_${UUID.randomUUID().toString()}".replaceAll("-", "_").replaceAll('/', "_").replaceAll(' ', "").toLowerCase()
                            retry(3){
                                checkout scm
                                timeout(60){
                                    powershell(label: 'Building Wheel for Windows', script: "contrib/build_windows.ps1 -PythonVersion ${pythonVersion} -DockerImageName ${dockerImageName}")
                                }
                                try{
                                    stash includes: 'dist/*.whl', name: "python${pythonVersion} windows wheel"
                                    wheelStashes << "python${pythonVersion} windows wheel"
                                    archiveArtifacts artifacts: 'dist/*.whl'
                                } finally {
                                    powershell(
                                        label: "Untagging Docker Image used",
                                        script: "docker image rm --no-prune ${dockerImageName}",
                                        returnStatus: true
                                    )
                                    bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                }
                            }
                        }
                    }
                    if(testPackages == true){
                        stage("Test Wheel (${pythonVersion} Windows)"){
                            node('windows && docker'){
                                docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python').inside('--mount source=uv_python_install_dir,target=C:\\Users\\ContainerUser\\Documents\\uvpython --mount source=msvc-runtime,target=c:\\msvc_runtime --mount source=windows-certs,target=c:\\certs'){
                                    installMSVCRuntime('c:\\msvc_runtime\\')
                                    checkout scm
                                    unstash "python${pythonVersion} windows wheel"
                                    withEnv([
                                        'PIP_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\pipcache',
                                        'UV_TOOL_DIR=C:\\Users\\ContainerUser\\Documents\\uvtools',
                                        'UV_PYTHON_INSTALL_DIR=C:\\Users\\ContainerUser\\Documents\\uvpython',
                                        'UV_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\uvcache',
                                        'UV_INDEX_STRATEGY=unsafe-best-match',
                                    ]){
                                        findFiles(glob: 'dist/*.whl').each{
                                            retry(3){
                                                timeout(60){
                                                    bat(label: 'Running Tox',
                                                        script: """python -m venv venv
                                                                   venv\\Scripts\\pip install --disable-pip-version-check uv
                                                                   venv\\Scripts\\uvx --python ${pythonVersion} --constraint=requirements-dev.txt --with tox-uv tox run -e py${pythonVersion.replace('.', '')}  --installpkg ${it.path}
                                                                   rmdir /S /Q venv
                                                                   rmdir /S /Q .tox
                                                                """
                                                    )
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
        }
    }
    parallel(wheelStages)
}

def linux_wheels(pythonVersions, testPackages, params, wheelStashes){
    def wheelStages = [:]
    def selectedArches = []
    def allValidArches = ['arm64', 'x86_64']
    if(params.INCLUDE_LINUX_ARM == true){
        selectedArches << 'arm64'
    }
    if(params.INCLUDE_LINUX_X86_64 == true){
        selectedArches << 'x86_64'
    }
     parallel([failFast: true] << pythonVersions.collectEntries{ pythonVersion ->
        [
            "Python ${pythonVersion} - Linux": {
                stage("Python ${pythonVersion} - Linux"){
                    parallel([failFast: true] << allValidArches.collectEntries{ arch ->
                        def newStageName = "Python ${pythonVersion} Linux ${arch} Wheel"
                        return [
                            "${newStageName}":{
                                stage(newStageName){
                                    if(selectedArches.contains(arch)){
                                        stage("Build Wheel (${pythonVersion} Linux ${arch})"){
                                            buildPythonPkg(
                                                agent: [
                                                    dockerfile: [
                                                        label: "linux && docker && ${arch}",
                                                        filename: 'ci/docker/linux/package/Dockerfile',
                                                        additionalBuildArgs: "--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=${arch=='x86_64'? 'quay.io/pypa/manylinux_2_28_x86_64': 'quay.io/pypa/manylinux_2_28_aarch64'}"
                                                    ]
                                                ],
                                                retries: 3,
                                                buildCmd: {
                                                    try{
                                                        timeout(60){
                                                            sh(label: 'Building python wheel',
                                                               script:"""python${pythonVersion} -m venv venv
                                                                         trap "rm -rf venv" EXIT
                                                                         ./venv/bin/pip install --disable-pip-version-check uv
                                                                         ./venv/bin/uv build --build-constraints=requirements-dev.txt --index-strategy unsafe-best-match --python ${pythonVersion} --wheel
                                                                         auditwheel repair ./dist/*.whl -w ./dist
                                                                         """
                                                               )
                                                       }
                                                    } catch(e) {
                                                        sh "python${pythonVersion} -m pip list"
                                                        throw e
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
                                                        stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux - ${arch} - wheel"
                                                        wheelStashes << "python${pythonVersion} linux - ${arch} - wheel"
                                                        archiveArtifacts artifacts: 'dist/*.whl'
                                                    }
                                                ]
                                            )
                                        }
                                        if(testPackages == true){
                                            stage("Test Wheel (${pythonVersion} Linux ${arch})"){
                                                retry(3){
                                                    node("docker && linux && ${arch}"){
                                                        checkout scm
                                                        unstash "python${pythonVersion} linux - ${arch} - wheel"
                                                        try{
                                                            withEnv([
                                                                'PIP_CACHE_DIR=/tmp/pipcache',
                                                                'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                'UV_TOOL_DIR=/tmp/uvtools',
                                                                'UV_PYTHON_INSTALL_DIR=/tmp/uvpython',
                                                                'UV_CACHE_DIR=/tmp/uvcache',
                                                                "TOX_INSTALL_PKG=${findFiles(glob:'dist/*.whl')[0].path}",
                                                                "TOX_ENV=py${pythonVersion.replace('.', '')}"
                                                            ]){
                                                                docker.image('python').inside{
                                                                    timeout(60){
                                                                        sh(
                                                                            label: 'Testing with tox',
                                                                            script: '''python3 -m venv venv
                                                                                       . ./venv/bin/activate
                                                                                       trap "rm -rf venv" EXIT
                                                                                       pip install --disable-pip-version-check uv
                                                                                       uvx --constraint=requirements-dev.txt --with tox-uv tox
                                                                                       rm -rf .tox
                                                                                    '''
                                                                        )
                                                                    }
                                                                }
                                                            }
                                                        } finally {
                                                            cleanWs(
                                                                patterns: [
                                                                    [pattern: '.tox/', type: 'INCLUDE'],
                                                                    [pattern: 'dist/', type: 'INCLUDE'],
                                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                    ]
                                                            )
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    } else {
                                        Utils.markStageSkippedForConditional(newStageName)
                                    }
                                }
                            }
                        ]
                    })
                }
            }
        ]
    })
}

def mac_wheels(pythonVersions, testPackages, params, wheelStashes){
    def selectedArches = []
    def allValidArches = ['arm64', 'x86_64']
    if(params.INCLUDE_MACOS_X86_64 == true){
        selectedArches << 'x86_64'
    }
    if(params.INCLUDE_MACOS_ARM == true){
        selectedArches << 'arm64'
    }

    parallel([failFast: true] << pythonVersions.collectEntries{ pythonVersion ->
        [
            "Python ${pythonVersion} - Mac":{
                stage("Python ${pythonVersion} - Mac"){
                    stage("Single arch wheels for Python ${pythonVersion}"){
                        parallel([failFast: true] << allValidArches.collectEntries{arch ->
                            def newWheelStage = "MacOS - Python ${pythonVersion} - ${arch}: wheel"
                            return [
                                "${newWheelStage}": {
                                    stage(newWheelStage){
                                        if(selectedArches.contains(arch)){
                                            stage("Build Wheel (${pythonVersion} MacOS ${arch})"){
                                                buildPythonPkg(
                                                    agent: [
                                                        label: "mac && python${pythonVersion} && ${arch}",
                                                    ],
                                                    retries: 3,
                                                    buildCmd: {
                                                        timeout(60){
                                                            sh(label: 'Building wheel',
                                                               script: "contrib/build_mac_wheel.sh . --venv-path=./venv --python-version={pythonVersion}"
                                                           )
                                                        }
                                                    },
                                                    post:[
                                                        cleanup: {
                                                            cleanWs(
                                                                patterns: [
                                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                                    ],
                                                                notFailBuild: true,
                                                                deleteDirs: true
                                                            )
                                                        },
                                                        success: {
                                                            stash includes: 'dist/*.whl', name: "python${pythonVersion} mac ${arch} wheel"
                                                            wheelStashes << "python${pythonVersion} mac ${arch} wheel"
                                                            archiveArtifacts artifacts: 'dist/*.whl'
                                                        }
                                                    ]
                                                )
                                            }
                                            if(testPackages == true){
                                                stage("Test Wheel (${pythonVersion} MacOS ${arch})"){
                                                    testPythonPkg(
                                                        agent: [
                                                            label: "mac && python${pythonVersion} && ${arch}",
                                                        ],
                                                        testSetup: {
                                                            checkout scm
                                                            unstash "python${pythonVersion} mac ${arch} wheel"
                                                        },
                                                        retries: 3,
                                                        testCommand: {
                                                            findFiles(glob: 'dist/*.whl').each{
                                                                timeout(60){
                                                                    sh(label: 'Running Tox',
                                                                       script: """python${pythonVersion} -m venv venv
                                                                       ./venv/bin/python -m pip install --disable-pip-version-check --upgrade pip
                                                                       ./venv/bin/pip install --disable-pip-version-check -r requirements-dev.txt
                                                                       ./venv/bin/tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
                                                                    )
                                                                }
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
                                                            }
                                                        ]
                                                    )
                                                }
                                            }
                                        } else {
                                            Utils.markStageSkippedForConditional(newWheelStage)
                                        }
                                    }
                                }
                            ]
                        }
                        )
                    }
                    if(params.INCLUDE_MACOS_X86_64 && params.INCLUDE_MACOS_ARM){
                        stage("Universal2 Wheel: Python ${pythonVersion}"){
                            stage('Make Universal2 wheel'){
                                retry(3){
                                    node("mac && python${pythonVersion}") {
                                        checkout scm
                                        unstash "python${pythonVersion} mac arm64 wheel"
                                        unstash "python${pythonVersion} mac x86_64 wheel"
                                        def wheelNames = []
                                        findFiles(excludes: '', glob: 'dist/*.whl').each{wheelFile ->
                                            wheelNames.add(wheelFile.path)
                                        }
                                        try{
                                            sh(label: 'Make Universal2 wheel',
                                               script: """python${pythonVersion} -m venv venv
                                                          . ./venv/bin/activate
                                                          pip install --disable-pip-version-check --upgrade pip
                                                          pip install --disable-pip-version-check wheel delocate
                                                          mkdir -p out
                                                          delocate-merge  ${wheelNames.join(' ')} --verbose -w ./out/
                                                          rm dist/*.whl
                                                           """
                                               )
                                           def fusedWheel = findFiles(excludes: '', glob: 'out/*.whl')[0]
                                           def props = readTOML( file: 'pyproject.toml')['project']
                                           def universalWheel = "py3exiv2bind-${props.version}-cp${pythonVersion.replace('.','')}-cp${pythonVersion.replace('.','')}-macosx_11_0_universal2.whl"
                                           sh "mv ${fusedWheel.path} ./dist/${universalWheel}"
                                           stash includes: 'dist/*.whl', name: "python${pythonVersion} mac-universal2 wheel"
                                           wheelStashes << "python${pythonVersion} mac-universal2 wheel"
                                           archiveArtifacts artifacts: 'dist/*.whl'
                                        } finally {
                                            cleanWs(
                                                patterns: [
                                                        [pattern: 'out/', type: 'INCLUDE'],
                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                       }
                                    }
                                }
                            }
                            if(testPackages == true){
                                stage("Test universal2 Wheel"){
                                    def archStages = [:]
                                    ['x86_64', 'arm64'].each{arch ->
                                        archStages["Test Python ${pythonVersion} universal2 Wheel on ${arch} mac"] = {
                                            testPythonPkg(
                                                agent: [
                                                    label: "mac && python${pythonVersion} && ${arch}",
                                                ],
                                                testSetup: {
                                                    checkout scm
                                                    unstash "python${pythonVersion} mac-universal2 wheel"
                                                },
                                                retries: 3,
                                                testCommand: {
                                                    findFiles(glob: 'dist/*.whl').each{
                                                        withEnv(['UV_INDEX_STRATEGY=unsafe-best-match']){
                                                            sh(label: 'Running Tox',
                                                               script: """python${pythonVersion} -m venv venv
                                                                          trap "rm -rf venv" EXIT
                                                                          ./venv/bin/python -m pip install --disable-pip-version-check uv
                                                                          trap "rm -rf venv && rm -rf .tox" EXIT
                                                                          ./venv/bin/uvx --python=${pythonVersion} --constraint=requirements-dev.txt --with tox-uv tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                       """
                                                            )
                                                        }
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
                                    }
                                    parallel(archStages)
                                }
                            }
                        }
                    }
                }
            }
        ]}
    )
}
def get_sonarqube_unresolved_issues(report_task_file){
    script{

        def props = readProperties  file: '.scannerwork/report-task.txt'
        def response = httpRequest url : props['serverUrl'] + '/api/issues/search?componentKeys=' + props['projectKey'] + '&resolved=no'
        def outstandingIssues = readJSON text: response.content
        return outstandingIssues
    }
}

// *****************************************************************************
stage('Pipeline Pre-tasks'){
    startup()
}
pipeline {
    agent none
    parameters {
        booleanParam(name: 'TEST_RUN_TOX', defaultValue: false, description: 'Run Tox Tests')
        booleanParam(name: 'RUN_CHECKS', defaultValue: true, description: 'Run checks on code')
        booleanParam(name: 'RUN_MEMCHECK', defaultValue: false, description: 'Run Memcheck. NOTE: This can be very slow.')
        booleanParam(name: 'USE_SONARQUBE', defaultValue: true, description: 'Send data test data to SonarQube')
        credentials(name: 'SONARCLOUD_TOKEN', credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl', defaultValue: 'sonarcloud_token', required: false)
        booleanParam(name: 'BUILD_PACKAGES', defaultValue: false, description: 'Build Python packages')
        booleanParam(name: 'INCLUDE_MACOS_ARM', defaultValue: false, description: 'Include ARM(m1) architecture for Mac')
        booleanParam(name: 'INCLUDE_MACOS_X86_64', defaultValue: false, description: 'Include x86_64 architecture for Mac')
        booleanParam(name: 'INCLUDE_LINUX_ARM', defaultValue: false, description: 'Include ARM architecture for Linux')
        booleanParam(name: 'INCLUDE_LINUX_X86_64', defaultValue: true, description: 'Include x86_64 architecture for Linux')
        booleanParam(name: 'INCLUDE_WINDOWS_X86_64', defaultValue: true, description: 'Include x86_64 architecture for Windows')
        booleanParam(name: 'TEST_PACKAGES', defaultValue: true, description: 'Test Python packages by installing them and running tests on the installed package')
        booleanParam(name: 'DEPLOY_PYPI', defaultValue: false, description: 'Deploy to pypi')
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: 'Update online documentation')
    }
    stages {
        stage('Building and Testing'){
            when{
                anyOf{
                    equals expected: true, actual: params.RUN_CHECKS
                    equals expected: true, actual: params.TEST_RUN_TOX
                }
            }
            stages{
                stage('Building and Testing'){
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL'
                            args '--mount source=sonar-cache-py3exiv2bind,target=/opt/sonar/.sonar/cache'
                        }
                    }
                    environment{
                        PIP_CACHE_DIR='/tmp/pipcache'
                        UV_INDEX_STRATEGY='unsafe-best-match'
                        UV_TOOL_DIR='/tmp/uvtools'
                        UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                        UV_CACHE_DIR='/tmp/uvcache'
                    }
                    options{
                        retry(3)
                    }
                    stages{
                        stage('Setup'){
                            stages{
                                stage('Setup Testing Environment'){
                                    steps{
                                        sh(
                                            label: 'Create virtual environment',
                                            script: '''python3 -m venv bootstrap_uv
                                                       bootstrap_uv/bin/pip install --disable-pip-version-check uv
                                                       bootstrap_uv/bin/uv venv venv
                                                       . ./venv/bin/activate
                                                       bootstrap_uv/bin/uv pip install --index-strategy unsafe-best-match uv
                                                       rm -rf bootstrap_uv
                                                       uv pip install --index-strategy unsafe-best-match -r requirements-dev.txt
                                                       '''
                                       )
                                    }
                                }
                                stage('Installing project as editable module'){
                                    steps{
                                        sh(label: 'Building debug build with coverage data',
                                           script: '''mkdir -p build/build_wrapper_output_directory
                                                      . ./venv/bin/activate
                                                      CFLAGS="--coverage -fprofile-arcs -ftest-coverage" LFLAGS="-lgcov --coverage" build-wrapper-linux --out-dir build/build_wrapper_output_directory uv pip install --verbose -e .
                                                   '''
                                       )
                                    }
                                }
                            }
                        }
                        stage('Building Documentation'){
                            steps {
                                catchError(buildResult: 'UNSTABLE', message: 'Building Sphinx documentation has issues', stageResult: 'UNSTABLE') {
                                    sh(label: 'Running Sphinx',
                                        script: '''. ./venv/bin/activate
                                                   sphinx-build -b html docs/source build/docs/html -d build/docs/doctrees -v -w logs/build_sphinx.log -W --keep-going
                                                '''
                                    )
                                }
                            }
                            post{
                                always {
                                    recordIssues(tools: [sphinxBuild(name: 'Sphinx Documentation Build', pattern: 'logs/build_sphinx.log', id: 'sphinx_build')])
                                }
                                success{
                                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                                    script{
                                        def props = readTOML( file: 'pyproject.toml')['project']
                                        zip archive: true, dir: 'build/docs/html', glob: '', zipFile: "dist/${props.name}-${props.version}.doc.zip"
                                    }
                                    stash includes: 'dist/*.doc.zip,build/docs/html/**', name: 'DOCS_ARCHIVE'
                                }
                            }
                        }
                        stage('Code Quality') {
                            when{
                                equals expected: true, actual: params.RUN_CHECKS
                            }
                            stages{
                                stage('Building C++ Tests with coverage data'){
                                    steps{
                                        tee('logs/cmake-build.log'){
                                            sh(label: 'Building C++ Code',
                                               script: '''. ./venv/bin/activate
                                                          conan install . -if build/cpp/
                                                          cmake -B build/cpp/ -Wdev -DCMAKE_TOOLCHAIN_FILE=build/cpp/conan_paths.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -Dpyexiv2bind_generate_python_bindings:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra" -DCMAKE_BUILD_TYPE=Debug
                                                          '''
                                            )
                                        }
                                        sh '''. ./venv/bin/activate
                                              mkdir -p build/build_wrapper_output_directory
                                              build-wrapper-linux --out-dir build/build_wrapper_output_directory cmake --build build/cpp -j $(grep -c ^processor /proc/cpuinfo) --target all
                                           '''
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
                                stage('Running Tests'){
                                    parallel {
                                        stage('Clang Tidy Analysis') {
                                            steps{
                                                tee('logs/clang-tidy.log') {
                                                    catchError(buildResult: 'SUCCESS', message: 'Clang-Tidy found issues', stageResult: 'UNSTABLE') {
                                                        sh(label: 'Run Clang Tidy', script: 'run-clang-tidy -clang-tidy-binary clang-tidy -p ./build/cpp/ src/py3exiv2bind/')
                                                    }
                                                }
                                            }
                                            post{
                                                always {
                                                    recordIssues(
                                                        tools: [clangTidy(pattern: 'logs/clang-tidy.log')]
                                                    )
                                                }
                                            }
                                        }
                                        stage('Task Scanner'){
                                            steps{
                                                recordIssues(tools: [taskScanner(highTags: 'FIXME', includePattern: 'src/py3exiv2bind/**/*.py, src/py3exiv2bind/**/*.cpp, src/py3exiv2bind/**/*.h', normalTags: 'TODO')])
                                            }
                                        }
                                        stage('Memcheck'){
                                            when{
                                                equals expected: true, actual: params.RUN_MEMCHECK
                                            }
                                            steps{
                                                generate_ctest_memtest_script('memcheck.cmake')
                                                timeout(30){
                                                    sh( label: 'Running memcheck',
                                                        script: '''. ./venv/bin/activate
                                                                   ctest -S memcheck.cmake --verbose -j $(grep -c ^processor /proc/cpuinfo)
                                                                '''
                                                        )
                                                }
                                            }
                                            post{
                                                always{
                                                    recordIssues(
                                                        filters: [
                                                            excludeFile('build/cpp/_deps/*'),
                                                        ],
                                                        tools: [
                                                            drMemory(pattern: 'build/cpp/Testing/Temporary/DrMemory/**/results.txt')
                                                            ]
                                                    )
                                                }
                                            }
                                        }
                                        stage('CPP Check'){
                                            steps{
                                                catchError(buildResult: 'SUCCESS', message: 'cppcheck found issues', stageResult: 'UNSTABLE') {
                                                    sh(label: 'Running cppcheck',
                                                       script: 'cppcheck --error-exitcode=1 --project=build/cpp/compile_commands.json -i_deps --enable=all --suppressions-list=cppcheck_suppression_file.txt -rp=$PWD/build/cpp  --xml --output-file=logs/cppcheck_debug.xml'
                                                       )
                                                }
                                            }
                                            post{
                                                always {
                                                    recordIssues(
                                                        filters: [
                                                            excludeType('unmatchedSuppression'),
                                                            excludeType('missingIncludeSystem'),
                                                            excludeFile('catch.hpp'),
                                                            excludeFile('value.hpp'),
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
                                                   script: '''. ./venv/bin/activate
                                                              cd build/cpp
                                                              ctest --output-on-failure --no-compress-output -T Test
                                                           '''
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
                                                sh '''. ./venv/bin/activate
                                                      coverage run --parallel-mode --source=src/py3exiv2bind -m sphinx docs/source reports/doctest -b doctest -d build/docs/.doctrees --no-color -w logs/doctest_warnings.log
                                                   '''
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
                                                       script: '''. ./venv/bin/activate
                                                                  mypy -p py3exiv2bind --html-report reports/mypy/html
                                                               '''
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
                                                                   . ./venv/bin/activate
                                                                   PYLINTHOME=. pylint src/py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                                   ''',
                                                        label: 'Running pylint'
                                                    )
                                                }
                                                sh(
                                                    label: 'Running pylint for sonarqube',
                                                    script: '''. ./venv/bin/activate
                                                               PYLINTHOME=. pylint  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt
                                                           ''',
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
                                            sh(
                                                returnStatus: true,
                                                script: '''. ./venv/bin/activate
                                                           flake8 src/py3exiv2bind --tee --output-file ./logs/flake8.log
                                                        '''
                                                )
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
                                                sh '''. ./venv/bin/activate
                                                      coverage run --parallel-mode --source=src/py3exiv2bind -m pytest --junitxml=./reports/pytest/junit-pytest.xml
                                                   '''
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
                                                  . ./venv/bin/activate
                                                  coverage combine
                                                  coverage xml -o ./reports/coverage/coverage-python.xml
                                                  gcovr --root . --filter src/py3exiv2bind --exclude-directories build/cpp/_deps/libcatch2-build --exclude-directories build/python/temp/conan_cache --exclude-throw-branches --exclude-unreachable-branches --print-summary --keep --json -o reports/coverage/coverage-c-extension.json
                                                  gcovr --root . --filter src/py3exiv2bind --exclude-directories build/cpp/_deps/libcatch2-build --exclude-throw-branches --exclude-unreachable-branches --print-summary --keep --json -o reports/coverage/coverage_cpp.json
                                                  gcovr --add-tracefile reports/coverage/coverage-c-extension.json --add-tracefile reports/coverage/coverage_cpp.json --keep --print-summary --xml -o reports/coverage/coverage_cpp.xml --sonarqube -o reports/coverage/coverage_cpp_sonar.xml
                                                  '''
                                          )
                                    recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'reports/coverage/*.xml']])
                                }
                            }
                        }
                        stage('Sonarcloud Analysis'){
                            options{
                                lock('py3exiv2bind-sonarcloud')
                            }
                            environment{
                                SONAR_USER_HOME = '/tmp/sonar'
                            }
                            when{
                                allOf{
                                    equals expected: true, actual: params.USE_SONARQUBE
                                    expression{
                                        try{
                                            withCredentials([string(credentialsId: params.SONARCLOUD_TOKEN, variable: 'dddd')]) {
                                                echo 'Found credentials for sonarqube'
                                            }
                                        } catch(e){
                                            return false
                                        }
                                        return true
                                    }
                                }
                            }
                            steps{
                                script{
                                    withSonarQubeEnv(installationName:'sonarcloud', credentialsId: params.SONARCLOUD_TOKEN) {
                                        if (env.CHANGE_ID){
                                            sh(
                                                label: 'Running Sonar Scanner',
                                                script: """. ./venv/bin/activate
                                                           uvx pysonar-scanner -Dsonar.projectVersion=\$VERSION -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory
                                                        """
                                                )
                                        } else {
                                            sh(
                                                label: 'Running Sonar Scanner',
                                                script: """. ./venv/bin/activate
                                                           uvx pysonar-scanner -Dsonar.projectVersion=\$VERSION -Dsonar.buildString=\"${env.BUILD_TAG}\" -Dsonar.branch.name=${env.BRANCH_NAME} -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=\$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.build-wrapper-output=build/build_wrapper_output_directory
                                                        """
                                                )
                                        }
                                    }
                                    timeout(time: 1, unit: 'HOURS') {
                                         def sonarqube_result = waitForQualityGate(abortPipeline: false)
                                         if (sonarqube_result.status != 'OK') {
                                             unstable "SonarQube quality gate: ${sonarqube_result.status}"
                                         }
                                         def outstandingIssues = get_sonarqube_unresolved_issues('.scannerwork/report-task.txt')
                                         writeJSON file: 'reports/sonar-report.json', json: outstandingIssues
                                    }
                                }
                            }
                            post {
                                always{
                                    milestone 1
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
                                        [pattern: 'venv/', type: 'INCLUDE'],
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
                    parallel{
                        stage('Linux'){
                            environment{
                                PIP_CACHE_DIR='/tmp/pipcache'
                                UV_INDEX_STRATEGY='unsafe-best-match'
                                UV_TOOL_DIR='/tmp/uvtools'
                                UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                                UV_CACHE_DIR='/tmp/uvcache'
                            }
                            when{
                                expression {return nodesByLabel('linux && docker').size() > 0}
                            }
                            steps{
                                script{
                                    def envs = []
                                    node('docker && linux'){
                                        docker.image('python').inside{
                                            try{
                                                checkout scm
                                                sh(script: 'python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv')
                                                envs = sh(
                                                    label: 'Get tox environments',
                                                    script: './venv/bin/uvx --quiet --constraint=requirements-dev.txt --with tox-uv tox list -d --no-desc',
                                                    returnStdout: true,
                                                ).trim().split('\n')
                                            } finally{
                                                cleanWs(
                                                    patterns: [
                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                        [pattern: '.tox', type: 'INCLUDE'],
                                                        [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                    ]
                                                )
                                            }
                                        }
                                    }
                                    parallel(
                                        envs.collectEntries{toxEnv ->
                                            def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                            [
                                                "Tox Environment: ${toxEnv}",
                                                {
                                                    node('docker && linux'){
                                                        def maxRetries = 3
                                                        checkout scm
                                                        def image
                                                        lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                            retry(maxRetries){
                                                                image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .')
                                                            }
                                                        }
                                                        try{
                                                            image.inside{
                                                                retry(maxRetries){
                                                                    try{
                                                                        sh( label: 'Running Tox',
                                                                            script: """python3 -m venv /tmp/venv && /tmp/venv/bin/pip install --disable-pip-version-check uv
                                                                                       . /tmp/venv/bin/activate
                                                                                       uvx -p ${version} --constraint=requirements-dev.txt --with tox-uv tox run -e ${toxEnv} -vvv
                                                                                    """
                                                                            )
                                                                    } catch(e) {
                                                                        sh(script: '''. ./venv/bin/activate
                                                                              uv python list
                                                                              '''
                                                                                )
                                                                        throw e
                                                                    } finally{
                                                                        cleanWs(
                                                                            patterns: [
                                                                                [pattern: 'venv/', type: 'INCLUDE'],
                                                                                [pattern: '.tox', type: 'INCLUDE'],
                                                                                [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                            ]
                                                                        )
                                                                    }
                                                                }
                                                            }
                                                        } finally {
                                                            sh "docker rmi ${image.id}"
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    )
                                }
                            }
                        }
                        stage('Windows'){
                             when{
                                 expression {return nodesByLabel('windows && docker && x86').size() > 0}
                             }
                             environment{
                                 UV_INDEX_STRATEGY='unsafe-best-match'
                                 PIP_CACHE_DIR='C:\\Users\\ContainerUser\\Documents\\pipcache'
                                 UV_TOOL_DIR='C:\\Users\\ContainerUser\\Documents\\uvtools'
                                 UV_PYTHON_INSTALL_DIR='C:\\Users\\ContainerUser\\Documents\\uvpython'
                                 UV_CACHE_DIR='C:\\Users\\ContainerUser\\Documents\\uvcache'
                             }
                             steps{
                                 script{
                                     def envs = []
                                     node('docker && windows'){
                                         docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python').inside("--mount source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR}"){
                                             try{
                                                 checkout scm
                                                 bat(script: 'python -m venv venv && venv\\Scripts\\pip install --disable-pip-version-check uv')
                                                 envs = bat(
                                                     label: 'Get tox environments',
                                                     script: '@.\\venv\\Scripts\\uvx --quiet --constraint=requirements-dev.txt --with-requirements requirements-dev.txt --with tox-uv tox list -d --no-desc',
                                                     returnStdout: true,
                                                 ).trim().split('\r\n')
                                             } finally{
                                                 cleanWs(
                                                     patterns: [
                                                         [pattern: 'venv/', type: 'INCLUDE'],
                                                         [pattern: '.tox', type: 'INCLUDE'],
                                                         [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                     ]
                                                 )
                                             }
                                         }
                                     }
                                     parallel(
                                         envs.collectEntries{toxEnv ->
                                             def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                             [
                                                 "Tox Environment: ${toxEnv}",
                                                 {
                                                     node('docker && windows'){
                                                        def maxRetries = 3
                                                        def image
                                                        checkout scm
                                                        lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                            retry(maxRetries){
                                                                image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/windows/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE' + (env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE ? " --build-arg FROM_IMAGE=${env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE} ": ' ') + '.')
                                                            }
                                                        }
                                                        try{
                                                            retry(maxRetries){
                                                                try{
                                                                    checkout scm
                                                                    image.inside("--mount source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR}"){
                                                                        bat(label: 'Running Tox',
                                                                            script: """CALL C:\\BuildTools\\Common7\\Tools\\VsDevCmd.bat -arch=amd64
                                                                                       uv python install cpython-${version}
                                                                                       uvx -p ${version} --constraint=requirements-dev.txt --with tox-uv tox run -e ${toxEnv} --workdir %WORKSPACE_TMP%\\.tox
                                                                                    """
                                                                        )
                                                                    }
                                                                } finally {
                                                                    bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                                }
                                                            }
                                                        } finally{
                                                            bat "docker rmi --force --no-prune ${image.id}"
                                                        }
                                                     }
                                                 }
                                             ]
                                         }
                                     )
                                 }
                             }
                        }
                    }
                }
            }
        }
        stage('Python Packaging'){
            when{
                anyOf{
                    equals expected: true, actual: params.BUILD_PACKAGES
                }
            }
            failFast true
            parallel{
                stage('Platform Wheels: Mac'){
                    when {
                        anyOf {
                            equals expected: true, actual: params.INCLUDE_MACOS_X86_64
                            equals expected: true, actual: params.INCLUDE_MACOS_ARM
                        }
                    }
                    steps{
                        mac_wheels(SUPPORTED_MAC_VERSIONS, params.TEST_PACKAGES, params, wheelStashes)
                    }
                }
                stage('Platform Wheels: Windows'){
                    when {
                        equals expected: true, actual: params.INCLUDE_WINDOWS_X86_64
                    }
                    steps{
                        windows_wheels(SUPPORTED_WINDOWS_VERSIONS, params.TEST_PACKAGES, params, wheelStashes)
                    }
                }
                stage('Platform Wheels: Linux'){
                    when {
                        anyOf {
                            equals expected: true, actual: params.INCLUDE_LINUX_X86_64
                            equals expected: true, actual: params.INCLUDE_LINUX_ARM
                        }
                    }
                    steps{
                        linux_wheels(SUPPORTED_LINUX_VERSIONS, params.TEST_PACKAGES, params, wheelStashes)
                    }
                }
                stage('Source Distribution'){
                    stages{
                        stage('Build sdist'){
                            agent {
                                docker{
                                    image 'python'
                                    label 'linux && docker'
                                  }
                            }
                            environment{
                                PIP_CACHE_DIR='/tmp/pipcache'
                                UV_INDEX_STRATEGY='unsafe-best-match'
                                UV_CACHE_DIR='/tmp/uvcache'
                            }
                            options {
                                retry(3)
                            }
                            steps{
                                script{
                                    try{
                                        timeout(60){
                                            sh(
                                                label: 'Package',
                                                script: '''python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv
                                                           trap "rm -rf venv" EXIT
                                                           venv/bin/uv build --build-constraints=requirements-dev.txt --sdist
                                                        '''
                                            )
                                        }
                                        stash includes: 'dist/*.tar.gz,dist/*.zip', name: 'sdist'
                                        archiveArtifacts artifacts: 'dist/*.tar.gz,dist/*.zip'
                                        script{
                                            wheelStashes << 'sdist'
                                        }
                                    } finally {
                                        cleanWs(
                                            patterns: [
                                                [pattern: 'venv/', type: 'INCLUDE'],
                                                [pattern: 'dist/', type: 'INCLUDE'],
                                            ],
                                            notFailBuild: true,
                                            deleteDirs: true
                                        )
                                    }
                                }
                            }
                        }
                        stage('Test sdist'){
                            when{
                                equals expected: true, actual: params.TEST_PACKAGES
                            }
                            steps{
                                script{
                                    def testSdistStages = [
                                        failFast: true
                                    ]
                                    testSdistStages << SUPPORTED_MAC_VERSIONS.collectEntries{ pythonVersion ->
                                        def selectedArches = []
                                        def allValidArches = ["x86_64", "arm64"]
                                        if(params.INCLUDE_MACOS_X86_64 == true){
                                            selectedArches << "x86_64"
                                        }
                                        if(params.INCLUDE_MACOS_ARM == true){
                                            selectedArches << "arm64"
                                        }
                                        return allValidArches.collectEntries{ arch ->
                                            def newStageName = "Test sdist (MacOS ${arch} - Python ${pythonVersion})"
                                            return [
                                                "${newStageName}": {
                                                    if(selectedArches.contains(arch)){
                                                        stage(newStageName){
                                                            node("mac && python${pythonVersion} && ${arch}"){
                                                                checkout scm
                                                                unstash 'sdist'
                                                                findFiles(glob: 'dist/*.tar.gz').each{
                                                                    retry(3){
                                                                        try{
                                                                            withEnv(["UV_INDEX_STRATEGY=unsafe-best-match"]){
                                                                                timeout(60){
                                                                                    sh(label: 'Running Tox',
                                                                                       script: """python${pythonVersion} -m venv venv
                                                                                                  trap "rm -rf venv" EXIT
                                                                                                  ./venv/bin/python -m pip install --disable-pip-version-check uv
                                                                                                  trap "rm -rf venv && rm -rf .tox" EXIT
                                                                                                  ./venv/bin/uvx --python=${pythonVersion} --constraint=requirements-dev.txt --with tox-uv tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                                           """
                                                                                    )
                                                                                }
                                                                            }
                                                                        }finally{
                                                                            cleanWs(
                                                                                patterns: [
                                                                                        [pattern: 'dist/', type: 'INCLUDE'],
                                                                                        [pattern: 'venv/', type: 'INCLUDE'],
                                                                                        [pattern: '.tox/', type: 'INCLUDE'],
                                                                                    ],
                                                                                notFailBuild: true,
                                                                                deleteDirs: true
                                                                            )
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    } else {
                                                        Utils.markStageSkippedForConditional(newStageName)
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                    testSdistStages << SUPPORTED_WINDOWS_VERSIONS.collectEntries{ pythonVersion ->
                                        def selectedArches = []
                                        def allValidArches = ["x86_64"]
                                        if(params.INCLUDE_WINDOWS_X86_64 == true){
                                            selectedArches << "x86_64"
                                        }
                                        return allValidArches.collectEntries{ arch ->
                                            def newStageName = "Test sdist (Windows ${arch} - Python ${pythonVersion})"
                                            return [
                                                "${newStageName}": {
                                                    if(selectedArches.contains(arch)){
                                                        stage(newStageName){
                                                            node('docker && windows'){
                                                                def image
                                                                checkout scm
                                                                lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                                    image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/windows/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE' + (env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE ? " --build-arg FROM_IMAGE=${env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE} ": ' ') + '.')
                                                                }
                                                                try{
                                                                    image.inside('--mount source=uv_python_install_dir,target=C:\\Users\\ContainerUser\\Documents\\uvpython'){
                                                                        checkout scm
                                                                        unstash 'sdist'
                                                                        findFiles(glob: 'dist/*.tar.gz').each{
                                                                            timeout(60){
                                                                                withEnv([
                                                                                    'PIP_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\pipcache',
                                                                                    'UV_TOOL_DIR=C:\\Users\\ContainerUser\\Documents\\uvtools',
                                                                                    'UV_PYTHON_INSTALL_DIR=C:\\Users\\ContainerUser\\Documents\\uvpython',
                                                                                    'UV_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\uvcache',
                                                                                    'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                                ]){
                                                                                    try{
                                                                                        retry(3){
                                                                                            timeout(60){
                                                                                                bat(label: 'Running Tox',
                                                                                                    script: """uvx --python ${pythonVersion} --constraint=requirements-dev.txt --with tox-uv tox run  --runner=uv-venv-runner --installpkg ${it.path} -e py${pythonVersion.replace('.', '')} -v
                                                                                                               rmdir /S /Q .tox
                                                                                                            """
                                                                                                )
                                                                                            }
                                                                                        }
                                                                                    } finally {
                                                                                        cleanWs(
                                                                                            patterns: [
                                                                                                    [pattern: '.tox/', type: 'INCLUDE'],
                                                                                                    [pattern: 'venv/', type: 'INCLUDE'],
                                                                                                    [pattern: 'dist/', type: 'INCLUDE'],
                                                                                                    [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                                                ],
                                                                                            notFailBuild: true,
                                                                                            deleteDirs: true
                                                                                        )
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                } finally {
                                                                    bat "docker rmi --no-prune ${image.id}"
                                                                }
                                                            }
                                                        }
                                                    } else {
                                                        Utils.markStageSkippedForConditional(newStageName)
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                    testSdistStages << SUPPORTED_LINUX_VERSIONS.collectEntries{ pythonVersion ->
                                        def selectedArches = []
                                        def allValidArches = ["x86_64", "arm64"]
                                        if(params.INCLUDE_LINUX_X86_64 == true){
                                            selectedArches << 'x86_64'
                                        }
                                        if(params.INCLUDE_LINUX_ARM == true){
                                            selectedArches << 'arm64'
                                        }
                                        return allValidArches.collectEntries{ arch ->
                                            def newStageName = "Test sdist (Linux ${arch} - Python ${pythonVersion})"
                                            return [
                                                "${newStageName}": {
                                                    if(selectedArches.contains(arch)){
                                                        stage(newStageName){
                                                            testPythonPkg(
                                                                agent: [
                                                                    dockerfile: [
                                                                        label: "linux && docker && ${arch}",
                                                                        filename: 'ci/docker/linux/tox/Dockerfile',
                                                                        additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                                    ]
                                                                ],
                                                                retries: 3,
                                                                testSetup: {
                                                                    checkout scm
                                                                    unstash 'sdist'
                                                                },
                                                                testCommand: {
                                                                    findFiles(glob: 'dist/*.tar.gz').each{
                                                                        withEnv([
                                                                            'PIP_CACHE_DIR=/tmp/pipcache',
                                                                            'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                            'UV_TOOL_DIR=/tmp/uvtools',
                                                                            'UV_PYTHON_INSTALL_DIR=/tmp/uvpython',
                                                                            'UV_CACHE_DIR=/tmp/uvcache',
                                                                        ]){
                                                                            timeout(60){
                                                                                sh(
                                                                                    label: 'Running Tox',
                                                                                    script: """python3 -m venv venv
                                                                                               trap "rm -rf ./venv" EXIT
                                                                                               venv/bin/pip install --disable-pip-version-check uv
                                                                                               venv/bin/uvx --python ${pythonVersion} --constraint=requirements-dev.txt --with tox-uv tox --runner=uv-venv-runner --installpkg ${it.path} --workdir /tmp/tox -e py${pythonVersion.replace('.', '')}
                                                                                            """
                                                                                )
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                post:[
                                                                    cleanup: {
                                                                        cleanWs(
                                                                            patterns: [
                                                                                    [pattern: 'venv/', type: 'INCLUDE'],
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
                                                    } else {
                                                        Utils.markStageSkippedForConditional(newStageName)
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                    parallel(testSdistStages)
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Deploy'){
            parallel {
                stage('Deploy to pypi') {
                    environment{
                        PIP_CACHE_DIR='/tmp/pipcache'
                        UV_INDEX_STRATEGY='unsafe-best-match'
                        UV_TOOL_DIR='/tmp/uvtools'
                        UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                        UV_CACHE_DIR='/tmp/uvcache'
                    }
                    agent {
                        docker{
                            image 'python'
                            label 'docker && linux'
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
                                choices: getPypiConfig(),
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
                            withEnv(
                                [
                                    "TWINE_REPOSITORY_URL=${SERVER_URL}",
                                    'UV_INDEX_STRATEGY=unsafe-best-match'
                                ]
                            ){
                                withCredentials(
                                    [
                                        usernamePassword(
                                            credentialsId: 'jenkins-nexus',
                                            passwordVariable: 'TWINE_PASSWORD',
                                            usernameVariable: 'TWINE_USERNAME'
                                        )
                                    ]){
                                        sh(
                                            label: 'Uploading to pypi',
                                            script: '''python3 -m venv venv
                                                       trap "rm -rf venv" EXIT
                                                       . ./venv/bin/activate
                                                       pip install --disable-pip-version-check uv
                                                       uvx --constraint=requirements-dev.txt twine upload --disable-progress-bar --non-interactive dist/*
                                                    '''
                                        )
                                }
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
                stage('Deploy Online Documentation') {
                    when{
                        equals expected: true, actual: params.DEPLOY_DOCS
                        beforeAgent true
                        beforeInput true
                    }
                    agent {
                        dockerfile {
                            filename 'ci/docker/python/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                        }
                    }
                    options{
                        timeout(time: 1, unit: 'DAYS')
                    }
                    input {
                        message 'Update project documentation?'
                    }
                    steps{
                        unstash 'DOCS_ARCHIVE'
                        withCredentials([usernamePassword(credentialsId: 'dccdocs-server', passwordVariable: 'docsPassword', usernameVariable: 'docsUsername')]) {
                            sh 'python utilities/upload_docs.py --username=$docsUsername --password=$docsPassword --subroute=py3exiv2bind build/docs/html apache-ns.library.illinois.edu'
                        }
                    }
                    post{
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
            }
        }
    }
}
