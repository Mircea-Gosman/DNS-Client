<h1 align='center'>DNS Client</h1>
<h3 align='center'>Implemented within the Scope of ECSE 316 at McGill University</h3>

## Authors
* Mircea Gosman - mirceagosman@mgail.com <br>
* Abdelmadjid Kamli 

## Abstract
DNS clients are readily available nowadays, but how do they work internally?
Using only sockets, this project implements a DNS client able to send and parse queries via Python's UDP sockets layer. We accomodate IP, CNAME, MX, and NS records from the Answer and Additional sections of the received packets. We also test our code on McGill's addresses to navigate the university's web hierarchy.


## Usage Guide

`python DnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name `

* `timeout` (optional) gives how long to wait, inseconds, before retransmitting an
unanswered query. Default value: 5.
* `max-retries` (optional) is the maximum number of times to retransmit an
unanswered query before giving up. Default value: 3.
* `port` (optional) is the UDP port number of the DNS server. Default value: 53.
* `-mx` or `-ns` flags (optional) indicate whether to send a MX (mail server) or NS (name server)
query.At most one ofthese can be given, and if neither is given then the client should send a
type A (IP address) query.
* `server` (required) is the IPv4 address of the DNS server, in a.b.c.d. format
* `name` (required) is the domain name to query for.