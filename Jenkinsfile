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
                bat 'mkdir build'


            }

        }
    }
}
