import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()

# Define constants
AUTH_TOKEN = 'b85935ef-89b2-43db-9566-60726b421187'
# PHONE_NUMBER_ID = "d91b2834-c1d4-4a57-acd7-2d778a64e417"
PHONE_NUMBER_ID = "d91b2834-c1d4-4a57-acd7-2d778a64e417"
CUSTOMER_NUMBER = "+16785689606"
CUSTOMER_NAME = "lalit patidar"
ASSISTANT_ID = "1245f591-0009-4f98-ad76-b4268540cae6"

FIRST_MESSAGE = "Hello, this is Mary from Bob's Mortgages. How can I assist you today?"
CONTENT = """You are a voice assistant for Bob's Mortgages, a mortgage office located in Detroit, MI. The bookable appointment hours are 9 AM to 8 PM daily ET time zone, but they are closed on Saturdays and Sundays.
Bob's Mortgages offers typical house mortgage services like discount mortgages and refinancing programs in real estate only. You are tasked with answering questions about the business and booking appointments. If they wish to book an appointment, your goal is to gather necessary information from callers in a friendly and efficient manner like follows:

1. Ask for their full name. Ask just for their first name if they refuse at first.
2. Ask for the purpose of their appointment.
3. Same-day appointments aren't available. Request their preferred date and time for the appointment and adjust to their time zone which is PT. Once set, verify the time zone.
4. Confirm the set date and time with the caller, including the date and time of the appointment.

You have the following information about the client:
- Name: {first_name} {last_name}
- DOB: {dob}
- Address: {full_address}
- FICO Score: {fico_score}
- Current balance of Mortgage: ${current_balance}

- If they ask how we got their name/phone/info, tell them they recently inquired from an ad or website.
- Be sure to be kind, and sincere. Be only slightly funny and witty, but not too much, very subtle.
- Don't jump from bland, monotone to witty, it's too drastic of a change.
- Keep all your responses short and simple. Use casual language, phrases like "Well...", and "I mean" are preferred.
- This is a conversation, so keep your responses short, like in a real conversation. Don't ramble for too long.

if a caller request not to be called than respectfully acknowledge and confirm removal from the call list.
if they are not intrested than Acknowledge their disinterest and leave a positive note 
about contacting the office if they need services in the future.
If someone needs to cancel or reschedule, ask for their name and the new preferred date and time.
"""


class VAPI:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
        }

    def make_call(self, phone_number_id, customer_number, customer_name, assistant_id, first_message, content):
        data = {
            "assistantOverrides": {
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en"
                },
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo-16k",
                    "temperature": 0.3,
                    "messages": [
                        {
                            "content": content,
                            "role": "assistant"
                        }
                    ],
                    "semanticCachingEnabled": True,
                    "maxTokens": 250
                },
                "voice": {
                    "fillerInjectionEnabled": False,
                    "provider": "11labs",
                    "voiceId": "sarah",
                    "stability": 0.5,
                    "useSpeakerBoost": False,
                    "model": "eleven_turbo_v2",
                    "style": 0,
                    "similarityBoost": 0.75
                },
                "recordingEnabled": False,
                "endCallFunctionEnabled": True,
                "dialKeypadFunctionEnabled": False,
                "hipaaEnabled": False,
                "backgroundSound": "office",
                "firstMessage": first_message,
                "voicemailDetectionEnabled": False,
                "endCallMessage": "Good Bye.",
                "serverUrl": "https://seanh@weblogixinc.com"
            },
            "customer": {
                "number": customer_number,
                "name": customer_name
            },
            "phoneNumberId": phone_number_id,
            "assistantId": assistant_id
        }

        response = requests.post(
            'https://api.vapi.ai/call/phone', headers=self.headers, json=data)

        if response.status_code == 201:
            print('Call created successfully')
            return response.json()
        else:
            print('Failed to create call')
            print(response.text)
            return None


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SAMPLE_SPREADSHEET_ID = os.getenv('SAMPLE_SPREADSHEET_ID')

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def write_to_google_sheet(values, headers):
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A1:Z1").execute()
    existing_headers = result.get('values', [])

    if not existing_headers:
        sheet.values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A1",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": [headers]}).execute()

    request = sheet.values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!A:A",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": values}).execute()

    print(request)


def main():
    headers = ["phone_number_id", "customer_number", "customer_name", "assistant_id", "first_message", "content"]
    dummy_data = [
        [123, 303, "lalit patidar", "1234", "Hello, this is Mary from Bob's Mortgages.", "........."],
        [123, 303, "Gourav Agrawal", "1221", "Hello, this is Mary from Bob's Mortgages.", "........."],
    ]
    # json_response = [
    #     {"phone_number_id": 123, "customer_number": 303, "customer_name": "abdul sami", "assistant_id": "123", "first_message": "Hello, this is Mary from Bob's Mortgages.", "content": "........."},
    #     {"phone_number_id": 456, "customer_number": 404, "customer_name": "john doe", "assistant_id": "456", "first_message": "Hi, this is John from XYZ Inc.", "content": "........."},
    # ]

    write_to_google_sheet(dummy_data, headers)


if __name__ == "__main__":
    main()

# uncomment to get data from response
# def main():
#     vapi = VAPI(auth_token=AUTH_TOKEN)
#     response = vapi.make_call(phone_number_id=PHONE_NUMBER_ID, customer_number=CUSTOMER_NUMBER,
#                               customer_name=CUSTOMER_NAME, assistant_id=ASSISTANT_ID,
#                               first_message=FIRST_MESSAGE, content=CONTENT)

#     if response:
#         # Flatten the response dictionary for easier writing to the sheet
#         flattened_response = [[k, str(v)] for k, v in response.items()]
#         write_to_google_sheet(flattened_response)

# if _name_ == "_main_":
#     main()