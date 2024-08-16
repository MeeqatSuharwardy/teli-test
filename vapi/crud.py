import time
import pandas as pd
from .vapi_api import VAPI
from dotenv import load_dotenv
# from env import OPENAI_API_KEY, VAPI_AUTHTOKEN
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from threading import Thread, Lock
from dateutil.parser import parse
from src.supabasedb import supabase
from langchain_community.chat_models import ChatOpenAI

load_dotenv()
# openai_api_key = OPENAI_API_KEY
# auth_token = VAPI_AUTHTOKEN


openai_api_key = os.getenv("OPENAI_API_KEY")
auth_token = os.getenv("VAPI_AUTHTOKEN")


def run_compaign(file_path, auth_token, compaigns):
    if file_path.split(".")[-1] == "csv":
        data = pd.read_csv(file_path)
    else:
        data = pd.read_excel(file_path)
    vapi = VAPI(auth_token)

    # Data Validation
    required_columns = ['First_Name', 'Last_Name', 'Phone_Number']

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    list_phone_number = vapi.get_phone_numbers()
    # print("compaigns: .....",compaigns)
    list_phone_number = [compaign['phonenumberid'] for compaign in compaigns['phone_assistant']]
    total_phone_numbers = len(list_phone_number)
    free_phone_numbers: list = list_phone_number

    # print(list_phone_number,total_phone_numbers,free_phone_numbers)
    # exit()
    with open("free_phone_numbers.json", "w") as f:
        for item in free_phone_numbers:
            f.write("%s\n" % item)
    # exit()
    # print(list_phone_number, free_phone_numbers)
    # exit()
    count = 0

    status_lock = Lock()

    for index, row in data.iterrows():

        assistant_id = None

        # exit()
        # csv validation
        # if pd.isnull(row['First_Name']):
        #     raise ValueError(f"First_Name is required at row {index + 1}")
        # if pd.isnull(row['Phone_Number']):
        #     raise ValueError(f"At least one phone number is required at row {index + 1}")
        # if pd.notna(row['Phone_Number']) and not str(row['Phone_Number']).isdigit():
        #     raise ValueError(f"Invalid phone number at row {index + 1}: {row['Phone_Number']}")
        # .................................................................................
        # exit()
        print("free phone numbers: ", len(free_phone_numbers))
        # exit()
        if count == total_phone_numbers:
            count = 0

        # check the status of compaign
        get_compaigns = supabase.table("campaigns").select("*").eq("campaignid", compaigns['compaign_id']).execute()
        print("get_compaigns: ", get_compaigns)
        # exit()
        tmpCompaigns = get_compaigns.data[0]
        print(tmpCompaigns)
        # exit()
        print(len(free_phone_numbers))
        # exit()
        # while len(free_phone_numbers) == 0 or tmpCompaigns['status'] == 0 or tmpCompaigns['status'] == -1:
        #     time.sleep(5)
        #     print("waiting for free phone numbers")
        #     print("status: ", tmpCompaigns['status'])
        #     # exit()
        #     get_compaigns = supabase.table("campaigns").select("*").eq("campaignid", compaigns['compaign_id']).execute()
        #     tmpCompaigns = get_compaigns.data[0]

        #     with open("free_phone_numbers.json", "r") as f:
        #         free_phone_numbers = f.read().splitlines()
        #     for i in range(len(free_phone_numbers)):
        #         free_phone_numbers[i] = free_phone_numbers[i].replace("'", "\"")
        # print("free phone numbers after while: ", len(free_phone_numbers))
        # exit()

        first_message = f"Hello {row['First_Name']}, this is Anthony from Rocket Mortgages. What were you looking for last week when you inquired about a mortgage?"
        customer_name = row['First_Name'] + " " + row['Last_Name']
        print("................................................................................")
        print(first_message, customer_name)
        # .....................................................................................

        customer_number = str(row['Phone_Number'])
        # print(customer_name, customer_number)
        # exit()

        # print('free_phone_numbers: ',free_phone_numbers)
        # if "assistantId" in free_phone_numbers[0].keys():
        #     assistant_id = free_phone_numbers[0]['assistantId']
        # else:
        #     assistant_id =  None
        phone_number_id = free_phone_numbers[0]
        print(assistant_id, phone_number_id)
        # exit()
        # phone_number_id="d91b2834-c1d4-4a57-acd7-2d778a64e417"

        if customer_number[0:2] == "+1" and len(customer_number) == 12:
            # Number is already in the correct format, do nothing
            customer_number = customer_number
        elif customer_number[0] == "1" and len(customer_number) == 11:
            # Number starts with 1 and is 11 digits long, add a +
            customer_number = "+" + customer_number
        elif customer_number[0:2] != "+1" and len(customer_number) == 10:
            # Number does not start with +1, add +1
            customer_number = "+1" + customer_number
        else:
            print("customer number is invalid")

        print(customer_number)
        # exit()
        # phone_number_id="d91b2834-c1d4-4a57-acd7-2d778a64e417"

        if assistant_id == None:
            # result = vapi.get_assistants()
            # assistant_id = result[0]['id']
            # assistant_id = [compaign['assistant_id'] for compaign in compaigns['phone_assistant'] if
            #                 compaign['phonenumberid'] == phone_number_id][0]
            assistant_id = [compaign['assistant_id'] for compaign in compaigns['phone_assistant'] if
                            compaign['phonenumberid'] == phone_number_id]
        # assistant_id="4b55fa07-98fe-470a-9e3a-6cf639d2a116"
        print(assistant_id)
        # exit()
        content = f"{compaigns['assistant']} {compaigns['script']}"
        print("Content: ", content)
        print("Assistant ID: ", assistant_id)
        print("Customer Name: ", customer_name)
        print("Customer Number: ", customer_number)
        print("Phone Number ID: ", phone_number_id)
        # exit()
        print(assistant_id)
        # Fetch system prompts from supabase
        assistant_data = supabase.table("assistants").select("system_prompt").eq("id", assistant_id[0]).execute()
        system_prompt = assistant_data.data[0]['system_prompt']
        # exit()
        # ..........................................................................
        # dynamic content
        content = f"""
        {system_prompt}
        [Identity]
        You role is text-based sales assistant for Rocket Mortgages, a Mortgage office located in Detroit, MI. Rocket Mortgages offers typical house mortgage services like discount mortgages and refinancing programs in real estate only. Our number is 888.-222-3575.

        [Tasks]
        Your goal is to gather the information needed below from callers in a friendly and efficient manner. Use a concise conversational tone. Your sequence of tasks in order are:
        1. Verify Data in [Verify Data] Section
        2. Book an appointment with prospect so they can chat with a mortgage specialist.
        3. Gather answers to the questions in the [Qualifying Questions] Section

        [Book the Appointment]
        Do not make appointments on Saturdays and Sundays or Major Holidays. You can make same-day appointments but do not make appointments within 4 hours from now nor within 4 hours of closing time.  Ask the for their preferred date and time for the appointment. Ask them what time zone they are in. Ask them to change the time in their time zone if it does not fall in the time window of 9 AM to 8 PM Eastern Time Zone.  Repeat back the date and time of the appointment as Day of the week, month, day of month.
        - Make sure you set an exact time for the appointment, not "evening" "some time" or "lunch time".
        - When someone says "in 2 days" make sure you add days to the calendar and say the weekday they chose for the person.
        - If a person says 1,2 or however many days from now, calculate the date of the appointment and repeat back to them accounting for only allowable Weekdays for appointment.

        [Verify Data]
        - Don't ask more than 2 questions in one turn
        1. Verify their full name is {row['First_Name'] + " " + row['Last_Name']}
        2. Ask if their credit score is still {row['FICO04_Score']}
        3. Is your current mortgage balance  {row['Current Balance of Most Recent Mortgage (1) Trade']}
        4. Your Monthly Payment is {row['Monthly Payment Amount of Most Recent Mortgage (1) Trade']}
        5. Your Loan Type you have now is {row['Loan Type of Most Recent Mortgage (1) Trade']}
        6. Your Social Security Number is {row['SSN']}

        [Qualifying Questions]
        - Don't ask more than 2 questions per turn
        - If the prospect is willing and not sounding frustrated to continue the call, ask these questions. Try to get a minimum of 3 questions answered.
        1. In this refinance, are you looking to save money monthly, pull some cash out, or pay of the home sooner?
        2. Ask if this is for a single family home
        3. Is this a conventional, VA, or FHA loan?
        4. What do you believe is a fair value of your home?
        5. Are you currently working, retired or self-employed?
        6. Do you pay taxes and insurance with the loan?
        7. How long have you been in this loan for?
        8.  Did you serve in military, if so what branch?
        9. Are you the only one on the loan?

        [Rules & Guidelines]
        - Speak to the Prospect in their first name only, unless you are verifying their full name in Verify Data section
        - Be sure to be kind, and sincere. Be only slightly funny and witty, but not too much, be very subtle.
        - Don't jump from bland to super witty. Make small changes in emotion.
        - Keep all your responses short and simple. Use casual language, phrases like "Well...", and "I mean" are preferred.
        - Don't ramble for too long. Keep responses short.
        - Avoid repeating the user's first name after every question. Use phrases like "Okay," "Alright," or "Got it" instead.

        [Handling Objections or Lack of Interest]
        - If they say "Remove", "Remove me", "Do Not Call me", "Stop Calling", "Never Call me", end the call quickly and get off the phone with a confirmation "We are removing you permanately from our list".
        - If they ask how we got their name/phone/info, tell them “That’s a great question. It looks like you had your credit pulled in regards to your mortgage, were a mortgage broker who works hand and hand with the credit bureaus.”
        - If they say “ I am not interested” respond back  “I hear you, but what made you change your mind when you originally inquired? Because as a broker, we can offer you much better options and structure it to best fit your needs.” Then proceed to gather more information or set an appointment.  Then pivot to a mortgage related question from above.
        - If they ask, Why do you need all this information? Respond back saying “The reason being is I want to get you an accurate of a quote as possible from banks, otherwise I’d be wasting your time.”
        - If they are not interested, respect and appreciate their decision, but ask them what inclined them to fill out the web form requesting financial services.
        """

        print("..............................................................")
        # print(content)
        # exit()
        try:
            call_data = vapi.make_call(phone_number_id, customer_number, customer_name, assistant_id, first_message,
                                       content)
            print("Call successful:", call_data)
            call_id = call_data['id']
            # call_id = '642ca530-8010-4f91-8f2d-fffd20d34245'
        except Exception as e:
            print(f"Failed to make call to {customer_name} ({customer_number}):", e)
            continue
        # exit()
        # call_data = vapi.make_call(phone_number_id, customer_number, customer_name, assistant_id, first_message,content)
        # call_id = 1234

        print("Call ID: ", call_id)
        print("Phone Number ID: ", phone_number_id)
        print("Customer Name: ", customer_name)
        print("Customer Number: ", customer_number)
        print("Assistant ID: ", assistant_id)

        existing_row = supabase.table("campaign_status").select("*").eq("campaign_id",
                                                                        tmpCompaigns['campaignid']).execute()
        # time.sleep(10)
        if existing_row.data:
            # Update existing row
            supabase.table("campaign_status").update({
                "created_at": str(datetime.now()),
                "row_number": index,
                "status": "",
                "total_records": len(data)
            }).eq("campaign_id", tmpCompaigns['campaignid']).execute()
        else:
            # Insert new row
            supabase.table("campaign_status").insert({
                "created_at": str(datetime.now()),
                "row_number": index,
                "campaign_id": tmpCompaigns['campaignid'],
                "status": "",
                "total_records": len(data)
            }).execute()

        status_lock.acquire()
        # exit()
        with open("free_phone_numbers.json", "r") as f:
            free_phone_numbers = f.read().splitlines()
        for i in range(len(free_phone_numbers)):
            free_phone_numbers[i] = free_phone_numbers[i].replace("'", "\"")
        free_phone_numbers.pop(0)
        with open("free_phone_numbers.json", "w") as f:
            for item in free_phone_numbers:
                f.write("%s\n" % item)
        status_lock.release()
        print("free phone numbers after pop: ", len(free_phone_numbers))
        status_thread = Thread(target=check_status_of_calls,
                               args=(vapi, call_id, list_phone_number[count], status_lock, file_path))
        status_thread.daemon = True
        status_thread.start()
        count += 1
    # set the status of compaign to completed
    supabase.table("campaigns").update({"status": -1}).eq("campaignid", compaigns['compaign_id']).execute()


def check_status_of_calls(vapi: VAPI, call_id, phone_number, lock: Lock, file_path):
    status = "queued"
    while status != "ended":
        call_data = vapi.get_phone_call(call_id)
        status = call_data['status']
        time.sleep(5)
    # exit()
    print("...........................................calldata..............")
    print(call_data)
    print("...........................................................")
    data = {
        "created_at": call_data['startedAt'],
        "metadata": "",
        "log_dump": ""
    }
    if "summary" in call_data.keys():
        data["summary"] = call_data['summary']
    if "transcript" in call_data.keys():
        data["transcript"] = call_data['transcript']
    if "cost" in call_data.keys():
        data["total_cost"] = call_data['cost']
    if "endedReason" in call_data.keys():
        data["end_reason"] = call_data['endedReason']
    if "customer" in call_data.keys():
        data["phone"] = call_data['customer']['number']

    Appointment_date = None
    Appointment_time = None
    Appointment_date_time = None

    if "analysis" in call_data.keys():
        Appointment_date = call_data['analysis']['structuredData']['Appointment Date']
        Appointment_time = call_data['analysis']['structuredData']['Appointment Time']
        Accuracy = call_data['analysis']['successEvaluation']
        if Appointment_date and Appointment_time:
            Appointment_date_time = f"{Appointment_date} {Appointment_time}"

    if "endedAt" in call_data.keys():
        data["call_date"] = call_data['endedAt'].split("T")[0]
        ended_at = parse(call_data['endedAt'])
        started_at = parse(call_data['startedAt'])
        data["duration"] = int((ended_at - started_at).total_seconds())
        print("...........................data..................................")
        print("data: ", data)
        # exit()
    result = supabase.table("call_logs").insert([data]).execute()
    print("result: ", result)
    data["summary"] = None

    Last_Date_called = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    Confidence = Accuracy
    print(Confidence)
    # Total_calls =

    model = ChatOpenAI(api_key=openai_api_key,
                       temperature=0.6,
                       model="gpt-4o")
    prompt = f"""You are a helpful assistant. Your job is read summary and write answer according to instructions.

### Summary:
{data["summary"]}   

### Instructions:
1. Call_back: if someone does not pick up the phone or if they do pick up but hard to understand or needs a follow up with no appt.
2. Wrong_Number: the number given does not correlate to the persons name. Need to make sure this is out of the dialing system or if there are Recorded Message ,Number not in service, call cannot be completed, Invalid Number, Silence on call, call dropped Immediately than we need to filter that out..
3. Do_not_call: if someone says the words "do not call" "stop calling Me" etc. we need to filter that out
4. Successful_sale: basically we have appt set this client and is sent our calendar so a human can call them back.
5. Not_Intrested: if someone says the words "not intrested" "stop" etc. we need to filter that out.
Make Sure Your answer only contains one of these options: Call_back, Wrong_Number, Do_not_call, Successful_sale, Not_Intrested.   
No need to write anything else.

### Answer:

"""
    # print("prompt: ", prompt)
    answer = model.invoke(prompt)
    # print("answer: ", answer)

    answers = model.invoke(prompt).content.strip()
    if answers == "Wrong_Number":
        status = "F"
    elif answers == "Not_Intrested":
        status = "NI"
    elif answers == "Do_not_call":
        status = "DNC"
    elif answers == "Successful_sale":
        status = "S"
    else:
        status = "C"

        # status="NI"
    if status == "NI":
        Next_call_Date = Last_Date_called + relativedelta(months=2)
    else:
        Next_call_Date = ""

    # status updation in csv
    if file_path.split(".")[-1] == "csv":
        datacsv = pd.read_csv(file_path)
    else:
        datacsv = pd.read_excel(file_path)

    # print(phone_number)
    # print(data['customer']['phone'])
    # exit()
    # if data['customer']['phone'].startswith("+1"):
    #     phone_num = data['phone'][2:]  # Remove the first two characters '+1'
    # else:
    #     phone_num = data['phone']  # Assign the phone number as is if it doesn't start with '+1'

    # print(phone_num)

    # # Ensure datacsv is a DataFrame and update the status for the phone number
    # if isinstance(datacsv, pd.DataFrame):
    #     if 'status' in datacsv.columns:
    #         datacsv['status'] = datacsv['status'].astype(str)
    #     else:
    #         datacsv['status'] = ""

    #     datacsv.loc[datacsv['Phone_Number'] == phone_num, 'status'] = status
    #     print(datacsv)
    # #exit()
    # #data.loc[datacsv['Phone_Number'] == phone_num, 'status'] = status

    # if file_path.split(".")[-1] == "csv":
    #     datacsv.to_csv(file_path, index=False)
    # else:
    #     datacsv.to_excel(file_path, index=False)

    # print("status updated for the specific Phone_Number")
    # print("..................................................................")
    print(status, Last_Date_called, Appointment_date_time, Next_call_Date, Confidence)
    print("...................................................................")

    # Convert datetime objects to strings
    last_call_date_str = Last_Date_called.isoformat() if Last_Date_called else None
    next_call_date_str = Next_call_Date.isoformat() if Next_call_Date else None

    # supabase.table("call_status").insert([{"call_log_id": result.data[0]['id'], "status": answer.content}]).execute()
    supabase.table("call_status").insert([{"call_log_id": result.data[0]['id'], "status": status,
                                           "last_call_date": last_call_date_str, "appt_date": Appointment_date_time,
                                           "next_call_date": next_call_date_str, "accuracy": Confidence}]).execute()

    lock.acquire()
    # append phone number to free phone numbers
    with open("free_phone_numbers.json", "r") as f:
        free_phone_numbers = f.read().splitlines()
    for i in range(len(free_phone_numbers)):
        free_phone_numbers[i] = free_phone_numbers[i].replace("'", "\"")
    free_phone_numbers.append(phone_number)
    with open("free_phone_numbers.json", "w") as f:
        for item in free_phone_numbers:
            f.write("%s\n" % item)
    lock.release()


def run_call_script(file_path, compaign_id):
    # get all data from compaigns table

    get_compaigns = supabase.table("campaigns").select("*").eq("campaignid", compaign_id).execute()
    compaigns = get_compaigns.data[0]
    print("compaigns: ", compaigns)
    compaign_details = supabase.table("campaign_details").select("*").eq("campaignid",
                                                                         compaigns['campaignid']).execute()
    print("assistants: ", compaign_details.data)
    count = 0
    compagin_data = {}
    compagin_data['phone_assistant'] = []
    compagin_data['compaign_id'] = compaigns['campaignid']
    compagin_data['assistant'] = compaigns['assistant']
    compagin_data['script'] = compaigns['script']
    for compaign_detail in compaign_details.data:
        assistant = supabase.table("assistants").select("*").eq("id", compaign_detail['assistant_id']).execute()
        phonelines = supabase.table("phonelines").select("*").eq("clients_id",
                                                                 compaigns['client_id']).execute()
        print("phonelines: ", phonelines.data)
        print("assistant_id: ", assistant.data[0]['assistant_id'])
        print("linenumber: ", phonelines.data[0]['linenumber'])
        print("provider: ", phonelines.data[0]['provider'])
        print("phoneNumberID: ", phonelines.data[0]['phoneNumberID'])
        compagin_data['phone_assistant'].append(
            {
                'assistant_id': assistant.data[0]['assistant_id'],
                'linenumber': phonelines.data[0]['linenumber'],
                'phonenumberid': phonelines.data[0]['phoneNumberID'],
            }
        )
        count += 1
    print("compaigns: ", compagin_data)
    result = supabase.table("campaigns").update({"status": 1}).eq("campaignid", compaign_id).execute()
    print("result: ", result)
    run_compaign(file_path, auth_token, compagin_data)


def pause_campaign(compaign_id):
    # check if the campaign is exists in the stop_campaign table
    data = supabase.table("stop_campaign").select("*").eq("campaign_id", compaign_id).execute()
    if data.data == []:
        compaigns = supabase.table("campaigns").select("*").eq("campaignid", compaign_id).execute()
        if compaigns.data == []:
            return "Campaign Not Found"
        else:
            if compaigns.data[0]['status'] == 0:
                return "Campaign Already Paused"
        compaigns = compaigns.data[0]
        if compaigns['status'] == 0:
            return "Campaign Already Paused"
        if compaigns['status'] == -1:
            return "Campaign not started yet"

        # insert the campaign id into the stop_campaign table
        result = supabase.table("stop_campaign").insert([{"campaign_id": compaign_id}]).execute()
        if result != []:
            result = supabase.table("campaigns").update({"status": 0}).eq("campaignid", compaign_id).execute()
            print("result: ", result)
            return "Campaign Paused"
        else:
            return "Error Occured"
    else:
        return "Campaign Already Paused"


def resume_campaign(compaign_id):
    # check if the campaign is exists in the stop_campaign table
    data = supabase.table("stop_campaign").select("*").eq("campaign_id", compaign_id).execute()
    if data.data != []:
        result = supabase.table("stop_campaign").delete().eq("campaign_id", compaign_id).execute()
        if result != []:
            result = supabase.table("campaigns").update({"status": 1}).eq("campaignid", compaign_id).execute()
            print("result: ", result)
            return "Campaign Resumed"
        else:
            return "Error Occured"
    else:
        return "Campaign Already Running"

# ...........................................................................................


# gourav code no use now

# import psycopg2
# import psycopg2.extras  # Import this for DictCursor

# def run_call_script(file_path, compaign_id):
#     # Establish a connection to the Supabase database using psycopg2
#     conn = psycopg2.connect(
#         dbname="postgres",
#         user="postgres.noftclbwuzuhixreykej",
#         password="Agrawal#123",
#         host="aws-0-ap-south-1.pooler.supabase.com",
#         port="6543"
#     )
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#     try:
#         # Fetch data from campaigns table
#         cursor.execute("SELECT * FROM campaign ", (compaign_id,))
#         compaigns = cursor.fetchone()

#         if compaigns is None:
#             print("Campaign not found.")
#             return

#         print("compaigns: ", compaigns)

#         # Fetch data from campaign_details table
#         cursor.execute("SELECT * FROM campaign_details ", (compaigns['campaignid'],))
#         compaign_details = cursor.fetchall()
#         print("assistants: ", compaign_details)

#         count = 0
#         compagin_data = {
#             'phone_assistant': [],
#             'compaign_id': compaigns['campaignid'],
#             'assistant': compaigns['assistant'],
#             'script': compaigns['script']
#         }

#         for compaign_detail in compaign_details:
#             # Fetch data from assistants table
#             cursor.execute("SELECT * FROM assistants WHERE id = %s", (compaign_detail['assistant_id'],))
#             assistant = cursor.fetchone()

#             # Fetch data from phonelines table
#             cursor.execute("SELECT * FROM phonelines WHERE phonelineid = %s", (compaign_detail['phoneline_id'],))
#             phonelines = cursor.fetchone()

#             print("phonelines: ", phonelines)
#             print("assistant_id: ", assistant['assistant_id'])
#             print("linenumber: ", phonelines['linenumber'])
#             print("provider: ", phonelines['provider'])
#             print("phoneNumberID: ", phonelines['phoneNumberID'])

#             compagin_data['phone_assistant'].append({
#                 'assistant_id': assistant['assistant_id'],
#                 'linenumber': phonelines['linenumber'],
#                 'phonenumberid': phonelines['phoneNumberID']
#             })

#             count += 1

#         print("compaigns: ", compagin_data)


#         cursor.execute("UPDATE campaign SET status = 1 WHERE campaignid = %s", (compaign_id,))
#         conn.commit()

#         print("Campaign status updated.")

#         run_compaign(file_path, auth_token, compagin_data)

#     except psycopg2.Error as e:
#         print("Error executing SQL:", e)


# def pause_campaign(compaign_id):
#     # no index data has been used only status updated using campaign table
#     try:

#         conn = psycopg2.connect(
#             dbname="postgres",
#             user="postgres.noftclbwuzuhixreykej",
#             password="Agrawal#123",
#             host="aws-0-ap-south-1.pooler.supabase.com",
#             port="6543"
#         )
#         cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


#         cursor.execute("SELECT * FROM stop_campaign", (compaign_id,))
#         stop_campaign_data = cursor.fetchone()

#         if not stop_campaign_data:

#             cursor.execute("SELECT * FROM campaign ", (compaign_id,))
#             campaign_data = cursor.fetchone()

#             if not campaign_data:
#                 return "Campaign Not Found"

#             if campaign_data['status'] == 0:
#                 return "Campaign Already Paused"

#             if campaign_data['status'] == -1:
#                 return "Campaign not started yet"


#             cursor.execute("INSERT INTO stop_campaign  VALUES (%s)", (compaign_id,))
#             conn.commit()


#             cursor.execute("UPDATE campaign SET status = 0 WHERE campaignid = %s", (compaign_id,))
#             conn.commit()

#             print("Campaign Paused")
#             return "Campaign Paused"

#         else:
#             print("Campaign Already Paused")
#             return "Campaign Already Paused"

#     except psycopg2.Error as e:
#         print("Error executing SQL:", e)
#         return "Error Occurred"

# def resume_campaign(compaign_id):
#     # no index data has been used only status updated using campaign table

#     try:

#         conn = psycopg2.connect(
#             dbname="postgres",
#             user="postgres.noftclbwuzuhixreykej",
#             password="Agrawal#123",
#             host="aws-0-ap-south-1.pooler.supabase.com",
#             port="6543"
#         )
#         cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#         # Check if the campaign exists in the stop_campaign table
#         cursor.execute("SELECT * FROM stop_campaign ", (compaign_id,))
#         stop_campaign_data = cursor.fetchone()

#         if stop_campaign_data:
#             # Delete the campaign from the stop_campaign table
#             cursor.execute("DELETE FROM stop_campaign ", (compaign_id,))
#             conn.commit()

#             # Update status in campaigns table to resume the campaign
#             cursor.execute("UPDATE campaign SET status = 1 WHERE campaignid = %s", (compaign_id,))
#             conn.commit()

#             print("Campaign Resumed")
#             return "Campaign Resumed"
#         else:
#             print("Campaign Already Running")
#             return "Campaign Already Running"

#     except psycopg2.Error as e:
#         print("Error executing SQL:", e)
#         return "Error Occurred"


