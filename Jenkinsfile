#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*
def name = "unknown"
def version = "unknown"
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
        
        // booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: false, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
    }
    stages {
        stage("Configure") {
            steps {
                script{
                    if (params.FRESH_WORKSPACE == true){
                        deleteDir()
                        checkout scm
                    }
                }
                dir("logs"){
                    echo "looking in ${pwd tmp: true}"
                    bat "dir ${pwd tmp: true}"
                    deleteDir()
                    echo "Cleaned out logs directory"
                    bat "dir"
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
                        name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                        version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    }
                }

                tee("logs/pippackages_system_${NODE_NAME}.log") {
                    bat "${tool 'CPython-3.6'} -m pip list"
                }
                
                bat "${tool 'CPython-3.6'} -m venv venv"
                bat "venv\\Scripts\\python.exe -m pip install -U pip"
                bat "venv\\Scripts\\pip.exe install devpi-client -r source\\requirements.txt -r source\\requirements-dev.txt --upgrade-strategy only-if-needed"

                tee("logs/pippackages_venv_${NODE_NAME}.log") {
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
                    archiveArtifacts artifacts: "logs/pippackages_system_${NODE_NAME}.log"
                    archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
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
                echo "Package name: ${name}"
                echo "Version     : ${version}"

                tee('logs/build.log') {
                    dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build -j ${NUMBER_OF_PROCESSORS}"
                    }
                
                }
            }
            post{
                always{
                    // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'build.log']]
                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MSBuild', pattern: 'logs/build.log']]
                    archiveArtifacts artifacts: 'logs/build.log'
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
                tee('logs/build_sphinx.log') {
                    dir("build/lib"){
                        bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest ${WORKSPACE}\\source\\docs\\source ${WORKSPACE}\\build\\docs\\html -d ${WORKSPACE}\\build\\docs\\doctrees"
    
                    }
                    // dir("source"){
                    //     bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py develop -b ${WORKSPACE}\\build"
                    //     bat script: "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build_sphinx --build-dir ${WORKSPACE}\\build\\docs"
                    // }
                        
                        // bat script: "${WORKSPACE}\\venv\\Scripts\\python.exe -m sphinx source\\docs\\source ${WORKSPACE}\\build\\docs\\html -d ${WORKSPACE}\\build\\docs\\doctrees"
                    // }
                    // }
                }
            }
            post{
                // cleanup{
                //     dir("source"){
                //         // bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py develop --uninstall"
                //         // dir("py3exiv2bind"){
                //             // bat "del *.pyd"
                            
                //         // }
                //     }
                    
                // }
                always {
                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build_sphinx.log']]
                    archiveArtifacts artifacts: 'logs/build_sphinx.log'
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
                            bat "${WORKSPACE}\\venv\\Scripts\\tox.exe --workdir ${WORKSPACE}\\.tox"
                        }
                        
                    }
                    post {
                        failure {
                            bat "@RD /S /Q ${WORKSPACE}\\.tox"
                        }
                    }
                }
                stage("Run Doctest Tests"){
                    when {
                       equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps {
                        dir("reports"){
                            echo "Running doctest"
                        }
                        dir("build/lib"){
                            bat "${WORKSPACE}\\venv\\Scripts\\sphinx-build.exe -b doctest ${WORKSPACE}\\source\\docs\\source ${WORKSPACE}\\build\\docs -d ${WORKSPACE}\\build\\docs\\doctrees"
        
                        }
                        dir("build/docs/"){
                            bat "dir"
                            bat "move output.txt ${WORKSPACE}\\reports\\doctest.txt"
                        }
                        
                    }
                    post{
                        always {
                            archiveArtifacts artifacts: 'reports/doctest.txt'
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
                            tee('logs/mypy.log') {
                                try{
                                    dir("source"){
                                        bat "dir"
                                        bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe ${WORKSPACE}\\build\\lib\\py3exiv2bind --html-report ${WORKSPACE}\\reports\\mypy\\html"
                                    }
                                } catch (exc) {
                                    echo "MyPy found some warnings"
                                }
                            }
                        }
                        // script{
                        //     try{
                        //         tee('mypy.log') {
                        //             def mypy_returnCode = bat returnStatus: true, script: "venv\\Scripts\\mypy.exe -p py3exiv2bind --html-report reports/mypy/html"
                        //         }
                        //     } catch (exc) {
                        //         echo "MyPy found some warnings"
                        //     }      
                        // }
                    }
                    post {
                        always {
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'logs/mypy.log']], unHealthy: ''
                            publishHTML([allowMissing: false, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy/html/', reportFiles: 'index.html', reportName: 'MyPy HTML Report', reportTitles: ''])
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
                
                // withEnv(['EXIV2_DIR=thirdparty\\dist\\exiv2\\share\\exiv2\\cmake']){
                    // bat """${tool 'Python3.6.3_Win64'} -m venv venv
                    //        call venv\\Scripts\\activate.bat
                    //        pip install -r requirements.txt
                    //        pip install -r requirements-dev.txt
                    //        pip list > installed_packages.txt
                    //        python setup.py sdist bdist_wheel
                    //        """
                    // archiveArtifacts artifacts: "installed_packages.txt"
                    dir("dist") {
                        archiveArtifacts artifacts: "*.whl", fingerprint: true
                        archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                    }
                // }
            }
        }
        stage("Deploy to Devpi Staging") {
            // when {
            //     expression { params.DEPLOY_DEVPI == true && (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev")}
            // }
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
                            bat "venv\\Scripts\\devpi.exe upload --only-docs --from-dir dist"
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

            // when {
            //     expression { params.DEPLOY_DEVPI == true && (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev")}
            // }
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
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        //     bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        // }
                        script {
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()                            
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${name} -s tar.gz  --verbose"
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
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        //     bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        // }
                        script {
                            // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                            // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --version").trim()
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${name} -s zip --verbose"
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
                        // withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        //     bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        //     bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        // }
                        script{
                            def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${name} -s whl  --verbose"
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
                        // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                        // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "venv\\Scripts\\devpi.exe push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }

                    }
                }
                failure {
                    echo "At least one package format on DevPi failed."
                }
            }
        }
        stage("Release to production") {
            when {
                expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
            }
            steps {
                script {
                    // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "venv\\Scripts\\devpi.exe push ${name}==${version} production/${params.RELEASE}"
                    }

                }
                node("Linux"){
                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
                }
            }
        }

    }
    post {
        cleanup{
            echo "Cleaning up."
            script {
                if(fileExists('source/setup.py')){
                    dir("source"){
                        try{
                            bat "${WORKSPACE}\\venv\\Scripts\\python.exe setup.py clean --all"
                        } catch (Exception ex) {
                            deleteDir()
                        }   
                    }
                }
            }
            // anyOf {
            //     equals expected: "master", actual: env.BRANCH_NAME
            //     equals expected: "dev", actual: env.BRANCH_NAME
            // }

            script {
                
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login DS_Jenkins --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /DS_Jenkins/${env.BRANCH_NAME}_staging"
                    }

                    // def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    // def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()

                    try {
                        def devpi_remove_return_code = bat returnStatus: true, script:"venv\\Scripts\\devpi.exe remove -y ${name}==${version}"
                        echo "Devpi remove exited with code ${devpi_remove_return_code}"

                    } catch (Exception ex) {
                        echo "Failed to remove ${name}==${version} from DS_Jenkins/${env.BRANCH_NAME}_staging"                       
                    }
                }
            }
        } 
        always {
            bat "dir /s/b *.*"
        //     // echo "Cleaning up workspace"
        //     // deleteDir()
        }
    }
}