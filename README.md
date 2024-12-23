# AWS-SpotifyApp

Spotify App made with AWS Lambda and API Gateway.

Lambda functions use a user's Spotify data to create a tailored playlist
based on their top artists, and also create a tailored playlist based on a user
inputted text sentiment, gathered by AWS Comprehend.

Python client makes calls to an AWS API GATEWAY webservice.

Spotify WebAPI used to gather user data and create playlist directly into
user's Spotify Account
