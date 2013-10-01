from django import template
register = template.Library()

import logging
logger = logging.getLogger(__name__)

@register.filter
def format_lease_state(value, role):
    """format the transaction status code"""
    
    labels = {
#        0: {
#            'status': 'need set price',
#            'buyer': "Please wait for the owner to set a price for this book",
#            'seller': "Pleaes set a price for this book first.",
#        },
        1: {
            'status': 'price updated',
            'buyer': 'Do you agree to rent the book for this price? If you agree, click accept. Otherwise, send the owner a message.',
            'seller': "Wait for renter to accept or decline your new price",
        },
        2: {
            'status': 'request pending',
            'buyer': "Wait for owner's response",
            'seller': '-',
        },
        3: {
            'status': 'request ignored',
            'buyer': "Wait for owner's response",
            'seller': 'You ignored this request',
        },
        4: {
            'status': 'request expired',
            'buyer': '-',
            'seller': '-',
        },
        5: {
            'status': 'request canceled by renter',
            'buyer': 'You canceled the request',
            'seller': 'The renter canceled the request',
        },
        6: {
            'status': 'request declined',
            'buyer': 'Owner declined your request',
            'seller': 'You declined the request',
        },
        10: {
            'status': 'request accepted',
            'buyer': 'Wait for owner to drop off the book.',
            'seller': 'Please drop off your book at the dropbox',
        },
        12: {
            'status': 'trade canceled',
            'buyer': '-',
            'seller': '-',
        },
        13: {
            'status': 'book not dropped off. trade canceled',
            'buyer': 'Please send a new request if you still want to rent the book',
            'seller': '-',
        },
        20: {
            'status': 'book dropped off',
            'buyer': "Please pick up the book at the dropbox and pay up front. Note that currently we are only accepting credit card or debit card payments.",
            'seller': 'Wait for renter to pick up the book',
        },
        21: {
            'status': 'book not picked up by renter. trade canceled',
            'buyer': 'Please send a new request if you still want to rent the book',
            'seller': 'Please pick up your book at the dropbox',
        },
        22: {
            'status': "book declined by renter",
            'buyer': "Please explain to the owner why you didn't pick up the book",
            'seller': "Buyer declined book- condition doesn't match listing. Please pick up your book at the dropbox.",
        },
        23: {
            'status': 'book picked up by owner',
            'buyer': '-',
            'seller': '-',
        },
        24: {
            'status': 'book not picked up by owner',
            'buyer': '-',
            'seller': 'Please contact us (help@idlebook.com) to pick up your book immediately.',    
        },
        30: {
            'status': 'book picked up by renter. book in use',
            'buyer': "Please return your book when it's due.",  # You can send a renew request to make keep the book longer.
            'seller': "Book successfully rented. Renter will return your book when it's due",
        },
        31: {
            'status': 'book renewal requested',
            'buyer': "Wait for owner's response",
            'seller': 'Do you allow the renter to renew the book?',
        },
        32: {
            'status': 'book is due',
            'buyer': 'Please return the book immediately or your deposit will be charged. If you want to keep the book longer, you can send a request to renew the book.',
            'seller': "If you don't get your book after the due date, please message the renter to receive your book.",
        },
        33: {
            'status': 'book renewal requested',
            'buyer': "Wait for owner's response",
            'seller': 'Do you allow the renter to renew the book?',
        },
        34: {
            'status': 'book not returned by renter',
            'buyer': "Warning: please return this book immediately. If you do not return it, all of your deposit will be forfeit and you'll receive negative reviews.",
            'seller': "We apologize for the loss of your book. We'll refund you the market price.",
        },
        40: {
            'status': 'book returned to dropbox',
            'buyer': 'Rental complete!',
            'seller': 'Please pick up your book at the dropbox.',
        },
        41: {
            'status': 'book returned to owner',
            'buyer': 'Thank you for using Idlebook. Please review your experience',
            'seller': 'Thank you for using Idlebook. Please review the experience',
        },
        42: {
            'status': 'book not picked up by owner',
            'buyer': '-',
            'seller': 'Please contact us (help@idlebook.com) to get your book back',
        },
    }
    try:
        return labels[value][role]
    except KeyError:
        logger.error('state %s not found for role %s' % (value, role))
    

@register.filter
def format_sale_state(value, role):
    
    labels = {
#        0: {
#            'status': 'need set price',
#            'buyer': "Please wait for the seller to set a price for this book",
#            'seller': "Pleaes set a price for this book first.",
#        },
        1: {
            'status': 'price updated',
            'buyer': 'Do you agree to buyer the book for this price? If you agree, click accept. Otherwise, send the seller a message.',
            'seller': "Wait for buyer to accept or decline your new price",
        },
        2: {
            'status': 'request pending',
            'buyer': "Wait for seller's response",
            'seller': '-',
        },
        3: {
            'status': 'request ignored',
            'buyer': "Wait for seller's response",
            'seller': 'You ignored this request',
        },
        4: {
            'status': 'request expired',
            'buyer': '-',
            'seller': '-',
        },
        5: {
            'status': 'request canceled by buyer',
            'buyer': 'You canceled the request',
            'seller': 'The buyer canceled the request',
        },
        6: {
            'status': 'request declined',
            'buyer': 'Seller declined your request',
            'seller': 'You declined the request',
        },
        10: {
            'status': 'request accepted',
            'buyer': 'Wait for seller to drop off the book.',
            'seller': 'Please drop off your book at the dropbox',
        },
        12: {
            'status': 'trade canceled',
            'buyer': '-',
            'seller': '-',
        },
        13: {
            'status': 'book not dropped off. trade canceled',
            'buyer': 'Please send a new request if you still want to buy the book',
            'seller': '-',
        },
        20: {
            'status': 'book dropped off',
            'buyer': 'Please pick up the book at the dropbox',
            'seller': 'Wait for buyer to pick up the book',
        },
        21: {
            'status': 'book not picked up by buyer. trade canceled',
            'buyer': 'Please send a new request if you still want to buy the book',
            'seller': 'Please pick up your book at the dropbox',
        },
        22: {
            'status': "book declined by buyer",
            'buyer': "Please explain to the seller why you didn't pick up the book",
            'seller': "Buyer declined book - condition doesn't match listing. Please pick up your book at the dropbox.",
        },
        23: {
            'status': 'book picked up by seller',
            'buyer': '-',
            'seller': '-',
        },
        24: {
            'status': 'book not picked up by seller',
            'buyer': '-',
            'seller': 'Please contact us (help@idlebook.com) to pick up your book immediately.',
        },
        30: {
            'status': 'book picked up by buyer. trade complete',
            'buyer': 'Book successfully purchased. Thank you for using Idlebook. Please review your experience.',
            'seller': 'Book successfully sold. Thank you for using Idlebook. Please review your experience.',
        },
    }
    try:
        return labels[value][role]
    except KeyError:
        logger.error('state %s not found for role %s' % (value, role))



@register.filter
def format_state_status(value, type):
    """format the transaction status code"""
    labels = {
        'lease': {
            1: 'price updated',
            2: 'request pending',
            3: 'request ignored',
            4: 'request expired',
            5: 'request canceled by renter',
            6: 'request declined',
            10: 'request accepted',
            12: 'trade canceled',
            13: 'book not dropped off. trade canceled',
            20: 'book dropped off',
            21: 'book not picked up by renter. trade canceled',
            22: "book declined by renter",
            23: 'book picked up by owner',
            24: 'book not picked up by owner',
            30: 'book picked up by renter. book in use',
            31: 'book renewal requested',
            32: 'book is due',
            33: 'book renewal requested',
            34: 'book not returned by renter',
            40: 'book returned to dropbox',
            41: 'book returned to owner',
            42: 'book not picked up by owner'
        },
        'sale': {
            1: 'price updated',
            2: 'request pending',
            3: 'request ignored',
            4: 'request expired',
            5: 'request canceled by buyer',
            6: 'request declined',
            10: 'request accepted',
            12: 'trade canceled',
            13: 'book not dropped off. trade canceled',
            20: 'book dropped off',
            21: 'book not picked up by buyer. trade canceled',
            22: "book declined by buyer",
            23: 'book picked up by seller',
            24: 'book not picked up by seller',
            30: 'book picked up by buyer. book sold'
        }
    }
    try:
        return labels[type][value]
    except KeyError:
        logger.error('type %s state %s not found' % (type, value))




@register.filter
def format_state_buyer(value, type):
    """format the transaction status code"""
    labels = {
        'lease': {
            1: 'Do you agree to rent the book for this price? If you agree, click accept. Otherwise, send the owner a message.',
            2: "Wait for owner's response",
            3: "Wait for owner's response",
            4: '-',
            5: 'You canceled the request',
            6: 'Owner declined your request',
            10: 'Wait for owner to drop off the book.',
            12: '-',
            13: 'Please send a new request if you still want to rent the book',
            20: 'Please pick up the book at the dropbox and pay. Note that currently we are only accepting credit card or debit card payments.',
            21: 'Please send a new request if you still want to rent the book',
            22: "Please explain to the owner why you didn't pick up the book",
            23: '-',
            24: '-',
            30: "Please return your book when it's due.",  # You can send a renew request to make keep the book longer.
            31: "Wait for owner's response",
            32: 'Please return the book immediately or your deposit will be charged. If you want to keep the book longer, you can send a request to renew the book.',
            33: "Wait for owner's response",
            34: "Warning: please return this book immediately. If you do not return it, all of your deposit will be forfeit and you'll receive negative reviews.",
            40: 'Rental complete!',
            41: 'Thank you for using Idlebook. Please review your experience',
            42:'-',
        },
        'sale': {
            1: 'Do you agree to buy the book for this price? If you agree, click accept. Otherwise, send the seller a message.',
            2: "Wait for seller's response",
            3: "Wait for seller's response",
            4: '-',
            5: 'You canceled the request',
            6: 'Seller declined your request',
            10: 'Wait for seller to drop off the book.',
            12: '-',
            13: 'Please send a new request if you still want to buy the book',
            20: 'Please pick up the book at the dropbox and pay. Note that currently we are only accepting credit card or debit card payments.',
            21: 'Please send a new request if you still want to buy the book',
            22: "Please explain to the seller why you didn't pick up the book",
            23: '-',
            24: '-',
            30: 'Book successfully purchased. Thank you for using Idlebook. Please review your experience.',
        }
    }
    try:
        return labels[type][value]
    except KeyError:
        logger.error('type %s state %s not found' % (type, value))



@register.filter
def format_state_seller(value, type):
    """format the transaction status code"""
    labels = {
        'lease': {
            1: "Wait for renter to accept or decline your new price",
            2: '-',
            3: 'You ignored this request',
            4: '-',
            5: 'The renter canceled the request',
            6: 'You declined the request',
            10: 'Please drop off your book at the dropbox',
            12: '-',
            13: '-',
            20: 'Wait for renter to pick up the book',
            21: 'Please pick up your book at the dropbox',
            22: "Buyer declined book - condition doesn't match listing. Please pick up your book at the dropbox.",
            23: '-',
            24: 'Please contact us (help@idlebook.com) to pick up your book immediately.',
            30: "Book successfully rented. Renter will return your book when it's due.",
            31: 'Do you allow the renter to renew the book?',
            32: "If your book is not returned after the due date, please message the renter immediately. If no response, we'll get you refunded the market price.",
            33: 'Do you allow the renter to renew the book?',
            34: "We apologize for the loss of your book. We'll refund you the market price.",
            40: 'Please pick up your book at the dropbox.',
            41: 'Thank you for using Idlebook. Please review the experience',
            42: 'Please contact us (help@idlebook.com) to get your book back',
        },
        'sale': {
            1: "Wait for buyer to accept or decline your new price",
            2: '-',
            3: 'You ignored this request',
            4: '-',
            5: 'The buyer canceled the request',
            6: 'You declined the request',
            10: 'Please drop off your book at the dropbox',
            12: '-',
            13: '-',
            20: 'Wait for buyer to pick up the book',
            21: 'Please pick up your book at the dropbox',
            22: "Buyer declined book- condition doesn't match listing. Please pick up your book at the dropbox.",
            23: '-',
            24: 'Please contact us (help@idlebook.com) to pick up your book immediately.',
            30: 'Book successfully sold. Thank you for using Idlebook. Please review your experience.',      
        }
    }
    try:
        return labels[type][value]
    except KeyError:
        logger.error('type %s state %s not found' % (type, value))

