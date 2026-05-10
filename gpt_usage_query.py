import requests
import json
import configparser
from datetime import datetime

def send_message(msg, key='69e37d82-5e5b-48fd-9417-e2a974eacbd1'):
    data = {
        "msg_type": "text",
        "content": {"text": msg}
    }
    headers = {'Content-Type': 'application/json'}
    send_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{key}"
    print("飞书url： " + send_url)
    response = requests.post(send_url, headers=headers, data=json.dumps(data))
    print(response.json())
    return response.json()

def query_usage(authorization):
    url = "https://chatgpt.com/backend-api/wham/usage"
    headers = {
        'Authorization': authorization,
        'User-Agent': 'codex-cli',
        'Accept': 'application/json',
        'ChatGPT-Account-Id': '4c61d369-a717-4228-abeb-ff2f077b34b1',
        'Cookie': '__cf_bm=9WsNMgCBQPG6dSdErWqRK4tVrVJ8xZlHkjWhCoCwrWQ-1778374197.4511027-1.0.1.1-9WhOYGai7jJYPuLo0LhsfdDuEo5y6LnpQh4SOUTcb6tA.k9PiagsVXYQ50KGqUqfF8aB8saqFWD.k.eVtVefQFcD8P8cXqhDd4V8Y6RYxA2LmrCs61FUpFX0aH5ci0mq; __cflb=04dTofELUVCxHqRn2Xc6Eb6eZgy5T2E4RY5B7ttDP9'
    }
    response = requests.request("GET", url, headers=headers, data={})
    # print(response.json())
    return response.json()

def read_authorizations_from_ini(ini_file):
    config = configparser.ConfigParser()
    config.read(ini_file, encoding='utf-8')
    authorizations = []
    for section in config.sections():
        if config.has_option(section, 'authorization'):
            auth = config.get(section, 'authorization')
            authorizations.append((section, auth))
    return authorizations

def convert_timestamp(ts):
    if ts:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return '-'

def main():
    ini_file = 'config.ini'
    authorizations = read_authorizations_from_ini(ini_file)

    results = []
    for name, auth in authorizations:
        try:
            data = query_usage(auth)
            email = data.get('email', '-')
            used_percent = data.get('rate_limit', {}).get('primary_window', {}).get('used_percent', '-')
            reset_at_ts = data.get('rate_limit', {}).get('primary_window', {}).get('reset_at')
            reset_at_str = convert_timestamp(reset_at_ts)

            results.append({
                'name': name,
                'email': email,
                'used_percent': used_percent,
                'reset_at': reset_at_str
            })
            print(f"{name}: {email}, used_percent: {used_percent}%, reset_at: {reset_at_str}")
        except Exception as e:
            print(f"Error querying {name}: {e}")
            results.append({
                'name': name,
                'email': '-',
                'used_percent': '-',
                'reset_at': '-'
            })

    content_feishu = "ChatGPT额度查询\n"
    for r in results:
        content_feishu += f"账号: {r['email']}, 已用: {r['used_percent']}%, 重置时间: {r['reset_at']}\n"

    send_message(content_feishu)

if __name__ == '__main__':
    main()