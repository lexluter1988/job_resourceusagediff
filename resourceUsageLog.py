__author__ = 'lexluter1988'
import sys
import re
import xmlrpclib
import socket
import urllib2
import xml.etree.ElementTree as ET
from poaupdater import openapi, uPEM
from classes import Api

def connect_via_rpc(mn_ip):
    """ Let's try if API is accessible """

    api_url = 'http://' + mn_ip + ':8440/RPC2'
    connection = xmlrpclib.ServerProxy(api_url)
    try:
        connection._()
    except xmlrpclib.Fault:
        pass
    except socket.error:
        return None
    return connection

def get_resource_usage_for_period(sub_id,api):
    params = {  'subscription_id': sub_id,
                'resource_type_ids': [1000974, 1000975, 1000008, 1002129, 1000961, 1000962, 1002632, 1000956, 1000976, 1000963, 1000964, 1000959, 1000960, 1000958, 1002215, 1000970, 1000971, 1000967, 1000966, 1000972, 1000973, 1002213, 1002214, 1000968, 1000222, 1000223, 1000006],
                'from_time': 1427846401,
                'to_time': 1431475201}
    return api.execute('pem.getResourceUsageForPeriod', **params)

sub_id = int(sys.argv[1])
connection = connect_via_rpc("192.168.133.12")
api = Api(connection)

responce = get_resource_usage_for_period(sub_id,api)
rt_types_usg = responce['resource_type_usages']

for i in rt_types_usg:
    summa = 0
    print "resource_type_id:", i['resource_type_id']
    for j in i['usage_statistics']:
        summa += int(j['delta64'])
    print "usage:", summa



#!/bin/python

from poaupdater import uPEM, uSysDB, uLogging, uDBSchema, uPDLDBSchema, uDLModel, uUtil, uFakePackaging, uPackaging, uBuild, openapi, PEMVersion, uDialog, uCert

con = uSysDB.connect()
cur = con.cursor()
cur.execute("SELECT location_id FROM sc_instances")
cur.close()
con.close()
