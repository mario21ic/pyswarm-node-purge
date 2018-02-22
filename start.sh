#1/bin/bash

docker run -e AWS_REGION=$AWS_REGION -v $PWD/.aws:/root/.aws -v /var/run/docker.sock:/var/run/docker.sock mario21ic/swarm-ec2-purge python main.py
