import imaplib
import email
import base64
import os
import time
from datetime import datetime
from dotenv import load_dotenv

updation_period = 60  # Check every 60 seconds

# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'

# Your email credentials
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def authenticate_gmail():
    """Authenticate to Gmail IMAP server."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    return mail

def get_image_from_gmail(mail):
    """Fetch the most recent email with an image attachment and save the image if it does not exist."""
    mail.select('inbox')

    result, data = mail.search(None, '(X-GM-RAW "has:attachment")')
    mail_ids = data[0].split()

    if not mail_ids:
        print("No messages found.")
        return None

    # Process the most recent email
    latest_email_id = mail_ids[-1]
    result, data = mail.fetch(latest_email_id, '(RFC822)')
    
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        if part.get_content_type().startswith('image/'):
            filename = part.get_filename()
            if filename:
                img_data = part.get_payload(decode=True)
                img_path = 'latest_image.jpg'
                if os.path.exists(img_path):
                    # Read data from existing file to compare
                    with open(img_path, 'rb') as f:
                        existing_img_data = f.read()
                        
                    if img_data == existing_img_data: # No new images arrived
                        return None
                    else:
                        with open(img_path, 'wb') as f:
                            f.write(img_data)
                        return img_path
                else:
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    return img_path
    return None

def main():
    """Main function to authenticate and periodically check for new images."""
    mail = authenticate_gmail()
    
    while True:
        image_path = get_image_from_gmail(mail)
        if image_path:
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"New image saved to {image_path} : {formatted_time}")
        time.sleep(updation_period)

if __name__ == '__main__':
    main()
