import dns.resolver 


"""****************************************************************************************************************************************************
* Function to retrieve the MX (Mail Exchange) record for a given domain.
* This function first checks if the domain exists by resolving its A record. 
* If it exists, it then attempts to retrieve the MX record, which is used to identify the mail server responsible for receiving emails for that domain.

* @param {string} domain - The domain name to check for MX records.
* @returns {string|null} - The primary MX record (mail server) for the domain, or None if not found.
****************************************************************************************************************************************************"""

def get_mx_record(domain):
    try:
        # First, ensure the domain exists by querying A records (basic DNS lookup)
        dns.resolver.resolve(domain, 'A') # This will raise an exception if the domain doesn't exist
    except dns.resolver.NXDOMAIN:
        print(f"Domain {domain} does not exist.") 
        return None
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")
        return None

    try:
        # Query DNS for MX record
        answers = dns.resolver.resolve(domain, 'MX')
        # Query for MX records
        answers = dns.resolver.resolve(domain, 'MX')
        
        # Extract priority and mail server from each MX record
        mx_records = [(r.preference, str(r.exchange).rstrip('.')) for r in answers]  # r.preference = priority (lower = higher priority) & r.exchange = mail server domain (e.g., 'mail.example.com.')
        # If the list is empty, log and return None
        if not mx_records:
            print(f"No MX records found for {domain}.")
            return None
        
        # Sort MX records by priority (ascending order)
        sorted_mx = sorted(mx_records, key=lambda x: x[0])  # Sort by priority
        return sorted_mx
    except dns.resolver.NoAnswer:
        print(f"MX record for {domain}: (no answer from DNS)")  # No answer from DNS
        return None
    except Exception as e:
        print(f"Error getting MX record for {domain}: {e}")  # General error handling
        return None
