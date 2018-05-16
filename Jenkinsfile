#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

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
    }
    environment {
        build_number = VersionNumber(projectStartDate: '2018-3-27', versionNumberString: '${BUILD_DATE_FORMATTED, "yy"}${BUILD_MONTH, XX}${BUILDS_THIS_MONTH, XX}', versionPrefix: '', worstResultForIncrement: 'SUCCESS')
    }
    parameters {
        booleanParam(name: "BUILD_DOCS", defaultValue: true, description: "Build documentation")
        booleanParam(name: "TEST_RUN_DOCTEST", defaultValue: true, description: "Test documentation")
        booleanParam(name: "TEST_RUN_FLAKE8", defaultValue: true, description: "Run Flake8 static analysis")
        booleanParam(name: "TEST_RUN_MYPY", defaultValue: true, description: "Run MyPy static analysis")
        booleanParam(name: "TEST_RUN_TOX", defaultValue: true, description: "Run Tox Tests")
        
        // booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
    }
    stages {
        stage("Configure") {
            steps {
                tee("pippackages_system_${NODE_NAME}.log") {
                    bat "${tool 'CPython-3.6'} -m pip list"
                }
                
                bat "${tool 'CPython-3.6'} -m venv venv"
                bat "venv\\Scripts\\pip.exe install devpi-client -r requirements.txt -r requirements-dev.txt"

                tee("pippackages_venv_${NODE_NAME}.log") {
                    bat "venv\\Scripts\\pip.exe list"
                }

                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi use https://devpi.library.illinois.edu"
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                }
            }
            post{
                always{
                    archiveArtifacts artifacts: "pippackages_system_${NODE_NAME}.log"
                    archiveArtifacts artifacts: "pippackages_venv_${NODE_NAME}.log"
                }
            }

        }
        stage("Python Package"){
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                tee('build.log') {
                    bat "venv\\Scripts\\python.exe setup.py build"
                }
            }
            post{
                always{
                    // warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'build.log']]
                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MSBuild', pattern: 'build.log']]
                    archiveArtifacts artifacts: 'build.log'
                }
            }
        }
        stage("Sphinx documentation"){
            when {
                equals expected: true, actual: params.BUILD_DOCS
            }
            steps {
                bat 'mkdir "build/docs/html"'
                echo "Building docs on ${env.NODE_NAME}"
                tee('build_sphinx.log') {
                    bat script: "venv\\Scripts\\python.exe setup.py build_sphinx"                            
                }
            }
            post{
                always {
                    warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'build_sphinx.log']]
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
                    environment {
                        PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
                    }
                    steps {
                        bat "venv\\Scripts\\tox.exe"
                    }
                }
                stage("Run Doctest Tests"){
                    when {
                       equals expected: true, actual: params.TEST_RUN_DOCTEST
                    }
                    steps {
                        bat "venv\\Scripts\\sphinx-build.exe -b doctest -d build/docs/doctrees docs/source reports/doctest"
                    }
                    post{
                        always {
                            archiveArtifacts artifacts: 'reports/doctest/output.txt'
                        }
                    }
                }
                stage("Run MyPy Static Analysis") {
                    when {
                        equals expected: true, actual: params.TEST_RUN_MYPY
                    }
                    steps{
                        bat 'mkdir "reports\\mypy\\html"'
                        script{
                            try{
                                tee('mypy.log') {
                                    bat "venv\\Scripts\\mypy.exe -p py3exiv2bind --html-report reports/mypy/html"
                                }
                            } catch (exc) {
                                echo "MyPy found some warnings"
                            }      
                        }
                    }
                    post {
                        always {
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'MyPy', pattern: 'mypy.log']], unHealthy: ''
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
                bat "venv\\Scripts\\python.exe setup.py bdist_wheel sdist"
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
                // bat "venv\\Scripts\\devpi.exe use https://devpi.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
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
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()                            
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                echo "Testing Source package in devpi"
                                def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz  --verbose"
                                echo "return code was ${devpi_test_return_code}"
                                }
                            echo "Finished testing Source Distribution: .tar.gz"
                        }
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
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --version").trim()
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                echo "Testing Source package in devpi"
                                def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${name} -s zip --verbose"
                                echo "return code was ${devpi_test_return_code}"
                                }
                            echo "Finished testing Source Distribution: .zip"
                        }
                    }
                    post {
                        failure {
                            echo "Tests for .zip source on DevPi failed."
                        }
                    }
                }
                stage("Built Distribution: .whl") {
                    steps {
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'}  setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                                
                                bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                echo "Testing Whl package in devpi"
                                def devpi_test_return_code = bat returnStatus: true, script: "venv\\Scripts\\devpi.exe test --index https://devpi.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}_staging ${name} -s whl  --verbose"
                                echo "return code was ${devpi_test_return_code}"
                            }
                                
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
                        def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
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
                    def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
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
            // anyOf {
            //     equals expected: "master", actual: env.BRANCH_NAME
            //     equals expected: "dev", actual: env.BRANCH_NAME
            // }
            script {
                if (env.BRANCH_NAME == "master" || env.BRANCH_NAME == "dev"){
                    def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        try {
                            bat "venv\\Scripts\\devpi.exe remove -y ${name}==${version}"
                        } catch (Exception ex) {
                            echo "Failed to remove ${name}==${version} from ${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        }
                        
                    }
                }
            }
        }
        // always {
        //     script {
        //         def name = bat(returnStdout: true, script: "venv\\Scripts\\python.exe setup.py --name").trim()
        //         def version = bat(returnStdout: true, script: "venv\\Scripts\\python.exe setup.py --version").trim()
        //         try {
        //             withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
        //                 bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
        //                 bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
        //                 bat "venv\\Scripts\\devpi.exe remove -y ${name}==${version}"
        //             }
        //         } catch (err) {
        //             echo "Unable to clean up ${env.BRANCH_NAME}_staging"
        //         }


        //     }
        // }
        
        success {
            echo "Cleaning up workspace"
            deleteDir()
        }
    }
}