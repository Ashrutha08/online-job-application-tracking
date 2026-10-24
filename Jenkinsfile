
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub.'
            }
        }

        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install --upgrade pip'
                bat '"%PYTHON%" -m pip install -r requirements.txt'
                bat '"%PYTHON%" -m pip install pytest'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All CI pipeline stages completed.'
        }
        failure {
            echo 'FAILURE: Check the Console Output for details.'
        }
        always {
            echo 'Jenkins pipeline execution completed.'
        }
    }
}
