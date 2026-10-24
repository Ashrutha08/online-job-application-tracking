
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '"C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pip install --default-timeout=120 --retries=10 -r requirements.txt'
                bat '"C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pip install pytest'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pytest -v'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker version'
                bat 'docker build -t job-application-tracker:%BUILD_NUMBER% .'
            }
        }
    }
}
