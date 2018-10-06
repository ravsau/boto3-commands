import boto3
s3 = boto3.client('s3')

bucket = raw_input("Enter your Bucket Name: ")
key= raw_input("Enter your desired filename/key for this upload: ")

print (" Generating pre-signed url...")

print(s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':key}, ExpiresIn=3600, HttpMethod='PUT'))
