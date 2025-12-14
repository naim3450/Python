from plyer import notification
from datetime import datetime

# Get the current date
current_date = datetime.now()
print(current_date)

# Check if today's date is March 3rd
if current_date.month == 3 and current_date.day == 3:
    # Show notification if it is March 3rd
    notification.notify(
        title='Happy Birthday!',
        message="🎉 Wishing you a wonderful birthday! 🎂",
        timeout=10  # Notification will be visible for 10 seconds
    )
