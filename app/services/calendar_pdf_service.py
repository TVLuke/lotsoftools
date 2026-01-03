"""
Calendar PDF Generation Service

Generates printable calendar PDFs with holidays marked.
"""

from io import BytesIO
from datetime import date, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from app.services.holiday_service import HolidayService
from app.utils.locale_helpers import WEEKDAYS, MONTHS, WEEK_PREFIX


class CalendarPDFService:
    """Service for generating calendar PDFs."""
    
    # Colors
    SCHOOL_HOLIDAY_BG = colors.Color(0.8, 0.9, 1.0)  # Light blue
    BANK_HOLIDAY_RED = colors.Color(0.8, 0.1, 0.1)   # Red
    SUNDAY_BOLD = True
    HEADER_BG = colors.Color(0.2, 0.4, 0.7)          # Dark blue
    
    @classmethod
    def generate_pdf(cls, country_code, subdivision_code=None, year=None, lang='DE'):
        """
        Generate a 12-page calendar PDF (one month per page).
        
        Args:
            country_code: Country ISO code (e.g., 'DE')
            subdivision_code: Subdivision code (e.g., 'DE-SH') or None for all
            year: Year to generate (default: current year)
            lang: Language for labels (DE, EN, FR, ES, IT)
            
        Returns:
            BytesIO object containing the PDF
        """
        if year is None:
            year = date.today().year
            
        # Get holidays
        holidays = HolidayService.get_holidays(
            country_code, 
            subdivision_code if subdivision_code != 'all' else None,
            include_past=True,
            lang=lang
        )
        
        # Build holiday lookup maps
        public_holidays = {}  # date_str -> name
        school_holidays = {}  # date_str -> name (first day only for display)
        school_holiday_days = set()  # all days that are school holidays
        
        for h in holidays:
            start = date.fromisoformat(h['start_date'])
            end = date.fromisoformat(h['end_date']) if h.get('end_date') else start
            
            if h['type'] == 'public':
                # Single day public holiday
                public_holidays[h['start_date']] = h['name']
            else:
                # School holiday - mark first day with name, rest just colored
                school_holidays[h['start_date']] = h['name']
                current = start
                while current <= end:
                    school_holiday_days.add(current.isoformat())
                    current += timedelta(days=1)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.Color(0.2, 0.3, 0.5),
            spaceAfter=10*mm,
            alignment=TA_CENTER
        )
        
        weekdays = WEEKDAYS.get(lang.upper(), WEEKDAYS['EN'])
        months = MONTHS.get(lang.upper(), MONTHS['EN'])
        
        # Get region name for title
        region_name = ""
        if subdivision_code and subdivision_code != 'all':
            subdivisions = HolidayService.get_subdivisions(country_code)
            for sub in subdivisions:
                if sub.get('code') == subdivision_code:
                    name_obj = next((n for n in sub.get('name', []) if n.get('language') == lang.upper()), None)
                    if not name_obj:
                        name_obj = next((n for n in sub.get('name', []) if n.get('language') == 'EN'), None)
                    if name_obj:
                        region_name = name_obj.get('text', '')
                    break
        
        elements = []
        
        for month in range(1, 13):
            # Month title
            month_name = months[month - 1]
            title_text = f"{month_name} {year}"
            if region_name:
                title_text += f" - {region_name}"
            elements.append(Paragraph(title_text, title_style))
            
            # Build table data
            table_data = []
            
            # Determine days in month
            if month == 12:
                days_in_month = (date(year + 1, 1, 1) - date(year, month, 1)).days
            else:
                days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days
            
            sunday_rows = []  # Track rows that are Sundays (for thick line after)
            monday_week_nums = {}  # row_idx -> week_num
            
            for day in range(1, days_in_month + 1):
                current_date = date(year, month, day)
                date_str = current_date.isoformat()
                weekday_idx = current_date.weekday()  # 0=Monday, 6=Sunday
                weekday_name = weekdays[weekday_idx]
                
                # Track Sundays for week separator lines
                if weekday_idx == 6:  # Sunday
                    sunday_rows.append(day - 1)
                
                # Track week numbers for Mondays
                if weekday_idx == 0:  # Monday
                    week_num = current_date.isocalendar()[1]
                    monday_week_nums[day - 1] = week_num
                
                # Determine holiday info - put in notes column
                holiday_name = ""
                if date_str in public_holidays:
                    holiday_name = public_holidays[date_str]
                elif date_str in school_holidays:
                    holiday_name = school_holidays[date_str]
                
                # Add week number in gray at start of notes for Mondays
                if weekday_idx == 0:
                    week_num = current_date.isocalendar()[1]
                    week_prefix = WEEK_PREFIX.get(lang.upper(), 'W')
                    if holiday_name:
                        holiday_name = f"{week_prefix}{week_num}  {holiday_name}"
                    else:
                        holiday_name = f"{week_prefix}{week_num}"
                
                table_data.append([
                    str(day),
                    weekday_name,
                    holiday_name  # Single notes/holiday column
                ])
            
            # Create table - calculate row height based on available space
            # A4 height 297mm, margins 30mm, title ~20mm = ~247mm for max 31 rows
            row_height = 7.5*mm  # ~7.5mm per row (31 × 7.5 = 232.5mm, fits safely)
            col_widths = [12*mm, 15*mm, 153*mm]  # Day, Weekday, Notes
            table = Table(table_data, colWidths=col_widths, rowHeights=[row_height] * len(table_data))
            
            # Build style commands
            style_commands = [
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8)),
            ]
            
            # Apply holiday styles row by row
            for day in range(1, days_in_month + 1):
                row_idx = day - 1
                current_date = date(year, month, day)
                date_str = current_date.isoformat()
                is_sunday = current_date.weekday() == 6
                
                # Sunday - bold
                if is_sunday:
                    style_commands.append(('FONTNAME', (0, row_idx), (1, row_idx), 'Helvetica-Bold'))
                
                # School holiday - light blue background
                if date_str in school_holiday_days:
                    style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), cls.SCHOOL_HOLIDAY_BG))
                    # Holiday name in gray
                    if date_str in school_holidays:
                        style_commands.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.Color(0.5, 0.5, 0.5)))
                
                # Bank holiday - red number and name
                if date_str in public_holidays:
                    style_commands.append(('TEXTCOLOR', (0, row_idx), (0, row_idx), cls.BANK_HOLIDAY_RED))
                    style_commands.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), cls.BANK_HOLIDAY_RED))
                    style_commands.append(('FONTNAME', (0, row_idx), (2, row_idx), 'Helvetica-Bold'))
            
            # Add thick line after Sundays as week separator
            for sunday_row in sunday_rows:
                if sunday_row < days_in_month - 1:  # Not last row
                    style_commands.append(('LINEBELOW', (0, sunday_row), (-1, sunday_row), 1.5, colors.Color(0.3, 0.3, 0.3)))
            
            # Make week numbers gray on Mondays
            for monday_row in monday_week_nums.keys():
                style_commands.append(('TEXTCOLOR', (2, monday_row), (2, monday_row), colors.Color(0.5, 0.5, 0.5)))
            
            table.setStyle(TableStyle(style_commands))
            elements.append(table)
            
            # Page break after each month (except last)
            if month < 12:
                from reportlab.platypus import PageBreak
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
