from sendgrid import SendGridAPIClient, Mail
import os
import base64
import json


def notify_new_submission(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8').replace("\'", "\"")
    message_json = json.loads(pubsub_message)
    message = Mail(
        from_email='noreply@ai-exchange.io',
        to_emails='admin@ai-exchange.io',
        subject=f"New code submission!",
        html_content=f"New submission by {message_json['user']}")
    try:
        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
