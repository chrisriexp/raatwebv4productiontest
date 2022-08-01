import streamlit as st
from PIL import Image
import pandas as pd
import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from datetime import date
import time
import shutil
import sqlite3


mainDB = sqlite3.connect('mainDB')
mainDBcursor = mainDB.cursor()
    
mainDBcursor.execute("select * from subagents")
    
result = mainDBcursor.fetchall();

#Path to Commission Spreadsheet Archives Folder    
archivePath = '././commissionArchive'
#Path to PDF Invoice Archives Folder    
invoiceArchivePath = '././pdfArchive'
#Path to Spreadsheets Folder
spreadsheetsPath = '././spreadsheets'
#Path to PDF Folder
pdfPath = '././PDF'
#Current Year Month [YYYY-MM]
ym = time.strftime("%Y-%m")



def easyAccountingScript():
    #Import Fonts
    pdfmetrics.registerFont(TTFont('OpenSansR', '././fonts/OpenSans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSansL', '././fonts/OpenSans-Light.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSansB', '././fonts/OpenSans-Bold.ttf'))
    registerFontFamily('OpenSans', normal='OpenSansR', bold='OpenSansB', italic='OpenSansL', boldItalic='OpenSansB')
    
    
    #Aon Edge Required Columns [Policy#, Insured Name, Prem, Comm, Agency Code, Eff]
    aonReqCols = [0, 3, 6, 8, 9, 17]

    #Wright Required Columns [ProducerNo, Policy#, Prem, Comm, Insured, Eff]
    wrightReqCols = [0, 6, 7, 8, 13, 14]

    #Palomar Required Columns [AgentCode, Policy#, Insured, Eff, Prem, Comm]
    palomarReqCols = [0, 2, 4, 7, 9, 11]
    
    #Aon Edge Data Frame
    aonReqDf = pd.read_excel(f'{spreadsheetsPath}/AON-Test.xlsx', usecols=aonReqCols)

    #Wright Data Frame
    wrightReqDf = pd.read_excel(f'{spreadsheetsPath}/WrightNational-Test.xlsx', usecols = wrightReqCols)

    #Palomar Data Frame
    palomarReqDf = pd.read_excel(f'{spreadsheetsPath}/Palomar-Test.xlsx', usecols = palomarReqCols, skiprows = 1)
    
    mainDB = sqlite3.connect('mainDB')
    
    mainDBcursor = mainDB.cursor()
    
    for agency in result:
        
        #Query to get Aon information that will append to PDF
        aonQuery = aonReqDf.query("`Agency Code`==@agency[4]")
        
        #Query to get Wright information that will append to PDF
        palomarQuery = palomarReqDf.query("`Agent Code`==@agency[5]")
        
        #Query to get Palomar information that will append to PDF
        wrightQuery = wrightReqDf.query("ProducerNo==@agency[6]")
        
        #====Aon Commission===
        #Get Aon Total Commission
        aonComm = round(aonQuery['Agency Commission'].sum()*0.98, 2)
        
        #Get Aon Commission Override
        aonCommOR = round(aonQuery['Agency Commission'].sum()*0.02, 2)
        
        mainDBcursor.execute("insert into overriderevenue(uniqueparam, month, agency_name, rocket_code, carrier_name, override_amount) values(?, ?, ?, ?, ?, ?)", (agency[3]+ym+"aon", ym, agency[1], agency[3], "Aon Edge", aonCommOR))
        
        #====Palomar Commission===
        
        #Array holding the float values of the commission column
        palomarCommArray = []
        
        #List of poicy commission amount without "$" in front
        palomarCommList = palomarQuery['Commission Amount'].str.replace("$", "")
        #Turn items in list to float and append to "palomarCommArray"
        for item in palomarCommList:
            palomarCommArray.append(float(item))
        
        #Get Palomar Total Commission
        palomarComm = round(sum(palomarCommArray)*0.98, 2)
        
        #Get Palomar Commission OverRide
        palomarCommOR = round(sum(palomarCommArray)*0.02, 2)
        
        mainDBcursor.execute("insert into overriderevenue(uniqueparam, month, agency_name, rocket_code, carrier_name, override_amount) values(?, ?, ?, ?, ?, ?)", (agency[3]+ym+"palomar", ym, agency[1], agency[3], "Palomar", palomarCommOR))
        
        #====Wright Commission===
        
        #Get Wright Total Commission
        wrightComm = round(wrightQuery['Commission Amt'].sum()*0.98, 2)
        
        #Get Wright Commission OverRide
        wrightCommOR = round(wrightQuery['Commission Amt'].sum()*0.02, 2)
        
        mainDBcursor.execute("insert into overriderevenue(uniqueparam, month, agency_name, rocket_code, carrier_name, override_amount) values(?, ?, ?, ?, ?, ?)", (agency[3]+ym+"wright", ym, agency[1], agency[3], "Wright National", wrightCommOR))
        
        #===Total Commission from all Carriers===
        
        #Producer Total Commission 
        commTotal = round(aonComm+palomarComm+wrightComm, 2)
        
        #===End Commission===
        
        #Create PDF Canvas
        canvas = Canvas(f"{pdfPath}/{agency[1]}Invoice.pdf", pagesize=(8.5 * inch, 11 * inch))
        #Set canvas font
        canvas.setFont("OpenSansR", 18)
        #Get todays date
        today = date.today()
        #Information on PDF
        #The values are (distance from left, distance from bottom, "String")
        canvas.drawString(1 * inch, 10 * inch, "RocketMGA Test Invoice")
        canvas.drawString(1 * inch, 9.5 * inch, f"{agency[1]} Commissions - {agency[3]}")
        canvas.setFont("OpenSansR", 15)
        canvas.drawString(6.5 * inch, 10 * inch, text=str(today))
        canvas.line(1 * inch, 9 * inch, 7.5 * inch, 9 * inch)
        
        #Palomar Invoice Headers
        canvas.setFont("OpenSansB", 10)
        canvas.drawString(0.5 * inch, 8.5 * inch, "Insured Name")
        canvas.drawString(2 * inch, 8.5 * inch, "Carrier")
        canvas.drawString(2.85 * inch, 8.5 * inch, "Policy Number")
        canvas.drawString(4.40 * inch, 8.5 * inch, "Effective Date")
        canvas.drawString(5.75 * inch, 8.5 * inch, "Premium")
        canvas.drawString(7 * inch, 8.5 * inch, "Commission")
        
        #Change canvas font for information to append
        canvas.setFont("OpenSansL", 8)
        
        
        #===Aon Edge Data Frame Lists===
        ##Insured Name
        aonInsuredList = aonQuery['Insured Name'].values.tolist()
        ##Policy List
        aonPolicyList = aonQuery['policy'].values.tolist()
        ##Effective Date
        aonEffStrArr = []
        for item in aonQuery['Effective Date']:
            aonEffStrArr.append(str(item).replace("00:00:00", ""))
        ##Premium
        aonPremList = aonQuery['Premium'].values.tolist()
        ##Commission
        ###Array holding commission amount after override
        aonPolCommArray = []
        #Add every commissiona amount to array after override
        for item in aonQuery['Agency Commission']:
            aonPolCommArray.append(round(float(item)*0.98, 2))
            
        #===Palomar Data Frame Lists===
        
        #Create list from Palomar Data Frame 
        ##Insured Name
        palomarInsuredList = palomarQuery['Insured Name'].values.tolist()
        ##Policy List
        palomarPolicyList = palomarQuery['Policy No'].values.tolist()
        ##Effective Date
        palomarEffList = palomarQuery['Policy Eff Date'].values.tolist()
        ##Premium
        palomarPremList = palomarQuery['Premium Collected'].values.tolist()
        ##Commission
        ###Array holding commission amount after override
        palomarPolCommArray = []
        #Remove "$" from commission amount 
        palomarPolCommList = palomarQuery['Commission Amount'].str.replace("$", "")
        #Add every commissiona amount to array after override
        for item in palomarPolCommList:
            palomarPolCommArray.append(round(float(item)*0.98, 2))
        
        #===Wrigth Data Frame Lists===
        
        #Create list from Wright Data Frame Policy Number Col
        ##Insured Name
        wrightInsuredList = wrightQuery['Insured Name'].values.tolist()
        ##Policy List
        wrightPolicyList = wrightQuery['Policy Number'].values.tolist()
        ##Effective Date
        ###Array holding the effective date as a string after removing the time stamp from date
        wrightEffStrArray = []
        ###Take every effective date and turn it into a string and remove the timestamp from effective date
        for item in wrightQuery['Eff Date MDY']:
            wrightEffStrArray.append(str(item).replace("00:00:00", ""))  
        ##Premium
        wrightPremList = wrightQuery['Written Premium'].values.tolist()
        ##Commission
        ###Array holding commission amount after override
        wrightPolCommArray = []
        #Add every commissiona amount to array after override
        for item in wrightQuery['Commission Amt']:
            wrightPolCommArray.append(round(float(item)*0.98, 2))
            
        #===Append Aon Transactions to PDF===
        ai = 0
        
        #Variable to determine height to append information on PDF to 
        n = 8.25
        
        #Loop to apend Aon Policys to PDF
        for policy in aonPolicyList:
            #Append Insured Name to PDF
            canvas.drawString(0.5 * inch, n * inch, text=aonInsuredList[ai][:23])
            
            #Append Carrier Name
            canvas.drawString(2 * inch, n * inch, text='Aon Edge')
            
            #Append Policy Number to PDF
            canvas.drawString(2.85 * inch, n * inch, text=policy)
            
            #Append Policy Effective Date to PDF
            canvas.drawString(4.40 * inch, n * inch, text=aonEffStrArr[ai])
            
            #Append Policy Premium Amount to PDF
            canvas.drawString(5.75 * inch, n * inch, text=f'${aonPremList[ai]}')
            
            #Append Policy Commission Amount to PDF
            canvas.drawString(7 * inch, n * inch, text=f'${aonPolCommArray[ai]}')
            
            #Decrease append height by 0.25 inch
            n = n - 0.25
            
            #Increase array index by 1
            ai = ai + 1
            
        
        #===Append Palomar Transactions to PDF===
        
        #Variable to keep array number for List Consistant
        pi = 0
        
        #Loop to apend Palomar Policys to PDF
        for policy in palomarPolicyList:
            #Append Insured Name to PDF
            canvas.drawString(0.5 * inch, n * inch, text=palomarInsuredList[pi][:23])
            
            #Append Carrier Name
            canvas.drawString(2 * inch, n * inch, text='Palomar')
            
            #Append Policy Number to PDF
            canvas.drawString(2.85 * inch, n * inch, text=policy)
            
            #Append Policy Effective Date to PDF
            canvas.drawString(4.40 * inch, n * inch, text=palomarEffList[pi])
            
            #Append Policy Premium Amount to PDF
            canvas.drawString(5.75 * inch, n * inch, text=palomarPremList[pi])
            
            #Append Policy Commission Amount to PDF
            canvas.drawString(7 * inch, n * inch, text=f'${palomarPolCommArray[pi]}')
            
            #Decrease append height by 0.25 inch
            n = n - 0.25
            
            #Increase array index by 1
            pi = pi + 1
            
        
        #===Append Wright Transactions to PDF===
        
        #Variable to keep array number for List Consistant
        wi = 0
        
        #Loop to apend Wright Policys to PDF
        for policy in wrightPolicyList:
            #Append Insured Name to PDF
            canvas.drawString(0.5 * inch, n * inch, text=wrightInsuredList[wi][:23])
            
            #Append Carrier Name
            canvas.drawString(2 * inch, n * inch, text='Wright')
            
            #Append Policy Number to PDF
            canvas.drawString(2.85 * inch, n * inch, text=policy)
            
            #Append Policy Effective Date to PDF
            canvas.drawString(4.40 * inch, n * inch, text=wrightEffStrArray[wi])
            
            #Append Policy Premium Amount to PDF
            canvas.drawString(5.75 * inch, n * inch, text=f'${wrightPremList[wi]}')
            
            #Append Policy Commission Amount to PDF
            canvas.drawString(7 * inch, n * inch, text=f'${wrightPolCommArray[wi]}')
            
            #Decrease append height by 0.25 inch
            n = n - 0.25
            
            #Increase array index by 1
            wi = wi + 1
        
        
        #===Append total Commission to PDF===
        
        #Line seperating commission from producer total commission
        canvas.line(0.5 * inch, n * inch, 8 * inch, n * inch)
        
        n = n - 0.25
        
        #Total Producer Commission across all carriers
        canvas.setFont("OpenSansB", 10)
        canvas.drawString(0.5 * inch, n * inch, text=f'{agency[1]} Total Commission')
        canvas.drawString(7 * inch, n * inch, text=f'${str(commTotal)}')
        
        
        canvas.save()
        
    
    
    #Check if a folder named the current Year Month exists within the Archive Folder
    archiveMonthExists = os.path.exists(f'{archivePath}/{ym}')
    
    if not archiveMonthExists:
            os.makedirs(f'{archivePath}/{ym}')
            
    for statement in os.listdir(spreadsheetsPath):
        shutil.move(f'{spreadsheetsPath}/{statement}', f'{archivePath}/{ym}/{statement}')
        
        
    #Check if a folder named the current Year Month exists within the Invoice Archive Folder
    invoiceArchiveMonthExists = os.path.exists(f'{invoiceArchivePath}/{ym}')
    
    #If a folder for the current Year Month does not exist create the folder 
    if not invoiceArchiveMonthExists:
            os.makedirs(f'{invoiceArchivePath}/{ym}')
    
    #For every PDF Invoice that was created into the PDF folder move the invoice to the PDF Archive Folder       
    for invoice in os.listdir(pdfPath):
        shutil.move(f'{pdfPath}/{invoice}', f'{invoiceArchivePath}/{ym}/{invoice}')
    
    #Save all changes made to DataBase
    mainDB.commit()
      
    #Alert box that script is done running
    st.success("Script is done running")

def app():
    #Defining the columns on the page
    left_column, right_column = st.columns(2)

    #Image Variable for the rocket image
    rocketImg = Image.open('./img/rocket.png')

    #Left Column Content
    with left_column:
        st.image(rocketImg)
        
    #Right Column Content
    with right_column:
        #Instructions        
        st.subheader("Instructions")
        st.write("• Rename statements to carrier name")
        st.write("(ie. Palomar.xlsx, WrightNational.xlsx)")
        st.write("• Upload Commission Statement below")
        st.write('• Click the "Easy Accouting!" button below!')
        
        st.markdown("---")
        #Required Commission Statements
        st.subheader("Required Commission Statements")
        
        #Variables to check if Commission Statement files exist in spreadsheets folder
        aonExists = os.path.exists(f'{spreadsheetsPath}/AON-Test.xlsx')
        palomarExists = os.path.exists(f'{spreadsheetsPath}/Palomar-Test.xlsx')
        wrightExists = os.path.exists(f'{spreadsheetsPath}/WrightNational-Test.xlsx')
        
        #Text showing if Aon Statement Exists or Not
        if aonExists == True:
            st.write(":heavy_check_mark:Aon Statement (Aon.xlsx)")
        else:
            st.write(":heavy_multiplication_x:Aon Statement (Aon.xlsx)")
        
        #Text showing if Palomar Statement Exists or Not
        if palomarExists == True:
            st.write(":heavy_check_mark:Palomar Statement (Palomar.xlsx)")
        else:
            st.write(":heavy_multiplication_x:Palomar Statement (Palomar.xlsx)")
            
        #Text showing if Wright Statement Exists or Not
        if wrightExists == True:
            st.write(":heavy_check_mark:Wright Statement (WrightNational.xlsx)")
        else:
            st.write(":heavy_multiplication_x:Wright Statement (WrightNational.xlsx)")
        
        #Upload Commission Statements
        st.subheader("Upload Statements")
        statementUpload = st.file_uploader("Upload Commission Statements",accept_multiple_files=True, type=['xlsx'])
        #If statement has been uploaded add the file to the spreadsheets folder
        if statementUpload is not None:
            for statement in statementUpload:
                with open(os.path.join("././spreadsheets", statement.name), "wb") as f:
                    f.write(statement.getbuffer())
                #Show filed uploaded Success Msg
                st.success("File Uploaded")
        
        st.markdown("---")
        
        #Button to run main script to create invoices
        if palomarExists == True & wrightExists == True & aonExists == True:
            st.button("Easy Accounting!", on_click=easyAccountingScript, disabled=False)
        else:
            st.button("Easy Accounting!", on_click=easyAccountingScript, disabled=True)