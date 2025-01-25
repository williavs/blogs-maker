import json
import os
from datetime import datetime
from anthropic import Anthropic
import streamlit as st
from utils.pdf_generator import generate_invoice
from tools.calculator import CalculatorTool
import sys
import re

def process_time_entries(raw_entries, hourly_rate, client_info=None):
    """
    Process raw time entries into structured invoice data.
    
    Args:
        raw_entries (str): Natural language time entries
        hourly_rate (float): Hourly rate for the invoice
        client_info (dict): Optional client information
        
    Returns:
        dict: Structured invoice data with entries and totals
    """
    st.write("## Processing Invoice")
    
    progress = st.progress(0)
    status = st.empty()
    
    # Initialize calculator
    status.write("🧮 Initializing Calculator...")
    calculator = CalculatorTool()
    progress.progress(10)
    
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
    client = Anthropic(api_key=api_key)
    
    status.write("🤖 Processing time entries with Claude...")
    progress.progress(20)
    
    prompt = f"""Process these timecard entries into professional invoice line items.
Hourly rate: ${hourly_rate}

Raw entries:
{raw_entries}

Return ONLY a valid JSON array of entries. Each entry must have:
- date (YYYY-MM-DD format)
- hours (number)
- description (clear, professional description)
- rate (${hourly_rate})
- amount (hours * rate)"""

    # Get processed entries from Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0,
        system="You are a JSON-only response bot. You must ONLY output valid JSON, nothing else.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    progress.progress(40)
    
    try:
        # Get just the text content from the response
        json_text = response.content[0].text.strip()
        status.write("📝 Parsing JSON response...")
        
        # Debug the response
        st.write("Raw response:", json_text)
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
        
        # Parse the entries
        entries = json.loads(json_text)
        if not isinstance(entries, list):
            raise ValueError("Expected JSON array of entries")
            
        # Validate entry structure
        for entry in entries:
            required_fields = ['date', 'hours', 'description', 'rate', 'amount']
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                raise ValueError(f"Entry missing required fields: {', '.join(missing_fields)}")
                
        st.success(f"✅ Successfully parsed {len(entries)} entries")
        progress.progress(60)
        
        status.write("🧮 Validating calculations...")
        # Validate and fix calculations
        entries = calculator.validate_calculations(entries, hourly_rate)
        progress.progress(80)
        
        status.write("📊 Calculating totals...")
        # Calculate totals using the calculator
        totals = calculator.calculate_totals(entries)
        
        # Generate invoice details
        today = datetime.now()
        first_date = min(entry['date'] for entry in entries)
        last_date = max(entry['date'] for entry in entries)
        
        status.write("📋 Preparing final invoice data...")
        # Create the final result with bank details from secrets
        result = {
            # Invoice details
            "invoice_number": f"INV-{today.strftime('%Y%m%d')}",
            "invoice_date": today.strftime("%Y-%m-%d"),
            "period_start": first_date,
            "period_end": last_date,
            
            # Time entries and totals
            "entries": entries,
            "total_hours": float(totals['total_hours']),
            "total_amount": float(totals['total_amount']),
            "hourly_rate": float(hourly_rate),
            
            # Bank details directly from secrets
            "bank_name": st.secrets["BANK_NAME"],
            "bank_address": st.secrets["BANK_ADDRESS"],
            "account_type": st.secrets["ACCOUNT_TYPE"],
            "routing_number": st.secrets["ROUTING_NUMBER"],
            "account_number": st.secrets["ACCOUNT_NUMBER"],
            
            # Service type for PDF generation
            "service_type": "Hourly"
        }
        
        # Add client info if provided
        if client_info:
            result["client_address"] = client_info.get("client_address", "")
            
        progress.progress(100)
        status.write("✅ Invoice processing complete!")
        
        # Display final invoice preview
        with st.expander("📄 Invoice Preview", expanded=False):
            st.write("### Invoice Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Invoice Number:** {result['invoice_number']}")
                st.write(f"**Date:** {result['invoice_date']}")
            with col2:
                st.write(f"**Period:** {result['period_start']} to {result['period_end']}")
                st.write(f"**Rate:** ${result['hourly_rate']}/hour")
            
            st.write("### Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Hours", f"{result['total_hours']}")
            with col2:
                st.metric("Total Amount", f"${result['total_amount']}")
        
        return result
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse JSON response: {str(e)}")
        raise ValueError(f"Error parsing time entries: {str(e)}")
    except Exception as e:
        st.error(f"❌ Failed to process entries: {str(e)}")
        raise ValueError(f"Error processing time entries: {str(e)}")

def generate_invoice_pdf(invoice_data):
    """Generate PDF invoice from the processed data."""
    try:
        with st.spinner("🔄 Generating PDF Invoice..."):
            pdf_path = generate_invoice(invoice_data)
            if pdf_path and os.path.exists(pdf_path):
                st.success(f"✅ Successfully generated PDF: {pdf_path}")
                return pdf_path
            else:
                st.error("❌ PDF generation failed - no path returned")
                raise ValueError("Failed to generate PDF invoice")
    except Exception as e:
        st.error(f"❌ PDF generation failed - {str(e)}")
        raise ValueError(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_invoice.py 'raw_entries' hourly_rate")
        sys.exit(1)
        
    raw_entries = sys.argv[1]
    hourly_rate = float(sys.argv[2])
    
    try:
        # Process the entries
        result = process_time_entries(raw_entries, hourly_rate)
        print("\nProcessed Invoice Data:")
        print(json.dumps(result, indent=2))
        
        # Generate PDF
        pdf_path = generate_invoice_pdf(result)
        print(f"\nGenerated PDF: {pdf_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 