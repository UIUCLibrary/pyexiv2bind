pipeline {
    agent any
    stages {

        stage("Building") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()
                checkout scm
                bat 'git submodule update --init --recursive'
                bat 'mkdir build'
                dir('build') {
                    bat 'cmake ..'
                    bat 'cmake --build . --target add_tests'
                    bat 'ctest'
                }


            }

        }
    }
}
