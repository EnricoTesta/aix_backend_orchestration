from sendgrid import SendGridAPIClient, Mail
import os
import base64
import json


def notify_new_subscription(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8').replace("\'", "\"")
    message_json = json.loads(pubsub_message)
    message = Mail(
        from_email='noreply@ai-exchange.io',
        to_emails='admin@ai-exchange.io',
        subject=f"New user! Welcome {message_json['email']}!",
        html_content='Auto-generated')
    try:
        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

event = 'new_user'
user_email = 'pippo@pluto.com'
user_id = None
EVENT = str({"event": f'{str(event)}', "email": f'{str(user_email)}', "user": f'{str(user_id)}'}).encode("utf-8")
notify_new_subscription(event=EVENT)
