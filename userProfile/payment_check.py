import os

import logging
from paypal.standard.models import ST_PP_COMPLETED

def check_payment(ipn_obj, log_error=True):
    PAYPAL_EMAIL = os.environ.get('PAYPAL_EMAIL')
    error_str = ''

    if ipn_obj.receiver_email == PAYPAL_EMAIL:
        try:
            price = int(ipn_obj.mc_amount3)
            return True
        except Exception as e:
            error_str = 'Failed to get user data - %s' % ipn_obj
    else:
        error_str = 'Invalid payment - %s' % ipn_obj

    if log_error:
        logging.error(error_str)
    return False