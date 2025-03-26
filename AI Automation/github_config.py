import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
CALLBACK_URL = os.getenv('GITHUB_CALLBACK_URL', 'http://localhost:8501/auth/github/callback')

# GitHub API endpoints
AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
API_BASE_URL = 'https://api.github.com/'

SCOPES = ['repo', 'user']