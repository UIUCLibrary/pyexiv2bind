#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*
def PKG_NAME = "unknown"
def PKG_VERSION = "unknown"
def DOC_ZIP_FILENAME = "doc.zip"
def junit_filename = "junit.xml"
def REPORT_DIR = ""
def VENV_ROOT = ""
def VENV_PYTHON = ""
def VENV_PIP = ""
pipeline {
    agent {
        label "Windows && VS2015 && Python3"
    }
    
    triggers {
        cron('@daily')
    }

    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(20)  // Timeout after 20 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    environment {
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
        PIP_CACHE_DIR="${WORKSPACE}\\pipcache\\"
    }
    parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
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
            steps {
                // Set up the reports directory variable 
                script{
                    REPORT_DIR = "${pwd tmp: true}\\reports"
                }
                
                script{
                    if (params.FRESH_WORKSPACE == true){
                        deleteDir()
                        checkout scm
                    }
                }

                
                dir(pwd(tmp: true)){
                    dir("logs"){
                        deleteDir()
                    }
                
                }
                dir("logs"){
                    deleteDir()
                }
                
                dir("build"){
                    deleteDir()
                    echo "Cleaned out build directory"
                    bat "dir"
                }
                dir("reports"){
                    deleteDir()
                    echo "Cleaned out reports directory"
                    bat "dir"
                }
                lock("system_python"){
                    bat "${tool 'CPython-3.6'} -m pip install --upgrade pip --quiet"
                }

                
                script {
                    dir("source"){
                        PKG_NAME = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                        PKG_VERSION = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    }
                }

                script{
                    DOC_ZIP_FILENAME = "${PKG_NAME}-${PKG_VERSION}.doc.zip"
                    junit_filename = "junit-${env.NODE_NAME}-${env.GIT_COMMIT.substring(0,7)}-pytest.xml"
                }

                tee("${pwd tmp: true}/logs/pippackages_system_${NODE_NAME}.log") {
                    bat "${tool 'CPython-3.6'} -m pip list"
                }
                bat "dir ${pwd tmp: true}"
                bat "dir ${pwd tmp: true}\\logs"
                
                bat "${tool 'CPython-3.6'} -m venv venv"
                
                script{
                    VENV_ROOT = "${WORKSPACE}\\venv\\"

                    VENV_PYTHON = "${WORKSPACE}\\venv\\Scripts\\python.exe"
                    bat "${VENV_PYTHON} --version"

                    VENV_PIP = "${WORKSPACE}\\venv\\Scripts\\pip.exe"
                    bat "${VENV_PIP} --version"
                }

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

                tee("${pwd tmp: true}/logs/pippackages_venv_${NODE_NAME}.log") {
                    bat "venv\\Scripts\\pip.exe list"
                }
                bat "venv\\Scripts\\devpi use https://devpi.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {    
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                }
                bat "dir"
            }
            post{
                always{
                    echo """Name                            = ${PKG_NAME}
Version                         = ${PKG_VERSION}
Report Directory                = ${REPORT_DIR}
documentation zip file          = ${DOC_ZIP_FILENAME}
Python virtual environment path = ${VENV_ROOT}
VirtualEnv Python executable    = ${VENV_PYTHON}
VirtualEnv Pip executable       = ${VENV_PIP}
junit_filename                  = ${junit_filename}
"""  
                    
                    dir(pwd(tmp: true)){
                        archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                        archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"

                    }
                }
                failure {
                    deleteDir()
                }
            }

        }
        stage("Python Package"){
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                tee("${pwd tmp: true}/logs/build.log") {
                    dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build -j ${NUMBER_OF_PROCESSORS}"
                    }
                
                }
            }
            post{
                always{
                    // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'build.log']]
                    dir(pwd(tmp: true)){
                        warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MSBuild', pattern: 'logs/build.log']]
                        archiveArtifacts artifacts: 'logs/build.log'
                    }
                }
            }
        }
        stage("Sphinx documentation"){
            when {
                equals expected: true, actual: params.BUILD_DOCS
            }
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                dir("build/docs/html"){
                    deleteDir()
                    echo "Cleaned out build/docs/html dirctory"

                }
                script{
                    // Add a line to config file so auto docs look in the build folder
                    def sphinx_config_file = 'source/docs/source/conf.py'
                    def extra_line = "sys.path.insert(0, os.path.abspath('${WORKSPACE}/build/lib'))"
                    def readContent = readFile "${sphinx_config_file}"
                    echo "Adding \"${extra_line}\" to ${sphinx_config_file}."
                    writeFile file: "${sphinx_config_file}", text: readContent+"\r\n${extra_line}\r\n"


                }
                echo "Building docs on ${env.NODE_NAME}"
                bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe --version"
                tee("${pwd tmp: true}/logs/build_sphinx.log") {
                    dir("build/lib"){
                        bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b html ${WORKSPACE}\\source\\docs\\source ${WORKSPACE}\\build\\docs\\html -d ${WORKSPACE}\\build\\docs\\doctrees"
    
                    }
                }
            }
            post{
                always {
                    dir(pwd(tmp: true)){
                        warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build_sphinx.log']]
                        archiveArtifacts artifacts: 'logs/build_sphinx.log'
                    }
                }
                success{
                    publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'build/docs/html', reportFiles: 'index.html', reportName: 'Documentation', reportTitles: ''])
                    script{
                        // Multibranch jobs add the slash and add the branch to the job name. I need only the job name
                        def alljob = env.JOB_NAME.tokenize("/") as String[]
                        def project_name = alljob[0]
                        dir('build/docs/') {
                            zip archive: true, dir: 'html', glob: '', zipFile: "${project_name}-${env.BRANCH_NAME}-docs-html-${env.GIT_COMMIT.substring(0,7)}.zip"
                        }
                    }
                }
            }
        
        }
        stage("Testing") {
            parallel {
                stage("Run Tox test") {
                    when {
                       equals expected: true, actual: params.TEST_RUN_TOX
                    }
                    environment {
                        PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
                    }
                    steps {
                        dir("source"){
                            bat "${VENV_PYTHON} -m tox --workdir ${WORKSPACE}\\.tox\\PyTest -- --junitxml=${REPORT_DIR}\\${junit_filename} --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${REPORT_DIR}\\coverage\\ --cov=py3exiv2bind"
                            // bat "${WORKSPACE}\\venv\\Scripts\\tox.exe --workdir ${WORKSPACE}\\.tox"
                        }
                        
                    }
                    post {
                        always{
                            dir("${REPORT_DIR}"){
                                bat "dir"
                                junit "${junit_filename}"
                            }              
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "${REPORT_DIR}/coverage", reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                        failure {
                            echo "Tox test failed. Removing ${WORKSPACE}\\.tox\\PyTest"
                            dir("${WORKSPACE}\\.tox\\PyTest"){
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
                        dir("${REPORT_DIR}/doctests"){
                            echo "Cleaning doctest reports directory"
                            deleteDir()
                        }
                        dir("source"){
                            dir("${REPORT_DIR}/doctests"){
                                echo "Cleaning doctest reports directory"
                                deleteDir()
                            }
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees -v" 
                        }
                        bat "move ${WORKSPACE}\\build\\docs\\output.txt ${REPORT_DIR}\\doctest.txt"
                        // dir("build/lib"){
                        //     bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest ${WORKSPACE}\\source\\docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees"
        
                        // }
                        // dir("build/docs/"){
                        //     bat "dir"
                        //     bat "move output.txt ${REPORT_DIR}\\doctest.txt"
                        // }
                        
                    }
                    post{
                        always {
                            dir("${REPORT_DIR}"){
                                archiveArtifacts artifacts: "doctest.txt"
                            }
                            // archiveArtifacts artifacts: "reports/doctest.txt"
                        }
                    }
                }
                stage("Run MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    steps{
                        dir("${REPORT_DIR}/mypy/html"){
                            deleteDir()
                            bat "dir"
                        }
                        script{
                            tee("${pwd tmp: true}/logs/mypy.log") {
                                try{
                                    dir("source"){
                                        bat "dir"
                                        bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe ${WORKSPACE}\\build\\lib\\py3exiv2bind --html-report ${REPORT_DIR}\\mypy\\html"
                                    }
                                } catch (exc) {
                                    echo "MyPy found some warnings"
                                }
                            }
                        }
                    }
                    post {
                        always {
                            dir(pwd(tmp: true)){
                                warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                            }
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: "${REPORT_DIR}/mypy/html/", reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
                        }
                    }
                }
            }

        }
        stage("Packaging") {
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                dir("source"){
                    bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py bdist_wheel sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                }

                dir("dist") {
                    archiveArtifacts artifacts: "*.whl", fingerprint: true
                    archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                }
            }
        }
        stage("Deploy to Devpi Staging") {

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
                            bat "venv\\Scripts\\devpi.exe upload --only-docs --from-dir build"
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
                stage("Source Distribution: .tar.gz") {
                    environment {
                        PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
                    }
                    steps {
                        echo "Testing Source tar.gz package in devpi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"

                        script {                          
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s tar.gz  --verbose"
                            echo "return code was ${devpi_test_return_code}"
                        }
                        echo "Finished testing Source Distribution: .tar.gz"
                    }
                    post {
                        failure {
                            echo "Tests for .tar.gz source on DevPi failed."
                        }
                    }

                }
                stage("Source Distribution: .zip") {
                    environment {
                        PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
                    }
                    steps {
                        echo "Testing Source zip package in devpi"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script {
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s zip --verbose"
                            echo "return code was ${devpi_test_return_code}"
                        }
                        echo "Finished testing Source Distribution: .zip"
                    }
                    post {
                        failure {
                            echo "Tests for .zip source on DevPi failed."
                        }
                    }
                }
                stage("Built Distribution: .whl") {
                    agent {
                        node {
                            label "Windows && Python3"
                        }
                    }
                    options {
                        skipDefaultCheckout(true)
                    }
                    steps {
                        echo "Testing Whl package in devpi"
                        bat "${tool 'CPython-3.6'} -m venv venv"
                        bat "venv\\Scripts\\pip.exe install tox devpi-client"
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"                        
                        }
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                        script{
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${PKG_NAME} -s whl  --verbose"
                            echo "return code was ${devpi_test_return_code}"
                        }
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
                            input 'Update project documentation?'
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
                            input "Release ${PKG_NAME} ${PKG_VERSION} to DevPi Production?"
                            withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"         
                            }

                            bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} production/release"

                            // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            //     bat "devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            //     bat "devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            //     bat "devpi push ${PKG_NAME}==${PKG_VERSION} production/release"
                            // }
                        }
                    }
                }
            }
        }
        // stage("Release to production") {
        //     when {
        //         expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
        //     }
        //     steps {
        //         script {
        //             withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
        //                 bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
        //                 bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
        //                 bat "venv\\Scripts\\devpi.exe push ${PKG_NAME}==${PKG_VERSION} production/${params.RELEASE}"
        //             }

        //         }
        //         node("Linux"){
        //             updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
        //         }
        //     }
        // }

    }
    post {
        cleanup {
            dir('_skbuild\\cmake-build\\_deps') {
                deleteDir()
            }
            // bat "venv\\Scripts\\python.exe setup.py clean --all"
            
            dir('dist') {
                deleteDir()
            }

            dir('build') {
                deleteDir()
            }
            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            bat "${VENV_PYTHON} setup.py clean --all"
                            } catch (Exception ex) {
                            // echo "Unable to succesfully run clean. Purging source directory."
                                dir("_skbuild"){
                                    deleteDir()
                                }
                                try{
                                    bat "${VENV_PYTHON} setup.py clean --all"
                                } catch (Exception ex2) {
                                    echo "Unable to succesfully run clean. Purging source directory."
                                }
                                deleteDir()
                            }
                        bat "dir"
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