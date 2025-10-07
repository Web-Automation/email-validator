import socket

"""********************************************************************************
* Helper function to attempt a socket connection to a specific domain and port.
* This replaces the use of the 'ping' command and works within AWS Lambda.

* @param domain: str - The domain name or IP address to connect to.
* @param port: int - The port to connect to (e.g., 443 for HTTPS).
* @param timeout: int - Timeout duration in seconds.
* @return: bool - True if the connection was successful, False otherwise.
*********************************************************************************"""

def try_port(domain, port, timeout=2):
    try:
        # Set a default timeout for socket operations
        socket.setdefaulttimeout(timeout)

        # Attempt to open a connection to the domain and port
        with socket.create_connection((domain, port), timeout=timeout):
            print(f"Domain {domain} is reachable on port {port}.")
            return True

    except (socket.timeout, socket.gaierror, OSError) as e:
        # Log connection errors such as timeouts or unreachable domains
        print(f"Domain {domain} is not reachable on port {port}. Error: {e}")
        return False



"""********************************************************************************
* Function to check if a domain is reachable by testing multiple common ports.
* Replaces system 'ping' command which is not available in AWS Lambda.

* @param domain: str - The domain name or IP address to check.
* @return: bool - Returns True if the domain responds on port 443 or 80,
*                 otherwise returns False.
*********************************************************************************"""

def ping_domain(domain):
    try:
        # Try connecting to port 443 (HTTPS)
        if try_port(domain, 443):
            return True

        # If port 443 fails, try connecting to port 80 (HTTP)
        if try_port(domain, 80):
            return True

        # If both ports fail, the domain is considered unreachable
        print(f"Domain {domain} did not respond to socket connection on port 443 or 80.")
        return False

    except Exception as e:
        # Handle unexpected errors such as invalid domain format
        print(f"Error while checking domain {domain}: {e}")
        return False
