import json
import requests
import time
from datetime import datetime, timedelta

# API 정보
USERNAME = 'youhost'
PASSWORD = '1dnsdud@%*)'
API_URL = f'http://{USERNAME}:{PASSWORD}@172.28.94.83:9096/api/v1/'

# API endpoint 목록
def get_clients():
    request_api('get', 'clients')

def get_schedules_status():
    request_api('get', 'schedules/status')

def get_jobs():
    request_api('get', 'jobs')

def get_job_shows():
    request_api('get', 'jobs/show')

def run_full_backup(jobName):
    request_data = {
        'name': 'hyper-v_150_i',
        'level': 'F',
        'client': 'hyper-v_150-client',
        'storage': 'hyper-v_150-sd',
        'pool': 'hyper-v_150-pool_i',
        'fileset': 'hyper-v_150-file'
    }

    request_api('post', 'jobs/run', request_data)

# API 요청 함수
def request_api(method, endpoint, request_data=''):
    request = getattr(requests, method)
    response = request(f'{API_URL}/{endpoint}', json=request_data)

    print(json.dumps(response.json(), indent=2))

# endpoint 실행
# get_clients()
get_jobs()
# run_full_backup('hyper-v_150_i')