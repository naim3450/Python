import pywhatkit as kit
from datetime import datetime
import time

# Get the current date
current_date = datetime.now()

# Check if today's date is March 3rd
if current_date.month == 3 and current_date.day == 4:
    # Time when the message should be sent (send at 10:00 AM, for example)
    hour = 24
    minute = 0
    
    # Phone number to send the message to (ensure the number includes the country code)
    phone_number = "+8801994337045"  # Bangladesh country code +880
    
    # Message to send
    message = "checck your inbox"

    # Send WhatsApp message using pywhatkit
    kit.sendwhatmsg(phone_number, message, hour, minute)
    print(f"Message scheduled to be sent at {hour}:{minute} on March 3rd.")
else:
    print("Today is not March 3rd.")
