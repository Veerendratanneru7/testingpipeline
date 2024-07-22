pipeline {
    agent any

    environment {
        REGISTRY = 'your-docker-registry-url'
        IMAGE_NAME = 'your-image-name'
        PROJECT_NAME = 'your-openshift-project'
        DEPLOYMENT_NAME = 'your-deployment-name'
        OPENSHIFT_API_URL = 'your-openshift-api-url'
        OPENSHIFT_TOKEN = credentials('openshift-token-credential-id')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def imageTag = "${env.BUILD_NUMBER}"
                    sh "docker build -t ${REGISTRY}/${IMAGE_NAME}:${imageTag} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    def imageTag = "${env.BUILD_NUMBER}"
                    sh "docker login ${REGISTRY} -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}"
                    sh "docker push ${REGISTRY}/${IMAGE_NAME}:${imageTag}"
                }
            }
        }

        stage('Deploy to OpenShift') {
            steps {
                script {
                    def imageTag = "${env.BUILD_NUMBER}"
                    sh """
                    oc login ${OPENSHIFT_API_URL} --token=${OPENSHIFT_TOKEN}
                    oc project ${PROJECT_NAME}
                    oc set image deployment/${DEPLOYMENT_NAME} ${DEPLOYMENT_NAME}=${REGISTRY}/${IMAGE_NAME}:${imageTag}
                    oc rollout status deployment/${DEPLOYMENT_NAME}
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
