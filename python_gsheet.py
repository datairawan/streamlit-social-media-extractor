from googleapiclient.discovery import build
from google.oauth2 import service_account
import config
creds = config.creds
    
class config_gsheet:
    
    def __init__(self):
        
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        #self.SERVICE_ACCOUNT_FILE = 'creds.json'

        self.credentials = creds

        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
        
    def write_gsheet(self, spreadsheet_id, df, sheet_name):
        
        self.SPREADSHEET_ID = spreadsheet_id        
        request = self.sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, 
                                        range=sheet_name+"!A1", 
                                        valueInputOption="USER_ENTERED", 
                                        body={"values" : df.values.tolist()}).execute()
        return("Success!")
    
    
    def append_gsheet(self, spreadsheet_id, df, sheet_name):
        
        self.SPREADSHEET_ID = spreadsheet_id  
        request = self.sheet.values().append(spreadsheetId=self.SPREADSHEET_ID, 
                                        range=sheet_name+"!A1", 
                                        valueInputOption="USER_ENTERED", 
                                        insertDataOption='INSERT_ROWS',
                                        body={"values" : df.values.tolist()}).execute()
        return("Success!")
    
    def read_gsheet(self, spreadsheet_id, sheet_name):
        
        self.SPREADSHEET_ID = spreadsheet_id  
        request = self.sheet.values().get(spreadsheetId=self.SPREADSHEET_ID, 
                                          range=sheet_name+"!A1:Z").execute()
        
        result = request.get("values", [])
        import pandas as pd
        df = pd.DataFrame(columns=result[0], 
                            data=result[1:]
                           )
        df.columns = [x.lower().replace(' ','_') for x in df.columns]
        
        return df