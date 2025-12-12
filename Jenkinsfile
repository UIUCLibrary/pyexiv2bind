import org.jenkinsci.plugins.pipeline.modeldefinition.Utils
library identifier: 'JenkinsPythonHelperLibrary@2024.1.2', retriever: modernSCM(
  [$class: 'GitSCMSource',
   remote: 'https://github.com/UIUCLibrary/JenkinsPythonHelperLibrary.git',
   ])

def createUVConfig(){
    if(isUnix()){
        def scriptFile = 'ci/scripts/create_uv_config.sh'
        if(! fileExists(scriptFile)){
            checkout scm
        }
        return sh(label: 'Setting up uv.toml config file', script: "sh ${scriptFile} " + '$UV_INDEX_URL $UV_EXTRA_INDEX_URL', returnStdout: true).trim()
    }
    def scriptFile = "ci\\scripts\\new-uv-global-config.ps1"
    if(! fileExists(scriptFile)){
        checkout scm
    }
    return powershell(
        label: 'Setting up uv.toml config file',
        script: "& ${scriptFile} \$env:UV_INDEX_URL \$env:UV_EXTRA_INDEX_URL",
        returnStdout: true
    ).trim()
}

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
def SUPPORTED_MAC_VERSIONS = ['3.10', '3.11', '3.12', '3.13']
def SUPPORTED_LINUX_VERSIONS = ['3.10', '3.11', '3.12', '3.13']
def SUPPORTED_WINDOWS_VERSIONS = ['3.10', '3.11', '3.12', '3.13']
// ============================================================================
//  Dynamic variables. Used to help manage state
def wheelStashes = []


def startup(){
    node(){
        parallel(
            [
                failFast: true,
//                'Loading Reference Build Information': {
//                    stage('Loading Reference Build Information'){
//                        discoverGitReferenceBuild(latestBuildIfNotFound: true)
//                    }
//                },
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
                                    powershell(label: 'Building Wheel for Windows', script: "scripts/build_windows.ps1 -PythonVersion ${pythonVersion} -DockerImageName ${dockerImageName}")
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
                                checkout scm
                                try{
                                    docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python')
                                        .inside('\
                                            --mount type=volume,source=uv_python_install_dir,target=C:\\Users\\ContainerUser\\Documents\\cache\\uvpython \
                                            --mount type=volume,source=pipcache,target=C:\\Users\\ContainerUser\\Documents\\cache\\pipcache \
                                            --mount type=volume,source=uv_cache_dir,target=C:\\Users\\ContainerUser\\Documents\\cache\\uvcache \
                                            --mount type=volume,source=msvc-runtime,target=c:\\msvc_runtime \
                                            --mount type=volume,source=windows-certs,target=c:\\certs \
                                            '
                                        ){
                                        installMSVCRuntime('c:\\msvc_runtime\\')
                                        unstash "python${pythonVersion} windows wheel"
                                        withEnv([
                                            'PIP_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\cache\\pipcache',
                                            'UV_PYTHON_INSTALL_DIR=C:\\Users\\ContainerUser\\Documents\\cache\\uvpython',
                                            'UV_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\cache\\uvcache',
                                            'UV_TOOL_DIR=C:\\Users\\ContainerUser\\Documents\\uvtools',
                                            'UV_INDEX_STRATEGY=unsafe-best-match',
                                            "UV_CONFIG_FILE=${createUVConfig()}"
                                        ]){
                                            findFiles(glob: 'dist/*.whl').each{
                                                retry(3){
                                                    timeout(60){
                                                        bat(label: 'Running Tox',
                                                            script: """python -m venv venv
                                                                       venv\\Scripts\\pip install --disable-pip-version-check uv
                                                                       venv\\Scripts\\uv run --only-group tox --python ${pythonVersion} --with tox-uv tox run -e py${pythonVersion.replace('.', '')}  --installpkg ${it.path}
                                                                       rmdir /S /Q venv
                                                                       rmdir /S /Q .tox
                                                                    """
                                                        )
                                                    }
                                                }
                                            }
                                        }
                                    }
                                } finally {
                                    bat "${tool(name: 'Default', type: 'git')} clean -dfx"
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
    def allValidArches = ['arm64', 'amd64']
    if(params.INCLUDE_LINUX_ARM == true){
        selectedArches << 'arm64'
    }
    if(params.INCLUDE_LINUX_X86_64 == true){
        selectedArches << 'amd64'
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
                                            node("linux && docker && ${arch}"){
                                                try{
                                                    checkout scm
                                                    withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                        def dockerImageName = "pyexiv2bind_builder-${UUID.randomUUID().toString()}"
                                                        try{
                                                            sh "scripts/build_linux_wheels.sh --python-version ${pythonVersion} --platform linux/${arch} --docker-image-name ${dockerImageName}"
                                                            stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux - ${arch} - wheel"
                                                            wheelStashes << "python${pythonVersion} linux - ${arch} - wheel"
                                                            archiveArtifacts artifacts: 'dist/*.whl'
                                                        } finally {
                                                            sh "docker rmi --force --no-prune ${dockerImageName}"
                                                        }
                                                    }
                                                } finally {
                                                    sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                }
                                            }
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
                                                                "TOX_ENV=py${pythonVersion.replace('.', '')}",
                                                                'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                "UV_CONFIG_FILE=${createUVConfig()}"
                                                            ]){
                                                                docker.image('python').inside('--mount source=python-tmp-py3exiv2bind,target=/tmp'){
                                                                    timeout(60){
                                                                        sh(
                                                                            label: 'Testing with tox',
                                                                            script: '''python3 -m venv venv
                                                                                       . ./venv/bin/activate
                                                                                       trap "rm -rf venv" EXIT
                                                                                       pip install --disable-pip-version-check uv
                                                                                       uv run --only-group tox --with tox-uv tox
                                                                                       rm -rf .tox
                                                                                    '''
                                                                        )
                                                                    }
                                                                }
                                                            }
                                                        } finally {
                                                            sh "${tool(name: 'Default', type: 'git')} clean -dfx"
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
                                                node("mac && python${pythonVersion} && ${arch}"){
                                                    timeout(60){
                                                        checkout scm
                                                        try{
                                                           withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                               sh(label: 'Building wheel',
                                                                  script: """python3 -m venv venv
                                                                             trap "rm -rf venv" EXIT
                                                                             venv/bin/pip install --disable-pip-version-check uv
                                                                             scripts/build_mac_wheel.sh --uv=./venv/bin/uv --python-version=${pythonVersion}
                                                                          """
                                                              )
                                                           }
                                                           stash includes: 'dist/*.whl', name: "python${pythonVersion} mac ${arch} wheel"
                                                           wheelStashes << "python${pythonVersion} mac ${arch} wheel"
                                                           archiveArtifacts artifacts: 'dist/*.whl'
                                                        } finally {
                                                            sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                        }
                                                    }
                                                }
                                            }
                                            if(testPackages == true){
                                                stage("Test Wheel (${pythonVersion} MacOS ${arch})"){
                                                    node("mac && python${pythonVersion} && ${arch}"){
                                                        unstash "python${pythonVersion} mac ${arch} wheel"
                                                        checkout scm
                                                        findFiles(glob: 'dist/*.whl').each{
                                                            try{
                                                                withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                                    timeout(60){
                                                                        sh(label: 'Running Tox',
                                                                           script: """python${pythonVersion} -m venv venv
                                                                           ./venv/bin/python -m pip install --disable-pip-version-check uv
                                                                           ./venv/bin/uv run --only-group tox --with tox-uv tox run --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}"""
                                                                        )
                                                                    }
                                                                }
                                                            } finally {
                                                                sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                            }
                                                        }
                                                    }
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
                                        try{
                                            checkout scm
                                            withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                unstash "python${pythonVersion} mac arm64 wheel"
                                                unstash "python${pythonVersion} mac x86_64 wheel"
                                                def wheelNames = []
                                                findFiles(excludes: '', glob: 'dist/*.whl').each{wheelFile ->
                                                    wheelNames.add(wheelFile.path)
                                                }
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
                                            }
                                        } finally{
                                            sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                        }
                                    }
                                }
                            }
                            if(testPackages == true){
                                stage("Test universal2 Wheel"){
                                    def archStages = [:]
                                    ['x86_64', 'arm64'].each{arch ->
                                        archStages["Test Python ${pythonVersion} universal2 Wheel on ${arch} mac"] = {
                                            stage("Test Python ${pythonVersion} universal2 Wheel on ${arch} mac"){
                                                if(! selectedArches.contains(arch)){
                                                    Utils.markStageSkippedForConditional("Test Python ${pythonVersion} universal2 Wheel on ${arch} mac")
                                                    return
                                                }
                                                node("mac && python${pythonVersion} && ${arch}"){
                                                    try{
                                                        checkout scm
                                                        withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                            unstash "python${pythonVersion} mac-universal2 wheel"
                                                            findFiles(glob: 'dist/*.whl').each{
                                                                sh(label: 'Running Tox',
                                                                   script: """python${pythonVersion} -m venv venv
                                                                              trap "rm -rf venv" EXIT
                                                                              ./venv/bin/python -m pip install --disable-pip-version-check uv
                                                                              trap "rm -rf venv && rm -rf .tox" EXIT
                                                                              ./venv/bin/uv run --only-group tox --python=${pythonVersion} --with tox-uv tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                           """
                                                                )
                                                            }
                                                        }
                                                        archiveArtifacts artifacts: 'dist/*.whl'
                                                    } finally {
                                                        sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                    }
                                                }
                                            }
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
        if(! fileExists(report_task_file)){
            error "Could not find ${report_task_file}"
        }
        def props = readProperties  file: report_task_file
        if(! props['serverUrl'] || ! props['projectKey']){
            error "Could not find serverUrl or projectKey in ${report_task_file}"
        }
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
                            additionalBuildArgs '--build-arg PIP_EXTRA_INDEX_URL --build-arg CONAN_CENTER_PROXY_V2_URL'
                            args '--mount source=sonar-cache-py3exiv2bind,target=/opt/sonar/.sonar/cache --mount source=python-tmp-py3exiv2bind,target=/tmp'
                        }
                    }
                    environment{
                        PIP_CACHE_DIR='/tmp/pipcache'
                        UV_INDEX_STRATEGY='unsafe-best-match'
                        UV_TOOL_DIR='/tmp/uvtools'
                        UV_PYTHON_INSTALL_DIR='/tmp/uvpython'
                        UV_CACHE_DIR='/tmp/uvcache'
                        UV_CONFIG_FILE=createUVConfig()
                    }
                    stages{
                        stage('Setup Testing Environment'){
                            environment{
                                CXXFLAGS='--coverage -fprofile-arcs -ftest-coverage'
                            }
                            steps{
                                sh(
                                     label: 'Create virtual environment',
                                     script: '''mkdir -p build/python
                                                uv sync --group ci --no-install-project
                                                mkdir -p build/temp
                                                mkdir -p build/lib
                                                mkdir -p build/docs
                                                mkdir -p build/python
                                                mkdir -p build/coverage
                                                mkdir -p coverage_data/python_extension
                                                mkdir -p coverage_data/cpp
                                                mkdir -p logs
                                                mkdir -p reports
                                                mkdir -p reports/coverage
                                             '''
                                )
                                sh(
                                    label: 'Install project as editable module with ci dependencies',
                                    script: '''uv pip install "pybind11>=2.13" "uiucprescon.build @ https://github.com/UIUCLibrary/uiucprescon_build/releases/download/v0.4.2/uiucprescon_build-0.4.2-py3-none-any.whl"
                                               mkdir -p build/build_wrapper_output_directory
                                               build-wrapper-linux --out-dir build/build_wrapper_output_directory uv run --no-sync setup.py build_clib build_ext --inplace --build-temp build/temp  --build-lib build/lib --debug -v
                                            '''
                               )
                               cleanWs(
                                   deleteDirs: true,
                                   patterns: [
                                       [pattern: 'build/**/cmake_builds/**/*.gcno', type: 'INCLUDE'],
                                   ]
                               )
                               sh 'find build -name "*.gcno"'
                            }
                        }
                        stage('Building Documentation'){
                            environment{
                                GCOV_PREFIX='build/temp'
                                GCOV_PREFIX_STRIP=5
                            }
                            steps {
                                catchError(buildResult: 'UNSTABLE', message: 'Building Sphinx documentation has issues', stageResult: 'UNSTABLE') {
                                    sh(label: 'Running Sphinx',
                                        script: 'uv run -m sphinx -b html docs/source build/docs/html -d build/docs/doctrees -v -w logs/build_sphinx.log -W --keep-going && find build/temp -name "*.gcda"'
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
                            parallel{
                                stage('Python tests'){
                                    environment{
                                        GCOV_PREFIX='build/temp'
                                        GCOV_PREFIX_STRIP=5
                                    }
                                    steps{
                                        script{
                                            parallel([
                                                failFast: false,
                                                'Run Doctest Tests': {
                                                    try{
                                                        sh 'uv run coverage run --parallel-mode --source=src/py3exiv2bind -m sphinx docs/source reports/doctest -b doctest -d build/docs/.doctrees --no-color -w logs/doctest_warnings.log'
                                                    } finally {
                                                        recordIssues(tools: [sphinxBuild(name: 'Doctest', pattern: 'logs/doctest_warnings.log', id: 'doctest')])
                                                    }
                                                },
                                                'MyPy Static Analysis': {
                                                    try{
                                                        tee('logs/mypy.log'){
                                                            sh(returnStatus: true,
                                                               script: 'uv run mypy -p py3exiv2bind --html-report reports/mypy/html'
                                                              )
                                                        }
                                                    } finally {
                                                        recordIssues(tools: [myPy(name: 'MyPy', pattern: 'logs/mypy.log')])
                                                        publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                                                    }
                                                },
                                                'Run Pylint Static Analysis': {
                                                    try{
                                                        catchError(buildResult: 'SUCCESS', message: 'Pylint found issues', stageResult: 'UNSTABLE') {
                                                            sh(
                                                                script: '''mkdir -p logs
                                                                           mkdir -p reports
                                                                           PYLINTHOME=. uv run pylint src/py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
                                                                           ''',
                                                                label: 'Running pylint'
                                                            )
                                                        }
                                                        sh(
                                                            label: 'Running pylint for sonarqube',
                                                            script: 'PYLINTHOME=. uv run pylint  -r n --msg-template="{path}:{module}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint_issues.txt',
                                                            returnStatus: true
                                                        )
                                                    } finally {
                                                        stash includes: 'reports/pylint_issues.txt,reports/pylint.txt', name: 'PYLINT_REPORT'
                                                        recordIssues(tools: [pyLint(pattern: 'reports/pylint.txt')])
                                                    }
                                                },
                                                'Flake8': {
                                                    try{
                                                        sh(
                                                            returnStatus: true,
                                                            script: 'uv run flake8 src/py3exiv2bind --tee --output-file ./logs/flake8.log'
                                                            )
                                                    } finally {
                                                        stash includes: 'logs/flake8.log', name: 'FLAKE8_REPORT'
                                                        recordIssues(tools: [flake8(name: 'Flake8', pattern: 'logs/flake8.log')])
                                                    }
                                                },
                                                'Running Unit Tests': {
                                                    try{
                                                        sh 'uv run coverage run --parallel-mode --source=src/py3exiv2bind -m pytest --junitxml=./reports/pytest/junit-pytest.xml'
                                                    } finally {
                                                        stash includes: 'reports/pytest/junit-pytest.xml', name: 'PYTEST_REPORT'
                                                        junit 'reports/pytest/junit-pytest.xml'
                                                    }
                                                }
                                            ])
                                        }
                                    }
                                    post {
                                        always{
                                            script{
                                                try{
                                                    sh(label: 'Creating gcovr coverage report',
                                                       script: 'uv run gcovr --root $WORKSPACE --exclude \'\\.venv\' --exclude \'/.*/build/\' --exclude-directories=$WORKSPACE/.venv --exclude-directories=$WORKSPACE/build/cpp --exclude-directories=$WORKSPACE/build/temp/cmake_builds/exiv2/_deps --print-summary --json=$WORKSPACE/reports/coverage/coverage-c-extension_tests.json --txt=$WORKSPACE/reports/coverage/coverage-c-extension_tests.txt --exclude-throw-branches --fail-under-line=1 --gcov-object-directory=$WORKSPACE/build/temp/src build/temp/src'
                                                    )
                                                } catch (e){
                                                    sh(label: 'locating gcno and gcda files', script: 'find . \\( -name "*.gcno" -o -name "*.gcda" \\)')
                                                    throw e
                                                } finally {
                                                    if(fileExists('reports/coverage/coverage-c-extension_tests.txt')){
                                                        sh 'cat reports/coverage/coverage-c-extension_tests.txt'
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                                stage('C++ tests'){
                                    stages{
                                        stage('Building C++ Tests with coverage data'){
                                            steps{
                                                tee('logs/cmake-build.log'){
                                                    sh(label: 'Building C++ Code',
                                                       script: '''uvx conan install conanfile.py -of build/cpp --build=missing -pr:b=default
                                                                  uv run cmake --preset conan-release -B build/cpp/ -Wdev -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -Dpyexiv2bind_generate_python_bindings:BOOL=false -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra"
                                                                  mkdir -p build/build_wrapper_output_directory
                                                                  build-wrapper-linux --out-dir build/build_wrapper_output_directory uv run cmake --build build/cpp --target all
                                                               '''
                                                    )
                                                }
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
                                            steps{
                                                script{
                                                    parallel([
                                                        failFast: false,
                                                        'Clang Tidy Analysis': {
                                                            try{
                                                                tee('logs/clang-tidy.log') {
                                                                    catchError(buildResult: 'SUCCESS', message: 'Clang-Tidy found issues', stageResult: 'UNSTABLE') {
                                                                        sh(label: 'Run Clang Tidy', script: 'run-clang-tidy -clang-tidy-binary clang-tidy -p ./build/cpp/ src/py3exiv2bind/')
                                                                    }
                                                                }
                                                            } finally {
                                                                recordIssues(tools: [clangTidy(pattern: 'logs/clang-tidy.log')])
                                                            }
                                                        },
                                                        'Memcheck': {
                                                            if (params.RUN_MEMCHECK){
                                                                generate_ctest_memtest_script('memcheck.cmake')
                                                                try{
                                                                    timeout(30){
                                                                        sh(label: 'Running memcheck', script: 'uv run ctest -S memcheck.cmake --verbose -j $(grep -c ^processor /proc/cpuinfo)')
                                                                    }
                                                                } finally {
                                                                    recordIssues(
                                                                        filters: [excludeFile('build/cpp/_deps/*'),],
                                                                        tools: [
                                                                            drMemory(pattern: 'build/cpp/Testing/Temporary/DrMemory/**/results.txt')
                                                                        ]
                                                                    )
                                                                }
                                                            } else {
                                                                Utils.markStageSkippedForConditional('Memcheck')
                                                            }
                                                        },
                                                        'CPP Check': {
                                                            try{
                                                                catchError(buildResult: 'SUCCESS', message: 'cppcheck found issues', stageResult: 'UNSTABLE') {
                                                                    sh(label: 'Running cppcheck',
                                                                       script: 'cppcheck --error-exitcode=1 --project=build/cpp/compile_commands.json -i_deps --enable=all --suppressions-list=cppcheck_suppression_file.txt -rp=$PWD/build/cpp  --xml --output-file=logs/cppcheck_debug.xml'
                                                                       )
                                                                }
                                                            } finally {
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
                                                        },
                                                        'CTest': {
                                                            try{
                                                                sh(label: 'Running CTest',
                                                                   script: '''cd build/cpp
                                                                              uv run ctest --output-on-failure --no-compress-output -T Test
                                                                           '''
                                                              )
                                                            } finally {
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
                                                        },
                                                    ])
                                                }
                                            }
                                        }
                                    }
                                    post{
                                        always{
                                            sh(label: 'Creating gcovr coverage report',
                                               script: '''uv run gcovr --root $WORKSPACE --print-summary --exclude \'/.*/build/\' --json=$WORKSPACE/reports/coverage/coverage_cpp_tests.json --txt=$WORKSPACE/reports/coverage/text_cpp_tests_summary.txt --exclude-throw-branches --gcov-object-directory=$WORKSPACE/build/cpp build/cpp
                                                          cat reports/coverage/text_cpp_tests_summary.txt
                                                       '''
                                            )
                                        }
                                    }
                                }
                                stage('Misc tests'){
                                    steps{
                                        script{
                                            parallel([
                                                'Task Scanner': {
                                                    recordIssues(tools: [taskScanner(highTags: 'FIXME', includePattern: 'src/py3exiv2bind/**/*.py, src/py3exiv2bind/**/*.cpp, src/py3exiv2bind/**/*.h', normalTags: 'TODO')])
                                                },
                                            ])
                                        }
                                    }
                                }
                            }
                            post{
                                always{
                                    script{
                                        if(fileExists('reports/coverage/coverage_cpp_tests.json') && fileExists('reports/coverage/coverage-c-extension_tests.json')){
                                            sh(label: 'combining coverage data',
                                               script: '''mkdir -p reports/coverage
                                                          uv run coverage combine
                                                          uv run coverage xml -o ./reports/coverage/coverage-python.xml
                                                          uv run gcovr --root $WORKSPACE --filter=src/py3exiv2bind --add-tracefile reports/coverage/coverage_cpp_tests.json --add-tracefile reports/coverage/coverage-c-extension_tests.json --keep --print-summary --cobertura reports/coverage/coverage_cpp.xml --txt reports/coverage/text_merged_summary.txt
                                                          cat reports/coverage/text_merged_summary.txt
                                                       '''
                                                  )
                                        }
                                    }
                                    archiveArtifacts artifacts: 'reports/coverage/*.xml'
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
                                    equals expected: true, actual: params.RUN_CHECKS
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
                                        withCredentials([string(credentialsId: params.SONARCLOUD_TOKEN, variable: 'token')]) {
                                            sh(
                                                label: 'Running Sonar Scanner',
                                                script: 'uv run pysonar -t $token -Dsonar.projectVersion=$VERSION -Dsonar.buildString="$BUILD_TAG" -Dsonar.cfamily.cache.enabled=false -Dsonar.cfamily.threads=$(grep -c ^processor /proc/cpuinfo) -Dsonar.cfamily.compile-commands=build/build_wrapper_output_directory/compile_commands.json -Dsonar.python.coverage.reportPaths=./reports/coverage/coverage-python.xml -Dsonar.cfamily.cobertura.reportPaths=reports/coverage/coverage_cpp.xml ' + (env.CHANGE_ID ?  '-Dsonar.pullrequest.key=$CHANGE_ID -Dsonar.pullrequest.base=$CHANGE_TARGET' : '-Dsonar.branch.name=$BRANCH_NAME')
                                            )
                                        }
                                    }
                                    timeout(time: 1, unit: 'HOURS') {
                                         def sonarqube_result = waitForQualityGate(abortPipeline: false)
                                         if (sonarqube_result.status != 'OK') {
                                             unstable "SonarQube quality gate: ${sonarqube_result.status}"
                                         }
                                         if(env.BRANCH_IS_PRIMARY){
                                            writeJSON(file: 'reports/sonar-report.json', json: get_sonarqube_unresolved_issues('.sonar/report-task.txt'))
                                        }
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
                                        checkout scm
                                        withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                            try{
                                                docker.image('python').inside('--mount source=python-tmp-py3exiv2bind,target=/tmp'){
                                                    sh(script: 'python3 -m venv venv && venv/bin/pip install --disable-pip-version-check uv')
                                                    envs = sh(
                                                        label: 'Get tox environments',
                                                        script: './venv/bin/uv run --quiet --only-group tox --with tox-uv --frozen tox list -d --no-desc',
                                                        returnStdout: true,
                                                    ).trim().split('\n')
                                                }
                                            } finally{
                                                sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                            }
                                        }

                                    }
                                    parallel(
                                        envs.collectEntries{toxEnv ->
                                            def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                            [
                                                "Tox Environment: ${toxEnv}",
                                                {
                                                    retry(2){
                                                        node('docker && linux'){
                                                            def maxRetries = 2
                                                            checkout scm
                                                            def image
                                                            lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                                retry(maxRetries){
                                                                    image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CONAN_CENTER_PROXY_V2_URL .')
                                                                }
                                                            }
                                                            try{
                                                                retry(maxRetries){
                                                                    try{
                                                                        withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                                            image.inside('--mount source=python-tmp-py3exiv2bind,target=/tmp'){
                                                                                sh( label: 'Running Tox',
                                                                                    script: "uv run --only-group tox -p ${version} --python-preference only-system --with tox-uv tox run -e ${toxEnv} --runner uv-venv-lock-runner -vvv"
                                                                                    )
                                                                            }
                                                                        }
                                                                    } finally{
                                                                        sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                                    }
                                                                }
                                                            } finally {
                                                                if (image){
                                                                    sh "docker rmi --force --no-prune ${image.id}"
                                                                }
                                                            }
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
                                 PIP_CACHE_DIR='C:\\Users\\ContainerUser\\Documents\\cache\\pipcache'
                                 UV_TOOL_DIR='C:\\Users\\ContainerUser\\Documents\\uvtools'
                                 UV_PYTHON_INSTALL_DIR='C:\\Users\\ContainerUser\\Documents\\cache\\uvpython'
                                 UV_CACHE_DIR='C:\\cache\\uvcache'
                             }
                             steps{
                                 script{
                                     def envs = []
                                     node('docker && windows'){
                                         checkout scm
                                         try{
                                            withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                docker.image(env.DEFAULT_PYTHON_DOCKER_IMAGE ? env.DEFAULT_PYTHON_DOCKER_IMAGE: 'python')
                                                    .inside("\
                                                        --mount type=volume,source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR} \
                                                        --mount type=volume,source=pipcache,target=${env.PIP_CACHE_DIR} \
                                                        --mount type=volume,source=uv_cache_dir,target=${env.UV_CACHE_DIR}\
                                                        "
                                                    ){
                                                     bat(script: 'python -m venv venv && venv\\Scripts\\pip install --disable-pip-version-check uv')
                                                     envs = bat(
                                                         label: 'Get tox environments',
                                                         script: '@.\\venv\\Scripts\\uv run --quiet --only-group tox --with tox-uv --frozen tox list -d --no-desc',
                                                         returnStdout: true,
                                                     ).trim().split('\r\n')
                                                }
                                            }
                                         } finally{
                                             bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                         }
                                     }
                                     parallel(
                                         envs.collectEntries{toxEnv ->
                                             def version = toxEnv.replaceAll(/py(\d)(\d+)/, '$1.$2')
                                             [
                                                 "Tox Environment: ${toxEnv}",
                                                 {
                                                     node('docker && windows'){
                                                        def maxRetries = 1
                                                        def image
                                                        checkout scm
                                                        lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                            retry(maxRetries){
                                                                image = docker.build(UUID.randomUUID().toString(), '-f scripts/resources/windows/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CONAN_CENTER_PROXY_V2_URL --build-arg CHOCOLATEY_SOURCE' + (env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE ? " --build-arg FROM_IMAGE=${env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE} ": ' ') + '.')
                                                            }
                                                        }
                                                        try{
                                                            try{
                                                                checkout scm
                                                                image.inside("\
                                                                    --mount type=volume,source=uv_python_install_dir,target=${env.UV_PYTHON_INSTALL_DIR} \
                                                                    --mount type=volume,source=pipcache,target=${env.PIP_CACHE_DIR} \
                                                                    --mount type=volume,source=uv_cache_dir,target=${env.UV_CACHE_DIR}\
                                                                    "
                                                                ){
                                                                    withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                                        retry(maxRetries){
                                                                            try{
                                                                                bat(label: 'Running Tox',
                                                                                    script: """uv python install cpython-${version}
                                                                                               uv run --only-group tox --with tox-uv tox run -e ${toxEnv} --runner uv-venv-lock-runner -vv
                                                                                            """
                                                                                )
                                                                            } catch(err){
                                                                                cleanWs(
                                                                                    patterns: [
                                                                                            [pattern: '.tox', type: 'INCLUDE'],
                                                                                        ],
                                                                                    notFailBuild: true,
                                                                                    deleteDirs: true
                                                                                )
                                                                                throw err
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            } finally {
                                                                bat "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                            }
                                                        } finally{
                                                            if (image){
                                                                bat "docker rmi --force --no-prune ${image.id}"
                                                            }
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
            environment{
                UV_FROZEN='1'
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
                                    args '--mount source=python-tmp-py3exiv2bind,target=/tmp'
                                  }
                            }
                            environment{
                                PIP_CACHE_DIR='/tmp/pipcache'
                                UV_INDEX_STRATEGY='unsafe-best-match'
                                UV_CACHE_DIR='/tmp/uvcache'
                                UV_CONFIG_FILE=createUVConfig()
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
                                                           venv/bin/uv build --sdist
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
                                                                            withEnv([
                                                                                "UV_INDEX_STRATEGY=unsafe-best-match",
                                                                                "UV_CONFIG_FILE=${createUVConfig()}"
                                                                            ]){
                                                                                timeout(60){
                                                                                    sh(label: 'Running Tox',
                                                                                       script: """python${pythonVersion} -m venv venv
                                                                                                  trap "rm -rf venv" EXIT
                                                                                                  ./venv/bin/python -m pip install --disable-pip-version-check uv
                                                                                                  trap "rm -rf venv && rm -rf .tox" EXIT
                                                                                                  ./venv/bin/uv run --only-group tox --python=${pythonVersion} --with tox-uv tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                                           """
                                                                                    )
                                                                                }
                                                                            }
                                                                        }finally{
                                                                            sh "${tool(name: 'Default', type: 'git')} clean -dfx"
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
                                                                withEnv([
                                                                    'PIP_CACHE_DIR=C:\\Users\\ContainerUser\\Documents\\pipcache',
                                                                    'UV_TOOL_DIR=C:\\Users\\ContainerUser\\Documents\\uvtools',
                                                                    'UV_PYTHON_INSTALL_DIR=C:\\Users\\ContainerUser\\Documents\\uvpython',
                                                                    'UV_CACHE_DIR=C:\\cache\\uvcache',
                                                                    'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                ]){
                                                                    def image
                                                                    checkout scm
                                                                    try{
                                                                        lock("${env.JOB_NAME} - ${env.NODE_NAME}"){
                                                                            image = docker.build(UUID.randomUUID().toString(), '-f scripts/resources/windows/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CONAN_CENTER_PROXY_V2_URL --build-arg CHOCOLATEY_SOURCE' + (env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE ? " --build-arg FROM_IMAGE=${env.DEFAULT_DOCKER_DOTNET_SDK_BASE_IMAGE} ": ' ') + '.')
                                                                        }
                                                                        retry(3){
                                                                            try{
                                                                                checkout scm
                                                                                withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){

                                                                                    image.inside(
                                                                                        '--mount type=volume,source=uv_python_install_dir,target=$UV_PYTHON_INSTALL_DIR ' +
                                                                                        '--mount type=volume,source=pipcache,target=$PIP_CACHE_DIR '
                                                                                        // + '--mount type=volume,source=uv_cache_dir,target=$UV_CACHE_DIR'
                                                                                    ){
                                                                                        unstash 'sdist'
                                                                                        findFiles(glob: 'dist/*.tar.gz').each{
                                                                                            timeout(60){
                                                                                                try{
                                                                                                    bat(label: 'Running Tox',
                                                                                                        script: """uv run --only-group tox --with tox-uv tox run --runner=uv-venv-runner --installpkg ${it.path} -e py${pythonVersion.replace('.', '')} -vv
                                                                                                                   rmdir /S /Q .tox
                                                                                                                """
                                                                                                    )
                                                                                                } finally{
                                                                                                    cleanWs(
                                                                                                        patterns: [
                                                                                                            [pattern: '.tox/', type: 'INCLUDE'],
                                                                                                            [pattern: 'CMakeUserPresets.json', type: 'INCLUDE'],
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
                                                                                bat "${tool(name: 'Default', type: 'git')} clean -dfx"

                                                                            }
                                                                        }
                                                                    } finally {
                                                                        if(image){
                                                                            bat "docker rmi --no-prune ${image.id}"
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
                                                            node("linux && docker && ${arch}"){
                                                                checkout scm
                                                                withEnv([
                                                                    'PIP_CACHE_DIR=/tmp/pipcache',
                                                                    'UV_INDEX_STRATEGY=unsafe-best-match',
                                                                    'UV_TOOL_DIR=/tmp/uvtools',
                                                                    'UV_PYTHON_INSTALL_DIR=/tmp/uvpython',
                                                                    'UV_CACHE_DIR=/tmp/uvcache',
                                                                ]){
                                                                    def image
                                                                    try{
                                                                        image = docker.build(UUID.randomUUID().toString(), '-f ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CONAN_CENTER_PROXY_V2_URL .')
                                                                        try{
                                                                            withEnv(["UV_CONFIG_FILE=${createUVConfig()}"]){
                                                                                unstash 'sdist'
                                                                                image.inside('--mount source=python-tmp-py3exiv2bind,target=/tmp'){
                                                                                    findFiles(glob: 'dist/*.tar.gz').each{
                                                                                        retry(3){
                                                                                            try{
                                                                                                timeout(60){
                                                                                                    sh(label: 'Running Tox',
                                                                                                       script: """trap "rm -rf .tox" EXIT
                                                                                                                  uv run --only-group tox --python=${pythonVersion} --python-preference only-system --with tox-uv tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                                                                               """
                                                                                                    )
                                                                                                }
                                                                                            } catch(err){
                                                                                                cleanWs(
                                                                                                    patterns: [
                                                                                                            [pattern: '**/__pycache__/', type: 'INCLUDE'],
                                                                                                            [pattern: 'venv/', type: 'INCLUDE'],
                                                                                                            [pattern: '.tox/', type: 'INCLUDE'],
                                                                                                        ],
                                                                                                    notFailBuild: true,
                                                                                                    deleteDirs: true
                                                                                                )
                                                                                                throw err
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        } finally{
                                                                            sh "${tool(name: 'Default', type: 'git')} clean -dfx"
                                                                        }
                                                                    } finally{
                                                                        if(image){
                                                                            sh "docker rmi --force --no-prune ${image.id}"
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
                        UV_CONFIG_FILE=createUVConfig()
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
                                                       uv run --only-group publish twine upload --disable-progress-bar --non-interactive dist/*
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
