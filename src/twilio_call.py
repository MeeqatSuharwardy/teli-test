

from twilio.rest import Client
from .utils import twilio_account_sid, twilio_auth_token

client = Client(twilio_account_sid, twilio_auth_token)

# get owned phone numbers
numbers = client.incoming_phone_numbers.list()
print(numbers)
for record in numbers:
    print(record.phone_number)
    print(record.sid)

