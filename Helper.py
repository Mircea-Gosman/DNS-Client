def validate_server(server):
    server = server.replace("@", "")
    fields = server.split(".")
    error = len(fields) != 4

    for field in fields:
        if not isinstance(field, int) or int(field) < 0:
            error = True

    if error: 
        print("ERROR:\tThe server should be of format: X.X.X.X where X is an integer.")
        exit(3)

    return int(field)


def validate_domain(domain):
    fields = domain.split(".")

    if len(fields) != 2 or len(fields) != 3:
        print("ERROR:\tThe domain should be of format: www.myDomain.com")
        exit(4)

    return domain


def validate_integer(switch, value):
    if not isinstance(value, int) or int(value) < 0:
        print(f"ERROR:\tThe switch {switch} needs to be a positive integer. Received {value} instead.")
        exit(2)

    return int(value)