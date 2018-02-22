#!/usr/bin/env python3

import boto3
import docker
import time
import platform
import logging
import os


docker_client = docker.from_env()
docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
region = str(os.environ['AWS_REGION'])
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s ' + platform.node() + " : ")


def main():
    while True:
        logging.info("### New iteration ###")
        # nodes_workers = client.nodes.list(filters={'role': 'worker'})
        nodes = docker_client.nodes.list()
        #logging.info(nodes)
        for node in nodes:
            if node.attrs['Status']['State'] == "down":
                node_id = node.attrs['ID']
                node_ip = node.attrs['Status']['Addr']
                node_role = node.attrs['Spec']['Role']
                logging.info("ID %s - Ip %s - Role %s" % (node_id, node_ip, node_role))

                # EC2 search instance_id
                ec2_client = boto3.client('ec2', region_name=region)
                ec2_response = ec2_client.describe_instances(
                    Filters=[{'Name': 'private-ip-address',
                              'Values': [node_ip]}],
                    MaxResults=10
                )

                # print("ec2_response: ", ec2_response)
                instance_id = ""
                if len(ec2_response['Reservations']) >= 1:
                    instance_id = ec2_response['Reservations'][0]['Instances'][0]['InstanceId']
                    logging.info("EC2 instance id: " + instance_id)
                else:
                    logging.warning("EC2 instance not found with private ip")

                # Node Drain
                try:
                    node.update({'Availability': 'drain',
                                 'Role': node_role
                                 })
                    logging.info("Drain: " + str(node_id))
                    time.sleep(2)
                except Exception as e:
                    logging.error("Node Error: " + str(e))

                # Node Remove
                try:
                    docker_api.remove_node(node_id, True)
                    logging.info("Node Remove: " + str(node_id))
                except Exception as e:
                   logging.error("Node error " + str(e))

                # EC2 Terminate
                try:
                    ec2_client.terminate_instances(
                        InstanceIds=[
                            instance_id,
                        ]
                    )
                    logging.info("Ec2 Terminate: " + str(instance_id))
                except Exception as e:
                    logging.error("Ec2 Error: " + str(e))

        time.sleep(10)

if __name__ == "__main__":
    main()
