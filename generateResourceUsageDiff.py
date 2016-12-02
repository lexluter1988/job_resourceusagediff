#!/bin/python

import re
import xmlrpclib
import socket
import urllib2
import xml.etree.ElementTree as ET
import sys
from classes import Api
from poaupdater import uPEM, uSysDB, uLogging, uDBSchema, uPDLDBSchema, uDLModel, uUtil, uFakePackaging, uPackaging, uBuild, openapi, PEMVersion, uDialog, uCert

# POA function to map CI resource id with variables for IM responces


def generate_update(sub_id, rt_id, delta):
    connect = uSysDB.connect()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT rt_instance_id FROM subs_resources WHERE rt_id = '%s' AND sub_id = '%s'" % (rt_id, sub_id))
    rti_id = cursor.fetchall()[0][0]
    cursor.close()
    connect.close()
    return "INSERT INTO resources_usage_log (rti_id, sub_id, time_from, time_to, usage_alter) values ('%s', '%s', '%s', '%s', '%s')" % (rti_id, sub_id, '2015-05-14', '2015-06-14', delta)


def map_ci_resource(sub_id, rt_name):
    connect = uSysDB.connect()
    cursor = connect.cursor()
    cursor.execute("SELECT rt_id FROM resource_types WHERE rt_id in(SELECT rt_id FROM subs_resources WHERE sub_id = '%s') AND restype_name = '%s'" % (sub_id, rt_name))
    result = cursor.fetchall()[0][0]
    cursor.close()
    connect.close()
    return result

# POA function to connect to POA via rpc


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


# POA function to get resource usage for period for specific resource


def get_resource_usage_for_period(sub_id, api, rt_id):
    params = {'subscription_id': sub_id,
              'resource_type_ids': [rt_id],
              'from_time': 1427846401,
              'to_time': 1431475201}
    return api.execute('pem.getResourceUsageForPeriod', **params)


# IM function to get image or backup usage
def get_root_resource(x, rt):
    if x.find(rt) is not None:
        return x.find(rt).text
    return 0

# function to get cpu usage for ct


def ct_get_cpu_usage(x, rut):
    usage_sum = 0
    for child in x:
        if child.get('technology') == "CT":
            for sub_child in child:
                if sub_child.get('resource-usage-type') is not None and sub_child.get('resource-type') == "cpu-hours" and sub_child.get('resource-usage-type') == rut:
                    usage_sum += int(sub_child.get('value'))
    return usage_sum


# function to get cpu usage for vm
def vm_get_cpu_usage(x, rut):
    usage_sum = 0
    for child in x:
        if child.get('technology') == "VM":
            for sub_child in child:
                if sub_child.get('resource-usage-type') is not None and sub_child.get('resource-type') == "cpu-hours" and sub_child.get('resource-usage-type') == rut:
                    usage_sum += int(sub_child.get('value'))
    return usage_sum


# IM function to get usage sum for subscription by ram,cpu,disk resources
def get_usage_by_type(x, rt, rut):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('resource-usage-type') is not None and sub_child.get('resource-type') == rt and sub_child.get('resource-usage-type') == rut:
                usage_sum += int(sub_child.get('value'))
    return usage_sum


# IM function to get usage sum for subscription by traffic resources
def get_usage_by_traffic(x, tt):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('traffic-type') is not None and sub_child.get('traffic-type') == tt:
                usage_sum += int(sub_child.get('used'))
    return usage_sum


# IM function to get usage sum for subscription by backup resources
def get_usage_by_backup(x, sn):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('schedule-name') is not None and sub_child.get('schedule-name') == sn:
                usage_sum += int(sub_child.get('was-assigned'))
    return usage_sum


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for image, backup sizes
def get_usage_delta_root(sub_id, api, resource_id, rt_name):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = get_root_resource(root, rt_name)

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print rt_name, ":", value
    print "delta:", delta
    print sql_command


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for ram, pcs, bandwidth
def get_usage_delta_by_type(sub_id, api, resource_id, rt_name, rt_status):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = get_usage_by_type(root, rt_name, rt_status)

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print rt_name, ":", rt_status, ":", value
    print "delta:", delta
    print sql_command


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for ram, pcs, bandwidth
def get_usage_delta_by_traffic(sub_id, api, resource_id, rt_name):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = get_usage_by_traffic(root, rt_name) / 1024

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print rt_name, ":", value
    print "delta:", delta
    print sql_command


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for ram, pcs, bandwidth
def get_usage_delta_by_backup(sub_id, api, resource_id, rt_name):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = get_usage_by_backup(root, rt_name)

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print rt_name, ":", value
    print "delta:", delta
    print sql_command


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for cpu CT
def get_ct_usage_delta_by_cpu(sub_id, api, resource_id, status):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = ct_get_cpu_usage(root, status)

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print "ct_cpu_usage", ":", status, ":", value
    print "delta:", delta
    print sql_command


# FINAL function to get final SQL with delta and actual usage from IM and POA
# applicable for cpu VM
def get_vm_usage_delta_by_cpu(sub_id, api, resource_id, status):

    response = get_resource_usage_for_period(sub_id, api, resource_id)
    rt_usg = response['resource_type_usages']

    print "subscription_id:", sub_id

    for i in rt_usg:
        summa = 0
        print "resource_type_id:", i['resource_type_id']
        for j in i['usage_statistics']:
            summa += int(j['delta64'])
        print "poa usage:", summa

    value = vm_get_cpu_usage(root, status)

    delta = value - summa
    sql_command = generate_update(sub_id, resource_id, delta)
    print "vm_cpu_usage", ":", status, ":", value
    print "delta:", delta
    print sql_command

sub_id = int(sys.argv[1])
connection = connect_via_rpc("192.168.133.12")
api = Api(connection)

external_incoming_traffic_resource_id = map_ci_resource(
    sub_id, 'CI external incoming traffic')
external_outgoing_traffic_resource_id = map_ci_resource(
    sub_id, 'CI external outgoing traffic')
internal_incoming_traffic_resource_id = map_ci_resource(
    sub_id, 'CI internal incoming traffic')
internal_outgoing_traffic_resource_id = map_ci_resource(
    sub_id, 'CI internal outgoing traffic')

ram_running_resource_id = map_ci_resource(sub_id, 'CI RAM usage running')
ram_stopped_resource_id = map_ci_resource(sub_id, 'CI RAM usage stopped')

network_disk_running_resource_id = map_ci_resource(
    sub_id, 'CI network disk usage running')
network_disk_stopped_resource_id = map_ci_resource(
    sub_id, 'CI network disk usage stopped')

bandwidth_limit_running_resource_id = map_ci_resource(
    sub_id, 'CI bandwidth limit running')
bandwidth_limit_stopped_resource_id = map_ci_resource(
    sub_id, 'CI bandwidth limit stopped')

daily_backup_resource_id = map_ci_resource(sub_id, 'CI daily backup')
weekly_backup_resource_id = map_ci_resource(sub_id, 'CI weekly backup')

image_disk_usage_resource_id = map_ci_resource(sub_id, 'CI image space usage')
backup_disk_usage_resource_id = map_ci_resource(
    sub_id, 'CI backup space usage')

ct_cpu_usage_running_resource_id = map_ci_resource(
    sub_id, 'CI Container CPU Usage running')
ct_cpu_usage_stopped_resource_id = map_ci_resource(
    sub_id, 'CI Container CPU Usage stopped')

vm_cpu_usage_running_resource_id = map_ci_resource(
    sub_id, 'CI Virtual Machine CPU Usage running')
vm_cpu_usage_stopped_resource_id = map_ci_resource(
    sub_id, 'CI Virtual Machine CPU Usage stopped')

tree = ET.parse('1039164')
root = tree.getroot()

get_usage_delta_root(
    sub_id, api, image_disk_usage_resource_id, "images-size-hours")
get_usage_delta_root(
    sub_id, api, backup_disk_usage_resource_id, "backup-size-hours")

get_usage_delta_by_type(
    sub_id, api, ram_running_resource_id, "ram-hours", "while-running")
get_usage_delta_by_type(
    sub_id, api, ram_stopped_resource_id, "ram-hours", "while-stopped")

get_usage_delta_by_type(
    sub_id, api, network_disk_running_resource_id, "pcs-hours", "while-running")
get_usage_delta_by_type(
    sub_id, api, network_disk_stopped_resource_id, "pcs-hours", "while-stopped")

get_usage_delta_by_type(
    sub_id, api, bandwidth_limit_running_resource_id, "bandwidth-hours", "while-running")
get_usage_delta_by_type(
    sub_id, api, bandwidth_limit_stopped_resource_id, "bandwidth-hours", "while-stopped")

get_ct_usage_delta_by_cpu(
    sub_id, api, ct_cpu_usage_running_resource_id, "while-running")
get_ct_usage_delta_by_cpu(
    sub_id, api, ct_cpu_usage_stopped_resource_id, "while-stopped")

get_vm_usage_delta_by_cpu(
    sub_id, api, vm_cpu_usage_running_resource_id, "while-running")
get_vm_usage_delta_by_cpu(
    sub_id, api, vm_cpu_usage_stopped_resource_id, "while-stopped")

get_usage_delta_by_traffic(
    sub_id, api, external_incoming_traffic_resource_id, "public-incoming")
get_usage_delta_by_traffic(
    sub_id, api, external_outgoing_traffic_resource_id, "public-outgoing")
get_usage_delta_by_traffic(
    sub_id, api, internal_incoming_traffic_resource_id, "private-incoming")
get_usage_delta_by_traffic(
    sub_id, api, internal_outgoing_traffic_resource_id, "private-outgoing")
