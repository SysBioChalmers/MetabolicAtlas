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
        sh '''cp db2_postgres.env.sample db2_postgres.env'''
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

          wget https://chalmersuniversity.box.com/shared/static/q41d7lvcqe18g0gwr9yaar8zoedqvhfl.db -P /home/jenkins/new/workspace/databases -O hmm.db
          wget https://chalmersuniversity.box.com/shared/static/om86nb6y8ji044wzoiljm8aghmbdvs41.db -P /home/jenkins/new/workspace/databases -O gems.db

          docker exec -i $(docker ps -qf "name=metabolicatlas_db_1")  psql -U postgres -c 'drop database "hmm"' || true
          docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres -c 'drop database "gems"' || true

          docker exec -i $(docker ps -qf "name=metabolicatlas_db_1")  psql -U postgres < '/home/jenkins/new/workspace/databases/hmm.db'
          docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres < '/home/jenkins/new/workspace/databases/gems.db'

          docker exec metabolicatlas_backend_1 python manage.py makemigrations
          docker exec metabolicatlas_backend_1 python manage.py migrate --database human
          docker exec metabolicatlas_backend_1 python manage.py migrate --database gems

          rm /home/jenkins/new/workspace/databases/hmm.db
          rm /home/jenkins/new/workspace/databases/gems.db
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
