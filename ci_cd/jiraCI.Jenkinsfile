node() {
    def os = System.properties['os.name'].toLowerCase()
    try {
        notifyBuild('STARTED')
    }
    catch(e) {
        // If there was an exception thrown, the build failed
        currentBuild.result = "FAILED"
        throw e
    } finally {
        // Success or failure, always send notifications
        echo "I AM HERE"
        // notifyBuild(currentBuild.result)
        echo currentBuild.result
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
def notifyBuild(String buildStatus = 'STARTED') {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESSFUL'
    // Default values
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def msg = "${env.subject}"
      // Override default values based on build status
      if (buildStatus == 'STARTED') {
        color = 'BLUE'
        colorCode = '#0000FF'
        msg = "${env.subject}"
      } else if (buildStatus == 'UNSTABLE') {
        color = 'YELLOW'
        colorCode = '#FFFF00'
        msg = "${env.subject}"
      } else if (buildStatus == 'SUCCESSFUL') {
        color = 'YELLOW'
        colorCode = '#FFFF00'
      } else {
        color = 'RED'
        msg = "${env.subject}"
        colorCode = '#FF0000'
      }
    // Send notifications
    slackSend baseUrl: 'https://hooks.slack.com/services/', 
    channel: 'wopr-jenkins-flask', 
    color: colorCode, 
    message: msg,
    teamDomain: 'https://wow-technology.slack.com', 
    tokenCredentialId: 'Slack-Token', 
    username: 'JenkinsAutomation'
}
