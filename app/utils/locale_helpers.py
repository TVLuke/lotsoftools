"""
Locale helpers for weekday and month names in multiple languages.
"""

WEEKDAYS = {
    'DE': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
    'EN': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    'FR': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
    'ES': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
    'IT': ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'],
}

MONTHS = {
    'DE': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
           'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    'EN': ['January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December'],
    'FR': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    'ES': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    'IT': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
           'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
}


def get_weekday_name(weekday_index, lang='EN'):
    """Get weekday name by index (0=Monday, 6=Sunday)."""
    return WEEKDAYS.get(lang.upper(), WEEKDAYS['EN'])[weekday_index]


def get_month_name(month, lang='EN'):
    """Get month name by number (1-12)."""
    return MONTHS.get(lang.upper(), MONTHS['EN'])[month - 1]


WEEK_PREFIX = {
    'DE': 'KW',
    'EN': 'W',
    'FR': 'S',
    'ES': 'S',
    'IT': 'S',
}


def get_week_prefix(lang='EN'):
    """Get week number prefix for language."""
    return WEEK_PREFIX.get(lang.upper(), 'W')
