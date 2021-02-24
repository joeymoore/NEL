import json
import boto3
import os
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    if event["httpMethod"] == "OPTIONS":
        return {"statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Methods": "POST",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
                }
    elif event["httpMethod"] == "POST":
        enrichment = {
            "asn": event["queryStringParameters"]["asn"],
            "site": event["queryStringParameters"]["site"],
            "account": event["queryStringParameters"]["account"],
            "epoch": event["queryStringParameters"]["epoch"],
            "address": {
                "state": event["queryStringParameters"]["state"],
                "city": event["queryStringParameters"]["city"],
                "country": event["queryStringParameters"]["country"],
                "postalcode": event["queryStringParameters"]["postalcode"],
                "latitude": event["queryStringParameters"]["latitude"],
                "longitude": event["queryStringParameters"]["longitude"]
            }
        }
        body = json.loads(event["body"])

        records = []
        for record in body:
            record["enrichment"] = enrichment
            msg_bytes = json.dumps(record).encode('utf-8')
            records.append({"Data": msg_bytes,
                            'PartitionKey': event["queryStringParameters"]["account"]})

        try:
            client = boto3.client('kinesis')
            response = client.put_records(
                Records=records,
                StreamName=os.environ['StreamName']
            )

            if "FailedRecordCount" in response:
                return {"statusCode": 201,
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": "ok"
                        }

        except ClientError as e:
            return {"statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": e.response['Error']['Message']
                    }