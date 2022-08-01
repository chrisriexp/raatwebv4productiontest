import streamlit as st
import os
import base64


def app():
    st.title("Download Sub Agent Invoices and Commission Statements")
    #Path for PDF Archive folder
    pdfDir = '././pdfArchive'
    #Path for Commission Archive folder
    archivePath = '././commissionArchive'
    
    cdi = 0
    #For loop to add invoice view and download buttons for every invoice and commission statemnet downloads for every month
    for folder in os.listdir(pdfDir):
        st.subheader(folder)
        
        viewCol, downloadCol, commissionCol = st.columns(3, gap="large")
        
        
        with viewCol:
            for item in os.listdir(f'{pdfDir}/{folder}'):
                with st.expander(f'View {item}'):
                    with open(f'{pdfDir}/{folder}/{item}', "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="395" height="520" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
        with downloadCol:
            for invoice in os.listdir(f'{pdfDir}/{folder}'):
                with open(f'{pdfDir}/{folder}/{invoice}', "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(f'Download {invoice}', data=PDFbyte, file_name=invoice, mime='application/octet-stream')
        with commissionCol:
            st.subheader("Commission Statement Download")
            st.markdown("---")
            for statement in os.listdir(f'{archivePath}/{folder}'):
                st.download_button(f'Download {statement}', data=open(f'{archivePath}/{folder}/{statement}', 'rb'), file_name=statement, mime='application/vnd.ms-excel', key=f'commdownloadbtn{cdi}')
                cdi = cdi + 1
            
        st.markdown('---')
        