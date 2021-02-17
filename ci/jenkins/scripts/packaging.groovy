def getNodeLabel(agent){
    def label
    if (agent.containsKey("dockerfile")){
        return agent.dockerfile.label
    }
    return label
}
def getToxEnv(args){
    try{
        def pythonVersion = args.pythonVersion.replace(".", "")
        return "py${pythonVersion}"
    } catch(e){
        return "py"
    }
}

def getAgent(args, dockerImageName=null){
    if (args.agent.containsKey("label")){
        return { inner ->
            node(args.agent.label){
                ws{
                    inner()
                }
            }
        }

    }

    if (args.agent.containsKey("dockerfile")){
        def nodeLabel = getNodeLabel(args.agent)
        return { inner ->
            node(nodeLabel){
                ws{
                    checkout scm
                    def dockerImage
                    dockerImageName = dockerImageName ? dockerImageName: "${currentBuild.fullProjectName}_${getToxEnv(args)}".replaceAll("-", "_").replaceAll('/', "_").replaceAll(' ', "").toLowerCase()
                    lock("docker build-${env.NODE_NAME}"){
                        dockerImage = docker.build(dockerImageName, "-f ${args.agent.dockerfile.filename} ${args.agent.dockerfile.additionalBuildArgs} .")
                    }
                    dockerImage.inside(){
                        inner()
                    }
                }
            }
        }
    }
    error('Invalid agent type, expect [dockerfile,label]')
}

def testPkg(args = [:]){
    def tox = args['toxExec'] ? args['toxExec']: "tox"
    def setup = args['testSetup'] ? args['testSetup']: {
        checkout scm
        unstash "${args.stash}"
    }
    def teardown =  args['testTeardown'] ? args['testTeardown']: {}

    def agentRunner = getAgent(args)
    agentRunner {
        setup()
        try{
            findFiles(glob: args.glob).each{
                def toxCommand = "${tox} --installpkg ${it.path} -e ${getToxEnv(args)}"
                if(isUnix()){
                    sh(label: "Testing tox version", script: "${tox} --version")
//                     toxCommand = toxCommand + " --workdir /tmp/tox"
                    sh(label: "Running Tox", script: toxCommand)
                } else{
                    bat(label: "Testing tox version", script: "${tox} --version")
                    toxCommand = toxCommand + " --workdir %TEMP%\\tox"
                    bat(label: "Running Tox", script: toxCommand)
                }
            }
        } finally{
            teardown()
        }
    }
}

def testPkg2(args = [:]){
    def testCommand = args['testCommand'] ? args['testCommand']: {
        def distroFiles = findFiles(glob: 'dist/*.tar.gz,dist/*.zip,dist/*.whl')
        if (distroFiles.size() == 0){
            error("No files located to test")
        }
        distroFiles.each{
            def toxCommand = "tox --installpkg ${it.path} -e py"
            if(isUnix()){
                sh(label: "Testing tox version", script: "tox --version")
                toxCommand = toxCommand + " --workdir /tmp/tox"
                sh(label: "Running Tox", script: toxCommand)
            } else{
                bat(label: "Testing tox version", script: "tox --version")
                toxCommand = toxCommand + " --workdir %TEMP%\\tox"
                bat(label: "Running Tox", script: toxCommand)
            }
        }
    }
    def setup = args['testSetup'] ? args['testSetup']: {
        checkout scm
    }
    def cleanup =  args['post']['cleanup'] ? args['post']['cleanup']: {}
    def successful = args['post']['success'] ? args['post']['success']: {}
    def failure = args['post']['failure'] ? args['post']['failure']: {}
    def dockerImageName = args['dockerImageName'] ? args['dockerImageName']:  "${currentBuild.fullProjectName}_${getToxEnv(args)}_build".replaceAll("-", "_").replaceAll('/', "_").replaceAll(' ', "").toLowerCase()
    def agentRunner = getAgent(args, dockerImageName)
    agentRunner {
        setup()
        try{
            testCommand()
            successful()
        } catch(e){
            failure()
            throw e
        } finally{
            cleanup()
        }
    }
}

def buildPkg(args = [:]){
    def dockerImageName = "${currentBuild.fullProjectName}_${getToxEnv(args)}_build".replaceAll("-", "_").replaceAll('/', "_").replaceAll(' ', "").toLowerCase()
    def agentRunner = getAgent(args, dockerImageName)
    def setup = args['buildSetup'] ? args['buildSetup']: {
        checkout scm
    }
    def cleanup =  args['post']['cleanup'] ? args['post']['cleanup']: {}
    def successful = args['post']['success'] ? args['post']['success']: {}
    def failure = args['post']['failure'] ? args['post']['failure']: {}
    def buildCmd = args['buildCmd'] ? args['buildCmd']: {
        if(isUnix()){
            sh "python -m pip wheel --no-deps -w ./dist ."
        } else {
            bat "py -m pip wheel --no-deps -w ./dist ."
        }
    }
    agentRunner {
        setup()
        try{
            buildCmd()
            successful()
        } catch(e){
            failure()
            throw e
        } finally{
            cleanup()
        }
    }
}
return [
    testPkg: this.&testPkg,
    testPkg2: this.&testPkg2,
    buildPkg: this.&buildPkg
]