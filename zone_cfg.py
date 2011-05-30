#!/usr/bin/env python
from subprocess import Popen, PIPE
import os
import string
import optparse

# Config Section
prefix_ip='192.168.10'
etherstub='etherstub0'

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
name="david_zone"

vnic = get_vnic()
ip = get_next_ip()

#cat <<EOF > zones/$name.config
zone_tmplt_str = """create
set zonepath=/export/zones/$name
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

zone_tmplt = string.Template(zone_tmplt_str)

output_file_str = "zones/%s.config" % (name,)

fh = open(output_file_str, "w")
fh.write(zone_tmplt.substitute(name=name, vnic=vnic, ip=ip))
fh.close()

print ip, name
# | tee /etc/hosts
print "Now do the following:"
print "dladm create-vnic -l etherstub0 %s" % (vnic, )
print "zonecfg -z %s -f %s" % (name, output_file_str)
print "zoneadm -z %s install" % (name,)
print "zoneadm -z %s boot" % (name,)
