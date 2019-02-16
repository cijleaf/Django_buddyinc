import os
import tempfile
from datetime import datetime

from django.conf import settings


def fill_out_schedule_z(generator_type, seller, buyer, output_filepath, date):
    input_folder = os.path.join(settings.STATICFILES_DIRS[0], 'pdf')
    
    generator = generator_type()
    generator.add_initials(seller['initials'])
    generator.add_seller_signature(seller['name'], date)
    generator.add_seller_allocation(seller['percentage_allocation'])
    generator.add_seller_info(
        seller['name'],
        seller['telephone'],
        seller['address'],
        seller['account_number'],
    )
    generator.add_buyer_info(
        buyer['name'],
        buyer['address'],
        buyer['account_number'],
        buyer['buyer_percentage_allocation'],
    )
    generator.add_all_to_pdf(input_folder, output_filepath)


def schedule_z_from_deal(deal, initials, generator_type, preview=False):
    temp_filename = tempfile.mkstemp()[1]
    current_date = datetime.now().strftime("%m/%d/%Y")

    seller_data = {
        'name': deal.seller.get_full_name(),
        'address': deal.seller.get_address_oneliner(),
        'telephone': deal.seller.phone,
        'account_number': deal.seller.utility_service_identifier,
        'initials': initials,
        'percentage_allocation': str(deal.seller.credit_to_sell_percent),
    }

    # Do not display actual buyer data on a contract preview
    if preview:
        buyer_data = {
            'name': 'Send inquiry to info@mysunbuddy.com',
            'address': '[HIDDEN]',
            'account_number': '[HIDDEN]',
        }
    else:
        buyer_data = {
            'name': deal.buyer.get_full_name(),
            'address': deal.buyer.get_address_oneliner(),
            'account_number': deal.buyer.utility_service_identifier,
        }

    buyer_data['buyer_percentage_allocation'] = '100'

    # create signed contract PDF
    fill_out_schedule_z(generator_type, seller_data, buyer_data, temp_filename, current_date)
    return temp_filename
