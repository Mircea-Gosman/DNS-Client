def validate_server(server):
    server = server.replace("@", "")
    fields = server.split(".")
    error = len(fields) != 4

    for field in fields:
        if not field.isdigit() or int(field) < 0:
            error = True
            break

    if error: 
        print("ERROR:\tThe server should be of format: X.X.X.X where X is an integer.")
        exit(3)

    return server


def validate_domain(domain):
    fields = domain.split(".")
    
    if not (len(fields) == 2 or len(fields) == 3):
        print("ERROR:\tThe domain name should be of format: www.myDomain.com")
        exit(4)

    return "www." + domain if "www" not in domain else domain


def validate_integer(switch, value):
    if not value.isdigit() or int(value) < 0:
        print(f"ERROR:\tThe switch {switch} needs to be a positive integer. Received {value} instead.")
        exit(2)

    return int(value)

def parse_resource(response, header):
    bytes = oct(int(response, 16)).lstrip("0o")
    auth = "auth" if header["AA"] == 1 else "nonauth"
    res_start = 43 # need to count query field size, tbd, should be byte#
    labels = {}
    records = {"Answer": [], "Additional": []}

    # Extract each Record
    for i in range(header["ANCOUNT"] + header["NSCOUNT"] + header["ARCOUNT"]):    
        if i >=  header["ANCOUNT"]  and i < header["ANCOUNT"] + header["NSCOUNT"]:
            continue

        record_store = "Answer" if i < header["ANCOUNT"] else "Additional"

        # Name
        NAME, end = parse_domain_name(labels, bytes, res_start)

        TYPE     = bytes[end, end + 16]
        CLASS    = bytes[end + 16, end + 32]
        TTL      = bytes[end + 32, end + 64]
        RDLENGTH = bytes[end + 64, end + 80]
        RDATA    = bytes[end + 80, end + 80 + RDLENGTH]

        if hex(TYPE) == 0x0001:
            IP = RDATA
            records[record_store] = f"IP \t {ocstr(IP)} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x0002:
            QNAME, _ = parse_domain_name(labels, bytes, end + 80) 
            records[record_store] = f"NS \t {ocstr(QNAME)} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x005:
            records[record_store] = f"CNAME \t {ocstr(RDATA)} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x00f:
            PREFERENCE = RDATA[:16]
            EXCHANGE, _ = parse_domain_name(labels, bytes, end + 96) 
            records[record_store] = f"MX \t {ocstr(EXCHANGE)}\t {ocstr(PREFERENCE)} \t {ocstr(TTL)} \t {auth}"

    print_records(records)


def parse_domain_name(labels, resource, start):
    #memoization [...] - WiP
    name = ""
    i = start

    while True:
        
        return

    return name, i + 1

def ocstr(octal):
    return ''.join([chr[c] for c in octal])

def print_records(records):
    for category in records:
        if len(records[category]) != 0:
            print(f"{category} Section ({len(records[category])} records)")

        for record in records[category]:
            print(f"{record}")

    if len(records["Answer"]) != 0 and len(records["Additional"]) != 0:
        print("NOTFOUND")