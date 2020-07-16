import requests
import json

def send_msg(msg, WEBHOOK_URL="https://hooks.slack.com/services/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"):
    payload = {
        "channel": "#rada",
        "username": "Slack Bot",
        "text": msg,
    }
    requests.post(WEBHOOK_URL, data=json.dumps(payload))
