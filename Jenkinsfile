pipeline {
    agent any
    stages {

        stage("Building") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: false, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'ccb29ea2-6d0f-4bfa-926d-6b4edd8995a8', url: 'git@github.com:UIUCLibrary/pyexiv2bind.git']]])
                bat 'mkdir build'
                dir('build') {
                    bat 'call "%vs140comntools%..\\..\\VC\\vcvarsall.bat" x86_amd64 && cmake .. -GNinja'
                    bat 'cmake --build . --target project_libexiv2'
                    bat 'cmake --build . --target add_tests'
                    bat 'ctest'
                }


            }

        }
    }
}
