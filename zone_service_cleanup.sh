svcadm disable svc:/application/management/wbem:default 
svcadm disable svc:/application/font/fc-cache:default
svcadm disable svc:/network/rpc/cde-calendar-manager:default
svcadm disable svc:/network/rpc/cde-ttdbserver:tcp
svcadm disable svc:/application/graphical-login/cde-login:default
svcadm disable svc:/application/cde-printinfo:default

svcadm disable svc:/network/dns/multicast:default
svcadm disable svc:/system/avahi-bridge-dsd:default
