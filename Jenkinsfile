pipeline {
    agent any
    environment {
        BRANCH_NAME = "${env.GIT_BRANCH}"
        SITE = 'deconvolute-me'
        COMMIT = "${env.GIT_COMMIT}"
    }
    stages {
        stage('Deploy landing page') {
            when {
                branch 'spectranalyzer2'
            }
            steps {
                sh 'docker build . -t deconvolute-me'
                sh 'docker stack deploy -c docker-compose.yml deconvolute-me'
            }
        }
    }
}