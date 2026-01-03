#!/usr/bin/env python3
"""
Generate holiday JSON and iCal files from CSV and bank holiday data.
Simple 1:1 conversion - no translations, just copy the data as-is.
"""
import csv
import json
import os
import re
from datetime import datetime, timedelta, timezone
import uuid

def get_years_from_filename(filename):
    """Extract school years from filename like 'germany_2425.csv' -> (2024, 2025)."""
    match = re.search(r'germany_(\d{4})(\d{4})\.csv', filename)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    match = re.search(r'germany_(\d{2})(\d{2})\.csv', filename)
    if match:
        return (2000 + int(match.group(1)), 2000 + int(match.group(2)))
    return None

def parse_date(date_str, year):
    """Parse a date string like '27.10.' into ISO format."""
    date_str = date_str.strip().rstrip('.')
    parts = date_str.split('.')
    if len(parts) >= 2:
        try:
            day = int(parts[0])
            month = int(parts[1])
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    return None

def parse_date_range(range_str, default_year):
    """Parse a date range like '27.10.-30.10.' or single date '31.10.'"""
    range_str = range_str.strip()
    if not range_str:
        return None
    
    if '-' in range_str and not range_str.endswith('-'):
        parts = range_str.split('-')
        if len(parts) == 2:
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            start_date = parse_date(start_str, default_year)
            if not start_date:
                return None
            
            # Determine end year - if end month < start month, it's next year
            end_parts = end_str.rstrip('.').split('.')
            start_parts = start_str.rstrip('.').split('.')
            
            end_year = default_year
            try:
                if len(end_parts) >= 2 and len(start_parts) >= 2:
                    end_month = int(end_parts[1])
                    start_month = int(start_parts[1])
                    if end_month < start_month:
                        end_year = default_year + 1
            except ValueError:
                pass
            
            end_date = parse_date(end_str, end_year)
            if end_date:
                return {"start": start_date, "end": end_date}
    else:
        date = parse_date(range_str.rstrip('-'), default_year)
        if date:
            return {"start": date, "end": date}
    
    return None

def parse_cell(cell_value, holiday_name, default_year):
    """Parse a cell - split by comma/und/slash, return list of holidays."""
    if not cell_value or cell_value.strip() == '':
        return []
    
    holidays = []
    # Split by comma, "und", or slash (for dates like "10.05./21.05.")
    parts = re.split(r',\s*|\s+und\s+|/', cell_value)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        date_range = parse_date_range(part, default_year)
        if date_range:
            holidays.append({
                "name": holiday_name,
                "start": date_range["start"],
                "end": date_range["end"]
            })
    
    return holidays

def get_year_for_column(column_name, school_years):
    """Determine which year based on column name."""
    first_year, second_year = school_years
    # Herbst and Weihnachten start in first year
    if 'Herbst' in column_name or 'Weihnachten' in column_name:
        return first_year
    return second_year

def process_csv(csv_path, school_years):
    """Process a CSV file, return holidays organized by year and state."""
    holidays_by_year = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            state_name = row.get('Land', '').strip()
            if not state_name:
                continue
            
            for column, value in row.items():
                if column == 'Land':
                    continue
                
                # Use column header as holiday name (strip year info for cleaner name)
                holiday_name = re.sub(r'\s*\d{4}(/\d{4})?\s*$', '', column).strip()
                year = get_year_for_column(column, school_years)
                
                if year not in holidays_by_year:
                    holidays_by_year[year] = {}
                
                if state_name not in holidays_by_year[year]:
                    holidays_by_year[year][state_name] = []
                
                parsed = parse_cell(value, holiday_name, year)
                holidays_by_year[year][state_name].extend(parsed)
    
    return holidays_by_year

def load_bank_holidays(holidays_dir):
    """Load bank holidays from germany_bank_holidays_*.json files."""
    bank_holidays = {}
    
    for filename in os.listdir(holidays_dir):
        if filename.startswith('germany_bank_holidays_') and filename.endswith('.json'):
            filepath = os.path.join(holidays_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            year = data.get('year')
            if year:
                bank_holidays[year] = {
                    'states': data.get('states', {}),
                    'source': data.get('source', '')
                }
                print(f"Loaded bank holidays from {filename}")
    
    return bank_holidays

def generate_json_files(school_holidays, bank_holidays, output_dir):
    """Generate combined JSON files for each year."""
    all_years = set(school_holidays.keys()) | set(bank_holidays.keys())
    combined_data = {}
    
    for year in sorted(all_years):
        school_data = school_holidays.get(year, {})
        bank_data = bank_holidays.get(year, {'states': {}, 'source': ''})
        bank_states = bank_data['states']
        
        all_states = set(school_data.keys()) | set(bank_states.keys())
        
        states = {}
        for state in sorted(all_states):
            school_list = school_data.get(state, [])
            bank_list = bank_states.get(state, [])
            
            # Sort school holidays by start date
            school_list.sort(key=lambda h: h.get('start', ''))
            
            states[state] = {
                'school_holidays': school_list,
                'bank_holidays': bank_list
            }
        
        sources = ["https://www.kmk.org/service/ferien.html"]
        if bank_data.get('source'):
            sources.append(bank_data['source'])
        
        output = {
            "country": "germany",
            "year": year,
            "sources": sources,
            "states": states
        }
        
        output_path = os.path.join(output_dir, f"germany_{year}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"Generated {output_path}")
        combined_data[year] = states
    
    return combined_data

def generate_ical_event(uid, summary, start_date, end_date=None):
    """Generate a VEVENT block."""
    start = start_date.replace('-', '')
    if end_date and end_date != start_date:
        # iCal DTEND is exclusive, add one day
        dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        end = dt.strftime('%Y%m%d')
    else:
        dt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
        end = dt.strftime('%Y%m%d')
    
    now = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    
    return f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now}
DTSTART;VALUE=DATE:{start}
DTEND;VALUE=DATE:{end}
SUMMARY:{summary}
END:VEVENT"""

def generate_ical_files(combined_data, output_dir):
    """Generate iCal files for each state and one for all of Germany."""
    # Collect events per state
    state_events = {}
    all_events = {}  # For deduplication in all-germany file
    
    for year, states in combined_data.items():
        for state, data in states.items():
            if state not in state_events:
                state_events[state] = []
            
            for h in data.get('school_holidays', []):
                uid = f"{state}-{h['start']}-{uuid.uuid4().hex[:8]}@usefull"
                event = generate_ical_event(uid, h['name'], h['start'], h.get('end'))
                state_events[state].append(event)
                
                # Track for all-germany deduplication
                key = (h['start'], h.get('end', h['start']), h['name'])
                if key not in all_events:
                    all_events[key] = {'states': set(), 'data': h}
                all_events[key]['states'].add(state)
            
            for h in data.get('bank_holidays', []):
                uid = f"{state}-{h['date']}-{uuid.uuid4().hex[:8]}@usefull"
                event = generate_ical_event(uid, h['name'], h['date'])
                state_events[state].append(event)
                
                key = (h['date'], h['date'], h['name'])
                if key not in all_events:
                    all_events[key] = {'states': set(), 'data': h, 'is_bank': True}
                all_events[key]['states'].add(state)
    
    # Generate per-state iCal files
    for state, events in state_events.items():
        if not events:
            continue
        
        safe_name = state.lower().replace(' ', '-').replace('ü', 'ue').replace('ä', 'ae').replace('ö', 'oe')
        content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//usefull//Holiday Calendar//EN
X-WR-CALNAME:Ferien & Feiertage {state}
CALSCALE:GREGORIAN
METHOD:PUBLISH
""" + "\n".join(events) + "\nEND:VCALENDAR"
        
        output_path = os.path.join(output_dir, f"germany_{safe_name}.ics")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {output_path}")
    
    # Generate all-germany iCal with state annotations
    germany_events = []
    for key, info in sorted(all_events.items(), key=lambda x: x[0][0]):
        states = info['states']
        data = info['data']
        name = data.get('name', '')
        
        if len(states) < 16:
            abbrevs = sorted([s[:2].upper() for s in states])
            name = f"{name} ({', '.join(abbrevs)})"
        
        uid = f"germany-{key[0]}-{uuid.uuid4().hex[:8]}@usefull"
        if info.get('is_bank'):
            event = generate_ical_event(uid, name, data['date'])
        else:
            event = generate_ical_event(uid, name, data['start'], data.get('end'))
        germany_events.append(event)
    
    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//usefull//Holiday Calendar//EN
X-WR-CALNAME:Ferien & Feiertage Deutschland
CALSCALE:GREGORIAN
METHOD:PUBLISH
""" + "\n".join(germany_events) + "\nEND:VCALENDAR"
    
    output_path = os.path.join(output_dir, "germany_all.ics")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {output_path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    holidays_dir = os.path.join(project_root, 'app', 'assets', 'holidays')
    
    # Load bank holidays
    bank_holidays = load_bank_holidays(holidays_dir)
    
    # Process school holiday CSVs
    csv_files = [f for f in os.listdir(holidays_dir) if f.startswith('germany_') and f.endswith('.csv')]
    
    all_school_holidays = {}
    
    for csv_file in sorted(csv_files):
        school_years = get_years_from_filename(csv_file)
        if not school_years:
            print(f"Skipping {csv_file} - could not parse years")
            continue
        
        print(f"Processing {csv_file} ({school_years[0]}/{school_years[1]})...")
        
        csv_path = os.path.join(holidays_dir, csv_file)
        holidays = process_csv(csv_path, school_years)
        
        for year, states in holidays.items():
            if year not in all_school_holidays:
                all_school_holidays[year] = {}
            for state, holiday_list in states.items():
                if state not in all_school_holidays[year]:
                    all_school_holidays[year][state] = []
                all_school_holidays[year][state].extend(holiday_list)
    
    if not all_school_holidays and not bank_holidays:
        print("No holiday data found")
        return
    
    # Generate JSON files
    combined_data = generate_json_files(all_school_holidays, bank_holidays, holidays_dir)
    
    # Generate iCal files
    print("\nGenerating iCal files...")
    generate_ical_files(combined_data, holidays_dir)

if __name__ == "__main__":
    main()
