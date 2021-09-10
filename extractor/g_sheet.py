from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = 'censored'
    SAMPLE_RANGE_NAME = 'SOLD Q3!A2:L'
    
    sheet_header = 'ID,D/O,EMAIL,Pass,PP,PROFIT,DAY TOTAL,STORE,QTY,Name,Tracking,OTC\n'
    # with open('orders_sheet.csv', 'w', encoding='utf-8') as f:
    #     f.write(sheet_header)
    
    orders_list = list()
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    path = os.path.dirname(os.path.abspath(__file__))

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    path_cred = os.path.join(path, 'token.pickle')
    if os.path.exists(path_cred):
        with open(os.path.join(path, path_cred), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(path, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(path, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            orders_list.append(row[0])
            # print(row)
            # Print columns A and E, which correspond to indices 0 and 4.
            # print('%s, %s' % (row[0], row[4]))
            line = ','.join(row)
            # with open('orders_sheet.csv', 'a', encoding='utf-8') as f:
            #     f.write(line + '\n')

    # print(orders_list)
    return orders_list


# Comment out if running from here
if __name__ == '__main__':
    main()

