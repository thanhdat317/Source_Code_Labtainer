#!/bin/bash
# Fix permissions on SSH keys for root ssh login
chmod 700 /root /root/.ssh
chmod 600 /root/.ssh/authorized_keys
chown -R root:root /root /root/.ssh
