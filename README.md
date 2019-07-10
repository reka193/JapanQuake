# JapanQuake
Notification about the latest earthquakes in Japan.

The code is written in Python in form of an AWS Lambda function. After setting up and adding our Telegram Bot Token, a message is sent every time a new earthquake occurs. I used a one-minute CloudWatch Event trigger to run the function.

It is important to grant the necessary permissions for the Lambda execution role to access the DynamoDB:
                "dynamodb:PutItem"
                "dynamodb:DeleteItem"
                "dynamodb:GetItem"
                "dynamodb:Scan"
