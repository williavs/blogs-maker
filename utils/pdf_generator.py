from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import Color, HexColor
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        # Define brand colors
        self.brand_color = HexColor('#2E5A88')  # Professional blue
        self.accent_color = HexColor('#4A90E2')  # Lighter blue for accents
        self.light_grey = HexColor('#F5F5F5')
        
        self.styles = getSampleStyleSheet()
        self.style_normal = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=HexColor('#333333')  # Dark grey for better readability
        )
        self.style_heading = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            leading=16,
            spaceAfter=6,
            textColor=self.brand_color
        )
        
        # Create custom styles
        self.style_table_header = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER
        )
        
        self.style_table_cell = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            textColor=HexColor('#333333')
        )
        
        self.style_amount_cell = ParagraphStyle(
            'AmountCell',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            textColor=self.brand_color
        )
        
    def generate_invoice_pdf(self, invoice_data, output_path):
        """Generate a PDF invoice from the provided data."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build the document
        story = []
        
        # Header with colored background
        header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=colors.white,
            alignment=TA_LEFT,
            leading=30
        )
        
        # Create header table with background color
        header_data = [[
            Paragraph("V3Consult", header_style)
        ]]
        header_table = Table(header_data, colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.brand_color),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 12))
        
        # Info section with subtle background
        info_data = [
            [
                # Left column - Your Info
                Paragraph(
                    f'<font color="{self.brand_color.hexval()}"><b>FROM</b></font><br/>'
                    "Willy VanSickle<br/>"
                    "375 Dean Apt 316<br/>"
                    "Brooklyn, NY 11217<br/>"
                    "vansicklewilly@gmail.com",
                    self.style_normal
                ),
                # Right column - Invoice Details
                Paragraph(
                    f'<font color="{self.brand_color.hexval()}"><b>INVOICE DETAILS</b></font><br/>'
                    f"Invoice Number: {invoice_data['invoice_number']}<br/>"
                    f"Date: {invoice_data['invoice_date']}<br/>"
                    f"Period: {invoice_data['period_start']} - {invoice_data['period_end']}",
                    self.style_normal
                )
            ]
        ]
        info_table = Table(info_data, colWidths=[4*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.light_grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 12))
        
        # Client Info
        story.append(Paragraph(f'<font color="{self.brand_color.hexval()}">BILL TO</font>', self.style_heading))
        client_lines = invoice_data['client_address'].split('\n')
        # Create a single-cell table with proper width to match info section
        client_data = [[
            Paragraph(
                "<br/>".join(client_lines),
                self.style_normal
            )
        ]]
        # Match the width of the info section above (4*inch) and align left
        client_table = Table(client_data, colWidths=[4*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.light_grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Ensure left alignment
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        # Create a wrapper table to ensure left alignment
        wrapper_data = [[client_table]]
        wrapper_table = Table(wrapper_data, colWidths=[7.5*inch])
        wrapper_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        story.append(wrapper_table)
        story.append(Spacer(1, 12))
        
        # Services
        story.append(Paragraph(f'<font color="{self.brand_color.hexval()}">Description of Services</font>', self.style_heading))
        
        if invoice_data.get('service_type', 'Hourly') == 'Hourly':
            # Create table for time entries with wrapped text
            table_data = [[
                Paragraph('Date', self.style_table_header),
                Paragraph('Hours', self.style_table_header),
                Paragraph('Description', self.style_table_header),
                Paragraph('Rate', self.style_table_header),
                Paragraph('Amount', self.style_table_header)
            ]]
            
            for entry in invoice_data['entries']:
                table_data.append([
                    Paragraph(entry['date'], self.style_table_cell),
                    Paragraph(str(entry['hours']), self.style_table_cell),
                    Paragraph(entry['description'], self.style_table_cell),
                    Paragraph(f"${entry['rate']:.2f}", self.style_amount_cell),
                    Paragraph(f"${entry['amount']:.2f}", self.style_amount_cell)
                ])
            
            # Add total row
            table_data.append([
                Paragraph('Total Hours:', self.style_table_cell),
                Paragraph(str(invoice_data['total_hours']), self.style_table_cell),
                Paragraph('', self.style_table_cell),
                Paragraph('Total:', self.style_table_cell),
                Paragraph(f"${invoice_data['total_amount']:.2f}", self.style_amount_cell)
            ])
            
            # Create table with proper column widths
            col_widths = [1.1*inch, 0.7*inch, 3.9*inch, 0.9*inch, 0.9*inch]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Headers
                ('BACKGROUND', (0, 0), (-1, 0), self.brand_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                # Totals row
                ('BACKGROUND', (0, -1), (-1, -1), self.light_grey),
                ('TEXTCOLOR', (0, -1), (-1, -1), self.brand_color),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.25, self.accent_color),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                # Align numbers right
                ('ALIGN', (1, 1), (1, -2), 'RIGHT'),
                ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
                # Cell padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                # Zebra striping for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.light_grey]),
            ]))
            story.append(table)
        
        story.append(Spacer(1, 12))
        
        # Payment Instructions in a styled box
        story.append(Paragraph(f'<font color="{self.brand_color.hexval()}">Payment Instructions</font>', self.style_heading))
        payment_info = [
            ["Business Name:", "V3Consult, LLC"],
            ["Bank Name:", invoice_data['bank_name']],
            ["Bank Address:", invoice_data['bank_address']],
            ["Type of Account:", invoice_data['account_type']],
            ["Routing Number:", invoice_data['routing_number']],
            ["Account Number:", invoice_data['account_number']]
        ]
        
        payment_table = Table(payment_info, colWidths=[1.5*inch, 6*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.light_grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), self.brand_color),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(payment_table)
        
        # Build PDF
        doc.build(story)
        return True

def generate_invoice(invoice_data, output_dir="outputs"):
    """Generate an invoice PDF file."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = f"invoice_{invoice_data['invoice_number']}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Create PDF
        pdf_gen = PDFGenerator()
        success = pdf_gen.generate_invoice_pdf(invoice_data, output_path)
        
        if success:
            return output_path
        return None
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None 