from dns import resolver, reversename

# DNS TLD's from:
# http://data.iana.org/TLD/tlds-alpha-by-domain.txt

def has_mx_rec(host_name):
    print('MX------------------------')
    try:
        answers = resolver.query(host_name, 'MX')
        for rdata in answers:
            print('Host', rdata.exchange, 'has preference', rdata.preference)
    except resolver.NXDOMAIN:
        print('no dns entry')


def has_mx_from_ip(ip_addr):
    n = reversename.from_address(ip_addr)

    print('IP------------------------')
    print(n)
    print(reversename.to_address(n))
    if n:
        print('has answers')
    else:
        print('no_answers')



def has_dns_entry(host_name):
    print('DNS------------------------')
    try:
        answers = resolver.query(host_name)
        for rdata in answers:
            print('Address', rdata.address)
    except resolver.NXDOMAIN:
        print('no domain')

