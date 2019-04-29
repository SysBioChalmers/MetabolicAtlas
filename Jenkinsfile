pipeline {
  agent any
  stages {
    stage('Docker cleanup') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker rm $(docker ps -a -q) || true
          docker rmi $(docker images -q) || true
          docker volume prune --force || true
        '''
        echo 'Deleted all Docker containers and images.'
      }
    }
    stage('Configure') {
      steps {
        sh '''cp /var/lib/jenkins/postgres.env .'''
        echo 'Copied PostgreSQL and Django environment.'
        sh '''
          sed -i "s/svgMapURL:.*/svgMapURL: 'https:\\/\\/ftp.icsb.chalmers.se\\/.maps',/g"  frontend/src/components/explorer/mapViewer/Svgmap.vue
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
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml build
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d
        '''
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          wget https://chalmersuniversity.box.com/shared/static/q41d7lvcqe18g0gwr9yaar8zoedqvhfl.db -O human1.db
          wget https://chalmersuniversity.box.com/shared/static/om86nb6y8ji044wzoiljm8aghmbdvs41.db -O gems.db
          wget https://chalmersuniversity.box.com/shared/static/yqov4k0r4mript3ybl6x2xq42ud9s535.db -O yeast.db

          docker exec -i db psql -U postgres < human1.db
          docker exec -i db psql -U postgres < yeast.db
          docker exec -i db psql -U postgres < gems.db

          docker exec backend python manage.py makemigrations
          docker exec backend python manage.py migrate --database yeast --fake
          docker exec backend python manage.py migrate --database human1 --fake
          docker exec backend python manage.py migrate --database gems --fake
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
}
