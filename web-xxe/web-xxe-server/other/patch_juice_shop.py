#!/usr/bin/env python3
"""Enable the XXE exercise and write deterministic grading events.

Juice Shop disables XXE parsing in Docker by default.  This lab deliberately
enables it only inside this isolated Labtainer image and records which
exercise payload was processed so that checkwork can grade the lab.
"""
from pathlib import Path

route = Path("/juice-shop_11.1.2/routes/fileUpload.js")
source = route.read_text(encoding="utf-8")
old_guard = "if (file.buffer && !utils.disableOnContainerEnv()) { // XXE attacks in Docker/Heroku containers regularly cause \"segfault\" crashes"
new_guard = "if (file.buffer) { // Intentionally enabled for this isolated Labtainer XXE exercise"
if old_guard not in source:
    raise SystemExit("expected Juice Shop XML-upload guard was not found")
source = source.replace(old_guard, new_guard, 1)
old_parse = """        const xmlString = xmlDoc.toString(false)
        utils.solveIf(challenges.xxeFileDisclosureChallenge"""
new_parse = """        const xmlString = xmlDoc.toString(false)
        const xxeTarget = data.includes('/opt/secret/flag.txt') ? '/opt/secret/flag.txt' :
          (data.includes('/etc/passwd') ? '/etc/passwd' : 'other')
        console.log('[LAB-XXE] payload=' + file.originalname + ' target=' + xxeTarget)
        utils.solveIf(challenges.xxeFileDisclosureChallenge"""
if old_parse not in source:
    raise SystemExit("expected Juice Shop XML parsing block was not found")
route.write_text(source.replace(old_parse, new_parse, 1), encoding="utf-8")
