pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        APP_NAME = 'job-application-tracker'
        K8S_DEPLOYMENT = 'job-application'
        K8S_CONTAINER = 'flask-app'
        K8S_NAMESPACE = 'default'
        PYTHON = 'C:\\Users\\ANAND L\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
        KUBECONFIG = 'C:\\Users\\ANAND L\\.kube\\config'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Tools') {
            steps {
                bat 'docker version'
                bat 'kubectl config current-context'
                bat 'kubectl get nodes'
                bat '"%PYTHON%" --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install --default-timeout=120 --retries=10 -r requirements.txt'
                bat '"%PYTHON%" -m pip install pytest'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t %APP_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl apply -f k8s/persistent-volume.yaml'
                bat 'kubectl apply -f k8s/deployment.yaml'
                bat 'kubectl apply -f k8s/service.yaml'

                bat 'kubectl set image deployment/%K8S_DEPLOYMENT% %K8S_CONTAINER%=%APP_NAME%:%BUILD_NUMBER% -n %K8S_NAMESPACE%'

                bat 'kubectl rollout status deployment/%K8S_DEPLOYMENT% -n %K8S_NAMESPACE% --timeout=180s'
            }
        }

        stage('Verify Deployment') {
            steps {
                bat 'kubectl get deployments -n %K8S_NAMESPACE%'
                bat 'kubectl get pods -n %K8S_NAMESPACE%'
                bat 'kubectl get services -n %K8S_NAMESPACE%'
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully. Application deployed to Kubernetes.'
        }

        failure {
            echo 'Pipeline failed. Check Console Output to identify the failed stage.'
        }
    }
}