import jwt
import os
from dotenv import load_dotenv
load_dotenv()

def get_user_id(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        payload['message'] = "Success"
        return payload
    except Exception as error:
        return {"_id":None, 'message':str(error)}