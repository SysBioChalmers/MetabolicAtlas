pipeline {
  agent any
  stages {
    stage('Docker cleanup') {
      steps {
        sh '''
          pwd
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
        sh '''
          sed -i "s/svgMapURL:.*/svgMapURL: 'http:\/\/ftp.icsb.chalmers.se\/.maps',/g"  frontend/src/components/explorer/mapViewer/Svgmap.vue
        '''
      }
    }
    stage('Test') {
      steps {
        echo 'Should do some testing..'
      }
    }
    stage('Build') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml -p metabolicatlas build
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml -p metabolicatlas up -d
        '''
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          wget https://chalmersuniversity.box.com/shared/static/q41d7lvcqe18g0gwr9yaar8zoedqvhfl.db -O hmr2.db
          wget https://chalmersuniversity.box.com/shared/static/om86nb6y8ji044wzoiljm8aghmbdvs41.db -O gems.db

          docker exec -i $(docker ps -qf "name=metabolicatlas_db_1")  psql -U postgres -c 'drop database "hmr2"' || true
          docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres -c 'drop database "gems"' || true

          docker exec -i $(docker ps -qf "name=metabolicatlas_db_1")  psql -U postgres < hmr2.db
          docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres < gems.db

          docker exec metabolicatlas_backend_1 python manage.py makemigrations
          docker exec metabolicatlas_backend_1 python manage.py migrate --database hmr2 --fake
          docker exec metabolicatlas_backend_1 python manage.py migrate --database gems --fake
        '''
      }
    }
    stage('Clean up') {
      steps {
        sh '''
          rm *.db
        '''
        echo 'We are live!'
      }
    }
  }
  post {
   success {
   }
   failure {
   }
  }
}
