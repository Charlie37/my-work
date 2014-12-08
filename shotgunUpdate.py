#!/usr/bin/env python

# update Shotgun data
# author : atrouve
# Shotgun support profile: https://support.shotgunsoftware.com/users/197578066
# 2012


import sys
sys.path.append("/shotgun/api/")
from shotgun_api3 import Shotgun
import re

SERVER_PATH = '#######################################' 
SCRIPT_USER = 'publish'    
SCRIPT_KEY = '#######################################'
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

import csv
from optparse import OptionParser
from datetime import date, datetime, timedelta
import urllib2
from xml.dom.minidom import parseString

        
        
        
def main():
    '''
    update Shotgun data.
    ----------------------------------------------------------------------------------------------------------------------
    Parameters: None
    Result: None
    
    Used to update bids and durations, when the work day changed from 10 hours to 8 hours.
    Used also to clean start/end dates of tasks.
    ----------------------------------------------------------------------------------------------------------------------
    '''

    # Options parser
    parser = OptionParser()
    (options, args) = parser.parse_args()

    # Find project
    project = sg.find_one('Project', [['name', 'is', options.project]])
    if project is None:
        print 'Project was not found in Shotgun'
        return
    
    # Filters
    project_id = project['id']
    filters=[ ['project','is',{'type':'Project','id':project_id}] ]
        
    # Find project's tasks
    fields=['id', 'project', 'content','duration','est_in_mins', 'start_date', 'due_date']
    order=[{'field_name':'content','direction':'asc'}]
    data = sg.find('Task', filters, fields, order)
    
    for line in data:
        print '---------------------name'
        print line['content']
        
        print 'id'
        print line['id']
        
        if line['duration']: # Duration
            durationTask = line['duration']
            print 'duration'
            print line['duration'] 
            newDurationTask = int(durationTask * 0.8)
            print newDurationTask
            # SG Update
           data = { 'duration': newDurationTask }
           result = sg.update('Task', line['id'], data) 
            
        if line['est_in_mins']: # Bid
            print 'bid'
            print line['est_in_mins'] 
            bidTask = line['est_in_mins']
            newBidTask = int(bidTask * 0.8)
            print newBidTask
            # SG Update
           data = { 'est_in_mins': newBidTask }
           result = sg.update('Task', line['id'], data) 

        if line['start_date']: # Start
            print 'start'
            print line['start_date'] 
            # SG Update
           data = { 'start_date': '' }
           result = sg.update('Task', line['id'], data) 

        if line['due_date']: # End
            print 'end'
            print line['due_date'] 
            # SG Update
           data = { 'due_date': '' }
           result = sg.update('Task', line['id'], data) 

    return
            
        
        
        
        
if __name__ == '__main__':
    try :
        main()
    except Exception, e :
        print "ERROR %s\n" % ( e )
        exit(1)
        


