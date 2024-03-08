from dotenv import load_dotenv
import os
load_dotenv()

#GOOGLE OAUTH2
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
#FACEBOOK OAUTH2
F_CLIENT_ID = os.getenv("F_CLIENT_ID")
F_CLIENT_SECRET = os.getenv("F_CLIENT_SECRET")