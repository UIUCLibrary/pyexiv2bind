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
                    sh 'ls -la'
                }

                bat "${env.TOX}"
//                dir('build') {
//                    bat 'ctest --verbose'
//                }


            }

        }
        stage("Packaging"){
            steps{
                dir('build') {
                    bat "${env.PYTHON3} setup.py bdist_wheel"
                    archiveArtifacts artifacts: "dist/*.whl", fingerprint: true
                }
            }
        }
    }
}
