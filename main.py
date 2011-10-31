#!/usr/bin/python
# -*- coding: utf-8 -*-

from config import config
from odict import odict
import os
import sys 
import re
import psycopg2
import commands   
import errno

# create directory with name dir and permissions 0755
def ensure_dir(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir, 0755)
        except os.error, e: 
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            sys.exit("%s" % (exceptionValue))

# open file with channels for read only and load it to list
def load_channels(file):
    if not os.path.isfile(file):
        print "ERROR: file does not exist"
    else:
        list = []
        try:
            f = open(file,'r').readlines()
            for line in f:
                list.append(line)
            return list
        except IOError as (errno, strerror):
            sys.exit ("I/O error({0}): {1}".format(errno, strerror))

# parse list with channels with regex and create sorted dictionary
def parse_channels(list):
    length = len(list)
    channels = { }
    for i in xrange(length):
        match = None
        for match in re.finditer('\(([0-9]+), from\("([^"]+)"\)', list[i]): 
            if match:
                type = 'plain'
                merged = None
                for merged in re.finditer('MERGED_SINGLE', list[i]):
                    type = 'merged'
                # group(0): table_id + table_name, group(1): only table_id, group(2): only table_name
                channels[match.group(1)]={ "table_name":match.group(2), "type":type }
    sorted_channels = odict(sorted(channels.items(), key=lambda item: item[0]))
    return sorted_channels 

# create connection string for psycopg2.connect |  type should be 'GameTool' or 'Logserver'
def createConnectionString(id, type):
    database =  eval( 'shard' + str(shard_num) + '.get' + type + 'Config()["database"]' )
    user = eval( 'shard' + str(shard_num) + '.get' + type + 'Config()["username"]' )
    password = eval( 'shard' + str(shard_num)     + '.get' + type + 'Config()["password"]' )
    host = eval( 'shard' + str(shard_num) + '.get' + type + 'Config()["hostname"]' )
    port = eval ('shard' + str(shard_num) + '.get' + type + 'Config()["port"]' )
    return ( 'dbname = \'' + database + '\' user = \'' + user + '\' password = \'' + password + '\' host = \'' + host + '\' port = \'' + port + '\'connect_timeout=5 options=\'--client_encoding=UTF8\'' )

# create command string for dumping tables
def createDumpString(id, relname, folder):
    password = eval('shard'+str(shard_num)+'.getLogserverConfig()["password"]')
    hostname = eval('shard'+str(shard_num)+'.getLogserverConfig()["hostname"]')
    username = eval('shard'+str(shard_num)+'.getLogserverConfig()["username"]')
    database = eval('shard'+str(shard_num)+'.getLogserverConfig()["database"]')
    port = eval('shard'+str(shard_num)+'.getLogserverConfig()["port"]')
    return ( "export PGPASSWORD='" + password + "' && pg_dump -i -p" + port + " -h" + hostname + " -U" + username + " " + database + " -t '\"" + relname + "\"' > \"" + folder + "/" + relname + ".sql\" ")

if __name__ == '__main__':
    mode = 'scan'
    if ((len(sys.argv) > 1) and (sys.argv[1] == 'drop')):
        mode = 'drop'
    else:
        mode='scan'

################################################ start of config part ###########################################################################################################
    # backup directory with '/' in the end                                                                                                                                      #
    backupDir = './backups/'                                                                                                                                                    #
    # file with channels                                                                                                                                                        #
    channels_file = './channels.txt'                                                                                                                                            #
                                                                                                                                                                                #
    ## configure shards                                                                                                                                                         #
    # You can add so many shards, how many it is necessary for you.                                                                                                             #
    # Objects names should be shard1, shard2, shard3, ...                                                                                                                       #
                                                                                                                                                                                #
    # Shards configuration                                                                                                                                                      #
    # shard or base name should be place between (' and ')                                                                                                                      #
                                                                                                                                                                                #
    shard1 = config('Allods')                                                                                                                                                   #
    shard1.setGameToolConfig('gmtool', 'gmtool', 'gmbr', '127.0.0.1', '5432')                                                                                                   #
    shard1.setLogserverConfig('logserver', 'logserver', 'logbr', '127.0.0.1', '5432')                                                                                           #
                                                                                                                                                                                #
    shard2 = config('Mail.Ru')                                                                                                                                                  #
    shard2.setGameToolConfig('gmtool', 'gmtool', 'd_gmtool_slave', '127.0.0.1', '5432')                                                                                         #
    shard2.setLogserverConfig('logserver', 'logserver', 'd_logserver_slave', '127.0.0.1', '5432')                                                                               #
                                                                                                                                                                                #
    shard3 = config('Base')                                                                                                                                                     #
    shard3.setGameToolConfig('gmtool', 'gmtool', 'd_gmtool_master', '127.0.0.1', '5432')                                                                                        #
    shard3.setLogserverConfig('logserver', 'logserver', 'd_logserver_master', '127.0.0.1', '5432')                                                                              #
                                                                                                                                                                                #
#    shardX = config('GameShardX')                                                                                                                                              #
#    shardX.setGameToolConfig('username', 'password', 'database name', 'hostname', 'port')                                                                                      #
#    shardX.setLogserverConfig('username', 'password', 'database name', 'hostname', 'port')                                                                                     #
############################################# ## end of config part #############################################################################################################

    # create root directory for backup 
    ensure_dir(backupDir)
    # get list of sorted channels(example: {('59', {'type': 'plain', 'table_name': 'channel.gm.FairyFeedChannel'}), }
    sorted_channels = parse_channels(load_channels(channels_file))  

    # create backup directories for all shards
    for index in xrange(config.counter):
        ensure_dir(backupDir + config.names_list[index])
    
    # started shard checking and started process
    for shard_num in xrange(1,config.counter+1):
        channels_with_lastid = { }
        
        # connection to GameTool database
        try:
            conn = psycopg2.connect( createConnectionString(shard_num, 'GameTool') )
            cursor = conn.cursor()
            for key,value in sorted_channels.items():
                query = 'select "lastImportedId" from "etl.watermark" where entity='+key
                cursor.execute( query )
                records = cursor.fetchall()
                for item in records:
                    if item[0] != 0:
                        value['lastid'] = item[0]
                        channels_with_lastid[key] = value
            conn.commit()
            cursor.close()
            conn.close()
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

        # connection to Logserver database
        try:
            conn = psycopg2.connect( createConnectionString(shard_num, 'Logserver') )
            cursor = conn.cursor()
            dropList = []
            sizeToDrop = float(0)
            for key,value in channels_with_lastid.items():
                if value['type'] == 'plain':
                    drop = { }
                    for match in re.finditer( '\.([^.]+)$', value['table_name'] ):
                        if match:
                            query = "select relname, pg_total_relation_size(oid) as size from pg_class where relname like 'f.%." + match.group(1) + "[%]' order by relname asc"
                            cursor.execute( query )
                            records = cursor.fetchall()
                            # item[0] - relation name, item[1] - relation size
                            for item in records:
                                size = round( float(item[1])/1024/1024, 2 )
                                query2 = 'select max(id) as id from "' + item[0] + '"';
                                cursor.execute( query2 )
                                records2 = cursor.fetchall()
                                # item2[0] - id
                                for item2 in records2:
                                    if item2[0] < value['lastid']:
                                        drop = { 'relname':item[0], 'size':size, 'lastid':value['lastid']  }
                                        dropList.append( drop )
            shardBackupDir = backupDir+config.names_list[shard_num - 1]
            if len( dropList ) > 0:
                totalDropSize = float(0)
                for item in dropList:
                    if( mode == 'drop' ):
                        cmd = createDumpString(shard_num, item['relname'], shardBackupDir ) 
                        os.system( cmd )
                        cmd = "tail -n3 \"" + shardBackupDir + "/" + item['relname'] + ".sql\" | grep -o 'PostgreSQL database dump complete'"
                        cmdResult = commands.getoutput( cmd )
                        if len(cmdResult) > 0:
                            cmd = "gzip < \"" + shardBackupDir + "/" + item['relname'] + ".sql\" > \"" + shardBackupDir + "/" + item['relname'] + ".sql.gz\""
                            retvalue = os.system( cmd )
                            if retvalue == 0:
                                os.unlink( shardBackupDir + "/" + item['relname'] + ".sql" )
                                query = 'drop table "' + item['relname'] + '"'
                                cursor.execute( query )
                                conn.commit()
                                totalDropSize += float(item['size'])
                    else:
                        totalDropSize += float(item['size'])
                sizeToDrop = float( totalDropSize )
            else:
                print ("[{0:^15}] Nothing to drop".format (config.names_list[shard_num - 1]))

            if sizeToDrop > 0:
                if mode == 'drop':
                    print ("[{0:^15}] dropped data size: {1} Mb".format (config.names_list[shard_num - 1],str(sizeToDrop)))
                else:
                    print ("[{0:^15}] to drop data size: {1} Mb".format (config.names_list[shard_num - 1],str(sizeToDrop)))
            cursor.close()
            conn.close()
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            sys.exit("Database connection failed!\n ->%s\n" % (exceptionValue))

