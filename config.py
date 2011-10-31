#!/usr/bin/python
# -*- coding: utf-8 -*-

class config(object):
    ##static variables
    counter = 0 
    names_list = []
    name = ''
    #default settings for gametool 
    gametool_username = "gmtool"
    gametool_password = "gmtool"
    gametool_database = "gmtool"
    gametool_hostname = "127.0.0.1"
    gametool_port = "5432"

    #defaul settings for logserver
    logserver_username = "logserver"
    logserver_password = "logserver"
    logserver_database = "logserver"
    logserver_hostname = "127.0.0.1"
    logserver_port = "5432"

    def __init__(self, shard_name):
        config.counter += 1
        self.name = shard_name
        config.names_list.append( shard_name )

    def setGameToolConfig(self, gametool_username = "gmtool" , gametool_password = "gmtool", gametool_database = "gmtool", gametool_hostname = "127.0.0.1", gametool_port = "5432"):
        self.gametool_username = gametool_username
        self.gametool_password = gametool_password
        self.gametool_database = gametool_database
        self.gametool_hostname = gametool_hostname
        self.gametool_port = gametool_port

    def getGameToolConfig(self):
        return { "username":self.gametool_username, "password":self.gametool_password, "database":self.gametool_database, "hostname":self.gametool_hostname, "port":self.gametool_port }

    def setLogserverConfig(self, logserver_username = "logserver" , logserver_password = "logserver", logserver_database = "logserver", logserver_hostname = "127.0.0.1", logserver_port = "5432"):
        self.logserver_username = logserver_username
        self.logserver_password = logserver_password
        self.logserver_database = logserver_database
        self.logserver_hostname = logserver_hostname
        self.logserver_port = logserver_port

    def getLogserverConfig(self):
        return { "username":self.logserver_username, "password":self.logserver_password, "database":self.logserver_database, "hostname":self.logserver_hostname, "port":self.logserver_port }

    def printConfig(self, settings):
        for key,value in settings.items():
            print key+': ', value

    def __del__(self):
        config.counter -= 1

#example:
if __name__ == '__main__':
    shard1 = config('base')
    print shard1.getGameToolConfig()["database"]
