# from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect, File, Form, UploadFile, status, \
#       Response
# from pydantic import BaseModel
# import pandas as pd
# import os
# import asyncio
# import glob
# from .crud import *
# from threading import Thread
# from supabase import create_client, Client
# import json

# router = APIRouter(
#     prefix="/vapi",
#     tags=["vapi"]
# )

# # Define the directory where the uploaded files will be stored
# UPLOAD_DIR = "static/"

# # Global variables to store the latest uploaded file path and campaign ID
# latest_file_path = None
# latest_campaign_id = None
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxeGJwd2p0enFwbndtaWl3d2tlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY0Mzk3ODksImV4cCI6MjAzMjAxNTc4OX0.G8LJ71M9VsC73bhyWJNMigvcv8ehVveq42Pu3cndQ-0"
# SUPABASE_URL = "https://iqxbpwjtzqpnwmiiwwke.supabase.co"

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# #event handling via websocket
# pause_event = asyncio.Event()
# pause_event.set()


# @router.post("/uploadfile/")
# async def handle_upload(ClientID: str = Form(), CampaignID: str = Form(), file: UploadFile = File(...)):
#     if file.filename.split(".")[-1] not in ['csv', 'xlsx']:
#         return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Only CSV and Excel files are allowed")
#     file_location = f"{file.filename}"
#     parrent_dir = "static/"
#     if not os.path.exists(parrent_dir):
#         os.makedirs(parrent_dir)
#     if not os.path.exists(f"{parrent_dir}{ClientID}"):
#         os.makedirs(f"{parrent_dir}{ClientID}")
#     if not os.path.exists(f"{parrent_dir}{ClientID}/{CampaignID}"):
#         os.makedirs(f"{parrent_dir}{ClientID}/{CampaignID}")
#     file_location = f"{parrent_dir}{ClientID}/{CampaignID}/{file_location}"
#     with open(file_location, "wb+") as file_object:
#         file_object.write(await file.read())

#     call_thread = Thread(target=run_call_script, args=(file_location, CampaignID))
#     call_thread.daemon = True
#     call_thread.start()
#     print(Response)
#     return Response(status_code=status.HTTP_200_OK, content="File uploaded successfully")

# @router.get("/pausecampaign/")
# async def pause_calls(campaign_id: int):
#     try:
#         result = pause_campaign(campaign_id)
#         if result == "Campaign Paused":
#             pause_event.clear()
#             return Response(status_code=status.HTTP_200_OK, content=json.dumps({"details": result}))
#             print(result)
#         else:
#             print(result)
#             return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": result}))
#     except Exception as e:
#         return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": str(e)}))


# @router.get("/resumecampaign/")
# async def resume_calls(campaign_id: int):
#     try:
#         result = resume_campaign(campaign_id)
#         if result == "Campaign Resumed":
#             pause_event.set()
#             return Response(status_code=status.HTTP_200_OK, content=json.dumps({"details": result}))
#             print("...................................................")
#             print(Response)
#         else:
#             print(result)
#             return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": result}))
#     except Exception as e:
#         return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": str(e)}))


# @router.websocket("/ws/get_dialer_index")
# async def websocket_get_dialer_index(websocket: WebSocket):
#     # file_location = f"{file.filename}"
#     parrent_dir = "static/"
#     if not os.path.exists(parrent_dir):
#         os.makedirs(parrent_dir)

#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_json()
#             campaign_id = data.get('campaign_id')
#             client_id = data.get('client_id')

#             file_location = parrent_dir + "/" + str(client_id) + "/" + str(campaign_id)

#             all_csv = glob.glob(f"{file_location}/*.csv")[0]

#             while True:
#                 await pause_event.wait() #if the pause campaign triggered than it should stop
#                 rows = supabase.table("campaign_status").select("*").eq("campaign_id", campaign_id).execute()

#                 print("...............................websocket.............................")
#                 print(rows)
#                 if not rows:
#                     await websocket.send_json({"error": "No matching records found for the given campaign ID."})
#                     break

#                 df = pd.read_csv(all_csv)
#                 print(df)
#                 result = df.loc[rows.data[0]['row_number'], ['First_Name', 'Last_Name', 'Phone_Number']]
#                 print(result)

#                 await websocket.send_json({
#                     "index": rows.data[0]['row_number'] + 1,
#                     "total": len(df),
#                     "CampaignID": campaign_id,
#                     "Name": result['First_Name'] + " " + result['Last_Name'],
#                     "phone_number": str(result['Phone_Number'])
#                 })

#                 await asyncio.sleep(1)  # Adjust the sleep time as needed to control the polling frequency
#     except WebSocketDisconnect:
#         print("Client disconnected")


from fastapi import FastAPI, APIRouter, Query, HTTPException, WebSocket, WebSocketDisconnect, File, Form, UploadFile, \
    status, Response
from pydantic import BaseModel
from starlette.responses import FileResponse
import pandas as pd
import os
import asyncio
import glob
from threading import Thread
from supabase import create_client, Client
import json
from .crud import *
from .config import get_latest_file_location, set_latest_file_location

router = APIRouter(
    prefix="/vapi",
    tags=["vapi"]
)

# Define the directory where the uploaded files will be stored
UPLOAD_DIR = "static/"

# Global variables to store the latest uploaded file path and campaign ID
latest_file_path = None
latest_campaign_id = None
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlxeGJwd2p0enFwbndtaWl3d2tlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY0Mzk3ODksImV4cCI6MjAzMjAxNTc4OX0.G8LJ71M9VsC73bhyWJNMigvcv8ehVveq42Pu3cndQ-0"
SUPABASE_URL = "https://iqxbpwjtzqpnwmiiwwke.supabase.co"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Event handling via websocket
pause_event = asyncio.Event()
pause_event.set()


def get_latest_file_location():
    return latest_file_path


@router.post("/uploadfile/")
async def handle_upload(ClientID: str = Form(), CampaignID: str = Form(), file: UploadFile = File(...)):
    if file.filename.split(".")[-1] not in ['csv', 'xlsx']:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Only CSV and Excel files are allowed")

    file_location = f"{file.filename}"
    parrent_dir = "static/"

    if not os.path.exists(parrent_dir):
        os.makedirs(parrent_dir)
    if not os.path.exists(f"{parrent_dir}{ClientID}"):
        os.makedirs(f"{parrent_dir}{ClientID}")
    if not os.path.exists(f"{parrent_dir}{ClientID}/{CampaignID}"):
        os.makedirs(f"{parrent_dir}{ClientID}/{CampaignID}")

    file_location = f"{parrent_dir}{ClientID}/{CampaignID}/{file_location}"
    set_latest_file_location(file_location)  # Set the latest file location

    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    # current id ( as this is he primary key which must be unique )
    response = supabase.table("file_management").select("id").order("id", desc=True).limit(1).execute()
    new_id = 1
    if response.data:
        new_id = response.data[0]["id"] + 1

    # current max priority for the given client
    response = supabase.table("file_management").select("priority").eq("client_id", ClientID).order("priority",
                                                                                                    desc=True).limit(
        1).execute()
    max_priority = 0
    if response.data:
        max_priority = response.data[0]["priority"] + 1
    else:
        max_priority = 1

    file_record = {
        "id": new_id,
        "file_name": file.filename,
        "campaignid": CampaignID,
        "upload_date": datetime.utcnow().isoformat(),
        "priority": max_priority,
        "dialer_index": 0,
        "client_id": ClientID
    }

    supabase.table("file_management").insert(file_record).execute()

    call_thread = Thread(target=run_call_script, args=(file_location, CampaignID))
    call_thread.daemon = True
    call_thread.start()

    return Response(status_code=status.HTTP_200_OK, content="File uploaded successfully")


@router.get("/pausecampaign/")
async def pause_calls(campaign_id: int):
    try:
        result = pause_campaign(campaign_id)
        if result == "Campaign Paused":
            pause_event.clear()
            return Response(status_code=status.HTTP_200_OK, content=json.dumps({"details": result}))
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": result}))
    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": str(e)}))


@router.get("/resumecampaign/")
async def resume_calls(campaign_id: int):
    try:
        result = resume_campaign(campaign_id)
        if result == "Campaign Resumed":
            pause_event.set()
            return Response(status_code=status.HTTP_200_OK, content=json.dumps({"details": result}))
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": result}))
    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": str(e)}))


@router.websocket("/ws/get_dialer_index")
async def websocket_get_dialer_index(websocket: WebSocket):
    parrent_dir = "static/"

    if not os.path.exists(parrent_dir):
        os.makedirs(parrent_dir)

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            campaign_id = data.get('campaign_id')
            client_id = data.get('client_id')

            file_location = f"{parrent_dir}{client_id}/{campaign_id}"

            all_csv = glob.glob(f"{file_location}/*.csv")[0]

            while True:
                await pause_event.wait()
                rows = supabase.table("campaign_status").select("*").eq("campaign_id", campaign_id).execute()

                if not rows:
                    await websocket.send_json({"error": "No matching records found for the given campaign ID."})
                    break

                df = pd.read_csv(all_csv)
                result = df.loc[rows.data[0]['row_number'], ['First_Name', 'Last_Name', 'Phone_Number']]

                await websocket.send_json({
                    "index": rows.data[0]['row_number'] + 1,
                    "total": len(df),
                    "CampaignID": campaign_id,
                    "Name": result['First_Name'] + " " + result['Last_Name'],
                    "phone_number": str(result['Phone_Number'])
                })

                await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")


# To download the latest csv file with updated status

@router.get("/download_updated_csv/")
async def download_updated_csv(client_id: str, campaign_id: str):
    parrent_dir = "static/"
    try:
        file_location = f"{parrent_dir}{client_id}/{campaign_id}"
        all_csv = glob.glob(f"{file_location}/*.csv")
        if not all_csv:
            return Response(status_code=status.HTTP_404_NOT_FOUND, content="No file available for download")

        latest_file = max(all_csv, key=os.path.getmtime)

        return FileResponse(latest_file, filename=latest_file.split('/')[-1])

    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"details": str(e)}))


@router.websocket("/ws/get_prev_call_status")
async def websocket_get_prev_call_status(websocket: WebSocket):
    error_file_path = "error.txt"

    if not os.path.exists(error_file_path):
        open(error_file_path, "w").close()

    await websocket.accept()
    file_position = 0

    while True:
        try:

            with open(error_file_path, "r") as file:
                file.seek(file_position)
                lines = file.readlines()

                file_position = file.tell()

                for line in lines:
                    await websocket.send_json({"message": line.strip()})

            await asyncio.sleep(1)
        except WebSocketDisconnect:
            print("Client disconnected")
            break
        except Exception as e:
            await websocket.send_json({"error": str(e)})
            break
