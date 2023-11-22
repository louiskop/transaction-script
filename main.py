import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def handleCredentials():
    creds = None

    # Check if credentials exist
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Create credentials if not exist
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def main():
    print("[+] Attempting to read inbox ...")
    creds = handleCredentials()

    try:
        
        # Filter by unread and banking address
        query = 'from:notifyme@absa.co.za AND is:unread'

        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print('[+] No messages found.')
        else:
            print('[+] Found ' + str(len(messages)) + ' transactions')
            for message in messages:
                
                # Mark the message as read by removing the UNREAD label
                # msg_id = message['id'] 
                # service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

                # extract data out of message
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                msg = msg["snippet"]
                transaction = {
                    "account": msg.split("Account : ")[1].split(" Date")[0],
                    "type": msg.split("Transaction: ")[1].split(" Merchant")[0],
                    "beneficiary": msg.split("Merchant : ")[1].split(" Reserved")[0],
                    "amount": msg.split("Reserved : ")[1].split(" Available")[0]
                }
                print(transaction);
                # call actual api


    except HttpError as error:
        # Print any errors
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()