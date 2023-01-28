import sys
import Helper
import socket
import random
import time

args = {
    "-t": 5,
    "-r": 3,
    "-p": 53,
    "-mx": False,
    "-ns": False,
    "server": "",
    "name": ""
}

sender_header = {}


def check_CLI():
    # Collect Data
    for i in range(1, len(sys.argv)):
        if i == len(sys.argv) - 2:
            args["server"] = Helper.validate_server(sys.argv[i])
            continue

        if i == len(sys.argv) - 1:
            args["name"] = Helper.validate_domain(sys.argv[i])
            continue

        if sys.argv[i] == "-mx" or sys.argv[i] == "-ns":
            args[sys.argv[i]] = True 
            continue

        if sys.argv[i] not in args:
            continue

        args[sys.argv[i]] = Helper.validate_integer(sys.argv[i], sys.argv[i + 1])

    # Check Errors
    if args["-mx"] and args["-ns"]:
        print("ERROR:\tCan not enable both mail server and name server at the same time.")
        exit(1)

    print("\n-------------------------------------------------------")
    print(f"Request Summary")
    print("-------------------------------------------------------")
    print(f"DNSClient sending request for {args['name']}")
    print(f"Server: {args['server']}")
    print(f"Request type: [{'MX' if args['-mx'] else 'NS' if args['-ns'] else 'A'}]")


def send_request():
    receptionByteSize = 1024
    server = (args["server"], args["-p"])
    query = ""

    ID = str(hex(random.getrandbits(16)).lstrip("0x"))
    query += ID

    FLAGS = ""
    QR = "0"
    FLAGS += QR
    OPCODE = "0000"
    FLAGS += OPCODE
    AA = "0"
    FLAGS += AA
    TC = "0"
    FLAGS += TC
    RD = "1"
    FLAGS += RD
    RA = "0"
    FLAGS += RA
    Z = "000"
    FLAGS += Z
    RCODE = "0000"
    FLAGS += RCODE
    FLAGS = hex(int(FLAGS,2)).zfill(4).lstrip("0x").zfill(4)

    query += FLAGS

    QDCOUNT = "0001"
    query += QDCOUNT

    ANCOUNT = "0000"
    query += ANCOUNT

    NSCOUNT = "0000"
    query += NSCOUNT

    ARCOUNT = "0000"
    query += ARCOUNT

    nameArray = args["name"].split(".")
    QNAME = ""
    for name in nameArray:
        length = hex(len(name)).lstrip("0x").zfill(2)
        asciiName = name.encode("utf-8").hex()
        QNAME += length
        QNAME += asciiName
    QNAME += "00"
    query += QNAME

    QTYPE = ""
    if args["-ns"]:
        QTYPE = "0002"

    elif args["-mx"]:
        QTYPE = "000f"

    else:
        QTYPE = "0001"
    query += QTYPE

    QCLASS = "0001"
    query += QCLASS

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(args['-t'])
    answer = None
    start_time = time.time()
    num_retries = 0

    for i in range(1, args['-r'] + 1):
        try:
            client.sendto(bytes.fromhex(query), server)

            answer = client.recvfrom(receptionByteSize)
            break
        except:
            print(f"The request {i}/{args['-r']} timed out.")
            num_retries += 1

    client.close()
    
    if answer is None or len(answer) == 0:
        print("ERROR \t Reached maximum number of retries and did not obtain a response.")
        exit(1)

    print(f"Response received after {time.time() - start_time} secondes. ({num_retries} retries)")

    Helper.parse_header(query, sender_header)

    return answer


def parse_response(response):
    # Header
    header = {}
    Helper.parse_header(response, header)
    Helper.validate_response_header(header, sender_header)

    # Question
    labels = {}
    
    QNAME, QNAME_end = Helper.parse_domain_names(labels, response, 24)
    QTYPE = response[QNAME_end: QNAME_end + 4]
    QCLASS = response[QNAME_end + 4: QNAME_end + 8]
    
    # Response
    Helper.parse_resource(response, header, labels, QNAME_end + 8)


if __name__ == "__main__":
    check_CLI()
    response = send_request()[0].hex()
    parse_response(response)
