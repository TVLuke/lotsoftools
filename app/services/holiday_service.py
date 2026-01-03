"""
Holiday data service - fetches from OpenHolidays API at startup, caches locally.
"""
import json
import os
import time
import requests
from datetime import datetime, timedelta
import uuid

API_BASE = "https://openholidaysapi.org"

SUPPORTED_COUNTRIES = {
    # Western Europe
    "DE": {"name": "Deutschland", "name_en": "Germany"},
    "AT": {"name": "Österreich", "name_en": "Austria"},
    "FR": {"name": "Frankreich", "name_en": "France"},
    "BE": {"name": "Belgien", "name_en": "Belgium"},
    "NL": {"name": "Niederlande", "name_en": "Netherlands"},
    "LU": {"name": "Luxemburg", "name_en": "Luxembourg"},
    "CH": {"name": "Schweiz", "name_en": "Switzerland"},
    "LI": {"name": "Liechtenstein", "name_en": "Liechtenstein"},
    "MC": {"name": "Monaco", "name_en": "Monaco"},
    "AD": {"name": "Andorra", "name_en": "Andorra"},
    # Southern Europe
    "IT": {"name": "Italien", "name_en": "Italy"},
    "ES": {"name": "Spanien", "name_en": "Spain"},
    "PT": {"name": "Portugal", "name_en": "Portugal"},
    "MT": {"name": "Malta", "name_en": "Malta"},
    "SM": {"name": "San Marino", "name_en": "San Marino"},
    "VA": {"name": "Vatikanstadt", "name_en": "Vatican City"},
    # Northern Europe
    "IE": {"name": "Irland", "name_en": "Ireland"},
    "SE": {"name": "Schweden", "name_en": "Sweden"},
    "EE": {"name": "Estland", "name_en": "Estonia"},
    "LV": {"name": "Lettland", "name_en": "Latvia"},
    "LT": {"name": "Litauen", "name_en": "Lithuania"},
    # Central/Eastern Europe
    "PL": {"name": "Polen", "name_en": "Poland"},
    "CZ": {"name": "Tschechien", "name_en": "Czechia"},
    "SK": {"name": "Slowakei", "name_en": "Slovakia"},
    "HU": {"name": "Ungarn", "name_en": "Hungary"},
    "SI": {"name": "Slowenien", "name_en": "Slovenia"},
    "HR": {"name": "Kroatien", "name_en": "Croatia"},
    "RS": {"name": "Serbien", "name_en": "Serbia"},
    "RO": {"name": "Rumänien", "name_en": "Romania"},
    "BG": {"name": "Bulgarien", "name_en": "Bulgaria"},
    "MD": {"name": "Moldau", "name_en": "Moldova"},
    "BY": {"name": "Belarus", "name_en": "Belarus"},
    "AL": {"name": "Albanien", "name_en": "Albania"},
    # Americas
    "BR": {"name": "Brasilien", "name_en": "Brazil"},
    "MX": {"name": "Mexiko", "name_en": "Mexico"},
    # Africa
    "ZA": {"name": "Südafrika", "name_en": "South Africa"},
}

class HolidayService:
    _instance = None
    _data = {}  # country -> {subdivisions, holidays_by_year}
    _holidays_dir = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def init(cls, holidays_dir):
        """Initialize the service and fetch/load data."""
        instance = cls.get_instance()
        instance._holidays_dir = holidays_dir
        os.makedirs(holidays_dir, exist_ok=True)
        
        # Try to load from cache first, fetch if needed
        for country_code in SUPPORTED_COUNTRIES.keys():
            cache_file = os.path.join(holidays_dir, f"{country_code.lower()}_holidays.json")
            
            if os.path.exists(cache_file):
                # Check if cache is recent (less than 24 hours old)
                mtime = os.path.getmtime(cache_file)
                if time.time() - mtime < 2592000:  # 30 days
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            instance._data[country_code] = json.load(f)
                        print(f"Loaded {country_code} holidays from cache")
                        continue
                    except Exception as e:
                        print(f"Error loading cache for {country_code}: {e}")
            
            # Fetch from API
            print(f"Fetching {country_code} holidays from API...")
            instance._fetch_country(country_code)
            time.sleep(1)  # Rate limiting
        
        # Generate iCal files
        instance._generate_ical_files()
        
        return instance
    
    @classmethod
    def _fetch_country(cls, country_code):
        """Fetch all data for a country from the API."""
        instance = cls.get_instance()
        
        try:
            # Fetch subdivisions
            resp = requests.get(
                f"{API_BASE}/Subdivisions",
                params={"countryIsoCode": country_code},
                headers={"accept": "application/json"},
                timeout=30
            )
            resp.raise_for_status()
            subdivisions = resp.json()
            time.sleep(0.5)
            
            # Fetch holidays year by year (API limit is 3 years per request)
            # Fetch in multiple languages and merge
            languages = ["DE", "EN", "FR", "ES", "IT"]
            all_public_by_lang = {lang: [] for lang in languages}
            all_school_by_lang = {lang: [] for lang in languages}
            
            current_year = datetime.now().year
            for lang in languages:
                for start_year in range(2020, current_year + 4, 3):
                    end_year = min(start_year + 2, current_year + 3)
                    
                    # Public holidays
                    try:
                        resp = requests.get(
                            f"{API_BASE}/PublicHolidays",
                            params={
                                "countryIsoCode": country_code,
                                "languageIsoCode": lang,
                                "validFrom": f"{start_year}-01-01",
                                "validTo": f"{end_year}-12-31"
                            },
                            headers={"accept": "application/json"},
                            timeout=30
                        )
                        resp.raise_for_status()
                        all_public_by_lang[lang].extend(resp.json())
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Error fetching public holidays {country_code} {lang} {start_year}-{end_year}: {e}")
                    
                    # School holidays
                    try:
                        resp = requests.get(
                            f"{API_BASE}/SchoolHolidays",
                            params={
                                "countryIsoCode": country_code,
                                "languageIsoCode": lang,
                                "validFrom": f"{start_year}-01-01",
                                "validTo": f"{end_year}-12-31"
                            },
                            headers={"accept": "application/json"},
                            timeout=30
                        )
                        resp.raise_for_status()
                        all_school_by_lang[lang].extend(resp.json())
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Error fetching school holidays {country_code} {lang} {start_year}-{end_year}: {e}")
            
            # Merge languages - use DE as base, add other language names
            def merge_languages(holidays_by_lang):
                # Index other languages by unique key
                def make_key(h):
                    subs = tuple(sorted(s.get("code", "") for s in h.get("subdivisions", [])))
                    return (h.get("startDate"), h.get("endDate"), subs)
                
                lang_indexes = {lang: {make_key(h): h for h in holidays_by_lang.get(lang, [])} 
                               for lang in ["EN", "FR", "ES", "IT"]}
                
                merged = []
                for h in holidays_by_lang.get("DE", []):
                    key = make_key(h)
                    # Get names from all languages
                    names = {"DE": h.get("name", [{}])[0].get("text", "") if h.get("name") else ""}
                    for lang, index in lang_indexes.items():
                        if key in index:
                            lang_h = index[key]
                            names[lang] = lang_h.get("name", [{}])[0].get("text", "") if lang_h.get("name") else ""
                    
                    # Replace single-language name with multi-language names
                    h["names"] = names
                    merged.append(h)
                return merged
            
            all_public = merge_languages(all_public_by_lang)
            all_school = merge_languages(all_school_by_lang)
            
            # Deduplicate holidays (API returns duplicates for year-spanning holidays)
            def dedup_holidays(holidays):
                seen = set()
                unique = []
                for h in holidays:
                    # Create a unique key based on dates, name, and subdivisions
                    name_text = h.get("name", [{}])[0].get("text", "") if h.get("name") else ""
                    subs = tuple(sorted(s.get("code", "") for s in h.get("subdivisions", [])))
                    key = (h.get("startDate"), h.get("endDate"), name_text, subs)
                    if key not in seen:
                        seen.add(key)
                        unique.append(h)
                return unique
            
            all_public = dedup_holidays(all_public)
            all_school = dedup_holidays(all_school)
            
            # Store in memory
            instance._data[country_code] = {
                "country": country_code,
                "country_name": SUPPORTED_COUNTRIES[country_code],
                "subdivisions": subdivisions,
                "public_holidays": all_public,
                "school_holidays": all_school,
                "fetched_at": datetime.now().isoformat()
            }
            
            # Save to cache
            cache_file = os.path.join(instance._holidays_dir, f"{country_code.lower()}_holidays.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(instance._data[country_code], f, ensure_ascii=False, indent=2)
            
            print(f"Fetched {country_code}: {len(all_public)} public, {len(all_school)} school holidays")
            
        except Exception as e:
            print(f"Error fetching {country_code}: {e}")
            instance._data[country_code] = {"error": str(e)}
    
    @classmethod
    def _generate_ical_files(cls):
        """Generate iCal files for all countries and subdivisions."""
        instance = cls.get_instance()
        
        for country_code, data in instance._data.items():
            if "error" in data:
                continue
            
            subdivisions = data.get("subdivisions", [])
            public = data.get("public_holidays", [])
            school = data.get("school_holidays", [])
            
            # Generate per-subdivision iCal files
            for sub in subdivisions:
                sub_code = sub.get("code", "")
                if not sub_code:
                    continue
                
                events = cls._build_events_for_subdivision(sub_code, public, school)
                if events:
                    ical = cls._build_ical(events, f"Holidays {sub_code}")
                    filename = f"{country_code.lower()}_{sub_code.lower().replace('-', '_')}.ics"
                    filepath = os.path.join(instance._holidays_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(ical)
            
            # Generate country-wide iCal
            events = cls._build_events_all(public, school)
            if events:
                ical = cls._build_ical(events, f"Holidays {country_code}")
                filepath = os.path.join(instance._holidays_dir, f"{country_code.lower()}_all.ics")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(ical)
        
        print("Generated iCal files")
    
    @classmethod
    def _build_events_for_subdivision(cls, sub_code, public, school):
        """Build events for a specific subdivision."""
        events = []
        now = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        for h in public:
            if "Exception" in h.get("tags", []):
                continue
            if h.get("nationwide") or any(s.get("code") == sub_code for s in h.get("subdivisions", [])):
                name = cls._get_name(h)
                uid = f"{sub_code}-{h.get('startDate')}-{uuid.uuid4().hex[:8]}@usefull"
                events.append(cls._make_event(uid, name, h.get("startDate"), now, h.get("endDate")))
        
        for h in school:
            if "Exception" in h.get("tags", []):
                continue
            if any(s.get("code") == sub_code for s in h.get("subdivisions", [])):
                name = cls._get_name(h)
                uid = f"{sub_code}-{h.get('startDate')}-{uuid.uuid4().hex[:8]}@usefull"
                events.append(cls._make_event(uid, name, h.get("startDate"), now, h.get("endDate")))
        
        return events
    
    @classmethod
    def _build_events_all(cls, public, school):
        """Build all events for a country."""
        events = []
        now = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        for h in public:
            if "Exception" in h.get("tags", []):
                continue
            name = cls._get_name(h)
            uid = f"public-{h.get('startDate')}-{uuid.uuid4().hex[:8]}@usefull"
            events.append(cls._make_event(uid, name, h.get("startDate"), now, h.get("endDate")))
        
        for h in school:
            if "Exception" in h.get("tags", []):
                continue
            name = cls._get_name(h)
            subs = h.get("subdivisions", [])
            if subs:
                abbrevs = ", ".join(s.get("shortName", "") for s in subs[:5])
                if len(subs) > 5:
                    abbrevs += "..."
                name = f"{name} ({abbrevs})"
            uid = f"school-{h.get('startDate')}-{uuid.uuid4().hex[:8]}@usefull"
            events.append(cls._make_event(uid, name, h.get("startDate"), now, h.get("endDate")))
        
        return events
    
    @classmethod
    def _get_name(cls, holiday, lang="DE"):
        """Extract name from holiday, supporting both old and new format."""
        # New format with merged names dict
        if "names" in holiday:
            names = holiday["names"]
            return names.get(lang) or names.get("EN") or names.get("DE") or ""
        # Old format with name list
        name_list = holiday.get("name", [])
        for n in name_list:
            if n.get("language") == lang:
                return n.get("text", "")
        for n in name_list:
            if n.get("language") == "EN":
                return n.get("text", "")
        return name_list[0].get("text", "") if name_list else ""
    
    @classmethod
    def _build_ical(cls, events, cal_name):
        """Build iCal file content."""
        return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//usefull//Holiday Calendar//EN
X-WR-CALNAME:{cal_name}
CALSCALE:GREGORIAN
METHOD:PUBLISH
""" + "\n".join(events) + "\nEND:VCALENDAR"
    
    @classmethod
    def _make_event(cls, uid, summary, start_date, dtstamp, end_date=None):
        """Create a VEVENT string."""
        if not start_date:
            return ""
        start = start_date.replace('-', '')
        
        if end_date and end_date != start_date:
            dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            end = dt.strftime('%Y%m%d')
        else:
            dt = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
            end = dt.strftime('%Y%m%d')
        
        return f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART;VALUE=DATE:{start}
DTEND;VALUE=DATE:{end}
SUMMARY:{summary}
END:VEVENT"""
    
    # Public API methods
    @classmethod
    def get_countries(cls):
        """Get list of supported countries."""
        return [{"code": k, **v} for k, v in SUPPORTED_COUNTRIES.items()]
    
    @classmethod
    def get_subdivisions(cls, country_code):
        """Get subdivisions for a country."""
        instance = cls.get_instance()
        data = instance._data.get(country_code, {})
        return data.get("subdivisions", [])
    
    @classmethod
    def get_holidays(cls, country_code, subdivision_code=None, include_past=False, lang="DE"):
        """Get holidays filtered by country and subdivision."""
        instance = cls.get_instance()
        data = instance._data.get(country_code, {})
        
        if "error" in data:
            return []
        
        today = datetime.now().strftime('%Y-%m-%d')
        results = []
        
        for h in data.get("public_holidays", []):
            # Skip exception entries (e.g., island-specific holidays)
            if "Exception" in h.get("tags", []):
                continue
            
            if subdivision_code and subdivision_code != "all":
                if not h.get("nationwide") and not any(s.get("code") == subdivision_code for s in h.get("subdivisions", [])):
                    continue
            
            end_date = h.get("endDate", h.get("startDate", ""))
            if not include_past and end_date < today:
                continue
            
            results.append({
                "type": "public",
                "name": cls._get_name(h, lang),
                "start_date": h.get("startDate"),
                "end_date": h.get("endDate"),
                "nationwide": h.get("nationwide", False),
                "subdivisions": [s.get("shortName") for s in h.get("subdivisions", [])]
            })
        
        for h in data.get("school_holidays", []):
            # Skip exception entries (e.g., island-specific holidays)
            if "Exception" in h.get("tags", []):
                continue
            
            if subdivision_code and subdivision_code != "all":
                if not any(s.get("code") == subdivision_code for s in h.get("subdivisions", [])):
                    continue
            
            end_date = h.get("endDate", h.get("startDate", ""))
            if not include_past and end_date < today:
                continue
            
            results.append({
                "type": "school",
                "name": cls._get_name(h, lang),
                "start_date": h.get("startDate"),
                "end_date": h.get("endDate"),
                "subdivisions": [s.get("shortName") for s in h.get("subdivisions", [])]
            })
        
        results.sort(key=lambda h: h.get("start_date", ""))
        
        # Cluster holidays with same name, start_date, end_date
        clustered = []
        seen = {}
        for h in results:
            key = (h["type"], h["name"], h["start_date"], h["end_date"])
            if key in seen:
                # Merge subdivisions
                existing = seen[key]
                existing["subdivisions"] = list(set(existing["subdivisions"] + h["subdivisions"]))
            else:
                seen[key] = h
                clustered.append(h)
        
        # Sort subdivisions alphabetically
        for h in clustered:
            h["subdivisions"] = sorted(h["subdivisions"])
        
        return clustered
    
    @classmethod
    def generate_ical(cls, country_code, subdivision_code=None):
        """Generate iCal content dynamically."""
        instance = cls.get_instance()
        data = instance._data.get(country_code, {})
        
        if "error" in data:
            return ""
        
        public = data.get("public_holidays", [])
        school = data.get("school_holidays", [])
        
        if subdivision_code and subdivision_code != "all":
            events = cls._build_events_for_subdivision(subdivision_code, public, school)
            cal_name = f"Holidays {subdivision_code}"
        else:
            events = cls._build_events_all(public, school)
            cal_name = f"Holidays {country_code}"
        
        return cls._build_ical(events, cal_name)
