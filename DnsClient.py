import sys
import Helper
import socket
import random

args = {
    "-t": 5,
    "-r": 3,
    "-p": 53,
    "-mx": False,
    "-ns": False,
    "server": "",
    "name": ""
}


def check_CLI():
    # Collect Data
    for i in range(1, len(sys.argv)):
        if sys.argv[i] not in args:
            continue

        if i == len(sys.argv) - 2:
            args["server"] = Helper.validate_server(sys.argv[i])
            continue

        if i == len(sys.argv) - 1:
            args["name"] = Helper.validate_domain(sys.argv[i])
            continue

        args[sys.argv[i]] = Helper.validate_integer(sys.argv[i], sys.argv[i + 1])

    # Check Errors
    if args["-mx"] and args["-ns"]:
        print("ERROR:\tCan not enable both mail server and name server at the same time.")
        exit(1)


def send_request():
    receptionByteSize = 1024
    server = (args["server"], args["-p"])
    query = ""

    ID = str(hex(random.getrandbits(16)).lstrip("0x"))
    query += ID

    FLAGS = "0x0100"
    query += FLAGS

    # Subfields don't seem needed from the DNS Query doc we will see when testing the code
    QR = "1"
    OPCODE = "0000"
    AA = "0"
    TC = "0"
    RD = "1"
    RA = "0"
    Z = "000"
    RCODE = "0000"
    # End of subfields

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
        length = str(oct(len(name)).lstrip("O"))
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
    client.sendto(query, server)

    answer = client.recvfrom(receptionByteSize)
    print(answer)
    return


def parse_response(response):
    return


if __name__ == "__main__":
    check_CLI()
    response = send_request()
    parse_response(response)
