import sys
import Helper

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
            args["server"] = validate_server(sys.argv[i])
            continue

        if i == len(sys.argv) - 1:
            args["name"] = validate_domain(sys.argv[i])
            continue

        args[sys.argv[i]] = validate_integer(sys.argv[i], sys.argv[i + 1])

    # Check Errors
    if args["-mx"] and args["-ns"]:
        print("ERROR:\tCan not enable both mail server and name server at the same time.")
        exit(1)

def send_request():
    return

def parse_response(response):
    return

if __name__ == "__main__": 
    check_CLI()
    response = send_request()
    parse_response(response)