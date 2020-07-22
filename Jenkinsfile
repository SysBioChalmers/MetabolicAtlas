pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh '''
          cp /var/lib/jenkins/dev.env production.env
          echo "VUE_APP_MATOMOID=14" >> frontend/.env.production
        '''
        echo 'Configure GitHub Package token.'
        withCredentials([string(credentialsId: 'AUTH_TOKEN', variable: 'gprauth')]) {
          sh '''
            echo $gprauth >> frontend/.npmrc
          '''
        }
        echo 'Downloaded source databases, configured .npmrc'
      }
    }
    stage('Clean build') {
      steps {
        sh '''
          . proj.sh
          clean-stack
          build-stack --build-arg SERVER_NAME=csbi.chalmers.se --build-arg USE_IP_FILTER=true
        '''
        echo 'Built new Docker images.'
      }
    }
    stage('Run') {
      steps {
        sh '''
          . ./proj.sh production
          start-stack
        '''
        echo 'Running the new Docker images.'
      }
    }
    stage('Clean up') {
      steps {
        sh '''
          docker system prune -af
        '''
        echo 'Deleted old Docker images and containers. We are live!'
      }
    }
  }
}
