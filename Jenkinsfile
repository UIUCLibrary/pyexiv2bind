pipeline {
    agent any
    stages {

        stage("Building") {
            agent {
                label "Windows"
            }

            steps {
                deleteDir()

                checkout([
                        $class: 'GitSCM',
                        branches: scm.branches,
                        doGenerateSubmoduleConfigurations: true,
                        extensions: scm.extensions + [[$class: 'SubmoduleOption', parentCredentials: true]],
                        userRemoteConfigs: scm.userRemoteConfigs
                    ])

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
