import json
import boto3

comprehend = boto3.client('comprehend', region_name='us-east-1')  # change region if needed

def analyze_sentiment(text):
    # Call comprehend to analyze the sentiment
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'  # Specify the language as English
    )

    # Extract sentiment and confidence scores from the response
    sentiment = response['Sentiment']  # This will be one of 'POSITIVE', 'NEGATIVE', 'NEUTRAL', or 'MIXED'
    sentiment_score = response['SentimentScore']

    # Print out the sentiment and its associated scores
    print(f"Sentiment: {sentiment}")
    print(f"Sentiment Scores: {sentiment_score}")
    
    return sentiment, sentiment_score

def lambda_handler(event, context):

    try:
 
        # Example usage:
        body = json.loads(event['body'])
        text = body['text']
        sentiment, sentiment_score = analyze_sentiment(text)
        return {
            'statusCode': 200,
            'body': json.dumps(sentiment)
        }
    except Exception as e:
        print("**ERROR**")
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
    
