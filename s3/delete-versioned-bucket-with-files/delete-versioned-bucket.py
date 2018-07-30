#!/usr/bin/env python
import boto3
import sys


bucket= sys.argv[1]
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket)
bucket.object_versions.all().delete()

bucket.delete()
