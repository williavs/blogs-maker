import streamlit as st
import subprocess
import json
import os
from datetime import datetime, timedelta
from tools.calculator import CalculatorTool
from utils.pdf_generator import PDFGenerator, generate_invoice
from run_invoice import process_time_entries, generate_invoice_pdf

# Initialize calculator tool
calculator = CalculatorTool()

@st.dialog("Name your PDF file")
def name_pdf_dialog(invoice_number):
    st.write("Choose a name for your invoice PDF file")
    default_name = f"invoice_{invoice_number}"
    filename = st.text_input("Filename", value=default_name)
    
    if st.button("Save PDF", use_container_width=True):
        st.session_state.pdf_filename = f"{filename}.pdf"
        st.rerun()

def show_invoice_generator():
    """Show the invoice generator interface"""
    st.title("📄 Professional Invoice Generator")
    st.markdown("""
    > Generate detailed invoices from natural language time entries. Perfect for freelancers and consultants.
    > Simply fill in your client details, enter your time entries, and get a professionally formatted PDF invoice.
    """)
    
    # Move time entries to sidebar
    with st.sidebar:
        st.subheader("⏱️ Time Entries")
        hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=150.0, step=25.0)
        
        with st.expander("ℹ️ Example Format", expanded=False):
            st.code("""3/15 - 4 hours - Initial project setup
3/16 - 6.5 hours - Development work
3/17 - 2 hours - Client meeting""")
        
        raw_entries = st.text_area("Enter your time entries below:", height=150)
        
        if st.button("Process Entries", use_container_width=True):
            with st.spinner("Processing time entries..."):
                try:
                    # Process time entries directly using the imported function
                    result = process_time_entries(raw_entries, hourly_rate)
                    
                    if result:
                        invoice_details = {
                            "invoice_number": result["invoice_number"],
                            "invoice_date": result["invoice_date"],
                            "period_start": result["period_start"],
                            "period_end": result["period_end"]
                        }
                        entries = result["entries"]
                        
                        # Store in session state
                        st.session_state.invoice_details = invoice_details
                        st.session_state.entries = entries
                        
                        st.success("Successfully processed time entries!")
                        with st.expander("View Processed Data"):
                            st.write("Invoice Details:", invoice_details)
                            st.write("Time Entries:", entries)
                            total_hours = sum(entry['hours'] for entry in entries)
                            total_amount = total_hours * hourly_rate
                            st.write(f"Total Hours: {total_hours}")
                            st.write(f"Total Amount: ${total_amount:,.2f}")
                    else:
                        st.error("Failed to process time entries")
                    
                except Exception as e:
                    st.error(f"Error processing entries: {str(e)}")
    
    # Create two columns for the main layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Client Information in an expander
        with st.expander("📋 Client Information", expanded=True):
            client_name = st.text_input("Client Name")
            client_email = st.text_input("Client Email")
            client_address = st.text_area("Client Address", height=100)
    
    with col2:
        st.markdown("### 📊 Preview & Download")
        st.info("Process your entries to see the preview here")
        
        # Preview and generate buttons
        if hasattr(st.session_state, 'invoice_details') and hasattr(st.session_state, 'entries'):
            with st.expander("🔍 Invoice Preview", expanded=True):
                preview_data = {
                    "Invoice Details": {
                        "Number": st.session_state.invoice_details["invoice_number"],
                        "Date": st.session_state.invoice_details["invoice_date"],
                        "Period": f"{st.session_state.invoice_details['period_start']} to {st.session_state.invoice_details['period_end']}"
                    },
                    "Summary": {
                        "Total Hours": sum(entry['hours'] for entry in st.session_state.entries),
                        "Rate": f"${hourly_rate:.2f}",
                        "Total Amount": f"${sum(entry['hours'] for entry in st.session_state.entries) * hourly_rate:.2f}"
                    }
                }
                st.json(preview_data)
            
            # Generate PDF button
            if st.button("Generate PDF", use_container_width=True):
                try:
                    with st.spinner("Generating PDF..."):
                        invoice_data = {
                            "client_address": f"{client_name}\n{client_address}",
                            "client_email": client_email,
                            "bank_name": st.secrets["BANK_NAME"],
                            "bank_address": st.secrets["BANK_ADDRESS"],
                            "account_type": st.secrets["ACCOUNT_TYPE"],
                            "routing_number": st.secrets["ROUTING_NUMBER"],
                            "account_number": st.secrets["ACCOUNT_NUMBER"],
                            **st.session_state.invoice_details,
                            "entries": st.session_state.entries,
                            "total_hours": sum(entry['hours'] for entry in st.session_state.entries),
                            "total_amount": sum(entry['hours'] for entry in st.session_state.entries) * hourly_rate,
                            "hourly_rate": hourly_rate
                        }
                        pdf_path = generate_invoice(invoice_data)
                        if pdf_path:
                            st.session_state.pdf_path = pdf_path
                            st.success("✅ PDF generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
            
            # Download button - only show if we have a PDF
            if hasattr(st.session_state, 'pdf_path') and st.session_state.pdf_path:
                if st.button("⬇️ Download Invoice PDF", use_container_width=True):
                    name_pdf_dialog(st.session_state.invoice_details['invoice_number'])
                
                if hasattr(st.session_state, 'pdf_filename'):
                    try:
                        with open(st.session_state.pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label=f"⬇️ Download {st.session_state.pdf_filename}",
                                data=pdf_file,
                                file_name=st.session_state.pdf_filename,
                                mime="application/pdf",
                                key="download_pdf",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error preparing download: {str(e)}")

if __name__ == "__main__":
    show_invoice_generator() 