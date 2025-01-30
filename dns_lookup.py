import dns.resolver


"""**************************************************************************************************
* Function to retrieve the MX (Mail Exchange) record for a given domain.

* @param {string} domain - The domain name to check for MX records.
* @returns {string|null} - The primary MX record (mail server) for the domain, or None if not found.
****************************************************************************************************"""

def get_mx_record(domain):
    try:
        # First, ensure the domain exists by querying A records (basic DNS lookup)
        dns.resolver.resolve(domain, 'A')  # Try to resolve the domain's A records
    except dns.resolver.NXDOMAIN:
        print(f"Domain {domain} does not exist.")  # Domain doesn't exist
        return None
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")
        return None

    try:
        # Query DNS for MX record
        answers = dns.resolver.resolve(domain, 'MX')
        if answers:
            # Return the first MX record (primary mail server)
            mx_record = str(answers[0].exchange)
            if not mx_record.strip():
                print(f"MX record for {domain}: (blank or invalid)")  # Invalid MX record
                return None
            print(f"MX record for {domain}: {mx_record}")
            return mx_record
        else:
            print(f"MX record for {domain}: (no MX records found)")  # No MX records found
            return None
    except dns.resolver.NoAnswer:
        print(f"MX record for {domain}: (no answer from DNS)")  # No answer from DNS
        return None
    except Exception as e:
        print(f"Error getting MX record for {domain}: {e}")  # General error handling
        return None
