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

    print(f"Parsed CLI: {args}")


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
        length = str(oct(len(name)).lstrip("0o")).zfill(2)
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
    for i in range(1, args['-r'] + 1):
        try:
            client.sendto(bytes.fromhex(query), server)

            answer = client.recvfrom(receptionByteSize)
            break
        except:
            print(f"The request {i}/{args['-r']} timed out.")
    client.close()
    print(query)
    return answer


# WoW SuCh ClEaN CoDe
def parse_response(response):
    r_len = response.bit_length()
    # Header
    ID       = response >> (r_len - 16)                                                         & bin(16)
    QR       = response >> (r_len - 16 - 1)                                                     & 1
    OP_CODE  = response >> (r_len - 16 - 1 - 4)                                                 & bin(4)
    AA       = response >> (r_len - 16 - 1 - 4 - 1)                                             & 1
    TC       = response >> (r_len - 16 - 1 - 4 - 1 - 1)                                         & 1
    RD       = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1)                                     & 1
    RA       = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1)                                 & 1
    Z        = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3)                             & bin(3)
    R_CODE   = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3 - 4)                         & bin(4)
    QD_COUNT = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3 - 4 - 16)                    & bin(16)
    AN_COUNT = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3 - 4 - 16 - 16)               & bin(16)
    NS_COUNT = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3 - 4 - 16 - 16 - 16)          & bin(16)
    AR_COUNT = response >> (r_len - 16 - 1 - 4 - 1 - 1 - 1 - 1 - 3 - 4 - 16 - 16 - 16 - 16)     & bin(16)

    # Original Query
    QUERY = response >> (r_len - 96 - 19 * 8) & bin(19*8)

    # Validate Header & Query [ wip]


    # Answer


    return

def parse_response_hex(response):
    ID = response[0:4]
    FLAGS = response[4:8]

    BIN_FLAGS = bin(int(FLAGS, 16)).lstrip("0b")
    QR = BIN_FLAGS[0:1]
    OPCODE = BIN_FLAGS[1:5]
    AA = BIN_FLAGS[5:6]
    TC = BIN_FLAGS[6:7]
    RD = BIN_FLAGS[7:8]
    RA = BIN_FLAGS[8:9]
    ZCODE = BIN_FLAGS[9:12]
    RCODE = BIN_FLAGS[12:16]

    QDCOUNT = response[8:12]
    ANCOUNT = response[12:16]
    NSCOUNT = response[16:20]
    ARCOUNT = response[20:24]


if __name__ == "__main__":
    check_CLI()
    response = send_request()[0].hex()
    # response = "3930e1010000000000000000"
    # I put it in binary but the parsing still does not work and sadely I tried mutliple things but
    # python is annoyed that it has to deal with concatenation of strings and ints
    # I think it would just be way simpler to use the hex parsing :)
    # furthermore, for some reason the DNS require a hexified byte encoding which makes sense
    # but at least say that somewhere teacher ); how would we know we would assume a utf-8
    # as any normal human being Well xD. At least it works ahaha.
    # responseBin = bin(int(response, 16))

    parse_response_hex(response)
