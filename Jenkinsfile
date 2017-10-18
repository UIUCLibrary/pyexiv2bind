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
        choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
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
                node('Linux') {
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
                bat """${tool 'Python3.6.3_Win64'} -m venv venv
                       call venv\\Scripts\\activate.bat
                       pip install -r requirements-dev.txt
                       python setup.py sdist bdist_wheel
                       """
                dir("dist") {
                    archiveArtifacts artifacts: "*.whl", fingerprint: true
                    archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
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
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
//                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}"
                    script {
                        try {
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --with-docs dist"
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --with-docs --formats bdist_wheel,sdist"

                        } catch (exc) {
                            echo "Unable to upload to devpi with docs. Trying without"
                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --from-dir dist"
//                            bat "${tool 'Python3.6.3_Win64'} -m devpi upload --formats bdist_wheel,sdist"
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

                            node("Windows") {
                                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                    echo "Testing Source package in devpi"
                                    bat "${tool 'Python3.6.3_Win64'} -m venv venv"
                                    unstash "tests"
                                    bat """ ${tool 'Python3.6.3_Win64'} -m pip install py3exiv2bind --no-cache-dir --no-use-wheel
                                            call venv\\Scripts\\activate.bat
                                            ${tool 'Python3.6.3_Win64'} -m pytest"""
                                }
                            }
                        },
                        "Wheel": {

                            node("Windows") {
                                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                    echo "Testing Whl package in devpi"
                                    bat "${tool 'Python3.6.3_Win64'} -m venv venv"
                                    unstash "tests"
                                    bat """ ${tool 'Python3.6.3_Win64'} -m pip install py3exiv2bind --no-cache-dir  --only-binary bdist_wheel
                                            call venv\\Scripts\\activate.bat
                                            ${tool 'Python3.6.3_Win64'} -m pytest"""
                                }
                            }
                        }
                )

            }
            post {
                success {
                    echo "it Worked. Pushing file to ${env.BRANCH_NAME} index"
                    script{
                        def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                        echo "I got ${name} with version of ${version}!"
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
                expression {params.RELEASE != "None" && env.BRANCH_NAME == "master"}
            }
            steps {
                echo "I'm Releasing it!"
            }
        }

    }
    post {
        always {
            script {
                def name = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --name").trim()
                def version = bat(returnStdout: true, script: "@${tool 'Python3.6.3_Win64'} setup.py --version").trim()
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "${tool 'Python3.6.3_Win64'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "${tool 'Python3.6.3_Win64'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    bat "${tool 'Python3.6.3_Win64'} -m devpi remove -y ${name}==${version}"
                }

            }
        }
        success {
            echo "Cleaning up workspace"
            deleteDir()
        }
    }
}