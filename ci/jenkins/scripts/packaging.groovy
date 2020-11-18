
def test_pkg(glob, timeout_time){

    def pkgFiles = findFiles( glob: glob)
    if( pkgFiles.size() == 0){
        error "Unable to check package. No files found with ${glob}"
    }
    echo "Starting ${glob}"
    pkgFiles.each{
        timeout(timeout_time){
            try{
                echo "Testing ${it} on ${env.NODE_NAME}"
                if(isUnix()){
                    sh(label: "Testing ${it}",
                       script: """python --version
                                  tox --installpkg=${it.path} -e py -vv --workdir=./.tox --recreate
                                  """
                    )
                } else {
                    bat(label: "Testing ${it}",
                        script: """python --version
                                   tox --installpkg=${it.path} -e py -vv --workdir=./.tox --recreate
                                   """
                    )
                }
                echo "Testing ${it} on ${env.NODE_NAME} - Success"
            } catch (e){
                echo "Testing ${it} on ${env.NODE_NAME} - Failed"
                throw e

            } finally{
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: '.tox/', type: 'INCLUDE']
                    ]
                )
            }
        }
    }
}
def test_one(pythonVersion, dockerAgent, dockerImageName, stashName, glob){


    def docker_build
    ws{
        checkout scm
        try{
            docker_build = docker.build(dockerImageName,"-f ${dockerAgent.filename} ${dockerAgent.additionalBuildArgs} .")
            docker_build.inside{
                cleanWs(
                    notFailBuild: true,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    patterns: [
                            [pattern: '.git/**', type: 'EXCLUDE'],
                            [pattern: 'tests/**', type: 'EXCLUDE'],
                            [pattern: 'tox.ini', type: 'EXCLUDE'],
                        ]
                )
                unstash stashName
                catchError(stageResult: 'FAILURE') {
                    test_pkg(glob, 15)
                }

            }
        } finally {
            if(isUnix()){
                sh "docker image rm ${docker_build.id}"
            } else {
                bat "docker image rm ${docker_build.id}"
            }
            cleanWs()
        }
    }
}
def test_package_stages(args = [:]){
    def platform        = args['platform']
    def pythonVersion   = args['pythonVersion']
    def whlTestAgent    = args['whlTestAgent']
    def sdistTestAgent  = args['sdistTestAgent']
    def sdistStashName  = args['sdistStashName']
    def whlStashName    = args['whlStashName']
    parallel(
        "Testing Wheel Package": {
            node(whlTestAgent.label){
                def dockerImageName = "${currentBuild.projectName}:wheel${pythonVersion}".replaceAll("-", "").toLowerCase()
                test_one(pythonVersion, whlTestAgent, dockerImageName, whlStashName, "dist/*.whl")
            }
        },
        "Testing sdist Package": {
            node(sdistTestAgent.label){
                def dockerImageName = "${currentBuild.projectName}:sdist${pythonVersion}".replaceAll("-", "").toLowerCase()
                test_one(pythonVersion, sdistTestAgent, dockerImageName, sdistStashName, "dist/*.zip,dist/*.tar.gz")
            }
        }
    )
}

return this
