__author__ = 'lexluter1988'
#!/bin/python

from poaupdater import uPEM, uSysDB, uLogging, uDBSchema, uPDLDBSchema, uDLModel, uUtil, uFakePackaging, uPackaging, uBuild, openapi, PEMVersion, uDialog, uCert

def map_public_incoming(sid)
    connect = uSysDB.connect()
    cursor = connect.cursor()
    cursor.execute("SELECT rt_id FROM resource_types WHERE rt_id in(SELECT rt_id FROM subs_resources WHERE sub_id = '%s') AND restype_name = 'CI iternal incoming traffic'" % sid)
    cursor.close()
    connect.close()
    return cursor.fetchall()[0][0]


def map_ci_resource(sid, rt_name):
    connect = uSysDB.connect()
    cursor = connect.cursor()
    cursor.execute("SELECT rt_id FROM resource_types WHERE rt_id in(SELECT rt_id FROM subs_resources WHERE sub_id = '%s') AND restype_name = '%s'" % sid, rt_name)
    cursor.close()
    connect.close()
    return cursor.fetchall()[0][0]


