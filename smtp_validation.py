import socket
import smtplib
from urllib import response
from suspicious_email import is_catch_all_domain



"""**************************************************************************************************************************************
* Safely terminates an SMTP connection while preventing crashes if the remote mail server has already closed the connection unexpectedly.
* This function avoids raising exceptions such as:
*     - smtplib.SMTPServerDisconnected
*     - BrokenPipeError
*     - ConnectionResetError

* @param server {smtplib.SMTP} - The SMTP connection object to be closed gracefully.
* @returns {None}
*****************************************************************************************************************************************"""

def safe_quit(server):
    try:
        if server is not None:
            try:
                server.noop()
                server.quit()
                print("SMTP connection closed cleanly.")
            except smtplib.SMTPServerDisconnected:
                print("SMTP server already disconnected, skipping quit().")
            except Exception as e:
                print(f"Graceful SMTP quit failed: {e}")
    except Exception as e:
        print(f"SMTP cleanup error: {e}")


"""******************************************************************************************************************************************************
* Performs SMTP-level verification to check if a given email address is deliverable.
* This function attempts to connect to the domain's MX server, performs a mail handshake and sends an SMTP RCPT TO command to simulate sending an email.
* Validation Steps:
*   - Attempt connection to MX host on port 25 (standard SMTP)
*   - If connection fails, retry on port 587 using STARTTLS
*   - Perform MAIL FROM and RCPT TO sequence for the target email
*   - Detect if the domain is configured as a catch-all
*   - Gracefully handle disconnections (especially from Outlook MX servers)

* @param email {string} - The recipient email address to validate.
* @param domain {string} - The MX host domain used for SMTP communication.
* @param sender_email {string} - A valid sender email used during SMTP handshake.
* @returns {tuple} - (smtp_deliverable, is_catch_all)
*                    - smtp_deliverable: True  → RCPT accepted (likely valid)
*                                        False → RCPT rejected (invalid)
*                                        None  → Unverifiable (e.g., Outlook blocks anonymous RCPT)
*                    - is_catch_all: True if the domain accepts all addresses, False otherwise.
*********************************************************************************************************************************************************"""

def smtp_delivery_check(email, domain, sender_email):
    smtp_deliverable = False
    is_catch_all = False
    smtp_connected = False
    server = None
    smtp_host = f"{domain}"
    
    # Try to connect to the SMTP server with a valid sender email for SMTP verification
    # Try SMTP on port 25 first (default SMTP port)
    try:
        print(f"Trying SMTP on port 25 for host: {smtp_host}")
        server = smtplib.SMTP(smtp_host, port=25, timeout=10)
        server.set_debuglevel(0)
        server.helo()
        server.mail(sender_email)
        smtp_connected = True
    except (socket.timeout, TimeoutError) as e:
        print(f"Port 25 timed out: {e}")
    except ConnectionRefusedError as e:
        print(f"Port 25: Connection refused: {e}")
    except Exception as e:
        print(f"Port 25 failed due to error: {e}")

     # If port 25 did not connect, fallback to port 587 with STARTTLS (secure alternative)
    if not smtp_connected:
        try:
            print(f"Falling back to port 587 with STARTTLS for host: {smtp_host}")
            server = smtplib.SMTP(smtp_host, port=587, timeout=10)
            server.set_debuglevel(0)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.mail(sender_email)
            smtp_connected = True
        except Exception as e2:
            print(f"Port 587 with STARTTLS also failed: {e2}")

    #  If connected successfully, test recipient email using RCPT TO
    if smtp_connected and server:
        try:
            # Send RCPT TO command to check if recipient exists
            code, response = server.rcpt(email)

            # Decode response bytes → lowercase string for safe text matching
            response_str = response.decode().lower() if isinstance(response, bytes) else str(response).lower()

            # Interpret SMTP status code and message to determine deliverability
            if code in (250, 251, 551):
                # 250: Accepted
                # 251: Not local but will forward
                # 551: Not local but alternative path exists
                smtp_deliverable = True

            elif code == 550:
                # 550: "Mailbox unavailable" (ambiguous — can mean invalid, blocked, or temp issue)
                if "does not exist" in response_str or "no such user" in response_str:
                    # Clear indication mailbox doesn’t exist
                    smtp_deliverable = False
                elif "spamhaus" in response_str or "blocked" in response_str or "blacklist" in response_str:
                    # Our IP or sender blocked: Cannot verify address
                    smtp_deliverable = None
                elif "mailbox full" in response_str or "over quota" in response_str:
                    # Mailbox temporarily full: Not a hard invalid
                    smtp_deliverable = None
                elif "greylist" in response_str or "try again later" in response_str:
                    # Greylisting, temporary throttle, mailbox likely exists
                    smtp_deliverable = None
                else:
                    # Any other unknown 550 message → treat as indeterminate
                    smtp_deliverable = None

            elif code in (553, 501):
                # 553: Mailbox name not allowed / invalid syntax
                # 501: Syntax error in parameters or address
                smtp_deliverable = False

            elif code in (421, 450, 451, 452, 500, 502, 503, 504, 552, 554, 252):
                # 421: Service not available (server busy)
                # 450–452: Mailbox busy, temp failure, insufficient storage
                # 500–504: Command or syntax errors
                # 552: Exceeded storage allocation
                # 554: Transaction failed / rejected
                # 252: Cannot verify user but will accept message
                # → These are not hard failures, so treat as unknown (temporary/unverifiable)
                smtp_deliverable = None

            else:
                # Unrecognized or unexpected response code → assume indeterminate
                smtp_deliverable = None

            # Check for catch-all domain behavior
            # Only perform this test if recipient was accepted (smtp_deliverable = True)
            if smtp_deliverable:
                is_catch_all = is_catch_all_domain(server, domain)

        # Error Handling for common SMTP issues during RCPT phase
        except smtplib.SMTPServerDisconnected:
            print("SMTP connection closed unexpectedly during RCPT check.")
            smtp_deliverable = None

        except smtplib.SMTPRecipientsRefused as e:
            # Happens if RCPT command was outright rejected by the server
            print(f"SMTP RCPT refused: {e}")
            smtp_deliverable = False

        except smtplib.SMTPException as e:
            # Covers other general SMTP-related exceptions
            print(f"SMTP RCPT TO error: {e}")
            smtp_deliverable = None

        except Exception as e:
            # Catches unexpected runtime or network issues
            print(f"Unexpected error during RCPT TO: {e}")
            smtp_deliverable = None

        finally:
            # Always terminate SMTP session gracefully
            safe_quit(server)

    # If SMTP never connected, mark as undeliverable (cannot verify)
    else:
        smtp_deliverable = False
        safe_quit(server)

    return smtp_deliverable, is_catch_all
