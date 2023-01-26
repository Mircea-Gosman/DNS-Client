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

    return domain


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
        record_store = "Answer" if i < header["ANCOUNT"] else "Additional"

        # Name
        names, end = parse_domain_names(labels, response, res_start) 
        
        TYPE     = int(response[end: end + 4], 16)
        CLASS    = int(response[end + 4: end + 8], 16)
        TTL      = int(response[end + 8: end + 16], 16)
        RDLENGTH = int(response[end + 16: end + 20], 16)
        RDATA    = response[end + 20: end + 20 + RDLENGTH * 2]

        if CLASS != 1:
            print("ERROR \t Skipped record with class not equal to 1.")

        # Don't bother with type checking & data section parsing if it is an authority record
        if (i >=  header["ANCOUNT"]  and i < header["ANCOUNT"] + header["NSCOUNT"]) or CLASS != 1:
            res_start = end + 20 + RDLENGTH * 2
            continue

        if TYPE == 0x0001:
            records[record_store].append(f"IP \t {parseIP(RDATA)} \t {TTL} \t {auth}")
        elif TYPE == 0x0002:
            QNAME, _ = parse_domain_names(labels, response, end + 20)
            records[record_store].append(f"NS \t {QNAME[0]} \t {TTL} \t {auth}")
        elif TYPE == 0x005:
            CNAME, _ = parse_domain_names(labels, response, end + 20) 
            records[record_store].append(f"CNAME \t {CNAME[0]} \t {TTL} \t {auth}")
        elif TYPE == 0x00f: 
            PREFERENCE = int(RDATA[:16], 16)
            EXCHANGE, _ = parse_domain_names(labels, response, end + 24, RDLENGTH * 2) 
            records[record_store].append(f"MX \t {EXCHANGE[0]}\t {PREFERENCE} \t {TTL} \t {auth}") 
        else:
            print(f"ERROR \t Skipped record with unhandled type {TYPE}.")


        res_start = end + 20 + RDLENGTH * 2
        
    print_records(records)


def parse_domain_names(labels, resource, start, size=0): 
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
            name = ""
            temp = ""
            letters = 0

            if size == 0:
                break

            size -= (i - start)
            start = i
            
        if letters == 0:
            pointer = int(''.join(resource[i:i+4]), 16)
            
            if (pointer >> 14) & 0b11: # TODO: 
                if int(pointer & 0b11111111111111) not in labels:
                    print(f"ERROR Response data has incorrect format. Found forward pointer {int(pointer & 0b11111111111111)} at byte {i}")
                    exit(1)

                subnames = [name, temp, labels[int(pointer & 0b11111111111111)]]
                sub_suffixes = [temp, labels[int(pointer & 0b11111111111111)]]
                name = '.'.join([name for name in subnames if name != ""])
                suffix = '.'.join([name for name in sub_suffixes if name != ""])

                names.append(name)
                add_to_labels(refs, labels, suffix)
                name = ""
                temp = ""
                i += 4

                if size == 0:
                    i -= 2
                    break
                
                size -= (i - start)
                start = i
            else:
                add_to_labels(refs, labels, temp)

                refs.append(int(i / 2))
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


def parseIP(IP):
    ip_string = ""
    i = 0
    
    while True:
        ip_string += "." + str(int(IP[i:i+2], 16))

        i += 2
        if i >= len(IP): 
            break
            
    return ip_string[1:]


def print_records(records):
    for category in records:
        if len(records[category]) != 0:
            print("\n-------------------------------------------------------")
            print(f"{category} Section ({len(records[category])} records)")
            print("-------------------------------------------------------")

        for record in records[category]:
            print(record)

    if len(records["Answer"]) == 0 and len(records["Additional"]) == 0:
        print("NOTFOUND No answers were returned in the Answer nor Additional sections.")


def parse_header(packet, header):
    header["ID"] = packet[0:4]
    FLAGS = packet[4:8]

    BIN_FLAGS = bin(int(FLAGS, 16)).lstrip("0b")
    header["QR"] = BIN_FLAGS[0:1]
    header["OPCODE"] = BIN_FLAGS[1:5]
    header["AA"] = BIN_FLAGS[5:6]
    header["TC"] = BIN_FLAGS[6:7]
    header["RD"] = BIN_FLAGS[7:8]
    header["RA"] = BIN_FLAGS[8:9]
    header["ZCODE"] = BIN_FLAGS[9:12]
    header["RCODE"] = BIN_FLAGS[12:16]

    header["QDCOUNT"] = int(packet[8:12] , 16)
    header["ANCOUNT"] = int(packet[12:16], 16)
    header["NSCOUNT"] = int(packet[16:20], 16)
    header["ARCOUNT"] = int(packet[20:24], 16)

def validate_response_header(received_header, sender_ID):
    print("\n-------------------------------------------------------")
    print(f"Error Logs")
    print("-------------------------------------------------------")

    if received_header["RA"] != 1:  
        print(f"ERROR \t Server does not support recursive queries. RA bit is set to {received_header['QR']}.")
        return

    if received_header["TC"] == 1:
        print(f"WARNING \t The response message was truncated. Found TC bit equal to {received_header['TC']}")

    if sent_header["ID"] != received_header["ID"]:
        print(f"ERROR \t Response header ID {received_header['ID']} does not match request header ID {received_header['ID']}.")

    if received_header["QDCOUNT"] != 1: 
        print(f"ERROR \t Response header indicates having more than 1 question. Found QDCOUNT of {received_header['QDCOUNT']}.")

    if received_header["QR"] != 1: 
        print(f"ERROR \t Response header is not a response. QR bit is set to {received_header['QR']}.")

    if received_header["RCODE"] == 1:
        print(f"ERROR \t Format error: the name server is unable to interpret the query.")

    if received_header["RCODE"] == 2:
        print(f"ERROR \t Server failure: the name server was unable to process this query" + 
                " due to a problem with the name server.")

    if received_header["RCODE"] == 3 and received_header["AA"]: 
        print(f"NOTFOUND \t Name error: authoritative server indicates the requested domain name does not exist.")

    if received_header["RCODE"] == 4:
        print(f"ERROR \t Not implemented: the name server does not support the requested kind of query.")

    if received_header["RCODE"] == 5:
        print(f"ERROR \t Refused: the name server refuses to perform the requested operation for policy reasons.")
        
    exit(1)