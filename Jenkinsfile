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

def getDevpiConfig() {
    node(){
        configFileProvider([configFile(fileId: 'devpi_config', variable: 'CONFIG_FILE')]) {
            def configProperties = readProperties(file: CONFIG_FILE)
            configProperties.stagingIndex = {
                if (env.TAG_NAME?.trim()){
                    return 'tag_staging'
                } else{
                    return "${env.BRANCH_NAME}_staging"
                }
            }()
            return configProperties
        }
    }
}
def DEVPI_CONFIG = getDevpiConfig()

SUPPORTED_MAC_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_LINUX_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
SUPPORTED_WINDOWS_VERSIONS = ['3.8', '3.9', '3.10', '3.11', '3.12']
// ============================================================================
//  Dynamic variables. Used to help manage state
wheelStashes = []

// ============================================================================
// Helper functions.
// ============================================================================

def getMacDevpiName(pythonVersion, format){
    if(format == 'wheel'){
        return "${pythonVersion.replace('.','')}-*macosx*.*whl"
    } else if(format == 'sdist'){
        return 'tar.gz'
    } else{
        error "unknown format ${format}"
    }
}

def getMacDevpiTestStages(packageName, packageVersion, pythonVersions, devpiServer, devpiCredentialsId, devpiIndex) {
    node(){
        checkout scm
        devpi = load('ci/jenkins/scripts/devpi.groovy')
    }
    def macPackageStages = [:]
    pythonVersions.each{pythonVersion ->
        if(params.INCLUDE_MACOS_X86_64 == true){
            macPackageStages["MacOS x86_64 - Python ${pythonVersion}: wheel"] = {
                withEnv(['PATH+EXTRA=./venv/bin']) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && x86 && devpi-access"
                        ],
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        retries: 3,
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(x86_64\\.whl)"
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label:'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                               . ./venv/bin/activate
                                               python -m pip install pip --upgrade
                                               python -m pip install 'devpi_client<7' -r requirements/requirements_tox.txt
                                               '''
                                )
                            },
                            clientDir: './devpi',
                            testCommands:{
                                def selector = "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(x86_64\\.whl)"
                                def toxEnv = "py${pythonVersion}".replace('.','')
                                withEnv([
                                        "_DEVPI_INDEX=${devpiIndex}",
                                        "PACKAGE_NAME=${packageName}",
                                        "PACKAGE_VERSION=${packageVersion}",
                                        "TOX_ENV=${toxEnv}",
                                        "TOX_PACKAGE_SELECTOR=${selector}",
                                        ]){

                                    sh(
                                        label: 'Running tests on Packages on DevPi',
                                        script: '''. ./venv/bin/activate
                                                   devpi test --index $_DEVPI_INDEX $PACKAGE_NAME==$PACKAGE_VERSION -s $TOX_PACKAGE_SELECTOR --clientdir './devpi' -e $TOX_ENV -v
                                                   '''
                                    )
                                }
                            },
                            toxEnv: "py${pythonVersion}".replace('.',''),
                            teardown: {
                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                            }
                        ]
                    )
                }
            }
            macPackageStages["MacOS x86_64 - Python ${pythonVersion}: sdist"]= {
                withEnv(['PATH+EXTRA=./venv/bin']) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && x86 && devpi-access"
                        ],
                        retries: 3,
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: 'tar.gz'
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label:'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                                venv/bin/python -m pip install pip --upgrade
                                                venv/bin/python -m pip install 'devpi_client<7' -r requirements/requirements_tox.txt
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
        }
        if(params.INCLUDE_MACOS_ARM == true){
            macPackageStages["MacOS m1 - Python ${pythonVersion}: wheel"] = {
                withEnv(['PATH+EXTRA=./venv/bin']) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && m1 && devpi-access"
                        ],
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(arm64\\.whl)"
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label:'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                                venv/bin/python -m pip install pip --upgrade
                                                venv/bin/python -m pip install 'devpi-client<7.0' -r requirements/requirements_tox.txt
                                                '''
                                )
                            },
                            toxEnv: "py${pythonVersion}".replace('.',''),
                            clientDir: './devpi',
                            testCommands:{
                                def selector = "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(arm64\\.whl)"
                                def toxEnv = "py${pythonVersion}".replace('.','')
                                withEnv([
                                        "_DEVPI_INDEX=${devpiIndex}",
                                        "PACKAGE_NAME=${packageName}",
                                        "PACKAGE_VERSION=${packageVersion}",
                                        "TOX_ENV=${toxEnv}",
                                        "TOX_PACKAGE_SELECTOR=${selector}",
                                        ]){

                                    sh(
                                        label: 'Running tests on Packages on DevPi',
                                        script: '''. ./venv/bin/activate
                                                   devpi test --index $_DEVPI_INDEX $PACKAGE_NAME==$PACKAGE_VERSION -s $TOX_PACKAGE_SELECTOR --clientdir './devpi' -e $TOX_ENV -v
                                                   '''
                                    )
                                }
                            },
                            teardown: {
                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                            }
                        ]
                    )
                }
            }
            macPackageStages["MacOS m1 - Python ${pythonVersion}: sdist"]= {
                withEnv(['PATH+EXTRA=./venv/bin']) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && m1 && devpi-access"
                        ],
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: 'tar.gz'
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label:'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                                venv/bin/python -m pip install pip --upgrade
                                                venv/bin/python -m pip install 'devpi_client<7' -r requirements/requirements_tox.txt
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
        }
        if(params.INCLUDE_MACOS_X86_64 && params.INCLUDE_MACOS_ARM && pythonVersion != '3.8'){
            macPackageStages["MacOS x86_64 - Python ${pythonVersion}: universal2 wheel"] = {
                withEnv([
                    'PATH+EXTRA=./venv/bin'
                ]) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && x86_64 && devpi-access"
                        ],
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(universal2\\.whl)"
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label: 'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                                venv/bin/python -m pip install pip --upgrade
                                                venv/bin/python -m pip install 'devpi_client<7' -r requirements/requirements_tox.txt
                                                '''
                                )
                            },
                            toxEnv: "py${pythonVersion}".replace('.',''),
                            teardown: {
                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                            }
                        ],
                        retries: 3
                    )
                }
            }
            macPackageStages["MacOS m1 - Python ${pythonVersion}: universal2 wheel"] = {
                withEnv([
                    'PATH+EXTRA=./venv/bin'
                ]) {
                    devpi.testDevpiPackage(
                        agent: [
                            label: "mac && python${pythonVersion} && m1 && devpi-access"
                        ],
                        devpi: [
                            index: devpiIndex,
                            server: devpiServer,
                            credentialsId: devpiCredentialsId,
                            devpiExec: 'venv/bin/devpi'
                        ],
                        package:[
                            name: packageName,
                            version: packageVersion,
                            selector: "(${pythonVersion.replace('.','')}).*(-*macosx_*).*(universal2\\.whl)"
                        ],
                        test:[
                            setup: {
                                checkout scm
                                sh(
                                    label: 'Installing Devpi client',
                                    script: '''python3 -m venv venv
                                                venv/bin/python -m pip install pip --upgrade
                                                venv/bin/python -m pip install 'devpi_client<7' -r requirements/requirements_tox.txt
                                                '''
                                )
                            },
                            toxEnv: "py${pythonVersion}".replace('.',''),
                            teardown: {
                                sh( label: 'Remove Devpi client', script: 'rm -r venv')
                            }
                        ],
                        retries: 3
                    )
                }
            }
        }
    }
    return macPackageStages;
}
def runToxTests(){
    script{
        def windowsJobs = [:]
        def linuxJobs = [:]
        parallel(
            'Linux':{
                linuxJobs = getToxTestsParallel(
                            envNamePrefix: 'Tox Linux',
                            label: 'linux && docker && x86',
                            dockerfile: 'ci/docker/linux/tox/Dockerfile',
                            dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                            dockerRunArgs: '-v pipcache_pyexiv2bind:/.cache/pip',
                            retry: 3,
                        )
            },
            'Windows':{
                windowsJobs = getToxTestsParallel(
                                envNamePrefix: 'Tox Windows',
                                label: 'windows && docker && x86',
                                dockerfile: 'ci/docker/windows/tox/Dockerfile',
                                dockerArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion',
                                dockerRunArgs: '-v pipcache_pyexiv2bind:c:/users/containeradministrator/appdata/local/pip',
                                retry: 3,
                            )
            }
        )
        parallel(windowsJobs + linuxJobs)
    }
}

def startup(){
    parallel(
        [
            failFast: true,
            'Loading Reference Build Information': {
                stage('Loading Reference Build Information'){
                    node(){
                        checkout scm
                        discoverGitReferenceBuild(latestBuildIfNotFound: true)
                    }
                }
            },
            'Enable Git Forensics': {
                stage('Enable Git Forensics'){
                    node(){
                        checkout scm
                        mineRepository()
                    }
                }
            },
            'Loading helper scripts and configs': {
                stage('Loading helper scripts and configs'){
                    node(){
                        ws{
                            checkout scm
                            devpi = load('ci/jenkins/scripts/devpi.groovy')
                        }
                    }
                }
            },
            'Getting Distribution Info': {
                stage('Getting Distribution Info'){
                    node('linux && docker && x86') {
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
                                        stash includes: '*.dist-info/**', name: 'DIST-INFO'
                                        archiveArtifacts artifacts: '*.dist-info/**'
                                    }
                                }
                            } finally{
                                cleanWs()
                            }
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

def windows_wheels(){
    def wheelStages = [:]
    SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
        if(params.INCLUDE_WINDOWS_X86_64 == true){
            wheelStages["Python ${pythonVersion} - Windows"] = {
                stage("Python ${pythonVersion} - Windows"){
                    stage("Build Wheel (${pythonVersion} Windows)"){
                        buildPythonPkg(
                            agent: [
                                dockerfile: [
                                    label: 'windows && docker',
                                    filename: 'ci/docker/windows/tox/Dockerfile',
                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion'
                                ]
                            ],
                            retries: 3,
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
                                    archiveArtifacts artifacts: 'dist/*.whl'
                                }
                            ]
                        )
                    }
                    stage("Test Wheel (${pythonVersion} Windows)"){
                        testPythonPkg(
                            agent: [
                                dockerfile: [
                                    label: 'windows && docker',
                                    filename: 'ci/docker/windows/tox_no_vs/Dockerfile',
                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion',
                                    dockerRunArgs: '-v pipcache_pyexiv2bind:c:/users/containeradministrator/appdata/local/pip',
                                    dockerImageName: "${currentBuild.fullProjectName}_test_no_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                ]
                            ],
                            retries: 3,
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
                            ]
                        )
                    }
                }
            }
        }
    }
    parallel(wheelStages)
}

def linux_wheels(){
    def wheelStages = [:]
     SUPPORTED_LINUX_VERSIONS.each{ pythonVersion ->
        wheelStages["Python ${pythonVersion} - Linux"] = {
            stage("Python ${pythonVersion} - Linux"){
                def archBuilds = [:]
                if(params.INCLUDE_LINUX_X86_64 == true){
                    archBuilds["Python ${pythonVersion} Linux x86_64 Wheel"] = {
                        stage("Python ${pythonVersion} Linux x86_64 Wheel"){
                            stage("Build Wheel (${pythonVersion} Linux x86_64)"){
                                buildPythonPkg(
                                    agent: [
                                        dockerfile: [
                                            label: 'linux && docker && x86',
                                            filename: 'ci/docker/linux/package/Dockerfile',
                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux_2_28_x86_64'
                                        ]
                                    ],
                                    retries: 3,
                                    buildCmd: {
                                        try{
                                            sh(label: 'Building python wheel',
                                               script:"""python${pythonVersion} -m build --wheel
                                                         auditwheel repair ./dist/*.whl -w ./dist
                                                         """
                                               )
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
                                            stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux-x86 wheel"
                                            wheelStashes << "python${pythonVersion} linux-x86 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} Linux x86_64)"){
                                    testPythonPkg(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker && x86',
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                args: '-v pipcache_pyexiv2bind:/.cache/pip'
                                            ]
                                        ],
                                        retries: 3,
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} linux-x86 wheel"
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
                                        ]
                                    )
                                }
                            }
                        }
                    }
                }
                if(params.INCLUDE_LINUX_ARM == true){
                    archBuilds["Python ${pythonVersion} Linux ARM64 wheel"] = {
                        stage("Python ${pythonVersion} Linux ARM64 Wheel"){
                            stage("Build Wheel (${pythonVersion} Linux ARM64)"){
                                buildPythonPkg(
                                    agent: [
                                        dockerfile: [
                                            label: 'linux && docker && arm',
                                            filename: 'ci/docker/linux/package/Dockerfile',
                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg manylinux_image=quay.io/pypa/manylinux_2_28_aarch64'
                                        ]
                                    ],
                                    retries: 3,
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
                                            stash includes: 'dist/*manylinux*.*whl', name: "python${pythonVersion} linux-arm64 wheel"
                                            wheelStashes << "python${pythonVersion} linux-arm64 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} Linux ARM64)"){
                                    testPythonPkg(
                                        agent: [
                                            dockerfile: [
                                                label: 'linux && docker && arm',
                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                args: '-v pipcache_pyexiv2bind:/.cache/pip'
                                            ]
                                        ],
                                        retries: 3,
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} linux-arm64 wheel"
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
                                        ]
                                    )
                                }
                            }
                        }
                    }
                }
                parallel(archBuilds)
            }
        }
    }
    parallel(wheelStages)
}

def mac_wheels(){
    def wheelStages = [:]
    SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
        wheelStages["Python ${pythonVersion} - Mac"] = {
            stage("Python ${pythonVersion} - Mac"){
                stage("Single arch wheels for Python ${pythonVersion}"){
                    def archStages = [:]
                    if(params.INCLUDE_MACOS_X86_64 == true){
                        archStages["MacOS - Python ${pythonVersion} - x86_64: wheel"] = {
                            stage("Build Wheel (${pythonVersion} MacOS x86_64)"){
                                buildPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && x86",
                                    ],
                                    retries: 3,
                                    buildCmd: {
                                        withEnv([
                                            '_PYTHON_HOST_PLATFORM=macosx-10.15-x86_64',
                                            'MACOSX_DEPLOYMENT_TARGET=10.15',
                                            'ARCHFLAGS=-arch x86_64'
                                        ]){
                                             sh(label: 'Building wheel',
                                                script: """python${pythonVersion} -m venv venv
                                                           . ./venv/bin/activate
                                                           python -m pip install --upgrade pip
                                                           pip install wheel==0.37
                                                           pip install build delocate
                                                           python -m build --wheel
                                                           """
                                               )
                                             findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Fixing up wheel',
                                                       script: """. ./venv/bin/activate
                                                                  pip list
                                                                  delocate-listdeps --depending ${it.path}
                                                                  delocate-wheel -w fixed_wheels --require-archs x86_64 --verbose ${it.path}
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
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*.whl', name: "python${pythonVersion} mac x86_64 wheel"
                                            wheelStashes << "python${pythonVersion} mac x86_64 wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            if(params.TEST_PACKAGES == true){
                                stage("Test Wheel (${pythonVersion} MacOS x86_64)"){
                                    testPythonPkg(
                                        agent: [
                                            label: "mac && python${pythonVersion} && x86",
                                        ],
                                        testSetup: {
                                            checkout scm
                                            unstash "python${pythonVersion} mac x86_64 wheel"
                                        },
                                        retries: 3,
                                        testCommand: {
                                            findFiles(glob: 'dist/*.whl').each{
                                                sh(label: 'Running Tox',
                                                   script: """python${pythonVersion} -m venv venv
                                                   ./venv/bin/python -m pip install --upgrade pip
                                                   ./venv/bin/pip install -r requirements/requirements_tox.txt
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
                                            }
                                        ]
                                    )
                                }
                            }
                        }
                    }
                    if(params.INCLUDE_MACOS_ARM == true){
                        archStages["MacOS - Python ${pythonVersion} - M1: wheel"] = {
                            stage("Build Wheel (${pythonVersion} MacOS m1)"){
                                buildPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && m1",
                                    ],
                                    retries: 3,
                                    buildCmd: {
                                        withEnv([
                                            '_PYTHON_HOST_PLATFORM=macosx-11.0-arm64',
                                            'MACOSX_DEPLOYMENT_TARGET=11.0',
                                            'ARCHFLAGS=-arch arm64'
                                            ]) {
                                                sh """
                                                python${pythonVersion} -m venv venv
                                                . ./venv/bin/activate
                                                python -m pip install --upgrade pip
                                                pip install wheel==0.37
                                                pip install build delocate
                                                python -m build --wheel .
                                                """
                                                findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Fixing up wheel',
                                                       script: """. ./venv/bin/activate
                                                                  pip list
                                                                  delocate-listdeps --depending ${it.path}
                                                                  delocate-wheel -w fixed_wheels --require-archs x86_64 --verbose ${it.path}
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
                                                    ],
                                                notFailBuild: true,
                                                deleteDirs: true
                                            )
                                        },
                                        success: {
                                            stash includes: 'dist/*.whl', name: "python${pythonVersion} m1 mac wheel"
                                            wheelStashes << "python${pythonVersion} m1 mac wheel"
                                            archiveArtifacts artifacts: 'dist/*.whl'
                                        }
                                    ]
                                )
                            }
                            stage("Test Wheel (${pythonVersion} MacOS m1)"){
                                testPythonPkg(
                                    agent: [
                                        label: "mac && python${pythonVersion} && m1",
                                    ],
                                    testSetup: {
                                        checkout scm
                                        unstash "python${pythonVersion} m1 mac wheel"
                                    },
                                    retries: 3,
                                    testCommand: {
                                        findFiles(glob: 'dist/*.whl').each{
                                            sh(label: 'Running Tox',
                                               script: """python${pythonVersion} -m venv venv
                                                          . ./venv/bin/activate
                                                          python -m pip install --upgrade pip
                                                          pip install -r requirements/requirements_tox.txt
                                                          tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                      """
                                            )
                                        }
                                    },
                                    post:[
                                        failure:{
                                            sh(script:'pip list')
                                        },
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
                    }
                    parallel(archStages)
                }
            }
            if(params.INCLUDE_MACOS_X86_64 && params.INCLUDE_MACOS_ARM && pythonVersion != '3.8'){
                stage("Universal2 Wheel: Python ${pythonVersion}"){
                    stage('Make Universal2 wheel'){
                        node("mac && python${pythonVersion}") {
                            unstash "python${pythonVersion} m1 mac wheel"
                            unstash "python${pythonVersion} mac x86_64 wheel"
                            def wheelNames = []
                            findFiles(excludes: '', glob: 'dist/*.whl').each{wheelFile ->
                                wheelNames.add(wheelFile.path)
                            }
                            try{
                                sh(label: 'Make Universal2 wheel',
                                   script: """python${pythonVersion} -m venv venv
                                              . ./venv/bin/activate
                                              pip install --upgrade pip
                                              pip install wheel delocate
                                              mkdir -p out
                                              delocate-fuse  ${wheelNames.join(' ')} --verbose -w ./out/
                                              rm dist/*.whl
                                               """
                                   )
                               def fusedWheel = findFiles(excludes: '', glob: 'out/*.whl')[0]
                               def universalWheel = "py3exiv2bind-${props.Version}-cp${pythonVersion.replace('.','')}-cp${pythonVersion.replace('.','')}-macosx_11_0_universal2.whl"
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
                    if(params.TEST_PACKAGES == true){
                        stage("Test universal2 Wheel"){
                            parallel(
                                "Test Python ${pythonVersion} universal2 Wheel on x86_64 mac": {
                                    stage("Test Python ${pythonVersion} universal2 Wheel on x86_64 mac"){
                                        testPythonPkg(
                                            agent: [
                                                label: "mac && python${pythonVersion} && x86_64",
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} mac-universal2 wheel"
                                            },
                                            retries: 3,
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Running Tox',
                                                       script: """python${pythonVersion} -m venv venv
                                                                  . ./venv/bin/activate
                                                                  python -m pip install --upgrade pip
                                                                  pip install -r requirements/requirements_tox.txt
                                                                  CONAN_REVISIONS_ENABLED=1 tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                               """
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
                                },
                                "Test Python ${pythonVersion} universal2 Wheel on M1 Mac": {
                                    stage("Test Python ${pythonVersion} universal2 Wheel on M1 Mac"){
                                        testPythonPkg(
                                            agent: [
                                                label: "mac && python${pythonVersion} && m1",
                                            ],
                                            testSetup: {
                                                checkout scm
                                                unstash "python${pythonVersion} mac-universal2 wheel"
                                            },
                                            retries: 3,
                                            testCommand: {
                                                findFiles(glob: 'dist/*.whl').each{
                                                    sh(label: 'Running Tox',
                                                       script: """python${pythonVersion} -m venv venv
                                                                  . ./venv/bin/activate
                                                                  python -m pip install --upgrade pip
                                                                  pip install -r requirements/requirements_tox.txt
                                                                  CONAN_REVISIONS_ENABLED=1 tox --installpkg ${it.path} -e py${pythonVersion.replace('.', '')}
                                                               """
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
                            )
                        }
                    }
                }
            }
        }
    }
    parallel(wheelStages)
}

def get_props(){
    stage('Reading Package Metadata'){
        node() {
            try{
                unstash 'DIST-INFO'
                def metadataFile = findFiles(excludes: '', glob: '*.dist-info/METADATA')[0]
                def package_metadata = readProperties interpolate: true, file: metadataFile.path
                echo """Metadata:

    Name      ${package_metadata.Name}
    Version   ${package_metadata.Version}
    """
                return package_metadata
            } finally {
                cleanWs(
                    patterns: [
                            [pattern: '*.dist-info/**', type: 'INCLUDE'],
                        ],
                    notFailBuild: true,
                    deleteDirs: true
                )
            }
        }
    }
}
// *****************************************************************************
stage('Pipeline Pre-tasks'){
    startup()
    props = get_props()
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
        booleanParam(name: 'DEPLOY_DEVPI', defaultValue: false, description: "Deploy to DevPi on ${DEVPI_CONFIG.server}/DS_Jenkins/${env.BRANCH_NAME}")
        booleanParam(name: 'DEPLOY_DEVPI_PRODUCTION', defaultValue: false, description: "Deploy to ${DEVPI_CONFIG.server}/production/release")
        booleanParam(name: 'DEPLOY_PYPI', defaultValue: false, description: 'Deploy to pypi')
        booleanParam(name: 'DEPLOY_DOCS', defaultValue: false, description: 'Update online documentation')
    }
    stages {
        stage('Building and Testing'){
            when{
                anyOf{
                    equals expected: true, actual: params.RUN_CHECKS
                    equals expected: true, actual: params.TEST_RUN_TOX
                    equals expected: true, actual: params.DEPLOY_DEVPI
                }
            }
            options{
                retry(3)
            }
            stages{
                stage('Building Documentation'){
                    agent {
                        dockerfile {
                            filename 'ci/docker/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.11  --build-arg PIP_EXTRA_INDEX_URL'
                        }
                    }
                    steps {
                        catchError(buildResult: 'UNSTABLE', message: 'Building Sphinx documentation has issues', stageResult: 'UNSTABLE') {
                            sh(label: 'Running Sphinx',
                               script: '''mkdir -p logs
                                          mkdir -p build/docs/html
                                          python setup.py build -b build --build-lib build/lib/ --build-temp build/temp build_ext -j $(grep -c ^processor /proc/cpuinfo) --inplace
                                          python -m sphinx docs/source build/docs/html -b html -d build/docs/.doctrees --no-color -w logs/build_sphinx.log -W --keep-going
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
                                    filename 'ci/docker/linux/jenkins/Dockerfile'
                                    label 'linux && docker && x86'
                                    additionalBuildArgs '--build-arg PYTHON_VERSION=3.11  --build-arg PIP_EXTRA_INDEX_URL'
                                    args '--mount source=sonar-cache-py3exiv2bind,target=/opt/sonar/.sonar/cache'
                                }
                            }
                            stages{
                                stage('Testing') {
                                    stages{
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
                                                                          cmake -B build/cpp/ -Wdev -DCMAKE_TOOLCHAIN_FILE=build/cpp/conan_paths.cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=ON -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=true -DBUILD_TESTING:BOOL=true -Dpyexiv2bind_generate_python_bindings:BOOL=true -DCMAKE_CXX_FLAGS="-fprofile-arcs -ftest-coverage -Wall -Wextra" -DCMAKE_BUILD_TYPE=Debug
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
                                                                script: 'ctest -S memcheck.cmake --verbose -j $(grep -c ^processor /proc/cpuinfo)'
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
                                                                           PYLINTHOME=. pylint src/py3exiv2bind -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" > reports/pylint.txt
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
                                                    sh returnStatus: true, script: 'flake8 src/py3exiv2bind --tee --output-file ./logs/flake8.log'
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
                                                        sh 'coverage run --parallel-mode --source=src/py3exiv2bind -m pytest --junitxml=./reports/pytest/junit-pytest.xml'
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
                                            load('ci/jenkins/scripts/sonarqube.groovy').sonarcloudSubmit(props, params.SONARCLOUD_TOKEN)
                                        }
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
                    }
                }
                stage('Run Tox test') {
                    when {
                       equals expected: true, actual: params.TEST_RUN_TOX
                       beforeAgent true
                    }
                    steps {
                        runToxTests()
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
                        mac_wheels()
                    }
                }
                stage('Platform Wheels: Windows'){
                    when {
                        equals expected: true, actual: params.INCLUDE_WINDOWS_X86_64
                    }
                    steps{
                        windows_wheels()
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
                        linux_wheels()
                    }
                }
                stage('Source Distribution'){
                    stages{
                        stage('Build sdist'){
                            agent {
                                docker {
                                    image 'python:3.11'
                                    label 'docker && linux'
                                }
                            }
                            environment{
                                PIP_NO_CACHE_DIR="off"
                            }
                            steps{
                                sh(
                                    label: 'Building sdist',
                                    script: '''python -m venv venv --upgrade-deps
                                               venv/bin/python -m pip install build
                                               venv/bin/python -m build --sdist --outdir ./dist
                                    '''
                                    )
                            }
                            post{
                                success {
                                    stash includes: 'dist/*.tar.gz,dist/*.zip', name: 'sdist'
                                    archiveArtifacts artifacts: 'dist/*.tar.gz,dist/*.zip'
                                    script{
                                        wheelStashes << 'sdist'
                                    }
                                }
                                cleanup {
                                    cleanWs(
                                        patterns: [
                                            [pattern: 'dist/', type: 'INCLUDE'],
                                        ],
                                        notFailBuild: true,
                                        deleteDirs: true
                                    )
                                }
                                failure {
                                    sh 'python3 -m pip list'
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
                                    SUPPORTED_MAC_VERSIONS.each{ pythonVersion ->
                                        def arches = []
                                        if(params.INCLUDE_MACOS_X86_64 == true){
                                            arches << "x86_64"
                                        }
                                        if(params.INCLUDE_MACOS_ARM == true){
                                            arches << "m1"
                                        }
                                        arches.each{arch ->
                                            testSdistStages["Test sdist (MacOS ${arch} - Python ${pythonVersion})"] = {
                                                stage("Test sdist (MacOS ${arch} - Python ${pythonVersion})"){
                                                    testPythonPkg(
                                                        agent: [
                                                            label: "mac && python${pythonVersion} && ${arch}",
                                                        ],
                                                        testSetup: {
                                                            checkout scm
                                                            unstash 'sdist'
                                                        },
                                                        retries: 3,
                                                        testCommand: {
                                                            findFiles(glob: 'dist/*.tar.gz').each{
                                                                sh(label: 'Running Tox',
                                                                   script: """python${pythonVersion} -m venv venv
                                                                   ./venv/bin/python -m pip install --upgrade pip
                                                                   ./venv/bin/pip install -r requirements/requirements_tox.txt
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
                                        }
                                    }
                                    SUPPORTED_WINDOWS_VERSIONS.each{ pythonVersion ->
                                        if(params.INCLUDE_WINDOWS_X86_64 == true){
                                            testSdistStages["Test sdist (Windows x86_64 - Python ${pythonVersion})"] = {
                                                testPythonPkg(
                                                    agent: [
                                                        dockerfile: [
                                                            label: 'windows && docker',
                                                            filename: 'ci/docker/windows/tox/Dockerfile',
                                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion',
                                                            dockerRunArgs: '-v pipcache_pyexiv2bind:c:/users/containeradministrator/appdata/local/pip',
                                                        ]
                                                    ],
                                                    testSetup: {
                                                        checkout scm
                                                        unstash 'sdist'
                                                    },
                                                    retries: 3,
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
                                    }
                                    SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                        if(params.INCLUDE_LINUX_X86_64 == true){
                                            testSdistStages["Test sdist (Linux x86_64 - Python ${pythonVersion})"] = {
                                                testPythonPkg(
                                                    agent: [
                                                        dockerfile: [
                                                            label: 'linux && docker && x86',
                                                            filename: 'ci/docker/linux/tox/Dockerfile',
                                                            additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                            args: '-v pipcache_pyexiv2bind:/.cache/pip'
                                                        ]
                                                    ],
                                                    retries: 3,
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
                                        if(params.INCLUDE_LINUX_ARM == true){
                                            testSdistStages["Test sdist (Linux ARM64 - Python ${pythonVersion})"] = {
                                                stage("Test sdist (Linux ARM64 - Python ${pythonVersion})"){
                                                    testPythonPkg(
                                                        agent: [
                                                            dockerfile: [
                                                                label: 'linux && docker && arm',
                                                                filename: 'ci/docker/linux/tox/Dockerfile',
                                                                additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                                args: '-v pipcache_pyexiv2bind:/.cache/pip'
                                                            ]
                                                        ],
                                                        retries: 3,
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
                            label 'linux && docker && x86 && devpi-access'
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
                                    clientDir: './devpi'
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
                            def macPackages = getMacDevpiTestStages(props.Name, props.Version, SUPPORTED_MAC_VERSIONS, DEVPI_CONFIG.server, DEVPI_CONFIG.credentialsId, DEVPI_CONFIG.stagingIndex)
                            def windowsPackages = [:]
                            SUPPORTED_WINDOWS_VERSIONS.each{pythonVersion ->
                                if(params.INCLUDE_WINDOWS_X86_64 == true){
                                    windowsPackages["Windows - Python ${pythonVersion}: sdist"] = {
                                        devpi.testDevpiPackage(
                                            agent: [
                                                dockerfile: [
                                                    filename: 'ci/docker/windows/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion',
                                                    label: 'windows && docker && devpi-access && x86'
                                                ]
                                            ],
                                            dockerImageName:  "${currentBuild.fullProjectName}_devpi_with_msvc".replaceAll('-', '_').replaceAll('/', '_').replaceAll(' ', '').toLowerCase(),
                                            retries: 3,
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
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL --build-arg CHOCOLATEY_SOURCE --build-arg chocolateyVersion',
                                                    label: 'windows && docker && x86 && devpi-access'

                                                ]
                                            ],
                                            retries: 3,
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
                            }
                            def linuxPackages = [:]
                            SUPPORTED_LINUX_VERSIONS.each{pythonVersion ->
                                if(params.INCLUDE_LINUX_X86_64 == true){
                                    linuxPackages["Linux - Python ${pythonVersion}: sdist"] = {
                                        devpi.testDevpiPackage(
                                            agent: [
                                                dockerfile: [
                                                    filename: 'ci/docker/linux/tox/Dockerfile',
                                                    additionalBuildArgs: '--build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL',
                                                    label: 'linux && docker && x86 && devpi-access'
                                                ]
                                            ],
                                            retries: 3,
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
                                                    label: 'linux && docker && x86 && devpi-access'
                                                ]
                                            ],
                                            retries: 3,
                                            devpi: [
                                                index: DEVPI_CONFIG.stagingIndex,
                                                server: DEVPI_CONFIG.server,
                                                credentialsId: DEVPI_CONFIG.credentialsId,
                                            ],
                                            package:[
                                                name: props.Name,
                                                version: props.Version,
                                                selector: "(${pythonVersion.replace('.','')}).+(manylinux).+x86"
                                            ],
                                            test:[
                                                toxEnv: "py${pythonVersion}".replace('.',''),
                                            ]
                                        )
                                    }
                                }
                            }
                            parallel(windowsPackages + linuxPackages + macPackages)
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
                            label 'linux && docker && x86 && devpi-access'
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
                    node('linux && docker && devpi-access') {
                        script{
                            if (!env.TAG_NAME?.trim()){
                                def dockerImage = docker.build('py3exiv2bind:devpi','-f ./ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .')
                                dockerImage.inside{
                                    devpi.pushPackageToIndex(
                                        pkgName: props.Name,
                                        pkgVersion: props.Version,
                                        server: DEVPI_CONFIG.server,
                                        indexSource: "DS_Jenkins/${DEVPI_CONFIG.stagingIndex}",
                                        indexDestination: "DS_Jenkins/${env.BRANCH_NAME}",
                                        credentialsId: DEVPI_CONFIG.credentialsId
                                    )
                                }
                                sh script: "docker image rm --no-prune ${dockerImage.imageName()}"
                            }
                        }
                    }
                }
                cleanup{
                    node('linux && docker && devpi-access') {
                        script{
                            def dockerImage = docker.build('py3exiv2bind:devpi','-f ./ci/docker/linux/tox/Dockerfile --build-arg PIP_EXTRA_INDEX_URL --build-arg PIP_INDEX_URL .')
                            dockerImage.inside{
                                devpi.removePackage(
                                    pkgName: props.Name,
                                    pkgVersion: props.Version,
                                    index: "DS_Jenkins/${DEVPI_CONFIG.stagingIndex}",
                                    server: DEVPI_CONFIG.server,
                                    credentialsId: DEVPI_CONFIG.credentialsId,

                                )
                            }
                            sh script: "docker image rm --no-prune ${dockerImage.imageName()}"
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
                            filename 'ci/docker/linux/jenkins/Dockerfile'
                            label 'linux && docker && x86'
                            additionalBuildArgs '--build-arg PYTHON_VERSION=3.11  --build-arg PIP_EXTRA_INDEX_URL'
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
                        }
                        pypiUpload(
                            credentialsId: 'jenkins-nexus',
                            repositoryUrl: SERVER_URL,
                            glob: 'dist/*'
                        )
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
