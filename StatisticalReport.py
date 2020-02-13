#! /usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import datetime
import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#--------------------------------- Files -------------------------------------------#

Path = "/home/sdmonitor/scripts/"
SwitchResultFile = "switchresult"
AllNodesInfoFile = "AllNodesInfoFile"
IVRAgent = ['IVR Server', 'Agent Server','IVR Server CMA','Agent Server CMA']
IVRAgentFiles = ['IVR_result.txt','Agent_result.txt','IVR_result.txt','Agent_result.txt']
ServicesVerficationHtmlFile = "ServicesVerficationHtmlFile.htm"
nondbservices = ['ILV_Socket','WebService_GreenDot','BHNWebService','VBV','C-Admin']
nondbservicesfile = 'nondb'

#--------------------------------- Files -------------------------------------------#


def createhtml(htmlfile):
    htmlFile = open(htmlfile, 'w')
    htmlFile.write('\n<!DOCTYPE html><html><head><style>table, td, th {border: 2px solid black;}table '
                   '{border-collapse: collapse;width: 80%;} th {background-color:yellow; }</style></head><body>')
    htmlFile.write('\n <br><br><p>Hi,</p> <p>Please find below daily service verification stats.</p><br>'
                   '<table><tr style="text-align: center;" height="40"><th>Node Name</th><th>IP Address </th><th>Transaction Count</th><th>Comment</th></tr>')
    for j in getswitchresultmodules(AllNodesInfoFile):
        htmlFile.write('\n<tr  style="background-color: orange";><td align="center"  colspan="4"><b> ' + j + ' <b/></td></tr>')
        for i in getswitchresultstations(j):
            s1 = i.split('/')
            servicename = s1[0]
            serviceip = s1[len(s1)-1]
            comment = 'OK'
            bgcolor = '#94FA92'
            if i.startswith('10.'):
                serviceip = s1[0].replace('#','')
                servicename = s1[len(s1) - 1]
            transcount = gettranscountfromline(getlinehavingnode(i))
            if transcount == 0:
                comment = 'Not OK, Please check'
                bgcolor = '#C14B52'
            htmlFile.write('\n<tr><td align="left" > ' + servicename + ' </td>'
             '<td align="center" > ' + serviceip + ' </td><td align="center" >'+ transcount.__str__() +' </td><td  style="background-color: '+bgcolor+'";align="left" >'+ comment +'</td></tr>')
    for countfor, j in enumerate(IVRAgent):
        htmlFile.write(
            '\n<tr  style="background-color: orange";><td align="center"  colspan="4"><b>'+ j +'<b/></td></tr>')
        for i in getivragentdata(IVRAgentFiles[countfor]):
            s1 = i.split('|')
            servicename = j
            serviceip = s1[0]
            transcount = s1[1]
            comment = 'OK'
            bgcolor = '#94FA92'
            if int(transcount) == 0:
                comment = 'Not OK, Please check'
                bgcolor = '#C14B52'
            htmlFile.write('\n<tr><td align="left" > ' + servicename + ' </td>'
            '<td align="center" > ' + serviceip + ' </td><td align="center" >' + transcount.__str__() + ' </td><td  style="background-color: '+bgcolor+'"; align="left" >' + comment + '</td></tr>')
    for countfor, j in enumerate(nondbservices):
        htmlFile.write(
            '\n<tr  style="background-color: orange";><td align="center"  colspan="4"><b>' + j + '<b/></td></tr>')
        for countfor1, i in enumerate(getdataNonDbServices(j,1)):
            servicename = getdataNonDbServices(i,1)
            serviceip = getdataNonDbServices(i,0)
            transcount = getdataNonDbServicesTrancount(i)

            comment = 'OK'
            bgcolor = '#94FA92'
            if int(transcount[countfor1]) == 0:
                comment = 'Not OK, Please check'
                bgcolor = '#C14B52'
            htmlFile.write('\n<tr><td align="left" > ' + servicename[countfor1].__str__() + ' </td>'
            '<td align="center" > ' + serviceip[countfor1].__str__() + ' </td><td align="center" >' + transcount[countfor1].__str__() + ''
             ' </td><td  style="background-color: '+bgcolor+'"; align="left" >' + comment + '</td></tr>')

    htmlFile.write(' </tbody></table></body></html>')
    htmlFile.write('\n </tbody></table>')
    htmlFile.close()

def getdataNonDbServices(service,index):
    data1 =[]
    datafile = open(nondbservicesfile, 'r')
    for data in datafile:
        line = data.split('|')
        if (line[1] == service):
            data1.append(line[index])
    return data1

def getdataNonDbServicesTrancount(service):
    data1 =[]
    datafile = open(nondbservicesfile, 'r')
    for data in datafile:
        line = data.split('|')
        if line[1] == service:
            lc = int(line[2])
            cc = int(line[3])
            if cc >= lc:
                data1.append(cc-lc)
            else:
                data1.append(cc)
    return data1

def swtichdetailhavingnoTrans(switch):
    data = ' '
    all = findinwsitchresult(getswitchresultstations(switch))
    for i in all:
        data = data +' '+ i.replace('/', '   <b>(') + ')</b><br>'
    return data

def getswitchresultmodules(AllNodesInfoFile):
    Allmodules = []
    datafile = open(AllNodesInfoFile, 'r')
    for data in datafile:
        line = data.split('|')
        Allmodules.append(line[0])
    return Allmodules

def getswitchresultstations(modulename):
    datafile = open(AllNodesInfoFile, 'r')
    for data in datafile:
        line = data.split('|')
        if (line[0] == modulename):
            allstaions = []
            line2 = line[1].split(',')
            for data2 in line2:
                allstaions.append(data2)
    return allstaions

def gettranscountfromline(line):
    if line == 0:
        return 0
    else:
        count = line.split('|')
        return count[4]

def getlinehavingnode(nodetofind):
    datafile = open(SwitchResultFile, 'r')
    line = datafile.readline()
    while line:
        line = datafile.readline()
        if nodetofind in line:
            return line
    return 0

def makesubject(description):
    timedeltawithpacific = 12
    nowtemp = datetime.datetime.now() + timedelta(hours=timedeltawithpacific) - timedelta(minutes=int(datetime.datetime.now().minute))
    now = nowtemp.strftime('%A][%B %d, %Y')
    subject = '[' + now.__str__()+']' + description
    return subject

def sendemail(subject, sendFrom, sendTo, sendcc):

    gmail_user = 'youemailaddress@gmail.com'
    gmail_password = 'yourpassword'

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sendFrom
    msg['cc'] = sendcc
    msg['To'] = sendTo

    file1 = open(ServicesVerficationHtmlFile, 'r')
    html1 = ""
    for data in file1:
        html1 = html1 + data

    part1 = MIMEText(html1, 'html')

    msg.attach(part1)

    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.ehlo()
    s.login(gmail_user, gmail_password)
    toaddrs = [sendTo] + [cc]
    s.sendmail(sendFrom, toaddrs, msg.as_string())
    s.quit()

def getivragentdata(file):
    alldate = []
    datafile = open(file, 'r')
    for data in datafile:
        line = data.split()
        line1 = line[0]+'|'+line[1]
        alldate.append(line1)
    alldate.pop(0)
    return alldate


#--------------------------------- Calling Functions -------------------------------------------#



createhtml(ServicesVerficationHtmlFile)

sendFrom = "sendingfrom@gmail.com"
sendTo = "sendingto@outlook.com"
cc = "cc@gmail.com"

sendemail(makesubject("[Daily] Service Verification Stats"), sendFrom, sendTo, cc)

#--------------------------------- Calling Functions -------------------------------------------#