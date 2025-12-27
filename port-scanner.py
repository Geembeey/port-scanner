import socket
import sys
import time
from datetime import datetime
import concurrent.futures


# This tool scans a target IP for open ports using multi-threading for speed.
# It demonstrates usage of: Sockets, Threading, and Error Handling.

def scan_port(target, port):
    """
    Attempts to connect to a specific port on the target.
    Returns the port number if open, None otherwise.
    """
    try:
        # Create a socket object (IPv4, TCP)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)  # 0.5s timeout to keep it fast
            
            # Attempt connection
            result = s.connect_ex((target, port))
            
            # If result is 0, the port is OPEN
            if result == 0:
                try:
                    # Optional: Try to grab the service banner
                    banner = s.recv(1024).decode().strip()
                except:
                    banner = "Unknown Service"
                return port, banner
    except:
        pass
    return None

def runner():
    # Get Target from User
    target_input = input("Enter target IP or URL (e.g., scanme.nmap.org): ")
    
    try:
        # Resolve hostname to IP to ensure we have a valid address
        target_ip = socket.gethostbyname(target_input)
    except socket.gaierror:
        print("\n[!] Error: Hostname could not be resolved.")
        sys.exit()

    print("-" * 50)
    print(f"Scanning Target: {target_ip}")
    print(f"Time Started:    {datetime.now()}")
    print("-" * 50)

    start_time = time.time()
    open_ports = []

    # Multi-threaded Scanning
    # ThreadPoolExecutor to scan multiple ports at once (much faster than a loop)
    print("Scanning ports 1-1024... please wait.\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Create a list of future tasks for ports 1 to 1024
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(1, 1025)}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                port_num, banner = result
                print(f"[+] Port {port_num:<5} is OPEN  :  {banner}")
                open_ports.append(port_num)

    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 50)
    print(f"Scan completed in {duration:.2f} seconds.")
    print(f"Total Open Ports: {len(open_ports)}")
    print("-" * 50)

if __name__ == "__main__":
    try:
        runner()
    except KeyboardInterrupt:
        print("\n\n[!] User interrupted the scan. Exiting...")
        sys.exit()