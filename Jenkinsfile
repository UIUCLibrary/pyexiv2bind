#!groovy
@Library("ds-utils@v0.2.0")
// Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

pipeline {
    agent {
        label "Windows"
    }
    parameters {
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
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
            }

        }
        stage("Testing") {
            steps {
                node('!Windows') {
                    sh 'wget https://jenkins.library.illinois.edu/jenkins/userContent/sample_images.tar.gz'
                    sh 'tar -xzf sample_images.tar.gz'
                    stash includes: 'sample_images/**', name: 'sample_images'
                }
                dir("tests") {
                    unstash 'sample_images'
                }
                stash includes: 'tests/**', name: 'tests'
                bat "${tool 'Python3.6.3_Win64'} -m tox"
                // bat "${env.TOX}"
//                }


            }

        }
        stage("Packaging") {
            steps {
                //bat """${env.PYTHON3} -m venv venv
                bat """${tool 'Python3.6.3_Win64'} -m venv venv
                       call venv\\Scripts\\activate.bat
                       pip install -r requirements-dev.txt
                       python setup.py bdist_wheel
                       """
                dir("dist") {
                    archiveArtifacts artifacts: "*.whl", fingerprint: true
                }
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
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                    script {
                        try {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --with-docs --formats bdist_wheel,sdist"

                        } catch (exc) {
                            echo "Unable to upload to devpi with docs. Trying without"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --formats bdist_wheel,sdist"
                        }
                    }
                // bat "${tool 'Python3.6.3_Win64'} -m devpi test py3exiv2bind -s win"
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

                            node("Windows"){
                                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                                    echo "Testing Source package in devpi"
                                    bat "${tool 'Python3.6.3_Win64'} -m install py3exiv2bind"
                                    unstash "tests"
                                    bat "dir"
                                    bat "${tool 'Python3.6.3_Win64'} -m pytest"
                                }
                            }
                        },
                        "Whl": {

                            node("Windows"){
                                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                                    echo "Testing Whl package in devpi"
                                    bat "${tool 'Python3.6.3_Win64'} -m install py3exiv2bind"
                                    unstash "tests"
                                    bat "dir"
                                    bat "${tool 'Python3.6.3_Win64'} -m pytest"
                                }
                            }
                        }
                )
                
            }
        }
    }
    post {
        success {
            echo "Cleaning up workspace"
            deleteDir()
        }
    }
}