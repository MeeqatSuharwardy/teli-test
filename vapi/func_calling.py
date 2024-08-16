import requests
import time


class VAPI:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
        }

    def get_phone_numbers(self):
        url = "https://api.vapi.ai/phone-number"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()

    def get_phone_calls(self):
        url = "https://api.vapi.ai/call"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()

    def get_phone_call(self, call_id):
        url = f"https://api.vapi.ai/call/{call_id}"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()

    def get_assistants(self):
        url = "https://api.vapi.ai/assistant"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()

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
                            "role": "system"
                        }
                    ],
                    "functions": [
                        {
                            "name": "bookAppointment",
                            "description": "Used to book the appointment.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "datetime": {
                                        "type": "string",
                                        "description": "The date and time of the appointment in ISO format."
                                    },
                                    "fullname": {
                                        "type": "string",
                                        "description": "The full name of the customer."
                                    },
                                    "phone": {
                                        "type": "string",
                                        "description": "The phone number of the customer."
                                    },
                                    "purpose": {
                                        "type": "string",
                                        "description": "The purpose of the Appointment."
                                    }
                                }
                            }
                        },
                        {
                            "name": "transferCall",
                            "description": "Used to transfer the call to another number.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "destination": {
                                        "type": "string",
                                        "enum": [
                                            "+1234567890",  # replace with the original numbers
                                            "+0987654321",
                                            "+1122334455"
                                        ],
                                        "description": "The destination to transfer the call to."
                                    }
                                },
                                "required": ["destination"]
                            }
                        }
                    ]
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
                "serverUrl": "https://seanh@weblogixinc.com",
                "analysisPlan": {

                    "summaryPrompt": "Summarize the call in 2-3 sentences, focusing on the appointment details if any were made.",
                    "structuredDataPrompt": "Extract the appointment details from the call, including date, time, customer name, and purpose.",
                    "structuredDataSchema": {
                        "type": "object",
                        "properties": {
                            "appointmentDate": {"type": "string"},
                            "appointmentTime": {"type": "string"},
                            "customerName": {"type": "string"},
                            "appointmentPurpose": {"type": "string"}
                        },
                        "required": ["appointmentDate", "appointmentTime", "customerName", "appointmentPurpose"]
                    },
                    "successEvaluationPrompt": "Determine if the call was successful based on whether an appointment was booked and the call was transferred to a salesman.",
                    "successEvaluationRubric": "PercentageScale"
                }
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
            print(response.json())
        else:
            print('Failed to create call')
            print(response.text)
        return response.json()

    def get_call_analysis(self, call_id):
        url = f"https://api.vapi.ai/call/{call_id}/analysis"
        response = requests.request("GET", url, headers=self.headers)
        return response.json()


# # Set up the credentials and parameters
auth_token = 'b85935ef-89b2-43db-9566-60726b421187'
phone_number_id = "d91b2834-c1d4-4a57-acd7-2d778a64e417"
customer_number = "+19876543210"
customer_name = "Lalit ptdr"
# assistant_id = "1245f591-0009-4f98-ad76-b4268540cae6"
first_message = "Hello, this is Mary from Mary's Dental. How can I assist you today?"
# content = """
# You are a voice assistant for Mary's Dental, a dental office located at 123 North Face Place,
# Anaheim, California. The hours are 8 AM to 5PM daily, but they are closed on Sundays.  Mary's dental provides
# dental services to the local Anaheim community. The practicing dentist is Dr. Mary Smith.  You are tasked with
# answering questions about the business, and booking appointments. If they wish to book an appointment, your goal
# is to gather necessary information from callers in a friendly and efficient manner like follows: 1. Ask for their
# full name. 2. Ask for the purpose of their appointment. 3. Request their preferred date and time for the appointment.
# 4. Confirm all details with the caller, including the date and time of the appointment. - Be sure to be kind of funny
# and witty! - Keep all your responses short and simple. Use casual language, phrases like
# Umm..., Well..., and I mean are preferred. - This is a voice conversation, so keep your responses short,
# like in a real conversation. Don't ramble for too long.
# """
content = """
You are an assistant for booking appointments. When a user wants to book an appointment, use the bookAppointment function. 
After successfully booking an appointment, you must immediately use the transferCall function to transfer the call to a salesman. 
Choose the first number in the destination list for the transfer.

Follow these steps:
1. Use the bookAppointment function when the user provides all necessary information.
2. If the bookAppointment function returns a success message, immediately use the transferCall function.
3. When using the transferCall function, use "+1234567890" as the destination.
4. Before transferring, inform the user that you'll be transferring them to a salesman for further assistance.

Remember, only transfer the call if an appointment has been successfully booked.
"""

time.sleep(60)
# Initialize VAPI
vapi = VAPI(auth_token)
# Get existing assistants
assistants = vapi.get_assistants()
# Use the first assistant from the list (or choose the desired one)
assistant_id = assistants[0]['id'] if assistants else None
print(assistant_id)
# exit()

if assistant_id:
    # Make a call using the existing assistant
    call = vapi.make_call(
        phone_number_id,
        customer_number,
        customer_name,
        assistant_id,
        first_message,
        content
    )
else:
    print("No assistants available.")

# After the call has ended
call_id = call['id']
call_details = vapi.get_phone_call(call_id)

# Get call analysis
call_analysis = vapi.get_call_analysis(call['id'])

# Print summary
print("Call Summary:", call_analysis.get('summary', 'No summary available'))

# Print structured data
structured_data = call_analysis.get('structuredData', {})
print("Appointment Details:")
print(f"Date: {structured_data.get('appointmentDate', 'N/A')}")
print(f"Time: {structured_data.get('appointmentTime', 'N/A')}")
print(f"Customer Name: {structured_data.get('customerName', 'N/A')}")
print(f"Purpose: {structured_data.get('appointmentPurpose', 'N/A')}")

# Print success evaluation
print("Call Success:", call_analysis.get('successEvaluation', 'N/A'))

# Check if the call was transferred
if 'forwardedPhoneNumber' in call_details:
    print(f"Call was transferred to: {call_details['forwardedPhoneNumber']}")
else:
    print("Call was not transferred")