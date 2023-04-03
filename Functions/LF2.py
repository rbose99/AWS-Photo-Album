import json
import os
import logging
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
REGION = 'us-east-1'
HOST = 'HOST_NAME'
INDEX = 'photos'
lexclient = boto3.client('lexv2-runtime')
def query(terms):
    if len(terms)==1:
        q = {  "query": { "term": { "labels": { "value": terms[0]} }}}
    else:
        q = {  "query": { "terms": { "labels":  terms} }}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    print(res)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        fileName=hit["_source"]["objectKey"]
        url = boto3.client('s3').generate_presigned_url(
    ClientMethod='get_object', 
    Params={'Bucket': 'ccbd-photos', 'Key': fileName},
    ExpiresIn=3600)
        results.append(url)
    return results



def lambda_handler(event, context):
    logger.debug(event)
    # msg_from_user = event['messages'][0]
    # change this to the message that user submits on
    # your website using the 'event' variable
    #msg_from_user = event['messages'][0]['unstructured']['text']
    msg_from_user = event['queryStringParameters']['q']
    print(f"Message from frontend: {msg_from_user}")
    # Initiate conversation with Lex
    response = lexclient.recognize_text(
    botId='BOT_ID', # MODIFY HERE
    botAliasId='BOT_ALIAS', # MODIFY HERE
    localeId='en_US',
    sessionId='testuser',
    text=msg_from_user)
    msg_from_lex = response['sessionState']
    if msg_from_lex:
        print(f"Message from Chatbot: {msg_from_lex['intent']}")
    terms=[]
    if msg_from_lex['intent']['name']!= 'SearchIntent' or msg_from_lex['intent']['slots']['X']==None:
        return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': []})
    }
    terms.append(msg_from_lex['intent']['slots']['X']['value']['resolvedValues'][0])
    if msg_from_lex['intent']['slots']['Y']!=None:
        terms.append(msg_from_lex['intent']['slots']['Y']['value']['resolvedValues'][0])
    logger.debug(terms)
    # modify resp to send back the next question Lex would ask from the user
    # format resp in a way that is understood by the frontend
    # HINT: refer to function insertMessage() in chat.js that you uploaded
    # to the S3 bucket

    results = query(terms)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': results})
    }




def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
