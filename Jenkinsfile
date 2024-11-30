pipeline {
    agent any

    stages {
        stage('Pull Repository & Build Containers') {
            steps {
                script {
                    git branch: 'main', url: 'https://github.com/skazy737/TrabalhoDevOps-22.7916-4'
                    sh 'docker-compose down -v'
                    sh 'docker-compose build'
                }
            }
        }

        stage('Start Containers & Run Tests') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                    sh 'sleep 30'

                    try {
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Os testes nao funcionaram. A Pipeline foi interrompida."
                    }
                }
            }
        }

        stage('Keep Services Running') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down -v'
        }
    }
}
