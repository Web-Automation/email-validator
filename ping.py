import subprocess
import platform


"""********************************************************************************
* Function to ping a domain and check if it responds.

* @param {string} domain - The domain name to ping.
* @returns {boolean} - Returns True if the domain responds to ping, False otherwise.
*********************************************************************************"""

def ping_domain(domain):
    try:
        # Platform-specific ping command
        command = ['ping', '-c', '4', domain] if platform.system().lower() != 'windows' else ['ping', '-n', '4', domain]
        
        # Run the ping command and capture the result
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Return True if the ping was successful
        if response.returncode == 0:
            print(f"Domain {domain} responded to ping.")
            return True
        else:
            print(f"Domain {domain} did not respond to ping.")
            return False
    except Exception as e:
        print(f"Error while pinging domain {domain}: {e}")
        return False
