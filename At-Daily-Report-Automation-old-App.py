from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

import pandas as pd
import numpy as np
from datetime import datetime
import time
import re
import glob
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument("C:\Users\P2818726\chromedriver.exe")
chromeOptions.add_experimental_option('useAutomationExtension', False)
chromeOptions.add_argument("--start-maximized")

browser = webdriver.Chrome(chrome_options=chromeOptions, desired_capabilities=chromeOptions.to_capabilities())
browser.get('https://cbo-sre-dashboard.netops.charter.com')
time.sleep(100)
elem = browser.find_element_by_link_text('Log In')
elem.get_attribute('href')
elem.click()
username = browser.find_element_by_xpath('//*[@id="id_username"]')
password = browser.find_element_by_xpath('//*[@id="id_password"]')
username.send_keys("P2818726")
password.send_keys("#######")
login_attempt = browser.find_element_by_xpath('/html/body/div[2]/section/div/div/form/button')
login_attempt.click()
elem = browser.find_element_by_link_text('Utilization')
elem.click()
elem = browser.find_element_by_link_text('Utilization Reports(BETA)')
elem.click()
Generate_Report = browser.find_element_by_xpath('/html/body/div[2]/button')
Generate_Report.click()
for _ in range(3):
    browser.refresh()
time.sleep(100)
for _ in range(3):
    browser.refresh()
elem = browser.find_element_by_xpath('//*[@id="DataTables_Table_0"]/tbody/tr[1]/td[1]/a')
elem.click()
x = glob.glob('C:\Users\P2818726\Downloads\Daily Utilization Report-*.xlsx')
#print x
latest_file = max(x, key=os.path.getctime)
#print(latest_file)
xls_file = pd.ExcelFile(latest_file)
df_cbo_bb_ip = xls_file.parse('CBO-BACKBONE-IP')
df_raw_sheet = xls_file.parse('raw')
df_cbo_bb_ip.drop(df_cbo_bb_ip.columns[[5, 6, 7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]], axis = 1, inplace = True)
df_cbo_bb_ip['device_name'] = df_cbo_bb_ip['device_name'].fillna(method = 'ffill')
df_raw_sheet.drop(df_raw_sheet.columns[[0,2,3,4,6,7,8,9,10,11,12]], axis = 1, inplace = True)
df_raw_sheet = df_raw_sheet.drop_duplicates(subset = ['device_name'], keep = 'first')
Utilization_Report = pd.merge( df_cbo_bb_ip,df_raw_sheet, on = 'device_name', how = 'left')
Utilization_Report["Z_Router_1"] = Utilization_Report['description'].str.extract(r'NAME=([A-Z]\w*)')
Utilization_Report["Z_Routers_2"] = Utilization_Report['description'].str.extract(r'to (\w*\w.\w*)')
Utilization_Report["Z Router"] = np.where(Utilization_Report["Z_Routers_2"].isnull(), Utilization_Report["Z_Router_1"], Utilization_Report["Z_Routers_2"])
Utilization_Report['Z Router'] = Utilization_Report['Z Router'].astype(str)
Utilization_Report['Z Router'] = map(lambda x: x.upper(), Utilization_Report['Z Router'])
Utilization_Report['Capacity'] = Utilization_Report['Speed'].str.extract(r'(\d*)')
Utilization_Report['Name'] = Utilization_Report['Name'].str.extract(r'(Bundle-Ether\d*|ae\d*)')
Utilization_Report= Utilization_Report[pd.notnull(Utilization_Report["Name"])]
Utilization_Report.drop('Speed', axis = 1, inplace = True)
Utilization_Report = Utilization_Report[pd.notnull(Utilization_Report['description'])]
file = pd.ExcelFile("Daily Report - SSP Utilization % above 85% - Revised.xlsx")
df_DNS_Names = file.parse('DNS Names')
df_DNS = df_DNS_Names
df_DNS.drop(['Legacy', 'Type', 'Router', 'DNS_IP', 'New Router Name'], axis = 1, inplace = True)
df_DNS =  df_DNS['DNS_A_NAME'].append(df_DNS['DNS_C_NAME']).append(df_DNS['New DNS']).reset_index(drop=True)

Utilization_Report['key']= Utilization_Report.device_name.apply(lambda x : [process.extract(x,  df_DNS, limit=1)][0][0][0])
df_DNS_Sheet = file.parse('DNS Names')

Trial_Report_1 = pd.merge( Utilization_Report,df_DNS_Sheet, left_on = 'key', right_on = 'DNS_A_NAME', how = 'left')
Trial_Report_2 = pd.merge( Utilization_Report,df_DNS_Sheet, left_on = 'key', right_on = 'DNS_C_NAME', how = 'left')
Trial_Report_3 = pd.merge( Utilization_Report,df_DNS_Sheet, left_on = 'key', right_on = 'New DNS', how = 'left')
concat = pd.concat([Trial_Report_1,Trial_Report_2,Trial_Report_3])


concat = concat.dropna(axis = 0, subset = ['Router'])

concat.drop(['DNS_IP','DNS_A_NAME','DNS_C_NAME','New DNS','New Router Name'], axis = 1, inplace = True)
concat.rename(columns = {'Router':'A Router'}, inplace = True)
concat['SSP Utilization %'] = concat['Max Utilization']/100

concat['Capacity'] = pd.to_numeric(concat['Capacity'])

concat['SSP Utilization %'] = pd.to_numeric(concat['SSP Utilization %'])

concat['calculated_SSP_Capacity'] = concat['Capacity'] * concat['SSP Utilization %']

concat['calculated_SSP_Capacity_85'] = concat['calculated_SSP_Capacity']/0.85

def roundup(x):
    return int(math.ceil(x / 100.0)) * 100

concat['calculated_SSP_Capacity_85'] = concat['calculated_SSP_Capacity_85'].apply(roundup)


concat['Addn. Capacity Requierd to Keep SSP % Util <85%'] = concat['calculated_SSP_Capacity_85'] - concat['Capacity']

concat['SSP_Utilization _%'] = concat['SSP Utilization %']*100
concat['SSP_Utilization _%'] = concat['SSP_Utilization _%'].apply(np.round)
concat['SSP_Utilization _%'] = concat['SSP_Utilization _%'].astype(int)
concat['Path'] = concat['A Router'] + ' to ' + concat['Z Router']
concat['A_Router'] = np.where(concat['Z Router'].isnull(), concat['device_name'], concat['A Router'])
file = pd.ExcelFile("Daily Report - SSP Utilization % above 85% - Revised.xlsx")
df_EOWeekly_Updates_Daily = file.parse('EoWeekly Updates on Daily')
df_EOWeekly_Updates_Daily.drop(df_EOWeekly_Updates_Daily.columns[[1,2,3,8,9,10]], axis = 1, inplace = True)
df_EOWeekly_Updates_Daily.columns = ["Path Take","Legacy Company","A Router","Z Router", "Segment Type", "Addn. Capacity Required to Keep SSP % Util <85%","Capacity to Augment","Post Mitigation Util%","# of times Recorded as >85% SSP Utilization\n%","P&D Mitigation Plan","CIOPS / Peer Mitigation Plan","Pending Peer","Pending CBO","Pending CIOPS","CBO Status","CIOPS Status","CIOPS Tickets","Additional Notes"]
df_EOWeekly_Updates_Daily= df_EOWeekly_Updates_Daily.drop(df_EOWeekly_Updates_Daily.index[[0]])
df_EOWeekly_Updates_Daily.rename(columns={'A Router':'A_Router'}, inplace = True)
df_EOWeekly_Updates_Daily.rename(columns={'Z Router':'Z_Router'}, inplace = True)

df_EOWeekly_Updates_Daily['Path'] = df_EOWeekly_Updates_Daily['A_Router'] + ' to ' + df_EOWeekly_Updates_Daily['Z_Router']
new_df = pd.merge(concat, df_EOWeekly_Updates_Daily,  how='left', left_on=['Path','Name'], right_on = ['Path','Segment Type'])
new_df['Link'] = "https://cbo-sre-dashboard.netops.charter.com/alarms/capc_graph/" + new_df['Name'].astype(str) +'/'+ new_df['device_name'].astype(str) + "/24/"
new_df.drop(['device_name', 'key', 'Legacy', 'Type', 'Path','Path Take','Legacy Company','Segment Type','Addn. Capacity Required to Keep SSP % Util <85%','# of times Recorded as >85% SSP Utilization\n%'], axis = 1, inplace = True)
new_df.rename(columns={'host':'Legacy Company'}, inplace = True)
new_df.rename(columns={'Name':'Bundle Info'}, inplace = True)
new_df.rename(columns={'Addn. Capacity Requierd to Keep SSP % Util <85%':'Addn. Capacity Required to Keep SSP % Util <85%'}, inplace = True)
new_df.drop(['SSP Utilization %', 'calculated_SSP_Capacity', 'calculated_SSP_Capacity_85'], axis = 1, inplace = True)
new_df.rename(columns={'Capacity to Augment':'Capacity available to Augment'}, inplace = True)
new_df.rename(columns={'Capacity':'Capacity(Gbps)'}, inplace = True)
new_df.rename(columns={'Post Mitigation Util%':'Post Mitigation Utilization'}, inplace = True)
new_df['Capacity available to Augment'].fillna(0, inplace=True)
Today_Daily_85_SSP = new_df[['Link','Legacy Company','A Router','Z Router','Bundle Info','description','Capacity(Gbps)','SSP_Utilization _%','Addn. Capacity Required to Keep SSP % Util <85%','Capacity available to Augment','P&D Mitigation Plan','CIOPS / Peer Mitigation Plan','Pending Peer','Pending CBO','Pending CIOPS','CBO Status','CIOPS Status','CIOPS Tickets','Additional Notes','Link']]
Today_Daily_85_SSP['Post Mitigation Utilization_%_P1'] = Today_Daily_85_SSP['Capacity(Gbps)']*Today_Daily_85_SSP['SSP_Utilization _%']
Today_Daily_85_SSP['Post Mitigation Utilization_%_P2'] = Today_Daily_85_SSP['Capacity(Gbps)'] + Today_Daily_85_SSP['Capacity available to Augment']
Today_Daily_85_SSP['Post Mitigation Utilization_%_P3']= Today_Daily_85_SSP['Post Mitigation Utilization_%_P1']/Today_Daily_85_SSP['Post Mitigation Utilization_%_P2']
Today_Daily_85_SSP['Post Mitigation Utilization_%'] = Today_Daily_85_SSP['Post Mitigation Utilization_%_P3'].fillna(0).astype(int)

Today_Daily_85_SSP.drop(['Post Mitigation Utilization_%_P1', 'Post Mitigation Utilization_%_P2', 'Post Mitigation Utilization_%_P3'], axis = 1, inplace = True)
Today_Daily = Today_Daily_85_SSP[['Legacy Company','A Router','Z Router','Bundle Info','description','Capacity(Gbps)','SSP_Utilization _%','Addn. Capacity Required to Keep SSP % Util <85%','Capacity available to Augment','Post Mitigation Utilization_%','P&D Mitigation Plan','CIOPS / Peer Mitigation Plan','Pending Peer','Pending CBO','Pending CIOPS','CBO Status','CIOPS Status','CIOPS Tickets','Additional Notes','Link']]

Today_Daily['SSP_Utilization _%'] = Today_Daily['SSP_Utilization _%'].astype(int)

Today_Daily = Today_Daily.loc[:,~Today_Daily.columns.duplicated()]
Today_Daily = Today_Daily.sort_values('SSP_Utilization _%',ascending=False)
Today_Daily['Legacy Company'] = map(lambda x: str(x).upper(), Today_Daily['Legacy Company'])

Today_Daily['Legacy Company'] = 'L-' + Today_Daily['Legacy Company']
Today_Daily['Date'] = datetime.today().strftime('%m/%d/%Y')
Today_Daily.index = np.arange(1, len(Today_Daily) + 1)
Today_Daily['Count'] = Today_Daily.index

Today_Daily.rename(columns ={'A Router':'A Node','Z Router':'Z Node','Bundle Info':'Bundle ID','SSP_Utilization _%':'Utilization %','Capacity available to Augment':'Capacity to Augment (Gbps)','Post Mitigation Utilization_%':'Post Mitigation Utilization %','Addn. Capacity Required to Keep SSP % Util <85%':'Addn. Capacity Requierd to Keep SSP % Util <85%'},inplace = True)
Today_Daily.drop(Today_Daily.columns[[4,14]], axis = 1, inplace = True)
Today_Daily = Today_Daily[['Count','Legacy Company','A Node','Z Node','Bundle ID','Capacity(Gbps)','Utilization %','Addn. Capacity Requierd to Keep SSP % Util <85%','Capacity to Augment (Gbps)', 'Post Mitigation Utilization %','P&D Mitigation Plan','CIOPS / Peer Mitigation Plan','Pending Peer','Pending CBO','CBO Status','CIOPS Status','CIOPS Tickets','Additional Notes','Link','Date']]
Today_Daily.to_excel('C:\Users\P2818726\Daily_Report_today.xlsx')


writer = pd.ExcelWriter('Daily_Report_today.xlsx', engine='xlsxwriter')

Today_Daily.to_excel(writer, index=False, sheet_name='Today Daily_>85% SSP', startrow = 0)
workbook = writer.book
worksheet = writer.sheets['Today Daily_>85% SSP']

worksheet.set_zoom(80)

number_format = workbook.add_format({'num_format': '#,##0', 'align': 'center',  'valign':'vcenter'})
float_format =  workbook.add_format({'num_format': '0"%"', 'align': 'center',  'valign':'vcenter'})
date_format = workbook.add_format({'num_format': 'mm/dd/yyyy', 'align': 'center',  'valign':'vcenter'})
text_format = workbook.add_format({'align': 'center',  'valign':'vcenter'})
#text_format = workbook.add_format({'align': 'center',  'valign':'vcenter', 'text_wrap':True})
header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'align':'center',
    'valign': 'vcenter',
    'fg_color': '#BFBFBF',
    'border': 1})

for col_num, value in enumerate(Today_Daily.columns.values):
    worksheet.write(0, col_num, value, header_format)

worksheet.set_column('A:A', 10, text_format)
worksheet.set_column('B:B', 15, text_format)
worksheet.set_column('C:D', 20, text_format)
worksheet.set_column('E:E', 20, text_format)
worksheet.set_column('F:F', 10, number_format)
worksheet.set_column('G:G', 10, float_format)
worksheet.set_column('H:H', 15, text_format)
worksheet.set_column('I:I', 15, text_format)
worksheet.set_column('J:J', 15, float_format)
worksheet.set_column('K:K', 15, text_format)
worksheet.set_column('L:L', 15, text_format)
worksheet.set_column('M:P', 10, text_format)
worksheet.set_column('Q:Q', 15, date_format)
worksheet.set_column('R:R', 80, date_format)
worksheet.set_column('S:T', 10, date_format)
worksheet.set_row(0,60, header_format)
worksheet.autofilter('A1:T1')

writer.save()
workbook.close()

# Sending the above generated report as an email attachment.
email_user = 'sonalika.bhandari@charter.com'
email_send = 'sonalika.bhandari@charter.com'   
msg = MIMEMultipart()   
msg['From'] = email_user   
msg['To'] = email_send
subject = 'Daily Report'
msg['Subject'] = subject
body = 'Hello, Please find attached Daily Report'
msg.attach(MIMEText(body, 'plain'))   
filename = 'Daily Report-' + timestr + '.xlsx'
attachment = open('C:\Users\P2818726\example24.xlsx', "rb")
p = MIMEBase('application', 'octet-stream') 
p.set_payload((attachment).read()) 
encoders.encode_base64(p)    
p.add_header('Content-Disposition', "attachment; filename= %s" % filename)  
msg.attach(p) 
s = smtplib.SMTP('smtp.gmail.com', 587) 
s.starttls() 
s.login(email_user,'Charter2019')
text = msg.as_string()   
s.sendmail(email_user,email_send,text)  
s.quit() 