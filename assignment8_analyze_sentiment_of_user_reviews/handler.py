import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Comprehend client
comprehend = boto3.client('comprehend')

def lambda_handler(event, context):
    """
    Lambda function to analyze sentiment of user reviews using Amazon Comprehend
    """
    try:
        # Extract review text from the incoming event
        review_text = event.get('review')
        if not review_text:
            logger.error("No review text found in event.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing review text'})
            }

        logger.info(f"Received review: {review_text}")

        # Call Amazon Comprehend for sentiment analysis
        response = comprehend.detect_sentiment(
            Text=review_text,
            LanguageCode='en'
        )

        sentiment = response['Sentiment']
        sentiment_scores = response['SentimentScore']

        logger.info(f"Detected Sentiment: {sentiment}")
        logger.info(f"Sentiment Scores: {json.dumps(sentiment_scores, indent=2)}")

        # Return result
        return {
            'statusCode': 200,
            'body': json.dumps({
                'review': review_text,
                'sentiment': sentiment,
                'scores': sentiment_scores
            })
        }

    except Exception as e:
        logger.error(f"Error processing review: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
