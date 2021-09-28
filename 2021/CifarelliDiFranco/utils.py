import pathlib
import argparse
import subprocess

wrong_dns_frames = {"0" : "", "1" : "", "2" : "", "3" : "", "4" : "", "5" : "", "6" : "", "7" : "", "8" : "", "9" : ""}

NOERROR = "0" #DNS query completed successfully
FORMERR = "1" #DNS query format error
SERVFAIL = "2" #server failed to complete the DNS request
NXDOMAIN = "3" #domain name does not exist
NOTIMP = "4" #function not implemented
REFUSED = "5" #the server refused to answer for the query
YXDOMAIN = "6" #name that should not exist, does exist
XRRSET = "7" #RRset that should not exist, does exist
NOTAUTH = "8" #server not authoritative for the zone
NOTZONE = "9" #name not in zone

DNSLA_PATH = str(pathlib.Path().resolve())
DNSLA_PATH = DNSLA_PATH[:len(DNSLA_PATH) - 4]
DEBUG_PATH = DNSLA_PATH+"/debug"
PCAP_PATH = DNSLA_PATH+"/pcap"
LIVECAPTURE_PATH = DNSLA_PATH+"/livecap"
SRC_PATH = DNSLA_PATH+"/src"
OUTPUT_PATH = DNSLA_PATH+"/output"
MERGED_PATH = DNSLA_PATH+"/merged"

noerror = 0
formerr = 0
servfail = 0
nxdomain = 0
notimp = 0
refused = 0
yxdomain = 0
xrrset = 0
notauth = 0
notzone = 0

measurement_name = "dns_table"

def define_point_body(time, alert, ipv4, threshold, count):
    body = [
        {
            "measurement": measurement_name,
            "time": time,
            "tags": {
                "IPv4": ipv4,
                "threshold": str(threshold),
                "count_alert": str(count)
            },
            "fields": {
                "alert": alert,
                "count": count,
            }
        }
    ]
    return body

def create_parser():
    parser = argparse.ArgumentParser(description="DNS Analyzer")
    parser.add_argument("-i", "--interface", type=str, metavar="", required=True, help="network interface to capture on (type 'ifconfig' if unknown)")
    parser.add_argument("-s", "--sample", type=int, metavar="", required=True, help="factor used to decide how many old values will affect new ones")
    parser.add_argument("-f", "--forge", type=int, metavar="", help="number of packets to forge for test purposes (not recommended)")
    parser.add_argument("-r", "--report", action="store_true", help="creates a .pcap file containing every packet sniffed on the chosen interface (can generate a several number of file during the execution)")
    parser.add_argument("-pa", "--postanalysis", action="store_true", help="applies an analysis to the .pcap file generated by the execution")
    parser.add_argument("-ign", "--ignore", action="store_true", help="ignores dns traffic addressed to this machine (PLEASE NOTE: setting this flag will cause Tshark's capture to be faster)")
    return parser.parse_args()

def print_dns_analysis(qht, rht, ql, rl):
    print(" DNS queries:")
    for id in qht.keys():
        print(id+" "+qht[id])
    print("------------ total of "+str(len(qht.keys()))+" queries")
    print("\n DNS reponses:")
    for id in rht.keys():
        print(id+" "+rht[id])
    print("------------ total of "+str(len(rht.keys()))+" responses")
    total = 0
    print("\n DNS queries (retransmitted):")
    for id in ql.keys():
        print(id+": "+ql[id])
        total += ql[id].count(" ")
    print("------------ total of "+str(total)+" queries")
    total = 0
    print("\n DNS reponses (retransmitted):")
    for id in rl.keys():
        print(id+": "+rl[id])
        total += rl[id].count(" ")
    print("------------ total of "+str(total)+" responses")

def check_dns_rcode(rcode, framenum):
    global noerror
    global formerr
    global servfail
    global nxdomain
    global notimp
    global refused
    global yxdomain
    global xrrset
    global notauth
    global notzone
    global wrong_dns_frames

    if rcode == NOERROR:
        noerror += 1
    elif rcode == FORMERR:
        formerr += 1
    elif rcode == SERVFAIL:
        servfail += 1
    elif rcode == NXDOMAIN:
        nxdomain += 1
    elif rcode == NOTIMP:
        notimp += 1
    elif rcode == REFUSED:
        refused += 1
    elif rcode == YXDOMAIN:
        yxdomain += 1
    elif rcode == XRRSET:
        xrrset += 1
    elif rcode == NOTAUTH:
        notauth += 1
    else:
        notzone += 1
    
    wrong_dns_frames[rcode] += " "+str(framenum)

def print_dns_rcodes():
    print("\n Report of DNS codes found:")
    print(str(noerror)+" no error (0) codes:"+wrong_dns_frames[str(0)])
    print(str(formerr)+" format error code (1) codes:"+wrong_dns_frames[str(1)])
    print(str(servfail)+" server fail (2) codes:"+wrong_dns_frames[str(2)])
    print(str(nxdomain)+" no such name (3) codes:"+wrong_dns_frames[str(3)])
    print(str(notimp)+" not implemented function (4) codes:"+wrong_dns_frames[str(4)])
    print(str(refused)+" refused query (5) codes:"+wrong_dns_frames[str(5)])
    print(str(yxdomain)+" yxdomain (6) codes (a name that shouldn't exists instead exists):"+wrong_dns_frames[str(6)])
    print(str(xrrset)+" xrrset (7) codes (a rrset that shouldn't exists instead exists):"+wrong_dns_frames[str(7)])
    print(str(notauth)+" notauth (8) codes:"+wrong_dns_frames[str(8)])
    print(str(notzone)+" notzone (9) codes:"+wrong_dns_frames[str(9)])
