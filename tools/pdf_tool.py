from pydantic import BaseModel, Field
from utils.pdf_generator import generate_invoice

class PDFGeneratorTool(BaseModel):
    """Tool for generating PDF invoices."""
    name: str = Field(default="PDF Generator Tool")
    description: str = Field(default="Generate a PDF invoice from structured invoice data")

    def run(self, invoice_data: dict) -> str:
        """
        Generate a PDF invoice from the provided invoice data.
        
        Args:
            invoice_data (dict): Dictionary containing invoice details including:
                - client_address
                - service_type
                - invoice_number
                - invoice_date
                - period_start
                - period_end
                - entries (list of time entries)
                - total_hours
                - total_amount
                - hourly_rate
                
        Returns:
            str: Path to the generated PDF file
        """
        try:
            pdf_path = generate_invoice(invoice_data)
            return pdf_path
        except Exception as e:
            return f"Error generating PDF: {str(e)}"