import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import asyncio
import re

def read_file(filename):
    try:
        file_path = filename
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
   
def CheckAbuse(data):
    print(data)
    input_dict = {"inputs":data}
    url = 'https://api-inference.huggingface.co/models/unitary/toxic-bert'
    try:
        response = requests.post(url, json=input_dict)
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def parse_url(chat_content):
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, chat_content)
    return urls

async def check_google_safe_browsing_list(chat_content):
    try:
        api_key = 'AIzaSyD_N2CoD95KczfavKY-9ceUppE8CKRWafA'  # Replace with your API key
        url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"

        request_data = {
            "client": {
                "clientId": "prayankhowal_safehaven",  # Replace with your unique client ID
                "clientVersion": "1.0",
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION", "THREAT_TYPE_UNSPECIFIED"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": chat_content}],
            },
        }

        response = requests.post(url, json=request_data)
        data = response.json()
        print("Response data:", data)

        if data.get("matches") and len(data["matches"]) > 0:
            return True  # Return true if the domain is in the Safe Browsing list
        else:
            return False

    except Exception as error:
        print("Error:", error)
        return False
    
def send_email(chat_content):
    print("")
    print("emailed")
    
    # Set up the sender and recipient email addresses
    sender_email = "game.guardian.techavishkar@gmail.com"
    recipient_email = read_file("configuration.txt")
    # Create a message object
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = "Potentially inappropriate or harmful behavior"
    # Add the message body
    body = f"Your child is facing potentially inappropriate or harmful behavior, here is thier conversation:\n\n{chat_content}\n\nMake sure that they don't feel bad for something they did not do wrong!\n\nThanks & Regards,\nThe GameGuardian Team"
    message.attach(MIMEText(body, 'plain'))
    # Set up the SMTP server and send the message
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(sender_email, 'cgqgyrctphiqnxzk')
    smtp_server.sendmail(sender_email, recipient_email, message.as_string())
    smtp_server.quit()

async def main(chat):
    abusive_content = 0
    phishing_content = 0
    chat_content = read_file(chat)
    response = CheckAbuse(chat_content)
    print("")
    print(response)

    for d in response:
        for data in d:
            #print(data)
            score = data["score"]
            if score > 0.5:
                abusive_content = 1
    
    urls_to_check = (parse_url(chat_content))
    #print(urls_to_check)
    for url in urls_to_check:
        is_harmful = await check_google_safe_browsing_list(url)

        if is_harmful:
            print("The URL(s) is/are potentially harmful.")
            phishing_content = 1
        else:
            print("The URL(s) is/are safe.")
    
    if abusive_content or phishing_content == 1:
        send_email(chat_content)

asyncio.run(main(chat="gamechat_example1.txt"))