pipeline {
  agent any
  stages {
    stage('Docker cleanup') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker rm $(docker ps -a -q) || true
          docker rmi $(docker images -q) || true
        '''
        echo 'Deleted all Docker containers and images.'
      }
    }
    stage('Configure') {
      steps {
        sh '''cp postgres.env.sample postgres.env'''
        echo 'Copied PostgreSQL environment.'
      }
    }
    stage('Test') {
      steps {
        echo 'Should do some testing..'
      }
    }
    stage('Deploy') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml -p metabolicatlas build
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml -p metabolicatlas up -d
          docker exec metabolicatlas_backend_1 python manage.py makemigrations
          docker exec metabolicatlas_backend_1 python manage.py migrate
        '''
        echo 'We are live!'
      }
    }
  }
  post {
   success {
     slackSend (color: '#00AA00', message: "Deployment successful")
   }
   failure {
     slackSend (color: '#cc0c0c', message: "Failed ${env.BUILD_URL}")
   }
  }
}
