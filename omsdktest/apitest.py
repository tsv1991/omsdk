import os
import sys
sys.path.append(os.getcwd())
import xml.etree.ElementTree as ET
import re
from omsdk.typemgr.ClassType import *
from omsdk.typemgr.FieldType import *
from omsdk.typemgr.BuiltinTypes import *
from omsdk.sdkcreds import UserCredentials
from omdrivers.types.iDRAC.iDRAC import *
from omdrivers.enums.iDRAC.iDRAC import *
from omdrivers.types.iDRAC.BIOS import *
from omdrivers.types.iDRAC.RAID import *
from omdrivers.types.iDRAC.NIC import *
from omdrivers.types.iDRAC.FCHBA import *
from omdrivers.types.iDRAC.SystemConfiguration import *
from omdrivers.lifecycle.iDRAC.SCPParsers import XMLParser
from omsdk.sdkinfra import sdkinfra
from omsdk.simulator.devicesim import Simulator
logging.basicConfig(level=logging.ERROR)
from omsdk.sdkfile import FileOnShare
from omsdk.sdkprint import PrettyPrint
import logging
from omdrivers.lifecycle.iDRAC.RAIDHelper import *

myshare = FileOnShare(remote = "\\\\100.96.20.115\\Share",
        mount_point='Z:\\', isFolder=True,
        creds = UserCredentials("Administrator@AJUDOM", "ajaya_123"))

#ipaddr = '100.96.25.120'
ipaddr = '100.100.249.114'
logging.basicConfig(level=logging.DEBUG)

Simulator.start_simulating()
myshare.valid = True
sd = sdkinfra()
sd.importPath()
idrac = sd.find_driver(ipaddr, UserCredentials('root', 'calvin'))
idrac.config_mgr.set_liason_share(myshare)

idrac.config_mgr._sysconfig.iDRAC.Users.new(
    UserName_Users = "ruse1",
    Password_Users = "calvin",
    Privilege_Users = "511",
    IpmiLanPrivilege_Users = "Administrator",
    IpmiSerialPrivilege_Users = "Administrator",
    Enable_Users = "Enabled",
    SolEnable_Users = "Enabled",
    ProtocolEnable_Users = "Disabled",
    AuthenticationProtocol_Users = "SHA",
    PrivacyProtocol_Users = "AES"
)
idrac.config_mgr.apply_changes()
user = idrac.config_mgr._sysconfig.iDRAC.Users.find_first(UserName_Users = "ruse1")
if user is None:
    print("No such user found!")
else:
    user.Password_Users = '_j2_2j_2j_j2_'
    user.SolEnable_Users = "Disabled"
    idrac.config_mgr.apply_changes()

idrac.config_mgr._sysconfig.iDRAC.Users.remove(UserName_Users = "ruse1")
idrac.config_mgr.apply_changes()
print(PrettyPrint.prettify_json(idrac.config_mgr._sysconfig.iDRAC.Users.Json))

exit()

def emailtest(idrac, address, expected, action=1):
    print(expected)
    idrac.config_mgr._sysconfig.iDRAC.EmailAlert._index_helper.printx()
    try:
        if action == 1:
            idrac.config_mgr._sysconfig.iDRAC.EmailAlert.new(
                Address_EmailAlert = address, CustomMsg_EmailAlert = address)
        else:
            idrac.config_mgr._sysconfig.iDRAC.EmailAlert.remove(
                Address_EmailAlert = address)
    except Exception as ex:
        print(str(ex))
    idrac.config_mgr.apply_changes()
    idrac.config_mgr._sysconfig.iDRAC.EmailAlert._index_helper.printx()
    print("=============")
print("Original Data")
print(PrettyPrint.prettify_json(idrac.config_mgr._sysconfig.iDRAC.EmailAlert.Json))
print("======")
emailtest(idrac, "hola@gmail.com", "added")
emailtest(idrac, "hungama@gmail.com", "added")
emailtest(idrac, "takur@gmail.com", "added")
emailtest(idrac, "hungama@gmail.com", "deleted", action=2)
emailtest(idrac, "test@gmail.com", "non-existent-delete-no-change", action=2)
emailtest(idrac, "pacific@gmail.com", "added")
emailtest(idrac, "antartic@gmail.com", "added")
emailtest(idrac, "notalone@gmail.com", "should-fail-for-index")
emailtest(idrac, "pacific@gmail.com", "deleted", action=2)
emailtest(idrac, "pacific@gmail.com", "deletion-fail", action=2)
emailtest(idrac, "pacific@gmail.com", "added")
print(PrettyPrint.prettify_json(idrac.config_mgr._sysconfig.iDRAC.EmailAlert.Json))

idrac.config_mgr.create_virtual_disk('hola',1,1,'RAID 1',0)
print("createvd")
print(idrac.config_mgr.CreateVD('hola', 1, 1, 'RAID 1'))
print("deletevd")
print(idrac.config_mgr.DeleteVD('hola'))

### Retrieving Timezone
print(idrac.config_mgr.Time.Timezone_Time)

#### Applying Timezone
idrac.config_mgr.Time.Timezone_Time = 'Asia/Kolkata'
print(idrac.config_mgr.apply_changes())

#### Boot Mode APIs
print(idrac.config_mgr.BootMode)
print(idrac.config_mgr.change_boot_mode('Uefi'))
print(idrac.config_mgr.change_boot_mode(BootModeTypes.Uefi))

print(idrac.config_mgr.CSIOR)
print(idrac.config_mgr.enable_csior())
print(idrac.config_mgr.apply_changes())
print(idrac.config_mgr.disable_csior())
print(idrac.config_mgr.apply_changes())

print(idrac.config_mgr.Location.Json)

print(idrac.config_mgr.configure_location(loc_datacenter = 'a', loc_room='b', loc_aisle='c', loc_rack='d', loc_rack_slot =1, loc_chassis='f'))

print(idrac.config_mgr.TLSProtocol)
print(idrac.config_mgr.SSLEncryptionBits)
print(idrac.config_mgr.SyslogServers)
print(idrac.config_mgr.enable_syslog())
print(idrac.config_mgr.apply_changes())
print(idrac.config_mgr.disable_syslog())

# new style
print(idrac.config_mgr.TLSProtocol)
print(idrac.config_mgr.SSLEncryptionBits)
print(idrac.config_mgr.SyslogServers)
print(idrac.config_mgr.NTPServers)
print(idrac.config_mgr.NTPEnabled)
print(idrac.config_mgr.NTPMaxDist)

print(idrac.config_mgr._sysconfig.System.ServerTopology.Json)

idrac.config_mgr._sysconfig.iDRAC.Users.new(
    UserName_Users = "ruse1",
    Password_Users = "calvin",
    Privilege_Users = "511",
    IpmiLanPrivilege_Users = "Administrator",
    IpmiSerialPrivilege_Users = "Administrator",
    Enable_Users = "Enabled",
    SolEnable_Users = "Enabled",
    ProtocolEnable_Users = "Disabled",
    AuthenticationProtocol_Users = "SHA",
    PrivacyProtocol_Users = "AES"
)
idrac.config_mgr.apply_changes()

try:
  idrac.config_mgr._sysconfig.iDRAC.Users.new(
    UserName_Users = "ruse1",
    Password_Users = "calvin",
    Privilege_Users = "511",
    IpmiLanPrivilege_Users = "Administrator",
    IpmiSerialPrivilege_Users = "Administrator",
    Enable_Users = "Enabled",
    SolEnable_Users = "Enabled",
    ProtocolEnable_Users = "Disabled",
    AuthenticationProtocol_Users = "SHA",
    PrivacyProtocol_Users = "AES"
  )
except Exception as ex:
    print(str(ex))
    print('passed')

idrac.config_mgr.apply_changes()
user = idrac.config_mgr._sysconfig.iDRAC.Users.find_first(UserName_Users = "ruse1")
if user is None:
    print("No such user found!")
else:
    user.Password_Users = '_j2_2j_2j_j2_'
    user.SolEnable_Users = "Disabled"
    idrac.config_mgr.apply_changes()

idrac.config_mgr._sysconfig.iDRAC.Users.remove(UserName_Users = "ruse1")
idrac.config_mgr.apply_changes()
idrac.config_mgr.apply_changes()


    #.Json => gives your JSON representation
    # .XML => gives you XML representation
    # without any - you can access as a typical class
print(PrettyPrint.prettify_json(idrac.config_mgr.SyslogConfig.Json))

idrac.config_mgr.configure_idrac_dnsname('name')
idrac.config_mgr.configure_idrac_ipv4(enable_ipv4=True, dhcp_enabled=True)
idrac.config_mgr.configure_idrac_ipv4static( '1.1.1.1', '1.1.1.1', '1.1.1.1', dnsarray=None, dnsFromDHCP=False)
idrac.config_mgr.configure_idrac_ipv4dns(dnsarray= ["100.96.25.40", "100.29.44.55"], dnsFromDHCP=False)
idrac.config_mgr.configure_idrac_ipv6static( '1:1:1:1', ipv6_prefixlen = 64, ipv6_gateway="::", dnsarray=None, dnsFromDHCP=False)
idrac.config_mgr.configure_idrac_ipv6dns(dnsarray= ["100:96:25:40", "100:29:44:55"], dnsFromDHCP=False)
print(idrac.config_mgr.apply_changes())
print(PrettyPrint.prettify_json(idrac.config_mgr.iDRAC_NIC.Json))
print(idrac.config_mgr.iDRAC_IPv4Static.Json)
print(idrac.config_mgr.iDRAC_IPv6Static.Json)
print(idrac.config_mgr.Time.Json)
print(idrac.config_mgr.apply_changes())
print(idrac.config_mgr.apply_changes())

print(PrettyPrint.prettify_json(idrac.config_mgr._sysconfig.iDRAC.Users.Json))
idrac.config_mgr._sysconfig.iDRAC.Users._index_helper.printx()
