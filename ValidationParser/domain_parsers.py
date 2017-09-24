from ValidationParser.parser_objects import *
from ValidationParser.parser_base_chars import *
from ValidationParser.is_ip_parsers import validate_ip_addr, validate_ipv6_addr, validate_ipv4_addr
from ValidationParser.exceptions import WrapperStop
from ValidationParser.parser_messages import STATUS_CODES
from helpers.general import make_char_str, make_list
from ipaddress import IPv4Address, IPv6Address, AddressValueError, IPv4Network, IPv6Network
import re
import textwrap
from collections import namedtuple

from helpers.meta_data import ISEMAIL_DNS_LOOKUP_LEVELS
try:
    from dns import resolver, reversename
    from dns import exception as dns_except
    USE_SOCKETS = False
except ImportError:
    import socket
    USE_SOCKETS = True



# Uses dnspython if it exists, otherwise will use socket, in which case MX lookup is not possible.


# DNS TLD's from:
# http://data.iana.org/TLD/tlds-alpha-by-domain.txt
#   Version 2017032901, Last Updated Thu Mar 30 07:07:01 2017 UTC


DNS_TLD = {'AAA': None, 'AARP': None, 'ABARTH': None, 'ABB': None, 'ABBOTT': None, 'ABBVIE': None, 'ABC': None,
           'ABLE': None, 'ABOGADO': None, 'ABUDHABI': None, 'AC': None, 'ACADEMY': None, 'ACCENTURE': None,
           'ACCOUNTANT': None, 'ACCOUNTANTS': None, 'ACO': None, 'ACTIVE': None, 'ACTOR': None, 'AD': None,
           'ADAC': None, 'ADS': None, 'ADULT': None, 'AE': None, 'AEG': None, 'AERO': None, 'AETNA': None, 'AF': None,
           'AFAMILYCOMPANY': None, 'AFL': None, 'AFRICA': None, 'AG': None, 'AGAKHAN': None, 'AGENCY': None, 'AI': None,
           'AIG': None, 'AIGO': None, 'AIRBUS': None, 'AIRFORCE': None, 'AIRTEL': None, 'AKDN': None, 'AL': None,
           'ALFAROMEO': None, 'ALIBABA': None, 'ALIPAY': None, 'ALLFINANZ': None, 'ALLSTATE': None, 'ALLY': None,
           'ALSACE': None, 'ALSTOM': None, 'AM': None, 'AMERICANEXPRESS': None, 'AMERICANFAMILY': None, 'AMEX': None,
           'AMFAM': None, 'AMICA': None, 'AMSTERDAM': None, 'ANALYTICS': None, 'ANDROID': None, 'ANQUAN': None,
           'ANZ': None, 'AO': None, 'AOL': None, 'APARTMENTS': None, 'APP': None, 'APPLE': None, 'AQ': None,
           'AQUARELLE': None, 'AR': None, 'ARAMCO': None, 'ARCHI': None, 'ARMY': None, 'ARPA': None, 'ART': None,
           'ARTE': None, 'AS': None, 'ASDA': None, 'ASIA': None, 'ASSOCIATES': None, 'AT': None, 'ATHLETA': None,
           'ATTORNEY': None, 'AU': None, 'AUCTION': None, 'AUDI': None, 'AUDIBLE': None, 'AUDIO': None, 'AUSPOST': None,
           'AUTHOR': None, 'AUTO': None, 'AUTOS': None, 'AVIANCA': None, 'AW': None, 'AWS': None, 'AX': None,
           'AXA': None, 'AZ': None, 'AZURE': None, 'BA': None, 'BABY': None, 'BAIDU': None, 'BANAMEX': None,
           'BANANAREPUBLIC': None, 'BAND': None, 'BANK': None, 'BAR': None, 'BARCELONA': None, 'BARCLAYCARD': None,
           'BARCLAYS': None, 'BAREFOOT': None, 'BARGAINS': None, 'BASEBALL': None, 'BASKETBALL': None, 'BAUHAUS': None,
           'BAYERN': None, 'BB': None, 'BBC': None, 'BBT': None, 'BBVA': None, 'BCG': None, 'BCN': None, 'BD': None,
           'BE': None, 'BEATS': None, 'BEAUTY': None, 'BEER': None, 'BENTLEY': None, 'BERLIN': None, 'BEST': None,
           'BESTBUY': None, 'BET': None, 'BF': None, 'BG': None, 'BH': None, 'BHARTI': None, 'BI': None, 'BIBLE': None,
           'BID': None, 'BIKE': None, 'BING': None, 'BINGO': None, 'BIO': None, 'BIZ': None, 'BJ': None, 'BLACK': None,
           'BLACKFRIDAY': None, 'BLANCO': None, 'BLOCKBUSTER': None, 'BLOG': None, 'BLOOMBERG': None, 'BLUE': None,
           'BM': None, 'BMS': None, 'BMW': None, 'BN': None, 'BNL': None, 'BNPPARIBAS': None, 'BO': None, 'BOATS': None,
           'BOEHRINGER': None, 'BOFA': None, 'BOM': None, 'BOND': None, 'BOO': None, 'BOOK': None, 'BOOKING': None,
           'BOOTS': None, 'BOSCH': None, 'BOSTIK': None, 'BOSTON': None, 'BOT': None, 'BOUTIQUE': None, 'BOX': None,
           'BR': None, 'BRADESCO': None, 'BRIDGESTONE': None, 'BROADWAY': None, 'BROKER': None, 'BROTHER': None,
           'BRUSSELS': None, 'BS': None, 'BT': None, 'BUDAPEST': None, 'BUGATTI': None, 'BUILD': None, 'BUILDERS': None,
           'BUSINESS': None, 'BUY': None, 'BUZZ': None, 'BV': None, 'BW': None, 'BY': None, 'BZ': None, 'BZH': None,
           'CA': None, 'CAB': None, 'CAFE': None, 'CAL': None, 'CALL': None, 'CALVINKLEIN': None, 'CAM': None,
           'CAMERA': None, 'CAMP': None, 'CANCERRESEARCH': None, 'CANON': None, 'CAPETOWN': None, 'CAPITAL': None,
           'CAPITALONE': None, 'CAR': None, 'CARAVAN': None, 'CARDS': None, 'CARE': None, 'CAREER': None,
           'CAREERS': None, 'CARS': None, 'CARTIER': None, 'CASA': None, 'CASE': None, 'CASEIH': None, 'CASH': None,
           'CASINO': None, 'CAT': None, 'CATERING': None, 'CATHOLIC': None, 'CBA': None, 'CBN': None, 'CBRE': None,
           'CBS': None, 'CC': None, 'CD': None, 'CEB': None, 'CENTER': None, 'CEO': None, 'CERN': None, 'CF': None,
           'CFA': None, 'CFD': None, 'CG': None, 'CH': None, 'CHANEL': None, 'CHANNEL': None, 'CHASE': None,
           'CHAT': None, 'CHEAP': None, 'CHINTAI': None, 'CHLOE': None, 'CHRISTMAS': None, 'CHROME': None,
           'CHRYSLER': None, 'CHURCH': None, 'CI': None, 'CIPRIANI': None, 'CIRCLE': None, 'CISCO': None,
           'CITADEL': None, 'CITI': None, 'CITIC': None, 'CITY': None, 'CITYEATS': None, 'CK': None, 'CL': None,
           'CLAIMS': None, 'CLEANING': None, 'CLICK': None, 'CLINIC': None, 'CLINIQUE': None, 'CLOTHING': None,
           'CLOUD': None, 'CLUB': None, 'CLUBMED': None, 'CM': None, 'CN': None, 'CO': None, 'COACH': None,
           'CODES': None, 'COFFEE': None, 'COLLEGE': None, 'COLOGNE': None, 'COM': None, 'COMCAST': None,
           'COMMBANK': None, 'COMMUNITY': None, 'COMPANY': None, 'COMPARE': None, 'COMPUTER': None, 'COMSEC': None,
           'CONDOS': None, 'CONSTRUCTION': None, 'CONSULTING': None, 'CONTACT': None, 'CONTRACTORS': None,
           'COOKING': None, 'COOKINGCHANNEL': None, 'COOL': None, 'COOP': None, 'CORSICA': None, 'COUNTRY': None,
           'COUPON': None, 'COUPONS': None, 'COURSES': None, 'CR': None, 'CREDIT': None, 'CREDITCARD': None,
           'CREDITUNION': None, 'CRICKET': None, 'CROWN': None, 'CRS': None, 'CRUISE': None, 'CRUISES': None,
           'CSC': None, 'CU': None, 'CUISINELLA': None, 'CV': None, 'CW': None, 'CX': None, 'CY': None, 'CYMRU': None,
           'CYOU': None, 'CZ': None, 'DABUR': None, 'DAD': None, 'DANCE': None, 'DATA': None, 'DATE': None,
           'DATING': None, 'DATSUN': None, 'DAY': None, 'DCLK': None, 'DDS': None, 'DE': None, 'DEAL': None,
           'DEALER': None, 'DEALS': None, 'DEGREE': None, 'DELIVERY': None, 'DELL': None, 'DELOITTE': None,
           'DELTA': None, 'DEMOCRAT': None, 'DENTAL': None, 'DENTIST': None, 'DESI': None, 'DESIGN': None, 'DEV': None,
           'DHL': None, 'DIAMONDS': None, 'DIET': None, 'DIGITAL': None, 'DIRECT': None, 'DIRECTORY': None,
           'DISCOUNT': None, 'DISCOVER': None, 'DISH': None, 'DIY': None, 'DJ': None, 'DK': None, 'DM': None,
           'DNP': None, 'DO': None, 'DOCS': None, 'DOCTOR': None, 'DODGE': None, 'DOG': None, 'DOHA': None,
           'DOMAINS': None, 'DOT': None, 'DOWNLOAD': None, 'DRIVE': None, 'DTV': None, 'DUBAI': None, 'DUCK': None,
           'DUNLOP': None, 'DUNS': None, 'DUPONT': None, 'DURBAN': None, 'DVAG': None, 'DVR': None, 'DZ': None,
           'EARTH': None, 'EAT': None, 'EC': None, 'ECO': None, 'EDEKA': None, 'EDU': None, 'EDUCATION': None,
           'EE': None, 'EG': None, 'EMAIL': None, 'EMERCK': None, 'ENERGY': None, 'ENGINEER': None, 'ENGINEERING': None,
           'ENTERPRISES': None, 'EPOST': None, 'EPSON': None, 'EQUIPMENT': None, 'ER': None, 'ERICSSON': None,
           'ERNI': None, 'ES': None, 'ESQ': None, 'ESTATE': None, 'ESURANCE': None, 'ET': None, 'EU': None,
           'EUROVISION': None, 'EUS': None, 'EVENTS': None, 'EVERBANK': None, 'EXCHANGE': None, 'EXPERT': None,
           'EXPOSED': None, 'EXPRESS': None, 'EXTRASPACE': None, 'FAGE': None, 'FAIL': None, 'FAIRWINDS': None,
           'FAITH': None, 'FAMILY': None, 'FAN': None, 'FANS': None, 'FARM': None, 'FARMERS': None, 'FASHION': None,
           'FAST': None, 'FEDEX': None, 'FEEDBACK': None, 'FERRARI': None, 'FERRERO': None, 'FI': None, 'FIAT': None,
           'FIDELITY': None, 'FIDO': None, 'FILM': None, 'FINAL': None, 'FINANCE': None, 'FINANCIAL': None,
           'FIRE': None, 'FIRESTONE': None, 'FIRMDALE': None, 'FISH': None, 'FISHING': None, 'FIT': None,
           'FITNESS': None, 'FJ': None, 'FK': None, 'FLICKR': None, 'FLIGHTS': None, 'FLIR': None, 'FLORIST': None,
           'FLOWERS': None, 'FLY': None, 'FM': None, 'FO': None, 'FOO': None, 'FOOD': None, 'FOODNETWORK': None,
           'FOOTBALL': None, 'FORD': None, 'FOREX': None, 'FORSALE': None, 'FORUM': None, 'FOUNDATION': None,
           'FOX': None, 'FR': None, 'FREE': None, 'FRESENIUS': None, 'FRL': None, 'FROGANS': None, 'FRONTDOOR': None,
           'FRONTIER': None, 'FTR': None, 'FUJITSU': None, 'FUJIXEROX': None, 'FUN': None, 'FUND': None,
           'FURNITURE': None, 'FUTBOL': None, 'FYI': None, 'GA': None, 'GAL': None, 'GALLERY': None, 'GALLO': None,
           'GALLUP': None, 'GAME': None, 'GAMES': None, 'GAP': None, 'GARDEN': None, 'GB': None, 'GBIZ': None,
           'GD': None, 'GDN': None, 'GE': None, 'GEA': None, 'GENT': None, 'GENTING': None, 'GEORGE': None, 'GF': None,
           'GG': None, 'GGEE': None, 'GH': None, 'GI': None, 'GIFT': None, 'GIFTS': None, 'GIVES': None, 'GIVING': None,
           'GL': None, 'GLADE': None, 'GLASS': None, 'GLE': None, 'GLOBAL': None, 'GLOBO': None, 'GM': None,
           'GMAIL': None, 'GMBH': None, 'GMO': None, 'GMX': None, 'GN': None, 'GODADDY': None, 'GOLD': None,
           'GOLDPOINT': None, 'GOLF': None, 'GOO': None, 'GOODHANDS': None, 'GOODYEAR': None, 'GOOG': None,
           'GOOGLE': None, 'GOP': None, 'GOT': None, 'GOV': None, 'GP': None, 'GQ': None, 'GR': None, 'GRAINGER': None,
           'GRAPHICS': None, 'GRATIS': None, 'GREEN': None, 'GRIPE': None, 'GROUP': None, 'GS': None, 'GT': None,
           'GU': None, 'GUARDIAN': None, 'GUCCI': None, 'GUGE': None, 'GUIDE': None, 'GUITARS': None, 'GURU': None,
           'GW': None, 'GY': None, 'HAIR': None, 'HAMBURG': None, 'HANGOUT': None, 'HAUS': None, 'HBO': None,
           'HDFC': None, 'HDFCBANK': None, 'HEALTH': None, 'HEALTHCARE': None, 'HELP': None, 'HELSINKI': None,
           'HERE': None, 'HERMES': None, 'HGTV': None, 'HIPHOP': None, 'HISAMITSU': None, 'HITACHI': None, 'HIV': None,
           'HK': None, 'HKT': None, 'HM': None, 'HN': None, 'HOCKEY': None, 'HOLDINGS': None, 'HOLIDAY': None,
           'HOMEDEPOT': None, 'HOMEGOODS': None, 'HOMES': None, 'HOMESENSE': None, 'HONDA': None, 'HONEYWELL': None,
           'HORSE': None, 'HOSPITAL': None, 'HOST': None, 'HOSTING': None, 'HOT': None, 'HOTELES': None,
           'HOTMAIL': None, 'HOUSE': None, 'HOW': None, 'HR': None, 'HSBC': None, 'HT': None, 'HTC': None, 'HU': None,
           'HUGHES': None, 'HYATT': None, 'HYUNDAI': None, 'IBM': None, 'ICBC': None, 'ICE': None, 'ICU': None,
           'ID': None, 'IE': None, 'IEEE': None, 'IFM': None, 'IKANO': None, 'IL': None, 'IM': None, 'IMAMAT': None,
           'IMDB': None, 'IMMO': None, 'IMMOBILIEN': None, 'IN': None, 'INDUSTRIES': None, 'INFINITI': None,
           'INFO': None, 'ING': None, 'INK': None, 'INSTITUTE': None, 'INSURANCE': None, 'INSURE': None, 'INT': None,
           'INTEL': None, 'INTERNATIONAL': None, 'INTUIT': None, 'INVESTMENTS': None, 'IO': None, 'IPIRANGA': None,
           'IQ': None, 'IR': None, 'IRISH': None, 'IS': None, 'ISELECT': None, 'ISMAILI': None, 'IST': None,
           'ISTANBUL': None, 'IT': None, 'ITAU': None, 'ITV': None, 'IVECO': None, 'IWC': None, 'JAGUAR': None,
           'JAVA': None, 'JCB': None, 'JCP': None, 'JE': None, 'JEEP': None, 'JETZT': None, 'JEWELRY': None,
           'JIO': None, 'JLC': None, 'JLL': None, 'JM': None, 'JMP': None, 'JNJ': None, 'JO': None, 'JOBS': None,
           'JOBURG': None, 'JOT': None, 'JOY': None, 'JP': None, 'JPMORGAN': None, 'JPRS': None, 'JUEGOS': None,
           'JUNIPER': None, 'KAUFEN': None, 'KDDI': None, 'KE': None, 'KERRYHOTELS': None, 'KERRYLOGISTICS': None,
           'KERRYPROPERTIES': None, 'KFH': None, 'KG': None, 'KH': None, 'KI': None, 'KIA': None, 'KIM': None,
           'KINDER': None, 'KINDLE': None, 'KITCHEN': None, 'KIWI': None, 'KM': None, 'KN': None, 'KOELN': None,
           'KOMATSU': None, 'KOSHER': None, 'KP': None, 'KPMG': None, 'KPN': None, 'KR': None, 'KRD': None,
           'KRED': None, 'KUOKGROUP': None, 'KW': None, 'KY': None, 'KYOTO': None, 'KZ': None, 'LA': None,
           'LACAIXA': None, 'LADBROKES': None, 'LAMBORGHINI': None, 'LAMER': None, 'LANCASTER': None, 'LANCIA': None,
           'LANCOME': None, 'LAND': None, 'LANDROVER': None, 'LANXESS': None, 'LASALLE': None, 'LAT': None,
           'LATINO': None, 'LATROBE': None, 'LAW': None, 'LAWYER': None, 'LB': None, 'LC': None, 'LDS': None,
           'LEASE': None, 'LECLERC': None, 'LEFRAK': None, 'LEGAL': None, 'LEGO': None, 'LEXUS': None, 'LGBT': None,
           'LI': None, 'LIAISON': None, 'LIDL': None, 'LIFE': None, 'LIFEINSURANCE': None, 'LIFESTYLE': None,
           'LIGHTING': None, 'LIKE': None, 'LILLY': None, 'LIMITED': None, 'LIMO': None, 'LINCOLN': None, 'LINDE': None,
           'LINK': None, 'LIPSY': None, 'LIVE': None, 'LIVING': None, 'LIXIL': None, 'LK': None, 'LOAN': None,
           'LOANS': None, 'LOCKER': None, 'LOCUS': None, 'LOFT': None, 'LOL': None, 'LONDON': None, 'LOTTE': None,
           'LOTTO': None, 'LOVE': None, 'LPL': None, 'LPLFINANCIAL': None, 'LR': None, 'LS': None, 'LT': None,
           'LTD': None, 'LTDA': None, 'LU': None, 'LUNDBECK': None, 'LUPIN': None, 'LUXE': None, 'LUXURY': None,
           'LV': None, 'LY': None, 'MA': None, 'MACYS': None, 'MADRID': None, 'MAIF': None, 'MAISON': None,
           'MAKEUP': None, 'MAN': None, 'MANAGEMENT': None, 'MANGO': None, 'MARKET': None, 'MARKETING': None,
           'MARKETS': None, 'MARRIOTT': None, 'MARSHALLS': None, 'MASERATI': None, 'MATTEL': None, 'MBA': None,
           'MC': None, 'MCD': None, 'MCDONALDS': None, 'MCKINSEY': None, 'MD': None, 'ME': None, 'MED': None,
           'MEDIA': None, 'MEET': None, 'MELBOURNE': None, 'MEME': None, 'MEMORIAL': None, 'MEN': None, 'MENU': None,
           'MEO': None, 'METLIFE': None, 'MG': None, 'MH': None, 'MIAMI': None, 'MICROSOFT': None, 'MIL': None,
           'MINI': None, 'MINT': None, 'MIT': None, 'MITSUBISHI': None, 'MK': None, 'ML': None, 'MLB': None,
           'MLS': None, 'MM': None, 'MMA': None, 'MN': None, 'MO': None, 'MOBI': None, 'MOBILE': None, 'MOBILY': None,
           'MODA': None, 'MOE': None, 'MOI': None, 'MOM': None, 'MONASH': None, 'MONEY': None, 'MONSTER': None,
           'MONTBLANC': None, 'MOPAR': None, 'MORMON': None, 'MORTGAGE': None, 'MOSCOW': None, 'MOTO': None,
           'MOTORCYCLES': None, 'MOV': None, 'MOVIE': None, 'MOVISTAR': None, 'MP': None, 'MQ': None, 'MR': None,
           'MS': None, 'MSD': None, 'MT': None, 'MTN': None, 'MTPC': None, 'MTR': None, 'MU': None, 'MUSEUM': None,
           'MUTUAL': None, 'MV': None, 'MW': None, 'MX': None, 'MY': None, 'MZ': None, 'NA': None, 'NAB': None,
           'NADEX': None, 'NAGOYA': None, 'NAME': None, 'NATIONWIDE': None, 'NATURA': None, 'NAVY': None, 'NBA': None,
           'NC': None, 'NE': None, 'NEC': None, 'NET': None, 'NETBANK': None, 'NETFLIX': None, 'NETWORK': None,
           'NEUSTAR': None, 'NEW': None, 'NEWHOLLAND': None, 'NEWS': None, 'NEXT': None, 'NEXTDIRECT': None,
           'NEXUS': None, 'NF': None, 'NFL': None, 'NG': None, 'NGO': None, 'NHK': None, 'NI': None, 'NICO': None,
           'NIKE': None, 'NIKON': None, 'NINJA': None, 'NISSAN': None, 'NISSAY': None, 'NL': None, 'NO': None,
           'NOKIA': None, 'NORTHWESTERNMUTUAL': None, 'NORTON': None, 'NOW': None, 'NOWRUZ': None, 'NOWTV': None,
           'NP': None, 'NR': None, 'NRA': None, 'NRW': None, 'NTT': None, 'NU': None, 'NYC': None, 'NZ': None,
           'OBI': None, 'OBSERVER': None, 'OFF': None, 'OFFICE': None, 'OKINAWA': None, 'OLAYAN': None,
           'OLAYANGROUP': None, 'OLDNAVY': None, 'OLLO': None, 'OM': None, 'OMEGA': None, 'ONE': None, 'ONG': None,
           'ONL': None, 'ONLINE': None, 'ONYOURSIDE': None, 'OOO': None, 'OPEN': None, 'ORACLE': None, 'ORANGE': None,
           'ORG': None, 'ORGANIC': None, 'ORIENTEXPRESS': None, 'ORIGINS': None, 'OSAKA': None, 'OTSUKA': None,
           'OTT': None, 'OVH': None, 'PA': None, 'PAGE': None, 'PAMPEREDCHEF': None, 'PANASONIC': None, 'PANERAI': None,
           'PARIS': None, 'PARS': None, 'PARTNERS': None, 'PARTS': None, 'PARTY': None, 'PASSAGENS': None, 'PAY': None,
           'PCCW': None, 'PE': None, 'PET': None, 'PF': None, 'PFIZER': None, 'PG': None, 'PH': None, 'PHARMACY': None,
           'PHILIPS': None, 'PHONE': None, 'PHOTO': None, 'PHOTOGRAPHY': None, 'PHOTOS': None, 'PHYSIO': None,
           'PIAGET': None, 'PICS': None, 'PICTET': None, 'PICTURES': None, 'PID': None, 'PIN': None, 'PING': None,
           'PINK': None, 'PIONEER': None, 'PIZZA': None, 'PK': None, 'PL': None, 'PLACE': None, 'PLAY': None,
           'PLAYSTATION': None, 'PLUMBING': None, 'PLUS': None, 'PM': None, 'PN': None, 'PNC': None, 'POHL': None,
           'POKER': None, 'POLITIE': None, 'PORN': None, 'POST': None, 'PR': None, 'PRAMERICA': None, 'PRAXI': None,
           'PRESS': None, 'PRIME': None, 'PRO': None, 'PROD': None, 'PRODUCTIONS': None, 'PROF': None,
           'PROGRESSIVE': None, 'PROMO': None, 'PROPERTIES': None, 'PROPERTY': None, 'PROTECTION': None, 'PRU': None,
           'PRUDENTIAL': None, 'PS': None, 'PT': None, 'PUB': None, 'PW': None, 'PWC': None, 'PY': None, 'QA': None,
           'QPON': None, 'QUEBEC': None, 'QUEST': None, 'QVC': None, 'RACING': None, 'RADIO': None, 'RAID': None,
           'RE': None, 'READ': None, 'REALESTATE': None, 'REALTOR': None, 'REALTY': None, 'RECIPES': None, 'RED': None,
           'REDSTONE': None, 'REDUMBRELLA': None, 'REHAB': None, 'REISE': None, 'REISEN': None, 'REIT': None,
           'RELIANCE': None, 'REN': None, 'RENT': None, 'RENTALS': None, 'REPAIR': None, 'REPORT': None,
           'REPUBLICAN': None, 'REST': None, 'RESTAURANT': None, 'REVIEW': None, 'REVIEWS': None, 'REXROTH': None,
           'RICH': None, 'RICHARDLI': None, 'RICOH': None, 'RIGHTATHOME': None, 'RIL': None, 'RIO': None, 'RIP': None,
           'RMIT': None, 'RO': None, 'ROCHER': None, 'ROCKS': None, 'RODEO': None, 'ROGERS': None, 'ROOM': None,
           'RS': None, 'RSVP': None, 'RU': None, 'RUHR': None, 'RUN': None, 'RW': None, 'RWE': None, 'RYUKYU': None,
           'SA': None, 'SAARLAND': None, 'SAFE': None, 'SAFETY': None, 'SAKURA': None, 'SALE': None, 'SALON': None,
           'SAMSCLUB': None, 'SAMSUNG': None, 'SANDVIK': None, 'SANDVIKCOROMANT': None, 'SANOFI': None, 'SAP': None,
           'SAPO': None, 'SARL': None, 'SAS': None, 'SAVE': None, 'SAXO': None, 'SB': None, 'SBI': None, 'SBS': None,
           'SC': None, 'SCA': None, 'SCB': None, 'SCHAEFFLER': None, 'SCHMIDT': None, 'SCHOLARSHIPS': None,
           'SCHOOL': None, 'SCHULE': None, 'SCHWARZ': None, 'SCIENCE': None, 'SCJOHNSON': None, 'SCOR': None,
           'SCOT': None, 'SD': None, 'SE': None, 'SEAT': None, 'SECURE': None, 'SECURITY': None, 'SEEK': None,
           'SELECT': None, 'SENER': None, 'SERVICES': None, 'SES': None, 'SEVEN': None, 'SEW': None, 'SEX': None,
           'SEXY': None, 'SFR': None, 'SG': None, 'SH': None, 'SHANGRILA': None, 'SHARP': None, 'SHAW': None,
           'SHELL': None, 'SHIA': None, 'SHIKSHA': None, 'SHOES': None, 'SHOP': None, 'SHOPPING': None, 'SHOUJI': None,
           'SHOW': None, 'SHOWTIME': None, 'SHRIRAM': None, 'SI': None, 'SILK': None, 'SINA': None, 'SINGLES': None,
           'SITE': None, 'SJ': None, 'SK': None, 'SKI': None, 'SKIN': None, 'SKY': None, 'SKYPE': None, 'SL': None,
           'SLING': None, 'SM': None, 'SMART': None, 'SMILE': None, 'SN': None, 'SNCF': None, 'SO': None,
           'SOCCER': None, 'SOCIAL': None, 'SOFTBANK': None, 'SOFTWARE': None, 'SOHU': None, 'SOLAR': None,
           'SOLUTIONS': None, 'SONG': None, 'SONY': None, 'SOY': None, 'SPACE': None, 'SPIEGEL': None, 'SPOT': None,
           'SPREADBETTING': None, 'SR': None, 'SRL': None, 'SRT': None, 'ST': None, 'STADA': None, 'STAPLES': None,
           'STAR': None, 'STARHUB': None, 'STATEBANK': None, 'STATEFARM': None, 'STATOIL': None, 'STC': None,
           'STCGROUP': None, 'STOCKHOLM': None, 'STORAGE': None, 'STORE': None, 'STREAM': None, 'STUDIO': None,
           'STUDY': None, 'STYLE': None, 'SU': None, 'SUCKS': None, 'SUPPLIES': None, 'SUPPLY': None, 'SUPPORT': None,
           'SURF': None, 'SURGERY': None, 'SUZUKI': None, 'SV': None, 'SWATCH': None, 'SWIFTCOVER': None, 'SWISS': None,
           'SX': None, 'SY': None, 'SYDNEY': None, 'SYMANTEC': None, 'SYSTEMS': None, 'SZ': None, 'TAB': None,
           'TAIPEI': None, 'TALK': None, 'TAOBAO': None, 'TARGET': None, 'TATAMOTORS': None, 'TATAR': None,
           'TATTOO': None, 'TAX': None, 'TAXI': None, 'TC': None, 'TCI': None, 'TD': None, 'TDK': None, 'TEAM': None,
           'TECH': None, 'TECHNOLOGY': None, 'TEL': None, 'TELECITY': None, 'TELEFONICA': None, 'TEMASEK': None,
           'TENNIS': None, 'TEVA': None, 'TF': None, 'TG': None, 'TH': None, 'THD': None, 'THEATER': None,
           'THEATRE': None, 'TIAA': None, 'TICKETS': None, 'TIENDA': None, 'TIFFANY': None, 'TIPS': None, 'TIRES': None,
           'TIROL': None, 'TJ': None, 'TJMAXX': None, 'TJX': None, 'TK': None, 'TKMAXX': None, 'TL': None, 'TM': None,
           'TMALL': None, 'TN': None, 'TO': None, 'TODAY': None, 'TOKYO': None, 'TOOLS': None, 'TOP': None,
           'TORAY': None, 'TOSHIBA': None, 'TOTAL': None, 'TOURS': None, 'TOWN': None, 'TOYOTA': None, 'TOYS': None,
           'TR': None, 'TRADE': None, 'TRADING': None, 'TRAINING': None, 'TRAVEL': None, 'TRAVELCHANNEL': None,
           'TRAVELERS': None, 'TRAVELERSINSURANCE': None, 'TRUST': None, 'TRV': None, 'TT': None, 'TUBE': None,
           'TUI': None, 'TUNES': None, 'TUSHU': None, 'TV': None, 'TVS': None, 'TW': None, 'TZ': None, 'UA': None,
           'UBANK': None, 'UBS': None, 'UCONNECT': None, 'UG': None, 'UK': None, 'UNICOM': None, 'UNIVERSITY': None,
           'UNO': None, 'UOL': None, 'UPS': None, 'US': None, 'UY': None, 'UZ': None, 'VA': None, 'VACATIONS': None,
           'VANA': None, 'VANGUARD': None, 'VC': None, 'VE': None, 'VEGAS': None, 'VENTURES': None, 'VERISIGN': None,
           'VERSICHERUNG': None, 'VET': None, 'VG': None, 'VI': None, 'VIAJES': None, 'VIDEO': None, 'VIG': None,
           'VIKING': None, 'VILLAS': None, 'VIN': None, 'VIP': None, 'VIRGIN': None, 'VISA': None, 'VISION': None,
           'VISTA': None, 'VISTAPRINT': None, 'VIVA': None, 'VIVO': None, 'VLAANDEREN': None, 'VN': None, 'VODKA': None,
           'VOLKSWAGEN': None, 'VOLVO': None, 'VOTE': None, 'VOTING': None, 'VOTO': None, 'VOYAGE': None, 'VU': None,
           'VUELOS': None, 'WALES': None, 'WALMART': None, 'WALTER': None, 'WANG': None, 'WANGGOU': None,
           'WARMAN': None, 'WATCH': None, 'WATCHES': None, 'WEATHER': None, 'WEATHERCHANNEL': None, 'WEBCAM': None,
           'WEBER': None, 'WEBSITE': None, 'WED': None, 'WEDDING': None, 'WEIBO': None, 'WEIR': None, 'WF': None,
           'WHOSWHO': None, 'WIEN': None, 'WIKI': None, 'WILLIAMHILL': None, 'WIN': None, 'WINDOWS': None, 'WINE': None,
           'WINNERS': None, 'WME': None, 'WOLTERSKLUWER': None, 'WOODSIDE': None, 'WORK': None, 'WORKS': None,
           'WORLD': None, 'WOW': None, 'WS': None, 'WTC': None, 'WTF': None, 'XBOX': None, 'XEROX': None,
           'XFINITY': None, 'XIHUAN': None, 'XIN': None, 'XN--11B4C3D': None, 'XN--1CK2E1B': None, 'XN--1QQW23A': None,
           'XN--30RR7Y': None, 'XN--3BST00M': None, 'XN--3DS443G': None, 'XN--3E0B707E': None,
           'XN--3OQ18VL8PN36A': None, 'XN--3PXU8K': None, 'XN--42C2D9A': None, 'XN--45BRJ9C': None, 'XN--45Q11C': None,
           'XN--4GBRIM': None, 'XN--54B7FTA0CC': None, 'XN--55QW42G': None, 'XN--55QX5D': None,
           'XN--5SU34J936BGSG': None, 'XN--5TZM5G': None, 'XN--6FRZ82G': None, 'XN--6QQ986B3XL': None,
           'XN--80ADXHKS': None, 'XN--80AO21A': None, 'XN--80AQECDR1A': None, 'XN--80ASEHDB': None, 'XN--80ASWG': None,
           'XN--8Y0A063A': None, 'XN--90A3AC': None, 'XN--90AE': None, 'XN--90AIS': None, 'XN--9DBQ2A': None,
           'XN--9ET52U': None, 'XN--9KRT00A': None, 'XN--B4W605FERD': None, 'XN--BCK1B9A5DRE4C': None,
           'XN--C1AVG': None, 'XN--C2BR7G': None, 'XN--CCK2B3B': None, 'XN--CG4BKI': None,
           'XN--CLCHC0EA0B2G2A9GCD': None, 'XN--CZR694B': None, 'XN--CZRS0T': None, 'XN--CZRU2D': None,
           'XN--D1ACJ3B': None, 'XN--D1ALF': None, 'XN--E1A4C': None, 'XN--ECKVDTC9D': None, 'XN--EFVY88H': None,
           'XN--ESTV75G': None, 'XN--FCT429K': None, 'XN--FHBEI': None, 'XN--FIQ228C5HS': None, 'XN--FIQ64B': None,
           'XN--FIQS8S': None, 'XN--FIQZ9S': None, 'XN--FJQ720A': None, 'XN--FLW351E': None, 'XN--FPCRJ9C3D': None,
           'XN--FZC2C9E2C': None, 'XN--FZYS8D69UVGM': None, 'XN--G2XX48C': None, 'XN--GCKR3F0F': None,
           'XN--GECRJ9C': None, 'XN--GK3AT1E': None, 'XN--H2BRJ9C': None, 'XN--HXT814E': None, 'XN--I1B6B1A6A2E': None,
           'XN--IMR513N': None, 'XN--IO0A7I': None, 'XN--J1AEF': None, 'XN--J1AMH': None, 'XN--J6W193G': None,
           'XN--JLQ61U9W7B': None, 'XN--JVR189M': None, 'XN--KCRX77D1X4A': None, 'XN--KPRW13D': None,
           'XN--KPRY57D': None, 'XN--KPU716F': None, 'XN--KPUT3I': None, 'XN--L1ACC': None, 'XN--LGBBAT1AD8J': None,
           'XN--MGB9AWBF': None, 'XN--MGBA3A3EJT': None, 'XN--MGBA3A4F16A': None, 'XN--MGBA7C0BBN0A': None,
           'XN--MGBAAM7A8H': None, 'XN--MGBAB2BD': None, 'XN--MGBAI9AZGQP6J': None, 'XN--MGBAYH7GPA': None,
           'XN--MGBB9FBPOB': None, 'XN--MGBBH1A71E': None, 'XN--MGBC0A9AZCG': None, 'XN--MGBCA7DZDO': None,
           'XN--MGBERP4A5D4AR': None, 'XN--MGBI4ECEXP': None, 'XN--MGBPL2FH': None, 'XN--MGBT3DHD': None,
           'XN--MGBTX2B': None, 'XN--MGBX4CD0AB': None, 'XN--MIX891F': None, 'XN--MK1BU44C': None, 'XN--MXTQ1M': None,
           'XN--NGBC5AZD': None, 'XN--NGBE9E0A': None, 'XN--NODE': None, 'XN--NQV7F': None, 'XN--NQV7FS00EMA': None,
           'XN--NYQY26A': None, 'XN--O3CW4H': None, 'XN--OGBPF8FL': None, 'XN--P1ACF': None, 'XN--P1AI': None,
           'XN--PBT977C': None, 'XN--PGBS0DH': None, 'XN--PSSY2U': None, 'XN--Q9JYB4C': None, 'XN--QCKA1PMC': None,
           'XN--QXAM': None, 'XN--RHQV96G': None, 'XN--ROVU88B': None, 'XN--S9BRJ9C': None, 'XN--SES554G': None,
           'XN--T60B56A': None, 'XN--TCKWE': None, 'XN--TIQ49XQYJ': None, 'XN--UNUP4Y': None,
           'XN--VERMGENSBERATER-CTB': None, 'XN--VERMGENSBERATUNG-PWB': None, 'XN--VHQUV': None, 'XN--VUQ861B': None,
           'XN--W4R85EL8FHU5DNRA': None, 'XN--W4RS40L': None, 'XN--WGBH1C': None, 'XN--WGBL6A': None,
           'XN--XHQ521B': None, 'XN--XKC2AL3HYE2A': None, 'XN--XKC2DL3A5EE0H': None, 'XN--Y9A3AQ': None,
           'XN--YFRO4I67O': None, 'XN--YGBI2AMMX': None, 'XN--ZFR164B': None, 'XPERIA': None, 'XXX': None, 'XYZ': None,
           'YACHTS': None, 'YAHOO': None, 'YAMAXUN': None, 'YANDEX': None, 'YE': None, 'YODOBASHI': None, 'YOGA': None,
           'YOKOHAMA': None, 'YOU': None, 'YOUTUBE': None, 'YT': None, 'YUN': None, 'ZA': None, 'ZAPPOS': None,
           'ZARA': None, 'ZERO': None, 'ZIP': None, 'ZIPPO': None, 'ZM': None, 'ZONE': None, 'ZUERICH': None,
           'ZW': None}


class DNSTimeoutError(Exception):
    def __init__(self, orig_error):
        self.orig_error = orig_error

    def __str__(self):
        return str(self.orig_error)


class DNSCommError(Exception):
    def __init__(self, orig_error):
        self.orig_error = orig_error

    def __str__(self):
        return str(self.orig_error)


"""
*****************************************************************'
Parsing Summary:
*****************************************************************'

    MUST: 
        full domain name <= 255 chars
        any one label between 1 - 63 octets

    hostname:
        any chars

    
        
    Escaping Unusual DNS Label Octets  (warning)
        used for 0x00 - 0x20 and 0x7F - 0xFF

        \\ == \
        \. == .
        \0 == \0
        \00 == \00
        \000 = char(00)
        \010 = char(10)
        \123 = char(123)
        \0924 = .4

   
    email spec:

        <domain> ::= <subdomain> | " "
        
        <subdomain> ::= <label> | <subdomain> "." <label>
        
        <label> ::= <letter> [ [ <ldh-str> ] <let-dig> ]
        
        <ldh-str> ::= <let-dig-hyp> | <let-dig-hyp> <ldh-str>
        
        <let-dig-hyp> ::= <let-dig> | "-"
        
        <let-dig> ::= <letter> | <digit>
        
        <letter> ::= any one of the 52 alphabetic characters A through Z in
        upper case and a through z in lower case
        
        <digit> ::= any one of the ten digits 0 through 9


Module Options
- Lookup options = 
    - check for valid domain syntax (no lookup)
    - check for lookup-able domain
    - check for valid mx rec
    - add host's default domain if not specified
    - add xxx default domain if not specified
    - check tld list before adding default domain.

- options:
    - check with email limits
    - validate ip addresses (email standard)
    - validate ip addresses (non-email standard)
    - use loose rules (any chars)
    - allow escaped chars
- 


"""

# **********************************************************************************
# <editor-fold desc="  Domain Messages  ">
# **********************************************************************************


RFC1035_TEXT = textwrap.dedent("""\
    2.3.1. Preferred name syntax

        The DNS specifications attempt to be as general as possible in the rules
        for constructing domain names.  The idea is that the name of any
        existing object can be expressed as a domain name with minimal changes.

        However, when assigning a domain name for an object, the prudent user
        will select a name which satisfies both the rules of the domain system
        and any existing rules for the object, whether these rules are published
        or implied by existing programs.

        For example, when naming a mail domain, the user should satisfy both the
        rules of this memo and those in RFC-822.  When creating a new host name,
        the old rules for HOSTS.TXT should be followed.  This avoids problems
        when old software is converted to use domain names.

        The following syntax will result in fewer problems with many

        applications that use domain names (e.g., mail, TELNET).

        <domain> ::= <subdomain> | " "

        <subdomain> ::= <label> | <subdomain> "." <label>

        <label> ::= <letter> [ [ <ldh-str> ] <let-dig> ]

        <ldh-str> ::= <let-dig-hyp> | <let-dig-hyp> <ldh-str>

        <let-dig-hyp> ::= <let-dig> | "-"

        <let-dig> ::= <letter> | <digit>

        <letter> ::= any one of the 52 alphabetic characters A through Z in
        upper case and a through z in lower case

        <digit> ::= any one of the ten digits 0 through 9

        Note that while upper and lower case letters are allowed in domain
        names, no significance is attached to the case.  That is, two names with
        the same spelling but different case are to be treated as if identical.

        The labels must follow the rules for ARPANET host names.  They must
        start with a letter, end with a letter or digit, and have as interior
        characters only letters, digits, and hyphen.  There are also some
        restrictions on the length.  Labels must be 63 characters or less.

        For example, the following strings identify hosts in the Internet:

        A.ISI.EDU XX.LCS.MIT.EDU SRI-NIC.ARPA
        """)

RFC4343_TEXT = textwrap.dedent("""\
    2.1.  Escaping Unusual DNS Label Octets

       In Master Files [STD13] and other human-readable and -writable ASCII
       contexts, an escape is needed for the byte value for period (0x2E,
       ".") and all octet values outside of the inclusive range from 0x21
       ("!") to 0x7E ("~").  That is to say, 0x2E and all octet values in
       the two inclusive ranges from 0x00 to 0x20 and from 0x7F to 0xFF.

       One typographic convention for octets that do not correspond to an
       ASCII printing graphic is to use a back-slash followed by the value
       of the octet as an unsigned integer represented by exactly three
       decimal digits.

       The same convention can be used for printing ASCII characters so that
       they will be treated as a normal label character.  This includes the
       back-slash character used in this convention itself, which can be
       expressed as \092 or \\, and the special label separator period
       ("."), which can be expressed as and \046 or \.  It is advisable to
       avoid using a backslash to quote an immediately following non-
       printing ASCII character code to avoid implementation difficulties.

       A back-slash followed by only one or two decimal digits is undefined.
       A back-slash followed by four decimal digits produces two octets, the
       first octet having the value of the first three digits considered as
       a decimal number, and the second octet being the character code for
       the fourth decimal digit.

    2.2.  Example Labels with Escapes

       The first example below shows embedded spaces and a period (".")
       within a label.  The second one shows a 5-octet label where the
       second octet has all bits zero, the third is a backslash, and the
       fourth octet has all bits one.

             Donald\032E\.\032Eastlake\0323rd.example.
       and   a\000\\\255z.example.


    3 .2.  Extended Label Type Case Insensitivity Considerations

       DNS wasextended by [RFC2671] so that additional label type numbers
       would be available.  (The only such type defined so far is the BINARY
       type [RFC2673], which is now Experimental [RFC3363].)

       The ASCII case insensitivity conventions only apply to ASCII labels;
       that is to say, label type 0x0, whether appearing directly or invoked
       by indirect labels.

    """)

RFC2181_TEXT = textwrap.dedent("""\
    11. Name syntax

       Occasionally it is assumed that the Domain Name System serves only
       the purpose of mapping Internet host names to data, and mapping
       Internet addresses to host names.  This is not correct, the DNS is a
       general (if somewhat limited) hierarchical database, and can store
       almost any kind of data, for almost any purpose.

       The DNS itself places only one restriction on the particular labels
       that can be used to identify resource records.  That one restriction
       relates to the length of the label and the full name.  The length of
       any one label is limited to between 1 and 63 octets.  A full domain
       name is limited to 255 octets (including the separators).  The zero
       length full name is defined as representing the root of the DNS tree,
       and is typically written and displayed as ".".  Those restrictions
       aside, any binary string whatever can be used as the label of any
       resource record.  Similarly, any binary string can serve as the value
       of any record that includes a domain name as some or all of its value
       (SOA, NS, MX, PTR, CNAME, and any others that may be added).
       Implementations of the DNS protocols must not place any restrictions
       on the labels that can be used.  In particular, DNS servers must not
       refuse to serve a zone because it contains labels that might not be
       acceptable to some DNS client programs.  A DNS server may be
       configurable to issue warnings when loading, or even to refuse to
       load, a primary zone containing labels that might be considered
       questionable, however this should not happen by default.

       Note however, that the various applications that make use of DNS data
       can have restrictions imposed on what particular values are
       acceptable in their environment.  For example, that any binary label
       can have an MX record does not imply that any binary name can be used
       as the host part of an e-mail address.  Clients of the DNS can impose
       whatever restrictions are appropriate to their circumstances on the
       values they use as keys for DNS lookup requests, and on the values
       returned by the DNS.  If the client has such restrictions, it is
       solely responsible for validating the data from the DNS to ensure
       that it conforms before it makes any use of that data.

       See also [RFC1123] section 6.1.3.5.""")

RFC1123_TEXT = textwrap.dedent("""\
       2.  GENERAL ISSUES

       This section contains general requirements that may be applicable to
       all application-layer protocols.

       2.1  Host Names and Numbers

          The syntax of a legal Internet host name was specified in RFC-952
          [DNS:4].  One aspect of host name syntax is hereby changed: the
          restriction on the first character is relaxed to allow either a
          letter or a digit.  Host software MUST support this more liberal
          syntax.

          Host software MUST handle host names of up to 63 characters and
          SHOULD handle host names of up to 255 characters.

          Whenever a user inputs the identity of an Internet host, it SHOULD
          be possible to enter either (1) a host domain name or (2) an IP
          address in dotted-decimal ("#.#.#.#") form.  The host SHOULD check
          the string syntactically for a dotted-decimal number before
          looking it up in the Domain Name System.

          DISCUSSION:
               This last requirement is not intended to specify the complete
               syntactic form for entering a dotted-decimal host number;
               that is considered to be a user-interface issue.  For
               example, a dotted-decimal number must be enclosed within
               "[ ]" brackets for SMTP mail (see Section 5.2.17).  This
               notation could be made universal within a host system,
               simplifying the syntactic checking for a dotted-decimal
               number.

               If a dotted-decimal number can be entered without such
               identifying delimiters, then a full syntactic check must be
               made, because a segment of a host domain name is now allowed
               to begin with a digit and could legally be entirely numeric
               (see Section 6.1.2.4).  However, a valid host name can never
               have the dotted-decimal form #.#.#.#, since at least the
               highest-level component label will be alphabetic.    
    """)

# TWO_DIGIT = '12'
# ADDR_CHAR_IPV4 = '0123456789.'
# ADDR_CHAR_IPV6 = make_char_str(HEXDIG, COLON)
# ADDR_CHAR_IPV64 = make_char_str(HEXDIG, ADDR_CHAR_IPV4, COLON)




DOMAIN_REFERENCES = [
    {'name': 'RFC1035',
     'description': 'Preferred name syntax for smtp',
     'url': '[RFC1035]',
     'text': RFC1035_TEXT},

    {'name': 'RFC4343',
     'description': 'Escaping un-usual lables',
     'url': '[RFC4343]',
     'text': RFC4343_TEXT},

    {'name': 'RFC2181',
     'description': 'DNS Name syntax errata',
     'url': '[RFC2181]',
     'text': RFC2181_TEXT},

    {'name': 'RFC1123',
     'description': 'Names and IP addresses',
     'url': '[RFC1123]',
     'text': RFC1123_TEXT},
]


DOMAIN_MESSAGES = [
    # DOMAIN ERRORS
    {'key': 'domain.DOMAIN_TOO_LONG',
     'description': 'Domain is longer than 255 chars',
     'status': STATUS_CODES.ERROR,
     'references': ['RFC2181']},
    {'key': 'domain.DOMAIN_NO_MX_REC_FOUND',
     'description': 'Lookup failed on mx record for domain',
     'status': STATUS_CODES.ERROR,
     'references': []},
    {'key': 'domain.DOMAIN_NO_DNS_REC_FOUND',
     'description': 'Lookup failed for A record.',
     'status': STATUS_CODES.ERROR,
     'references': []},
    {'key': 'domain.DOMAIN_DOUBLE_DOT_FOUND',
     'description': 'Labels must have at least one char.',
     'status': STATUS_CODES.ERROR,
     'references': []},

    # DOMAIN WARNINGS
    {'key': 'domain.DOMAIN_UNKNOWN_TLD',
     'description': 'Domain tld is not in TLD lookup list.',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC1123']},
    {'key': 'domain.DOMAIN_ENDS_WITH_DOT',
     'description': 'Domain ends with dot, some apps may not work with this.',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC1123']},
    {'key': 'domain.DOMAIN_IS_IP_ADDR',
     'description': 'Domain is a valid IP address',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC1123']},
    {'key': 'domain.DOMAIN_ONLY_TLD_WARN',
     'description': 'Domain only contains a TLD (this may be a problem for email)',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC1123']},
    {'key': 'domain.DOMAIN_DNS_COMM_ERROR',
     'description': 'Received a comm error when trying to lookup record',
     'status': STATUS_CODES.WARNING,
     'references': []},

    # LABEL ERRORS
    {'key': 'label.DOMAIN_LABEL_TOO_LONG',
     'description': 'Label is longer than 63 chars',
     'status': STATUS_CODES.ERROR,
     'references': ['RFC2181']},
    {'key': 'label.DOMAIN_LABEL_INVALID_CHAR_FOR_EMAIL',
     'description': 'Label uses characters invalid for email use',
     'status': STATUS_CODES.ERROR,
     'references': ['RFC1035']},
    {'key': 'label.DOMAIN_LABEL_USES_NON_ASCII_CHARS_ERR',
     'description': 'Label uses non-ascii chars - may not be compatible with applications',
     'status': STATUS_CODES.ERROR,
     'references': ['RFC2181', 'RFC1035']},

    # LABEL WARNINGS
    {'key': 'label.DOMAIN_LABEL_USES_ESCAPED_CHARS',
     'description': 'Label uses escaped chars - may not be compatible with applications',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC4343']},
    {'key': 'label.DOMAIN_LABEL_USES_NON_ASCII_CHARS_WARN',
     'description': 'Label uses non-ascii chars - may not be compatible with applications',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC2181', 'RFC1035']},
    {'key': 'label.DOMAIN_LABEL_USES_NON_ALPHA_NUM_HY_CHARS',
     'description': '',
     'status': STATUS_CODES.WARNING,
     'references': ['RFC2181', 'RFC1123']},
    {'key': 'label.DOMAIN_LABEL_USES_MIXED_CASE',
     'description': 'Domain uses mixed case chars - dns does not care, but may cause application problems',
     'status': STATUS_CODES.WARNING,
     'references': []},
]


# **********************************************************************************
# </editor-fold>
# **********************************************************************************


# **********************************************************************************
# <editor-fold desc="  Parse Objects  ">
# **********************************************************************************


class DNSLabel(BaseParser):
    name = 'dns_label'

    def _parse(self, tmp_ret, parse_obj, position, use_email_ip_rules=False, ascii_only=False, **kwargs):
        if tmp_ret.l > 63:
            raise WrapperStop(self, tmp_ret('DOMAIN_LABEL_TOO_LONG'))
        tmp_domain_str = str(tmp_ret)
        if not tmp_domain_str.isupper() and not tmp_domain_str.islower():
            tmp_ret('DOMAIN_LABEL_USES_MIXED_CASE')
        try:
            tmp_ascii = tmp_domain_str.encode('ascii')
        except UnicodeError:
            if use_email_ip_rules:
                tmp_ret('DOMAIN_LABEL_INVALID_CHAR_FOR_EMAIL')
            elif ascii_only:
                tmp_ret('DOMAIN_LABEL_USES_NON_ASCII_CHARS_ERR')
            else:
                tmp_ret('DOMAIN_LABEL_USES_NON_ASCII_CHARS_WARN')
        else:
            if not tmp_domain_str.isalnum() and '-' not in tmp_domain_str:
                if use_email_ip_rules:
                    tmp_ret('DOMAIN_LABEL_INVALID_CHAR_FOR_EMAIL')
                else:
                    tmp_ret('DOMAIN_LABEL_USES_NON_ALPHA_NUM_HY_CHARS')

        if '\\' in tmp_domain_str:
            if use_email_ip_rules:
                tmp_ret('DOMAIN_LABEL_INVALID_CHAR_FOR_EMAIL')
            else:
                tmp_split_dom = tmp_domain_str.split('\\')
                did_first = False
                for item in tmp_split_dom:
                    if not did_first:
                        did_first = True
                    else:
                        if len(item) >= 3:
                            if item[:3].isnumeric():
                                tmp_ret('DOMAIN_LABEL_USES_ESCAPED_CHARS')
                                break


dns_label = DNSLabel()


class DNSDomain(BaseParser):
    name = 'dns_domain'
    messages = DOMAIN_MESSAGES
    references = DOMAIN_REFERENCES

    lookup_in_dns = True
    check_tld_list = True
    tld_list = None
    check_for_ip = True
    use_email_ip_rules = False
    lookup_mx_rec_if_email = True
    ascii_only = False


    """
    Module Options
    - Lookup options = 
        - check for valid domain syntax (no lookup)
        - check for lookup-able domain
        - check for valid mx rec
        - add host's default domain if not specified
        - add xxx default domain if not specified
        - check tld list before adding default domain.
    
    - options:
        - check with email limits
        - validate ip addresses (email standard)
        - validate ip addresses (non-email standard)
        - use loose rules (any chars)
        - allow escaped chars
    - 

    """

    def _parse(self, tmp_ret, parse_obj, position, **kwargs):

        tmp_email = None

        if self.use_email_ip_rules:
            if parse_obj[position].isnumeric():
                tmp_email = validate_ipv4_addr(parse_obj, position)
            elif parse_obj[position] == '[' and parse_obj[-1] == ']':
                with parse_obj(-1):
                    tmp_email = validate_ipv6_addr(parse_obj, position+1)
        else:
            if parse_obj[position].isnumeric():
                tmp_email = validate_ip_addr(parse_obj, position)

        if tmp_email:
            tmp_ret(tmp_email('DOMAIN_IS_IP_ADDR'))
            return

        tmp_labels = str(tmp_ret).split('.')
        label_count = len(tmp_labels)
        tld = None
        text_label_count = 0
        for cur_count, label in enumerate(tmp_labels, start=1):
            if label == '':
                tmp_ret += dot(parse_obj, position + tmp_ret)
                if label_count == cur_count:
                    tmp_ret('DOMAIN_ENDS_WITH_DOT')
                else:
                    tmp_ret('DOMAIN_DOUBLE_DOT_FOUND')
                    raise WrapperStop(self, tmp_ret)
            else:
                with parse_obj(tmp_ret + position + len(label)):
                    tmp_label = dns_label(parse_obj,
                                          position + tmp_ret,
                                          use_email_ip_rules=False,
                                          ascii_only=False)
                tmp_ret(tmp_label)
                if not tmp_label:
                    raise WrapperStop(self, tmp_ret)
                tld = label
                text_label_count += 1
                if label_count != cur_count:
                    tmp_ret += dot(parse_obj, position + tmp_ret)

        if text_label_count == 1 and self.use_email_ip_rules:
            tmp_ret('DOMAIN_ONLY_TLD_WARN')

        if len(tmp_ret) > 255:
            tmp_ret('DOMAIN_TOO_LONG')
            raise WrapperStop(self, tmp_ret)

        tld_list = DNS_TLD
        if tld.upper() not in tld_list:
            tmp_ret('DOMAIN_UNKNOWN_TLD')

        tmp_error = self.dns_lookup(str(tmp_ret))

        if tmp_error:
            tmp_ret(tmp_error)

    def dns_lookup(self,
                   domain_name,
                   servers=None,
                   timeout=None,
                   raise_on_comm_error=True,
                   force_sockets=False):

        dns_python_resolver = None

        if force_sockets:
            if not USE_SOCKETS:
                import socket
            use_sockets = True
        else:
            use_sockets = USE_SOCKETS

        if use_sockets:
            if self.use_email_ip_rules and self.lookup_mx_rec_if_email:
                raise ImportError('DNS Python (http://www.dnspython.org/) not available, MX lookups not available')
            if servers is not None:
                raise AttributeError('Servers cannot be set when using the socket library')
            if timeout is not None:
                socket.settimeout(timeout)
        else:
            if servers is not None or timeout is not None:
                dns_python_resolver = resolver.Resolver()
                if servers is not None:
                    if isinstance(servers, str):
                        servers = [servers]
                        dns_python_resolver.nameservers = servers
                if timeout is not None:
                    dns_python_resolver.lifetime = float(timeout)
            else:
                dns_python_resolver = resolver

        if self.use_email_ip_rules and self.lookup_mx_rec_if_email:
            if not use_sockets:
                try:
                    answers = dns_python_resolver.query(domain_name, 'MX')
                    return ''
                except resolver.NXDOMAIN:
                    return 'DOMAIN_NO_DNS_REC_FOUND'
                except resolver.NoAnswer:
                    pass
                except resolver.Timeout as err:
                    if raise_on_comm_error:
                        raise DNSTimeoutError(err)
                    else:
                        return 'DOMAIN_DNS_COMM_ERROR'
                except dns_except.DNSException as err:
                    if raise_on_comm_error:
                        raise DNSCommError(err)
                    else:
                        return 'DOMAIN_DNS_COMM_ERROR'
            else:
                raise ImportError('DNS Python (http://www.dnspython.org/) not available, MX lookups not available')

        if not use_sockets:
            try:
                answers = dns_python_resolver.query(domain_name)
            except resolver.NXDOMAIN:
                return 'DNSWARN_NO_RECORD'
            except resolver.Timeout as err:
                if raise_on_comm_error:
                    raise DNSTimeoutError(err)
                else:
                    return 'DOMAIN_DNS_COMM_ERROR'
            except dns_except.DNSException as err:
                if raise_on_comm_error:
                    raise DNSCommError(err)
                else:
                    return 'DOMAIN_DNS_COMM_ERROR'
            if self.use_email_ip_rules and self.lookup_mx_rec_if_email:
                return 'DOMAIN_NO_DNS_REC_FOUND'
            else:
                return ''
        else:
            try:
                answer = socket.getaddrinfo(domain_name, 80)
            except socket.gaierror:
                return 'DNSWARN_NO_RECORD'
            except socket.timeout as err:
                if raise_on_comm_error:
                    raise DNSTimeoutError(err)
                else:
                    return 'DOMAIN_DNS_COMM_ERROR'
            except socket.error as err:
                if raise_on_comm_error:
                    raise DNSTimeoutError(err)
                else:
                    return 'DOMAIN_DNS_COMM_ERROR'

            return ''


# **********************************************************************************
# </editor-fold>
# **********************************************************************************
