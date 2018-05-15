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
        booleanParam(name: "ADDITIONAL_TESTS", defaultValue: true, description: "Run additional tests")
        booleanParam(name: "DEPLOY_DEVPI", defaultValue: true, description: "Deploy to devpi on http://devpy.library.illinois.edu/DS_Jenkins/${env.BRANCH_NAME}")
        choice(choices: 'None\nrelease', description: "Release the build to production. Only available in the Master branch", name: 'RELEASE')
        string(name: 'URL_SUBFOLDER', defaultValue: "py3exiv2bind", description: 'The directory that the docs should be saved under')
    }
    stages {
        stage("Configure") {
            steps {
                bat "${tool 'CPython-3.6'} -m venv venv"
                bat "venv\\Scripts\\pip.exe install -r requirements.txt -r requirements-dev.txt"
            }

        }
        stage("Build") {
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                bat "venv\\Scripts\\python.exe setup.py build"
            }

        }
        stage("Testing") {
            environment {
                PATH = "${tool 'cmake3.11.1'}//..//;$PATH"
            }
            steps {
                bat "venv\\Scripts\\tox.exe"
                // node('Linux') {
                //     sh 'wget -N https://jenkins.library.illinois.edu/jenkins/userContent/sample_images.tar.gz'
                //     sh 'tar -xzf sample_images.tar.gz'
                //     stash includes: 'sample_images/**', name: 'sample_images'
                // }
                // dir("tests") {
                //     unstash 'sample_images'
                // }
                // stash includes: 'tests/**', name: 'tests'
                // //withEnv(['EXIV2_DIR=thirdparty\\dist\\exiv2\\share\\exiv2\\cmake']){
                //     bat "${tool 'Python3.6.3_Win64'} -m tox -e py36"
                // //}


            }

        }
        // stage("Additional tests") {
        //     when {
        //         expression { params.ADDITIONAL_TESTS == true }
        //     }

        //     steps {
        //         parallel(
        //                 "Documentation": {
        //                     bat "${tool 'Python3.6.3_Win64'} -m tox -e docs"
        //                     dir('.tox/dist/html/') {
        //                         stash includes: '**', name: "HTML Documentation", useDefaultExcludes: false
        //                     }
        //                 }
        //         )
        //     }

        // }

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
        stage("Deploying to Devpi staging index") {
            when {
                expression { params.DEPLOY_DEVPI == true }
            }
            steps {
                bat "venv\\Scripts\\devpi.exe use http://devpy.library.illinois.edu"
                withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                    bat "venv\\Scripts\\devpi.exe login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                    bat "venv\\Scripts\\devpi.exe use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                    script {
                        bat "venv\\Scripts\\devpi.exe upload --from-dir dist"
                        try {
                            bat "venv\\Scripts\\devpi.exe upload --only-docs --from-dir dist"
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
                                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                                node("Windows") {
                                    deleteDir()
                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Source package in devpi"
                                        script {
                                             def devpi_test = bat(returnStdout: true, script: "${tool 'CPython-3.6'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name}==${version} --verbose -s tar.gz").trim()
                                             if(devpi_test =~ 'tox command failed') {
                                                echo "${devpi_test}"
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
                                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                                node("Windows") {
                                    deleteDir()

                                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                                        bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                                        bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                                        echo "Testing Whl package in devpi"
                                        script {
                                            def devpi_test =  bat(returnStdout: true, script: "${tool 'CPython-3.6'} -m devpi test --index http://devpy.library.illinois.edu/${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging ${name}==${version} --verbose -s whl").trim()
                                            if(devpi_test =~ 'tox command failed') {
                                                echo "${devpi_test}"
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
                        def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                        def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                        withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                            bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                            bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                            bat "${tool 'CPython-3.6'} -m devpi push ${name}==${version} ${DEVPI_USERNAME}/${env.BRANCH_NAME}"
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
                    def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                    def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'CPython-3.6'} -m devpi push ${name}==${version} production/${params.RELEASE}"
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
                def name = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --name").trim()
                def version = bat(returnStdout: true, script: "@${tool 'CPython-3.6'} setup.py --version").trim()
                try {
                    withCredentials([usernamePassword(credentialsId: 'DS_devpi', usernameVariable: 'DEVPI_USERNAME', passwordVariable: 'DEVPI_PASSWORD')]) {
                        bat "${tool 'CPython-3.6'} -m devpi login ${DEVPI_USERNAME} --password ${DEVPI_PASSWORD}"
                        bat "${tool 'CPython-3.6'} -m devpi use /${DEVPI_USERNAME}/${env.BRANCH_NAME}_staging"
                        bat "${tool 'CPython-3.6'} -m devpi remove -y ${name}==${version}"
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