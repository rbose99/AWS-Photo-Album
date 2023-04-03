import json
import urllib.parse
import boto3
import logging
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
REGION = 'us-east-1'
HOST = 'HOST_NAME'
INDEX = 'photos'
s3 = boto3.client('s3')
rec = boto3.client('rekognition')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    json_dict={}
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    logger.debug(bucket)
    logger.debug(key)
    json_dict['objectKey']=key
    json_dict['bucket']=bucket
    try:
        cust_labels=s3.head_object(Bucket= bucket, Key=key)
        json_dict["createdTimestamp"]=cust_labels["LastModified"].isoformat()
        awslist=cust_labels["Metadata"]["customlabels"].split(",")
        if awslist[0]=='':
            awslist=[]
        #logger.debug(cust_labels["ResponseMetadata"]["LastModified"])
        #logger.debug(cust_labels["ResponseMetadata"]["Metadata"]["customlabels"])
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    response = rec.detect_labels(Image = {"S3Object": {"Bucket": bucket, "Name": key}})
    for item in response['Labels']:
        awslist.append(item['Name'])
    json_dict['labels']=awslist
    logger.debug(json_dict)
    logger.debug("Returns")
    data=json.dumps(json_dict)
    osClient = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
            http_auth=get_awsauth(REGION, 'es'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)

    createIndex(osClient)
    resp=insert_data(osClient,data,key)
    logger.debug("RESPONSE")
    logger.debug(resp)
    #print(response)
    return "Thanks"
    #print("CONTENT TYPE: " + response['ContentType'])
    #return response['ContentType']

def createIndex(client):
    try:
        res = client.indices.exists(INDEX)
        logger.debug("Index Exists ... {}".format(res))
        if not res:
            response = client.indices.create(INDEX)
        return 1
    except Exception as E:
        print("Unable to Create Index {0}".format("metadata-store"))
        print(E)
        exit(4)
  
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

def insert_data(client,obj,k):

    response = client.index(
    index = INDEX,
    body = obj,
    id = k,
    refresh = True
)
    return response