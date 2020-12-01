def getToxEnvs(){
    def envs
    if(isUnix()){
        envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
    } else{
        envs = bat(returnStdout: true, script: "@tox -l").trim().split('\n')
    }
    envs.collect{
        it.trim()
    }
    return envs
}
def generateToxPackageReport(testEnv){

        def packageReport = "\n**Installed Packages:**"
        testEnv['installed_packages'].each{
            packageReport =  packageReport + "\n ${it}"
        }

        return packageReport
}

def generateToxReport(tox_env, toxResultFile){
    if(!fileExists(toxResultFile)){
        error "No file found for ${toxResultFile}"
    }
    try{
        def tox_result = readJSON(file: toxResultFile)
        def checksReportText = ""

        def testingEnvReport = """# Testing Environment

**Tox Version:** ${tox_result['toxversion']}
**Platform:**   ${tox_result['platform']}
"""
    if(! tox_result['testenvs'].containsKey(tox_env)){
        tox_result['testenvs'].each{test_env->
            echo "${test_env}"
            test_env.each{
                echo "${it}"

            }
        }
        error "No test env for ${tox_env} found in ${toxResultFile}"
    }
    def tox_test_env = tox_result['testenvs'][tox_env]
    echo "${tox_env}"
//         =========
        def packageReport = generateToxPackageReport(tox_test_env)
        checksReportText = testingEnvReport + " \n" + packageReport
//         =========


        def errorMessages = []
        try{
            tox_env["test"].each{
                if (it['retcode'] != 0){
                    echo "Found error ${it}"
                    def errorOutput =  it['output']
                    def failedCommand = it['command']
                    errorMessages += "**${failedCommand}**\n${errorOutput}"
                }
            }
        }
        catch (e) {
            echo "unable to parse Error output"
            throw e
        }
        def resultsReport = "# Results"
        if (errorMessages.size() > 0){
            resultsReport = resultsReport + "\n" + errorMessages.join("\n") + "\n"
        } else{
            resultsReport = resultsReport + "\n" + "Success\n"
        }
//         =========
        checksReportText = testingEnvReport + " \n" + resultsReport
        return checksReportText
    } catch (e){
        echo "Unable to parse json file"
        def data =  "No data available"
//         def data =  readFile(file: toxResultFile)
//         data = "``` json\n${data}\n```"
        return data
    }
}

def getToxTestsParallel(args = [:]){
    def envNamePrefix = args['envNamePrefix']
    def label = args['label']
    def dockerfile = args['dockerfile']
    def dockerArgs = args['dockerArgs']
    script{
        def TOX_RESULT_FILE_NAME = "tox_result.json"
        def envs
        def originalNodeLabel
        node(label){
            originalNodeLabel = env.NODE_NAME
            checkout scm
            def dockerImageName = "${currentBuild.projectName}:tox".replaceAll("-", "").toLowerCase().toLowerCase()
            def dockerImage = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} .")
            dockerImage.inside{
                envs = getToxEnvs()
            }
//             if(isUnix()){
//                 sh(
//                     label: "Removing Docker Image used to run tox",
//                     script: "docker image ls ${dockerImageName}"
//                 )
//             } else {
//                 bat(
//                     label: "Removing Docker Image used to run tox",
//                     script: """docker image ls ${dockerImageName}
//                                """
//                 )
//             }
        }
        echo "Found tox environments for ${envs.join(', ')}"
        def dockerImageForTesting = "${currentBuild.projectName}:tox".replaceAll("-", "").toLowerCase()
        node(originalNodeLabel){
            def dockerImageName = "tox"
            checkout scm
            dockerImageForTesting = docker.build(dockerImageName, "-f ${dockerfile} ${dockerArgs} . ")

        }
        echo "Adding jobs to ${originalNodeLabel}"
        def jobs = envs.collectEntries({ tox_env ->
//             def tox_result
            def githubChecksName = "Tox: ${tox_env} ${envNamePrefix}"
            def jenkinsStageName = "${envNamePrefix} ${tox_env}"

            [jenkinsStageName,{
                node(originalNodeLabel){
                    ws{
                        checkout scm
                        def containerName = "${currentBuild.fullProjectName}_tox_${tox_env}".replaceAll('/','_' )
                        dockerImageForTesting.inside("--name=${containerName}"){
                            try{
                                publishChecks(
                                    conclusion: 'NONE',
                                    name: githubChecksName,
                                    status: 'IN_PROGRESS',
                                    summary: 'Use Tox to test installed package',
                                    title: 'Running Tox'
                                )
                                if(isUnix()){
                                    sh(
                                        label: "Running Tox with ${tox_env} environment",
                                        script: "tox  -vv --parallel--safe-build --recreate --result-json=${TOX_RESULT_FILE_NAME} -e $tox_env"
                                    )
                                } else {
                                    bat(
                                        label: "Running Tox with ${tox_env} environment",
                                        script: "tox  -vv --parallel--safe-build --recreate --result-json=${TOX_RESULT_FILE_NAME} -e $tox_env "
                                    )
                                }
                            } catch (e){
                                def text
                                try{
                                    text = generateToxReport(tox_env, 'tox_result.json')
                                }
                                catch (ex){
                                    text = "No details given. Unable to read tox_result.json"
                                }
                                publishChecks(
                                    name: githubChecksName,
                                    summary: 'Use Tox to test installed package',
                                    text: text,
                                    conclusion: 'FAILURE',
                                    title: 'Failed'
                                )
                                throw e
                            }
                            def checksReportText = generateToxReport(tox_env, 'tox_result.json')
                            publishChecks(
                                    name: githubChecksName,
                                    summary: 'Use Tox to test installed package',
                                    text: "${checksReportText}",
                                    title: 'Passed'
                                )
                            cleanWs(
                                deleteDirs: true,
                                patterns: [
                                    [pattern: TOX_RESULT_FILE_NAME, type: 'INCLUDE'],
                                    [pattern: ".tox/", type: 'INCLUDE'],
                                ]
                            )
                        }
                    }
                }
            }]
        })
        return jobs
    }
}
return this