# New ROUTER page that handles Actions/Hooks from Server URL from VAPI
import requests


webhook_url="https://hook.integrator.boost.space/lnqd7ztx3p7wtctorrfee7vy3simxnbl"


def send_data_to_webhook(call_data):
    response = requests.post(webhook_url, json=call_data)
    if response.status_code != 200:
        print(f"Failed to send data to webhook: {response.status_code}")