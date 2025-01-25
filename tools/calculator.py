import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Dict
import streamlit as st

class CalculatorTool:
    """A tool for precise financial calculations."""
    
    def __init__(self):
        """Initialize the calculator tool with 2 decimal places precision for currency."""
        self.precision = Decimal('0.01')
        st.write("🧮 Calculator initialized")
    
    def _to_decimal(self, value):
        """Convert a value to Decimal with proper rounding."""
        try:
            # Remove currency symbols and spaces if present
            if isinstance(value, str):
                value = value.replace('$', '').replace(',', '').strip()
            result = Decimal(str(value)).quantize(self.precision, rounding=ROUND_HALF_UP)
            return result
        except Exception as e:
            st.error(f"Error converting {value} to Decimal: {str(e)}")
            return None
    
    def multiply(self, a, b):
        """Multiply two numbers with proper decimal handling."""
        a_decimal = self._to_decimal(a)
        b_decimal = self._to_decimal(b)
        if a_decimal is not None and b_decimal is not None:
            result = (a_decimal * b_decimal).quantize(self.precision, rounding=ROUND_HALF_UP)
            return result
        return None
    
    def validate_calculations(self, entries, hourly_rate):
        """Validate and fix calculations in time entries."""
        with st.expander("🔍 Calculation Details", expanded=False):
            st.write("### Validating Time Entry Calculations")
            
            # Create columns for input and calculated values
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📥 Input Values")
            with col2:
                st.markdown("#### 📊 Calculated Values")
            
            st.divider()
            
            validated_entries = []
            hourly_rate = self._to_decimal(hourly_rate)
            
            for entry in entries:
                # Create columns for each entry
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Date:** {entry['date']}")
                    st.markdown(f"**Hours:** {entry['hours']}")
                    st.markdown(f"**Rate:** ${hourly_rate}")
                
                # Calculate amount
                hours = self._to_decimal(entry['hours'])
                if hours is not None and hourly_rate is not None:
                    amount = self.multiply(hours, hourly_rate)
                    
                    with col2:
                        st.markdown("**Calculated Amount:**")
                        st.metric(
                            label="",
                            value=f"${amount:,.2f}",
                            delta=f"{hours} hrs × ${hourly_rate:,.2f}/hr"
                        )
                    
                    validated_entry = {
                        'date': entry['date'],
                        'hours': float(hours),
                        'description': entry['description'],
                        'rate': float(hourly_rate),
                        'amount': float(amount)
                    }
                    validated_entries.append(validated_entry)
                
                st.divider()
            
            return validated_entries
    
    def calculate_totals(self, entries):
        """Calculate total hours and amount from entries."""
        with st.expander("📊 Totals Calculation", expanded=False):
            st.write("### Calculating Invoice Totals")
            
            total_hours = Decimal('0')
            total_amount = Decimal('0')
            
            # Create a table for the totals
            data = []
            for entry in entries:
                hours = self._to_decimal(entry['hours'])
                amount = self._to_decimal(entry['amount'])
                if hours is not None and amount is not None:
                    total_hours += hours
                    total_amount += amount
                    data.append([entry['date'], f"{hours} hrs", f"${amount:,.2f}"])
            
            # Display totals in a metric
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Hours", f"{total_hours:,.2f} hrs")
            with col2:
                st.metric("Total Amount", f"${total_amount:,.2f}")
            
            # Return the totals as a dictionary with float values
            return {
                'total_hours': float(total_hours),
                'total_amount': float(total_amount)
            }
    
    @staticmethod
    def clean_number(number: Union[str, float, int]) -> Decimal:
        """Convert number to Decimal, handling string formatting."""
        if isinstance(number, str):
            # Remove any non-digit characters except . and -
            number = re.sub(r'[^\d.-]', '', number)
        return Decimal(str(number))
    
    @staticmethod
    def format_currency(amount: Decimal) -> str:
        """Format decimal as currency string."""
        return f"${amount:.2f}"
    
    def calculate_hours_amount(self, hours: Union[str, float, int], rate: Union[str, float, int]) -> Dict[str, Union[Decimal, str]]:
        """Calculate amount for hours worked at given rate."""
        hours_dec = self.clean_number(hours)
        rate_dec = self.clean_number(rate)
        
        amount = (hours_dec * rate_dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            "hours": hours_dec,
            "rate": rate_dec,
            "amount": amount,
            "formatted_amount": self.format_currency(amount)
        } 