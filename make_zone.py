#!/usr/bin/env python
from subprocess import Popen, PIPE
import os
import sys
import string
import optparse
from optparse import OptionParser

# Config Section
prefix_ip='192.168.10'
etherstub='etherstub0'
zone_storage_prefix='/export/zones'

# functions
def get_vnic():
    # dladm show-vnic 
    # awk ' { print $1 } ' 
    # sed s/vnic// 
    # tail -1 
    # awk ' { print $1+1 } '
    
    p1 = Popen(["dladm", "show-vnic"], stdout=PIPE)
    p2 = Popen(["awk", "{ print $1 }"], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["sed", "s/vnic//"], stdin=p2.stdout, stdout=PIPE)
    p4 = Popen(["tail", "-1"], stdin=p3.stdout, stdout=PIPE)
    p5 = Popen(["awk", "{ print $1 + 1 }"], stdin=p4.stdout, stdout=PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p3.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p4.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    return "vnic"+p5.communicate()[0].strip()

def get_next_ip ():
    fh = open('/etc/hosts', 'r')
    lines = fh.readlines()
    fh.close()
    last_line = lines[-1]
    last_ip = last_line.split()[0]
    last_quad = last_ip.split('.')[3]
    next_suffix = int(last_quad) + 1
    return prefix_ip + "." + str(next_suffix)

# Do the work

parser = OptionParser(usage="usage: %prog [options] ZONE_NAME")
# ip option
# vnic option
# name is a required argument

parser.add_option("-n", "--nic", dest="vnic",
                  help="Defaults to using NIC", metavar="NIC")

parser.add_option("-c", "--create-vnic", dest="make_vnic",
                  action="store_true",
                  help="Create the specified vnic ", default=False)

parser.add_option("-i", "--ip", dest="ip", help="Use IP for the zone.  Default is to find the next prefix address to use.")

(options, args) = parser.parse_args()

print options

if len(args) == 0:
    print "ZONE_NAME argument is required."
    sys.exit(-1)

if len(args) != 1:
    print "Too many arguments. We can only use one ZONE_NAME."
    sys.exit(-1)


name=args[0]
print "Will use name:", name

if options.ip:
    # BUG: Add code to verify the supplied IP.
    ip = options.ip
else:
    ip = get_next_ip()

print "Will use IP:", ip

if options.vnic:
    vnic = options.vnic
    if options.make_vnic:
        make_nic = True
    else:
        make_nic = False
else:
    vnic = get_vnic()
    make_nic = True

print "Will user nic:", vnic
if make_nic:
    print "Will create new vnic."
else:
    print "Will NOT create new vnic."

zone_tmplt_str = """create
set zonepath=$zone_storage_prefix/$name
set autoboot=true
set ip-type=exclusive
add net
set physical=$vnic
set address=$ip/24
end
add fs
set dir=/export/home/jdboyd
set special=/export/home/jdboyd
set type=lofs
end
info
verify
commit
"""

sysidcfg_tmplt_str = """system_locale=C
terminal=vt100
name_service=none
network_interface=$vnic {primary hostname=$name ip_address=$ip netmask=255.255.255.0 protocol_ipv6=no default_route=NONE}
nfs4_domain=dynamic
root_password=cmuL.HSJtwJ.I
security_policy=none
timeserver=localhost
timezone=US/Central
"""

zone_tmplt = string.Template(zone_tmplt_str)

output_file_str = "zones/%s.config" % (name,)

fh = open(output_file_str, "w")
fh.write(zone_tmplt.substitute(name=name, vnic=vnic, ip=ip, 
                               zone_storage_prefix=zone_storage_prefix))
fh.close()

print ip, name
# | tee /etc/hosts
print "Now do the following:"
if make_nic:
    print "dladm create-vnic -l etherstub0 %s" % (vnic, )
print "zonecfg -z %s -f %s" % (name, output_file_str)
print "zoneadm -z %s install" % (name,)
print "zoneadm -z %s boot" % (name,)
