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

def parse_resource(response, header, labels, res_start):
    auth = "auth" if header["AA"] == 1 else "nonauth"
    records = {"Answer": [], "Additional": []}

    # Extract each Record
    for i in range(header["ANCOUNT"] + header["NSCOUNT"] + header["ARCOUNT"]):    
        if i >=  header["ANCOUNT"]  and i < header["ANCOUNT"] + header["NSCOUNT"]:
            continue

        record_store = "Answer" if i < header["ANCOUNT"] else "Additional"

        # Name
        names, end = parse_domain_names(labels, response, res_start) 
        
        TYPE     = int(response[end: end + 4], 16)
        CLASS    = response[end + 4: end + 8]
        TTL      = response[end + 8: end + 16]
        RDLENGTH = int(response[end + 16: end + 24], 16)
        RDATA    = response[end + 24: end + 24 + RDLENGTH]
        print(end)
        print(response)
        print(response[end:])
        print(hex(TYPE))
        if hex(TYPE) == 0x0001:
            IP = RDATA
            records[record_store] = f"IP \t {ocstr(IP)} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x0002:
            QNAME, _ = parse_domain_names(labels, response, end + 80) 
            records[record_store] = f"NS \t {ocstr(QNAME[0])} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x005:
            records[record_store] = f"CNAME \t {ocstr(RDATA)} \t {ocstr(TTL)} \t {auth}"
        elif hex(TYPE) == 0x00f:
            PREFERENCE = RDATA[:16]
            EXCHANGE, _ = parse_domain_names(labels, response, end + 28) 
            records[record_store] = f"MX \t {ocstr(EXCHANGE[0])}\t {ocstr(PREFERENCE)} \t {ocstr(TTL)} \t {auth}"

        res_start = end + 24 + RDLENGTH

    print_records(records)


def parse_domain_names(labels, resource, start): 
    names = []
    name = ""
    i = start
    temp = ""
    refs = []
    letters = 0
    
    while True:
        byte = int(''.join(resource[i:i+2]), 16)
        
        if byte == 0:
            name += temp if name == "" else "." + temp
            names.append(name)
            add_to_labels(refs, labels, temp)
            break
            
        if letters == 0:
            if (byte >> 6) & 0b11: # TODO: Check Not in dict error
                name = (name + '.' + labels[int(byte & 0b111111)]).removeprefix('.') 
                names.append(name)
                name = ""
            else:
                add_to_labels(refs, labels, temp)

                refs.append(i)
                name += temp if name == "" else "." + temp
                letters = byte
                temp = ""
        else:
            temp += chr(byte)       
            letters -= 1

        i += 2
    
    return names, i + 2

def add_to_labels(refs, labels, temp): 
    for ref in refs:
        if ref not in labels: 
            labels[ref] = ""

        labels[ref] += temp if labels[ref] == "" else "." + temp

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

