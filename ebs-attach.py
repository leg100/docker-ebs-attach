#!/usr/bin/python

import argparse
import os
import signal
import sys
import time

import boto.ec2
import requests

# on close, detach ebs
parser = argparse.ArgumentParser(description='Attach and mount EBS volume to local instance')
parser.add_argument('--volumeid', metavar='<VOLUME_ID>', default=os.environ.get('VOLUME_ID'),
                    help='Volume ID of EBS volume to attach')
parser.add_argument('--device', metavar='<DEVICE>', default=os.environ.get('DEVICE'),
                    help='Device to expose volume on')
parser.add_argument('--region', metavar='<REGION>', default=os.environ.get('REGION'),
                    help='AWS region')
args = parser.parse_args()

conn = boto.ec2.connect_to_region(args.region)

instance = requests.get("http://169.254.169.254/latest/meta-data/instance-id").content

print "Attaching volume {} to device {} on instance {}".format(args.volumeid, args.device, instance)
conn.attach_volume(args.volumeid, instance, args.device) or sys.exit(1)

def detach_func(volume, instance, device):
    def handler(*args, **kwargs):
        print "Detaching volume {} from device {} on instance {}".format(volume, device, instance)
        conn.detach_volume(volume, instance, device)
        sys.exit(0)
    return handler

detach = detach_func(args.volumeid, instance, args.device)
signal.signal(signal.SIGTERM, detach)
signal.signal(signal.SIGINT, detach)

while True:
    time.sleep(5)
