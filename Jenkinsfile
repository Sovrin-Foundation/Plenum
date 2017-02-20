#!groovy​

echo 'Plenum test...'

parallel 'ubuntu-test':{
    node('ubuntu') {
        try {
            stage('Ubuntu Test: Checkout csm') {
                checkout scm
            }

            stage('Ubuntu Test: Build docker image') {
                sh 'ln -sf ci/plenum-ubuntu.dockerfile Dockerfile'

                def orientdb = docker.image('orientdb')
                orientdb.run(['-d', '-p 2424:2424', '-p 2480:2480', '-e ORIENTDB_ROOT_PASSWORD=password'])

                def testEnv = docker.build 'plenum-test'
                
                testEnv.inside(['-p 2424:2424']) {
                    stage('Ubuntu Test: Install dependencies') {
                        sh 'virtualenv -p python3.5 test'
                        sh 'test/bin/python setup.py install'
                        sh 'test/bin/pip install pytest'
                    }

                    stage('Ubuntu Test: Test') {
                        sh 'test/bin/python runner.py --pytest "test/bin/python -m pytest" --output "/home/sovrin/test/result.txt"'
                    }
                }
            }
        }
        finally {
            stage('Ubuntu Test: Cleanup') {
                orientdb.stop
                step([$class: 'WsCleanup'])
            }
        }
    }   
}, 
'windows-test':{
    echo 'TODO: Implement me'
}

echo 'Plenum test: done'

if (env.BRANCH_NAME != 'master' && env.BRANCH_NAME != 'stable') {
    echo "Plenum ${env.BRANCH_NAME}: skip publishing"
    return
}

echo 'Plenum build...'

node('ubuntu') {
    try {
        stage('Publish: Checkout csm') {
            checkout scm
        }

        stage('Publish: Prepare package') {
        	sh 'chmod -R 777 ci'
        	sh 'ci/prepare-package.sh . $BUILD_NUMBER'
        }
        
        stage('Publish: Publish pipy') {
            sh 'chmod -R 777 ci'
            withCredentials([file(credentialsId: 'pypi_credentials', variable: 'FILE')]) {
                sh 'ln -sf $FILE $HOME/.pypirc' 
                sh 'ci/upload-pypi-package.sh .'
                sh 'rm -f $HOME/.pypirc'
            }
        }

        stage('Publish: Build debs') {
            withCredentials([usernameColonPassword(credentialsId: 'evernym-githib-user', variable: 'USERPASS')]) {
                sh 'git clone https://$USERPASS@github.com/evernym/sovrin-packaging.git'
            }
            echo 'TODO: Implement me'
            // sh ./sovrin-packaging/pack-Plenum.sh $BUILD_NUMBER
        }

        stage('Publish: Publish debs') {
            echo 'TODO: Implement me'
            // sh ./sovrin-packaging/upload-build.sh $BUILD_NUMBER
        }
    }
    finally {
        stage('Publish: Cleanup') {
            step([$class: 'WsCleanup'])
        }
    }
}

echo 'Plenum build: done'

stage('QA notification') {
    echo 'TODO: Add email sending'
    // emailext (template: 'qa-deploy-test')
}