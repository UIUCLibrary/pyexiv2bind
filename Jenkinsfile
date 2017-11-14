#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

pipeline {
    agent {
        label "Windows"
    }
    environment {
        mypy_args = "--junit-xml=mypy.xml"
        pytest_args = "--junitxml=reports/junit-{env:OS:UNKNOWN_OS}-{envname}.xml --junit-prefix={env:OS:UNKNOWN_OS}  --basetemp={envtmpdir}"
    }
    parameters {
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
    }
    stages {
        stage("Checking Out from Source Control") {
            steps {
                deleteDir()
                checkout([
                        $class                           : 'GitSCM',
                        branches                         : [
                                [name: "*/${env.BRANCH_NAME}"]
                        ],
                        doGenerateSubmoduleConfigurations: false,
                        extensions                       : [
                                [
                                        $class             : 'SubmoduleOption',
                                        disableSubmodules  : false,
                                        parentCredentials  : false,
                                        recursiveSubmodules: true,
                                        reference          : '',
                                        trackingSubmodules : false
                                ]
                        ],
                        submoduleCfg                     : [],
                        userRemoteConfigs                : [
                                [
                                        credentialsId: 'ccb29ea2-6d0f-4bfa-926d-6b4edd8995a8',
                                        url          : 'git@github.com:UIUCLibrary/pyexiv2bind.git'
                                ]
                        ]
                ])
                bat "dir"
            }

        }
        stage("Testing") {
            steps {
                node('Linux') {
                    sh 'wget https://jenkins.library.illinois.edu/jenkins/userContent/sample_images.tar.gz'
                    sh 'tar -xzf sample_images.tar.gz'
                    stash includes: 'sample_images/**', name: 'sample_images'
                }
                dir("tests") {
                    unstash 'sample_images'
                }
                stash includes: 'tests/**', name: 'tests'
                //withEnv(['EXIV2_DIR=thirdparty\\dist\\exiv2\\share\\exiv2\\cmake']){
                    bat "${tool 'Python3.6.3_Win64'} -m tox"
                //}


            }

        }
        stage("Additional tests") {
            when {
                expression { params.ADDITIONAL_TESTS == true }
            }

            steps {
                parallel(
                        "Documentation": {
                            bat "${tool 'Python3.6.3_Win64'} -m tox -e docs"
                            dir('.tox/dist/html/') {
                                stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
                            }
                        }
                )
            }

        }

        stage("Packaging") {
            steps {
                // withEnv(['EXIV2_DIR=thirdparty\\dist\\exiv2\\share\\exiv2\\cmake']){
                    bat """${tool 'Python3.6.3_Win64'} -m venv venv
                           call venv\\Scripts\\activate.bat
                           pip install -r requirements.txt
                           pip install -r requirements-dev.txt
                           python setup.py sdist bdist_wheel
                           """
                    dir("dist") {
                        archiveArtifacts artifacts: "*.whl", fingerprint: true
                        archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                    }
                // }
            }
        }
        stage("Deploying to Devpi") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                bat "${tool 'Python3.6.3_Win64'} -m devpi use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi upload --from-dir dist"
                        try {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --only-docs"
                        } catch (exc) {
                            echo "Unable to upload docs."
                        }
                    }
                }

            }
        }
        stage("Test Devpi packages") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                parallel(
                        "Source": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                node("Windows") {
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Source package in devpi"
                                        script {
                                             def devpi_test = bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s tar.gz").trim()
                                             if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                        }
                                        // bat "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpi.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging py3exiv2bind -s tar.gz"
                                        // bat "${tool 'Python3.6.3_Win64'} -m venv venv"
                                        // unstash "tests"
                                        // bat """ ${tool 'Python3.6.3_Win64'} -m pip install -Iv ${name}==${version} -i http://devpi.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging --no-cache-dir --no-binary :all: --trusted-host devpi.library.illinois.edu
                                            // call venv\\Scripts\\activate.bat
                                            // ${tool 'Python3.6.3_Win64'} -m pytest"""
                                    }
                                }

                            }
                        },
                        "Wheel": {
                            script {
                                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                                echo("using ${name} for name and ${version} for version")
                                node("Windows") {

                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Whl package in devpi"
                                        script {
                                            def devpi_test =  bat(returnStdout: true, script: "${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name} -s whl").trim()
                                            if(devpi_test =~ 'tox command failed') {
                                                error("Tox command failed")
                                            }
                                            
                                        }
                                        // bat " ${tool 'Python3.6.3_Win64'} -m devpi test --index http://devpi.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging py3exiv2bind -s whl"
                                        // bat "${tool 'Python3.6.3_Win64'} -m venv venv"
                                        // unstash "tests"
                                        // bat """ ${tool 'Python3.6.3_Win64'} -m pip install -Iv ${name}==${version} -i http://devpi.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging --no-cache-dir  --only-binary bdist_wheel --trusted-host devpi.library.illinois.edu
//                                            call venv\\Scripts\\activate.bat
  //                                          ${tool 'Python3.6.3_Win64'} -m pytest"""
                                    }
                                }

                            }
                        }
                )

            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script {
                        def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                        }

                    }
                }
            }
        }
        stage("Release to production") {
            when {
                expression { params.RELEASE != "None" && env.BRANCH_NAME == "master" }
            }
            steps {
                script {
                    def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi push ${name}==${version} production/${params.RELEASE}"
                    }

                }
                node("Linux"){
                    updateOnlineDocs url_subdomain: params.URL_SUBFOLDER, stash_name: "HTML Documentation"
                }
            }
        }

    }
    post {
        always {
            script {
                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                try {
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'Python3.6.3_Win64'} -m devpi remove -y ${name}==${version}"
                    }
                } catch (err) {
                    echo "Unable to clean up ${env.BRANCH_NAME}_staging"
                }


            }
        }
        
        success {
            echo "Cleaning up workspace"
            deleteDir()
        }
    }
}