#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from datetime import date
from datetime import datetime
from datetime import timedelta
import collections
import pdb
import csv

def as_ordered_dict(dictionary):
    return collections.OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))

cloudwatch = boto3.client('cloudwatch')

period=60
namespace = "AWS/ELB"
metric_name = 'RequestCount'
load_balancers = ['awseb-e-r-AWSEBLoa-LLUOP3IMS3OR','awseb-e-s-AWSEBLoa-1VOWO717O53D9','awseb-e-t-AWSEBLoa-8DND8M2NXA06','awseb-e-e-AWSEBLoa-1PS22JQJBUXKT']

today = datetime.now().date()
dates = [today - timedelta(days=i) for i in range(14,0,-1)]

dataset = {}
for date in dates:
    dataset[date] = {}
    for load_balancer in load_balancers:
        print([{'Name': 'LoadBalancerName','Value': load_balancer}])
        print(datetime.combine(date, datetime.min.time()))
        print(datetime.combine((date + timedelta(1)), datetime.min.time()))
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': 'LoadBalancerName','Value': load_balancer}],
            StartTime=datetime.combine(date, datetime.min.time()),
            EndTime=datetime.combine((date + timedelta(1)), datetime.min.time()),
            Period=period,
            Statistics=['Sum'],
            Unit='Count'
        )
        #pdb.set_trace()
        for datapoint in response['Datapoints']:
            if datapoint['Timestamp'] in dataset[date]:
                dataset[date][datapoint['Timestamp']] += datapoint['Sum']
            else:
                dataset[date][datapoint['Timestamp']] = datapoint['Sum']
            #print(len(dataset[date]))

with open('event-api-request-count.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(["timestamp","request count"])
    for day, data in as_ordered_dict(dataset).iteritems():
         for minute, request_sum in as_ordered_dict(data).iteritems():
             print("minute=%s,request_sum=%s" % (minute,request_sum))
             csvwriter.writerow([minute,request_sum])
