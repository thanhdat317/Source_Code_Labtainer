#!/usr/bin/env python3
"""Apply the reference net-dmz firewall policy from the Labtainer VM host.

Run after ``start.py net-dmz -q`` as the VM's student account.  The script
discovers the parameterized DMZ address instead of embedding a seed-specific
value, then configures the two gateway containers and runs the student-side
tests that checkwork consumes after the lab is stopped.
"""
from __future__ import annotations

import json
import subprocess


LAB = "net-dmz"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def docker(container: str, script: str, *args: str) -> None:
    subprocess.run(
        ["docker", "exec", f"{LAB}.{container}.student", "bash", "-c", script, "bash", *args],
        check=True,
    )


def main() -> None:
    networks = json.loads(
        run(
            "docker",
            "inspect",
            f"{LAB}.web_server.student",
            "--format",
            "{{json .NetworkSettings.Networks}}",
        )
    )
    web_ip = networks["dmz"]["IPAddress"]
    inner_networks = json.loads(
        run(
            "docker",
            "inspect",
            f"{LAB}.inner_gw.student",
            "--format",
            "{{json .NetworkSettings.Networks}}",
        )
    )
    inner_dmz_ip = inner_networks["dmz"]["IPAddress"]

    # Bring up the parameterized routing/NAT baseline before applying the
    # restrictive rules.  Students normally get this baseline from fixlocal.
    for container in ("remote_gw", "outer_gw", "inner_gw", "ws1", "ws2", "ws3", "isp", "dns"):
        docker(container, "bash /etc/rc.local || true")
    docker("remote_ws", "ip route replace default via 203.0.113.1")
    docker("web_server", "ip route replace default via 198.18.1.2")
    docker("web_server", f"ip route add 198.18.1.128/25 via {inner_dmz_ip} || true")

    docker(
        "outer_gw",
        """
        set -eu
        web_ip=$1
        iptables --flush
        iptables -t nat --flush
        iptables --delete-chain
        iptables -t nat --delete-chain
        iptables -P INPUT ACCEPT
        iptables -P OUTPUT ACCEPT
        iptables -P FORWARD DROP
        iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
        # remote_gw performs source NAT, so Outer Gateway sees 198.18.0.3.
        iptables -A FORWARD -s 198.18.0.3 -d "$web_ip" -p tcp -m multiport --dports 22,80,443 -j ACCEPT
        iptables -A FORWARD -s 198.18.1.128/25 ! -d 198.18.1.0/24 -j ACCEPT
        """,
        web_ip,
    )
    docker(
        "inner_gw",
        """
        set -eu
        web_ip=$1
        iptables --flush
        iptables -t nat --flush
        iptables --delete-chain
        iptables -t nat --delete-chain
        iptables -P INPUT ACCEPT
        iptables -P OUTPUT ACCEPT
        iptables -P FORWARD DROP
        iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
        iptables -A FORWARD -s 198.18.1.128/25 -d "$web_ip" -p tcp -m multiport --dports 22,80,443,3306 -j ACCEPT
        iptables -A FORWARD -s 198.18.1.128/25 ! -d "$web_ip" -j ACCEPT
        """,
        web_ip,
    )
    docker("remote_ws", "nmap -n www.example.com; wget 198.18.1.194 -T 3 -t 1 || true")
    docker("ws1", "nmap -n www.example.com; wget www.google.com -T 5 -t 1 || true")


if __name__ == "__main__":
    main()
