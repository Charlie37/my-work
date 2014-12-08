#!/usr/bin/env python

# export Shotgun timelog data
# author : atrouve
# 2012

# Shotgun support profile: https://support.shotgunsoftware.com/users/197578066


import sys
sys.path.append("/shotgun/api/")
from shotgun_api3 import Shotgun
import re

SERVER_PATH = '###############################' 
SCRIPT_USER = 'publish'    
SCRIPT_KEY = '###############################'
sg = Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

import csv
from optparse import OptionParser
from datetime import date, datetime, timedelta
import urllib2
from xml.dom.minidom import parseString

        

def startAndEndDates():
    '''
    Retrieves start date/end date of project from earliest/latest task dates.
    ----------------------------------------------------------------------------------------------------------------------
    Parameters: none
    Result: start date - end date
    ----------------------------------------------------------------------------------------------------------------------
    '''

    # Connect to SG
    #projectName = str(assetmg.io.ConnectUserInfo()[2]) # retrieved from asset manager
    projectName = projectName.lower()

    result = sg.find_one('Project', [['name', 'is', projectName]])
    if result is None:
        print 'Current project was not found in Shotgun'
        return

    # Find project sequence data
    project_id = result['id']
    filters=[ ['sg_status_list','is','ip'],['project','is',{'type':'Project','id':project_id}] ]
    fields=['id','code','description','sg_status_list']
    order=[{'field_name':'code','direction':'asc'}]
    data = sg.find('Sequence', filters, fields, order)

    listInfo = []

    # loop on project sequences
    for line in data:
        startDateSeq = date.today() # init
        dueDateSeq = date.today() # init

        # Find sequence task data
        filtersTask=[ ['project','is',{'type':'Project','id':project_id}], ['entity', 'is', {'type':'Sequence', 'id':line['id']}] ]
        fieldsTask=['id','content','start_date','due_date']
        dataTask = sg.find("Task", filtersTask, fieldsTask)

        # loop on sequence tasks
        for lineTask in dataTask:
            strStartDate = str(lineTask['start_date'])
            strDueDate = str(lineTask['due_date'])

            arrayStartDate = strStartDate.split('-')
            startDate = date( int(arrayStartDate[0]), int(arrayStartDate[1]), int(arrayStartDate[2]) )
            if startDate < startDateSeq:
                startDateSeq = startDate

            arrayDueDate = strDueDate.split('-')
            dueDate = date( int(arrayDueDate[0]), int(arrayDueDate[1]), int(arrayDueDate[2]) )
            if dueDate > dueDateSeq:
                dueDateSeq = dueDate
	    
        listInfo.append([str(line['code']), startDateSeq, dueDateSeq])

    print listInfo
    return listInfo     
            
        
        
        
def main():
    '''
    export Shotgun timelog data.
    ----------------------------------------------------------------------------------------------------------------------
    Parameters: project/time range/user
    Result: CSV
    ----------------------------------------------------------------------------------------------------------------------
    '''

    # Options parser
    parser = OptionParser()
    parser.add_option("-p", "--project", dest="project", help="get timelogs from PROJECT", metavar="PROJECT")
    parser.add_option("-f", "--date from", dest="date_from", help="get timelogs after DATE", metavar="DATE RANGES")
    parser.add_option("-t", "--date to", dest="date_to", help="get timelogs before DATE", metavar="DATE RANGES")
    parser.add_option("-u", "--user", dest="user_login", help="get timelogs from USER LOGIN", metavar="USER LOGIN")
    (options, args) = parser.parse_args()

    project = sg.find_one('Project', [['name', 'is', options.project]])
    if project is None:
        print 'Project was not found in Shotgun'
        #print 'Project ' + options.project + ' was not found in Shotgun'
        return

    # Filters
    project_id = project['id']
    filters=[ ['project','is',{'type':'Project','id':project_id}] ]

    if options.date_from is not None:
        year, month, day = map(int, options.date_from.split("-") )
        date_from = date(year, month, day) - timedelta(days=1)
        filters.append( ['date','greater_than',date_from] )

    if options.date_to is not None:
        year, month, day = map(int, options.date_to.split("-") )
        date_to = date(year, month, day) + timedelta(days=1)
        filters.append( ['date','less_than',date_to] )

    #filters=[ ['project','is',{'type':'Project','id':project_id}], ['date','between', [[options.date_from, options.date_to]] ] ] # 'between' 'relation' expects a 2-element array:

    if options.user_login is not None:
        filtersUser=[ ['login','is',options.user_login] ]
        fieldsUser=['id','login']
        dataUser = sg.find_one("HumanUser", filtersUser, fieldsUser)
        if not dataUser:
            print "couldn't find user " + options.user_login
            return
        else:
            filters.append( ['user','is',{'type':'HumanUser','id':dataUser['id']}] )


    # Find project timelog data
    fields=['date','duration','entity', 'project', 'user']
    order=[{'field_name':'user','direction':'asc'},{'field_name':'date','direction':'asc'}]
    data = sg.find('TimeLog', filters, fields, order)

    listTimelog = []

    cpt = 0
    # Loop on project timelogs
    for line in data:
        
        cpt = cpt+1
        percentage = cpt*100/len(data)
        print percentage, '%'
               
        strDate = str(line['date'])
        nbHoursDuration = float(line['duration'])/60.0 # 1 SG DAY = 10 HOURS

        strTaskName = "<no task>"
        if line['entity']:
            strTaskName = line['entity']['name']

        #strProjectName = line['project']['name']

        # USER: login, first/last name
        strUserLogin = "<no user>"
        strUserFirstName = strUserLastName = ""
        # other way to retrieve first and last names
        #strUserName = line['user']['name'].partition(' ') # returns 3-tuple: part before sep, sep, part after sep.
        #strUserFirstName = strUserName[0]
        #strUserLastName = strUserName[2]

        if line['user']:
            idUser = line['user']['id']
            filtersUser=[ ['id','is',idUser] ]
            fieldsUser=['id','firstname', 'lastname', 'login']
            dataUser = sg.find_one("HumanUser", filtersUser, fieldsUser)
            if not dataUser:
                print "couldn't find user"
            else:
                strUserLogin = dataUser['login']
                strUserFirstName = dataUser['firstname']
                strUserLastName = dataUser['lastname']
               
        # SHOT(S) linked to task
        strShotName = "<no shot>"

        if line['entity']:
            idTask = line['entity']['id']
            filtersTask=[ ['id','is',idTask] ]
            fieldsTask=['id']
            dataTask = sg.find_one("Task", filtersTask, fieldsTask)
            if dataTask: # task entity
                shots = sg.find('Shot', filters=[['tasks','in',dataTask]])
                if len(shots) >= 1: # if shot(s) linked, take the first
                    idShot = shots[0]['id']
                    filtersShot=[ ['id','is',idShot] ]
                    fieldsShot=['id','code']
                    dataShot = sg.find_one("Shot", filtersShot, fieldsShot)
                    if dataShot:
                        strShotName = dataShot['code']


        # PRODUCTION: cf Project > Description
        strProd = "<no prod>"
        # TODO: retrieve this data from Shotgun

        listTimelog.append([strUserLogin, strUserLastName, strUserFirstName, strDate, strProd, options.project, strTaskName, strShotName, nbHoursDuration])
        
        
    # CSV export
    with open('statShotgun.csv','wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar= "\"", quoting=csv.QUOTE_MINIMAL)
        for line in listTimelog:
            writer.writerow(line)
            

    if len(listTimelog) < 1:
        print 'No timelog was found'
    else:
        print listTimelog
        print 'Data exported to statShotgun.csv'
        
    return listTimelog
            
        
        
        
        
if __name__ == '__main__':
    try :
        main()
    except Exception, e :
        print "ERROR %s\n" % ( e )
        exit(1)
        


