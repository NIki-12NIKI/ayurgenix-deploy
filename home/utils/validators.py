# utils/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_blood_pressure(value):
    if not re.match(r'^\d{2,3}/\d{2,3}$', value):
        raise ValidationError(_('Blood pressure must be in format "120/80"'))
    
    systolic, diastolic = map(int, value.split('/'))
    if not (70 <= systolic <= 200 and 40 <= diastolic <= 130):
        raise ValidationError(_('Blood pressure values out of normal range'))

def validate_phone_number(value):
    if not re.match(r'^\d{10}$', re.sub(r'\D', '', value)):
        raise ValidationError(_('Phone number must contain exactly 10 digits'))

def validate_dosage(value):
    if not re.match(r'^\d+(\.\d+)?\s*(mg|ml|g)$', value.lower()):
        raise ValidationError(_('Dosage must be in format "100 mg" or "5 ml"'))