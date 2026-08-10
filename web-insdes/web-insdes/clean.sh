#!/bin/sh
sleep 5
while true; do
  find /home -type d \( -name ".mozilla" \) -exec rm -rf {} + 2>/dev/null
  sleep 1
done
