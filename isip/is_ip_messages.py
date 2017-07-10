from helpers.parsing_messages import RESULT_CODES, ParseMessageHelper

# ------------------------------------------------------------------------
# References
# ------------------------------------------------------------------------

# <editor-fold desc="References">
# 	<References>

IP_META_REFERENCES = []

# </editor-fold>

# ------------------------------------------------------------------------
# <editor-fold desc="Segments">
# ------------------------------------------------------------------------

IP_META_SEGMENTS = [
    {'name': 'IPv4_literal',
     'references': ['address-literal-IPv4'],
     'messages': {
        'TOO_MANY_SEGMENTS': {},
        'TOO_FEW_SEGMENTS': {},
        }
     },
    {'name': 'Snum', 
     'references': [], 
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6_literal',
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6_hex', 
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6_full', 
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6_comp', 
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6v4_full', 
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },

    {'name': 'IPv6v4_comp', 
     'references': ['address-literal-IPv6'],
     'messages': {
        '': {},
        }
     },
]


# </editor-fold "Segments">
# ------------------------------------------------------------------------
