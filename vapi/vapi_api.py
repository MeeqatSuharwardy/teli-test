import requests

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

      

  def make_call(self,phone_number_id, customer_number, customer_name, assistant_id, first_message, content):

    data ={
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
      print(response.json())
    else:
      print('Failed to create call')
      print(response.text)
    return response.json()