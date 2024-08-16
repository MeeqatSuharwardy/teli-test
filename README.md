## Create virtual Environment
Go to the project directory and create virtual environment 
python3 -m venv env python3.10

# To activate the environment
source env/bin/activate
make sure the environment is activated 

## installing requirements
pip install -r requirements.txt
make sure you are inside the teli-bot-backend


#after installing all the requirements 
## to run the app
uvicorn main:app --reload

## to test the websocket based route on postman
ws://localhost/vapi/ws/get_dialer_index

required Json 
{
    "campaign_id":1,
    "client_id":16
}





