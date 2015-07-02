__author__ = 'lexluter1988'
import xml.etree.ElementTree as ET
tree = ET.parse('example')
root = tree.getroot()


# function to get image or backup usage
def get_root_resource(x, rt):
 #   return x.find(rt).text
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


# function to get usage sum for subscription by ram,cpu,disk resources
def get_usage_by_type(x, rt, rut):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('resource-usage-type') is not None and sub_child.get('resource-type') == rt and sub_child.get('resource-usage-type') == rut:
                usage_sum += int(sub_child.get('value'))
    return usage_sum


# function to get usage sum for subscription by traffic resources
def get_usage_by_traffic(x, tt):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('traffic-type') is not None and sub_child.get('traffic-type') == tt:
                usage_sum += int(sub_child.get('used'))
    return usage_sum


# function to get usage sum for subscription by backup resources
def get_usage_by_backup(x, sn):
    usage_sum = 0
    for child in x:
        for sub_child in child:
            if sub_child.get('schedule-name') is not None and sub_child.get('schedule-name') == sn:
                usage_sum += int(sub_child.get('was-assigned'))
    return usage_sum


ct_cpu_running_value = ct_get_cpu_usage(root, "while-running")
ct_cpu_stopped_value = ct_get_cpu_usage(root, "while-stopped")

vm_cpu_running_value = vm_get_cpu_usage(root, "while-running")
vm_cpu_stopped_value = vm_get_cpu_usage(root, "while-stopped")

ram_running_value = get_usage_by_type(root, "ram-hours", "while-running")
ram_stopped_value = get_usage_by_type(root, "ram-hours", "while-stopped")

pcs_running_value = get_usage_by_type(root, "pcs-hours", "while-running") * 1024
pcs_stopped_value = get_usage_by_type(root, "pcs-hours", "while-stopped") * 1024

bandwidth_running_value = get_usage_by_type(root, "bandwidth-hours", "while-running")
bandwidth_stopped_value = get_usage_by_type(root, "bandwidth-hours", "while-stopped")

public_incoming = get_usage_by_traffic(root, "public-incoming")
public_outgoing = get_usage_by_traffic(root, "public-outgoing")

private_incoming = get_usage_by_traffic(root, "private-incoming")
private_outgoing = get_usage_by_traffic(root, "private-outgoing")

weekly = get_usage_by_backup(root, "weekly")
daily = get_usage_by_backup(root, "daily")

images_size_hours = get_root_resource(root, "images-size-hours")
backup_size_hours = get_root_resource(root, "backup-size-hours")

print "ct_cpu_running_value", ":", ct_cpu_running_value
print "ct_cpu_stopped_value", ":", ct_cpu_stopped_value

print "vm_cpu_running_value", ":", vm_cpu_running_value
print "vm_cpu_stopped_value", ":", vm_cpu_stopped_value

print "ram_running_value", ":", ram_running_value
print "ram_stopped_value", ":", ram_stopped_value

print "pcs_running_value", ":", pcs_running_value
print "pcs_stopped_value", ":", pcs_stopped_value

print "bandwidth_running_value", ":", bandwidth_running_value
print "bandwidth_stopped_value", ":", bandwidth_stopped_value

print "public_incoming", ":", public_incoming
print "public_outgoing", ":", public_outgoing

print "private_incoming", ":", private_incoming
print "private_outgoing", ":", private_outgoing

print "weekly", ":", weekly
print "daily", ":", daily

print "images_size_hours", ":", images_size_hours
print "backup_size_hours", ":", backup_size_hours