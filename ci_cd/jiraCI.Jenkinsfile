node() {
    def STC_INSTALL = "/opt/STC_CLIENT/Spirent_TestCenter_5.16/Spirent_TestCenter_Application_Linux64Client/"
    def os = System.properties['os.name'].toLowerCase()
    try {
        def passthruString = sh(script: "printenv", returnStdout: true)
        passthruString = passthruString.replaceAll('\n',' ').trim()
        def paramsString1 = params.toString().replaceAll("[\\[\\](){}]","")
        paramsString = paramsString1.replaceAll(', ',' ')
        def paramsStringXray = formatXray(paramsString1, ', ')
        def HUDSON_URL = "${env.HUDSON_URL}"
        def SERVER_JENKINS = ""
        if (HUDSON_URL.contains("10.88.48.21")) {
            SERVER_JENKINS = "WOPR-SB"
        } else {
            SERVER_JENKINS = "WOPR-PROD-JENKINS"
        }
        stage("XRAY") {
            echo "*** Prepare Workspace ***"
            cleanWs()
            sh "ls -l"
            env.WORKSPACE_LOCAL = sh(returnStdout: true, script: 'pwd').trim()
            env.BUILD_TIME = "${BUILD_TIMESTAMP}"
            echo "Workspace set to:" + env.WORKSPACE_LOCAL
            echo "Build time:" + env.BUILD_TIME
            def blahh = sh(script: "echo ${env.cucumber} >> cucumber.json", returnStdout: true)
            cucumber buildStatus: "UNSTABLE",
            fileIncludePattern: "cucumber.json",
            jsonReportDirectory: 'reports'
            echo "*** Import Results to XRAY ***"
            def description = "Jenkins Project: ${env.JOB_NAME}\\n\\nTest Report: [${env.JOB_NAME}-Link|${env.BUILD_URL}/cucumber-html-reports/overview-features.html]\\n\\nINPUTS:\\n${paramsStringXray}\\n\\nOUTPUTS:\\n${env.awx_output_xray}"
            def labels = '["regression","automated_regression"]'
            def environment = "DEV"
            def testExecutionFieldId = 10552
            def testEnvironmentFieldName = "customfield_10372"
            def projectKey = "XT"
            def projectId = 10606
            def xrayConnectorId = "${env.xrayConnectorIdUser}"
            def info = '''{
                "fields": {
                    "project": {
                        "id": "''' + projectId + '''"
                    },
                    "labels":''' + labels + ''',
                    "description":"''' + description + '''",
                    "summary": "''' + env.JOB_NAME + ''' Automated Test Execution @ ''' + env.BUILD_TIME + ' ' + environment + ''' " ,
                    "issuetype": {
                        "id": "''' + testExecutionFieldId + '''"
                    }
                }
            }'''
            echo info
            step([$class: 'XrayImportBuilder', 
            endpointName: '/cucumber/multipart', 
            importFilePath: 'cucumber.json', 
            importInfo: info, 
            inputInfoSwitcher: 'fileContent', 
            serverInstance: xrayConnectorId])
        }
    }
    catch(e) {                           
        // If there was an exception thrown, the build failed
        currentBuild.result = "FAILED"
    } finally {
        // Success or failure, always send notifications
        echo "I AM HERE"
    }
}
def formatXray(input_string, String delimiter = "\n") {
    result = ""
    for(line in input_string.split(delimiter)) {
        result = result.replaceAll("\t","    ") + "\\n" + line
        // single to double / for all
    }
    return result
}
