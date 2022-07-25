from datetime import datetime

def validate(str_date):
    """
    Function to validate input format "YYYY-MM-DD"
    
    """
    try:
        datetime.strptime(str_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Incorrect date format, should be YYYY-MM-DD')