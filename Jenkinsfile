#!groovy
@Library("ds-utils@v0.2.0") // Uses library from https://github.com/UIUCLibrary/Jenkins_utils
import org.ds.*

pipeline {
    agent {
        label "Windows"
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
                bat "${env.TOX}"
//                }


            }

        }
        stage("Packaging") {
            steps {
//                virtualenv python_path: env.PYTHON3, requirements_file: "requirements-dev.txt", windows: true, "python setup.py bdist_wheel"
                bat """${env.PYTHON3} -m venv venv
                       dir
                       dir venv\\
                       dir venv\\Scripts\\
                       venv\\Scripts\\activate.bat
                       pip install -r requirements-dev.txt
                       python setup.py bdist_wheel
                       """
//                bat "${env.PYTHON3} setup.py bdist_wheel"
                dir("dist"){
                    bat "dir"
                    archiveArtifacts artifacts: "*.whl", fingerprint: true
                }
            }
        }
    }
    post {
        success {
            echo "Cleaning up workspace"
        }
    }
}
