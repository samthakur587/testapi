import time
import requests
from stem import Signal
from stem.control import Controller
# Tor proxy configuration
PROXY = {
        "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
            }
# Optional: Add the Tor control port password here if authentication is configured
TOR_PASSWORD = '16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C'  # Replace with your password if required, otherwise keep as None
def get_current_ip():
    """Fetch current IP using an external service."""
    try:
        response = requests.get("http://httpbin.org/ip", proxies=PROXY, timeout=10)
        response.raise_for_status()
        return response.json().get("origin", "Unknown")
    except requests.exceptions.RequestException as e:
        return f"Error fetching IP: {e}"
def renew_tor_ip():
    """Send NEWNYM signal to Tor to get a new IP."""
    try:
        with Controller.from_port(port=9051) as controller:
            if TOR_PASSWORD:
                controller.authenticate(password=TOR_PASSWORD)
            else:
                controller.authenticate()  # Use cookie authentication if no password is set
            controller.signal(Signal.NEWNYM)
            print("New Tor identity requested.")
    except Exception as e:
        print(f"Error while renewing Tor IP: {e}")
# if __name__ == "__main__":
#     for attempt in range(5):  # Attempt to change IP and make multiple requests
#         print(f"Attempt {attempt + 1}:")
#         current_ip = get_current_ip()
#         print("Current IP:", current_ip)
        
#         renew_tor_ip()
        
#         # Wait for the new identity to be established
#         print("Waiting for Tor to establish a new identity...")
#         time.sleep(5)  # Adjust the delay if needed
