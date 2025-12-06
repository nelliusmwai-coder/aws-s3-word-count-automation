import json
import boto3
import urllib.parse

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# --- CONFIGURATION ---
SNS_TOPIC_ARN = "arn:aws:sns:us-west-2:052519175953:WordCountResultTopic" 
# --- CONFIGURATION ---

def lambda_handler(event, context):
    try:
        # 1. Get the S3 object details from the event
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        
        # S3 object keys with spaces are URL encoded, so decode the key.
        object_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        # 2. Retrieve the text file content from S3
        print(f"Fetching file {object_key} from bucket {bucket_name}")
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read the content (the file is expected to be a text file)
        file_content = response['Body'].read().decode('utf-8')
        
        # 3. Count the words
        # Simple word count: split the content by whitespace and count non-empty strings.
        word_count = len(file_content.split())
        
        # 4. Format the message
        subject = "Word Count Result"
        message = f"The word count in the {object_key} file is {word_count}."
        
        # 5. Publish the result to SNS
        print(f"Publishing result to SNS topic: {SNS_TOPIC_ARN}")
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        
        print("Successfully published word count to SNS.")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Word count successful and reported via SNS', 'word_count': word_count})
        }
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # In a real environment, you might publish an error notification here as well.
        raise e