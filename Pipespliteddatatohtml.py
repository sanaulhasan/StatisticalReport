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
MaxTransAndDateFile = "MaxTrans&DateFile"
SwitchResultFile = "switchresult"
AllNodesInfoFile = "AllNodesInfoFile"
AgentServerResultFile = "Agent_result.txt"
IVRServerResultFile = "IVR_result.txt"
AgentServerResultFileCMA = "Agent_result.txt"
IVRServerResultFileCMA = "IVR_result.txt"
AllModuleHtmlFile = "AllModuleHtmlFile.htm"
SwitchResultHtmlFile = "SwitchResultHtmlFile.htm"
GraphicalRepresentationImg = "graphical_representation.png"

modulesforGraph.sort()

#--------------------------------- Files -------------------------------------------#

def getModules():
    modules = []
    datafile = open(files[0], 'r')
    for data in range(0,30):
        data = datafile.readline();
        line = data.split('|')
        modules.append(line[3])
        mod = modules[1:len(modules)]
        mod.sort()
    return mod

def getdatafilenames(path):
    fileslist = []
    for i in range(6,0,-1):
        file = path+'Result_'+(datetime.datetime.now()-timedelta(hours=i)).strftime('%H')+'.txt'
        fileslist.append(file)
    return fileslist

def gettransCountfromModules(modulename, files):
  nums = []
  for i in files:
    datafile = open(i, 'r')
    for data in range(0,30):
        data = datafile.readline();
        line = data.split('|')
        if(line[3]==modulename):
            nums.append(int(line[1]))
  return nums

def getIdletimeModules(modulename, files):
  requireddata = []
  for i in files:
    datafile = open(i, 'r')
    for data in range(0,30):
        data = datafile.readline();
        line = data.split('|')
        if(line[3]==modulename):
            requireddata.append(line[2])
  requireddata.sort(reverse=True)
  return requireddata[0]

def getMaxTransDatefromFile(modulename, index):
    datafile = open(MaxTransAndDateFile, 'r')
    for data in datafile:
        line = data.split('|')
        if(line[0]==modulename):
            return line[index]

def gettransCountforlasthour(modulename, file):
        datafile = open(file, 'r')
        for data in range(0, 30):
            data = datafile.readline();
            line = data.split('|')
            if (line[3] == modulename):
                return line[1]

def setbgcolor(transcountforlasthour):
    if int(transcountforlasthour)==0:
        return 'red'
    else:
       return 'white'

def createhtmlforAllmodules():
    checkforchangeinMax()      #In this function first we will check if MaxTrans needs to update in MaxTransAndDateFile
    htmlFile = open(AllModuleHtmlFile, 'w')
    htmlFile.write('\n<!DOCTYPE html><html><head><style>table, td, th {border: 2px solid black;}table '
                   '{border-collapse: collapse;width: 80%;} th {background-color:yellow; }</style></head><body>')

    htmlFile.write('\n<p><h4>All,</h4></p><p><h4> Please find Below Periodic Service stats. Red highlighted services (if any) require attention.</h4> </p>'
                   '<table><tr style="text-align: center;" height="40"><th>Module</th><th>Max Idle time </th><th>Min Trans </th><th>Max Trans</th><th>Overall Max Trans</th><th>Overall Max Trans Date</th></tr>')
    for i in getModules():
        htmlFile.write('\n<tr  style="background-color: '+ setbgcolor(gettransCountforlasthour(i, files[5])).__str__() +'";><td>'+ i.replace('!','') +'</td><td align="center" > '+ getIdletimeModules(i, files).__str__() +' </td>'
        '<td align="center" > '+ min(gettransCountfromModules(i, files)).__str__() +' </td><td align="center" > '+ max(gettransCountfromModules(i, files)).__str__()  +' '
         '</td><td align="center" >'+getMaxTransDatefromFile(i.replace('!',''),1)+'</td><td align="center" >'+getMaxTransDatefromFile(i.replace('!',''),2)+'</td></tr>')

    htmlFile.write('\n<tr  align="center"  style="background-color: yellow";><td> <b>Server Type</b> </td><td><b>Maximum Idle Time</b> </td><td><b>IP Address</b></td></tr>')

    htmlFile.write('\n<tr align="center" ><td> Agent Server </td><td>'+ readfromAgentIVRresultfile(AgentServerResultFile, 4) +'</td><td> '+ readfromAgentIVRresultfile(AgentServerResultFile, 0) +' </td></tr>')
    htmlFile.write('\n<tr align="center" ><td> IVR Server </td><td>'+ readfromAgentIVRresultfile(IVRServerResultFile, 4) +'</td><td> '+ readfromAgentIVRresultfile(IVRServerResultFile, 0) +' </td></tr>')
    htmlFile.write('\n<tr align="center" ><td> Agent Server CMA </td><td>'+ readfromAgentIVRresultfile(AgentServerResultFileCMA, 4) +'</td><td> '+ readfromAgentIVRresultfile(AgentServerResultFileCMA, 0) +' </td></tr>')
    htmlFile.write('\n<tr align="center" ><td> IVR Server CMA </td><td>'+ readfromAgentIVRresultfile(IVRServerResultFileCMA, 4) +'</td><td> '+ readfromAgentIVRresultfile(IVRServerResultFileCMA, 0) +' </td></tr>')

    htmlFile.write('\n </tbody></table><br> <h3>Graphical representation of transactions for servies (last 6 hour):</h3><br></body></html>')
    htmlFile.close()
    createhtmlforSwitchresult(SwitchResultHtmlFile)
    makeplot()

def createhtmlforSwitchresult(htmlfile):
    htmlFile = open(htmlfile, 'w')
    htmlFile.write('\n<!DOCTYPE html><html><head><style>table, td, th {border: 2px solid black;}table '
                   '{border-collapse: collapse;width: 80%;} th {background-color:yellow; }</style></head><body>')

    htmlFile.write('\n <br><br><h3>Stats below represent number of nodes receiving/not-receiving transactions:</h3><br>'
                   '<table><tr style="text-align: center;" height="40"><th>Switch</th><th>No of Stations</th><th>Trans Received </th><th>No Transaction</th><th>Station Detail Having no Transaction </th></tr>')
    for i in getswitchresultmodules(AllNodesInfoFile):
        totalstations = len(getswitchresultstations(i))
        stationsnotfound = len(findinwsitchresult(getswitchresultstations(i)))
        stationsfound = totalstations - stationsnotfound
        htmlFile.write('\n<tr  style="background-color: '+ setbgcolor(stationsfound).__str__() +'";><td>'+ i +'</td><td align="center" > '+ totalstations.__str__() +' </td>'
        '<td align="center" > '+ stationsfound.__str__() +' </td><td align="center" >'+ stationsnotfound.__str__() +' </td><td align="center" >'+ swtichdetailhavingnoTrans(i) +'</td></tr>')

    htmlFile.write(' </tbody></table></body></html>')

    htmlFile.write('\n </tbody></table>')
    htmlFile.close()

def swtichdetailhavingnoTrans(switch):
    data = ' '
    all = findinwsitchresult(getswitchresultstations(switch))
    for i in all:
        data = data +' '+ i.replace('/', '   <b>(') + ')</b><br>'
    return data

def readfromAgentIVRresultfile(file,index):
    data1 = ''
    datafile = open(file, 'r')
    data = datafile.readline();
    data = datafile.readline();
    line = data.split()
    data1= line[index].replace('-','')
    return data1

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

def findinwsitchresult(allnodes):
    nodesnotfound = []
    for i in allnodes:
        if(searchnode(i)==0):
            nodesnotfound.append(i)
    return nodesnotfound

def searchnode(nodetofind):
    datafile = open(SwitchResultFile, 'r')
    if nodetofind in datafile.read():
        return 1
    else:
        return 0
    datafile.close()

def checkforchangeinMax():
    now = datetime.datetime.now().strftime('%B %d, %Y')
    modules = getModules()
    datafile = open(MaxTransAndDateFile, 'r')
    alldata = ''
    for data in datafile:
        alldata = alldata + data
    for i in modules:
        x = max(gettransCountfromModules(i, files))
        y = int(getMaxTransDatefromFile(i.replace('!', ''), 1))
        if x > y:
            strtoreplace = i.replace('!', '')+"|" + y.__str__() + "|" + getMaxTransDatefromFile(i.replace('!', ''), 2)
            strreplacewith = i.replace('!', '')+"|" + x.__str__() + "|" + now
            alldata = alldata.replace(strtoreplace, strreplacewith)
    datafile = open(MaxTransAndDateFile, 'w')
    datafile.write(alldata)

def getdatafromModules(modulename, files):
  nums = []
  for i in files:
    datafile = open(i, 'r')
    for data in range(0, 30):
        data = datafile.readline();
        line = data.split('|')
        if(line[3]==modulename):
            nums.append(int(line[1]))
  return nums

def getcolor(value):
    if value == 0:
       return 'r'
    else:
        return 'steelblue'

def makeplot():
    fig, ax = plt.subplots(7, 4)
    fig.subplots_adjust(wspace=0.4)
    fig.set_size_inches(10, 14)
    ax2 = np.ravel(ax)
    for count, i in enumerate(modulesforGraph):
        ax2[count].bar(['1', '2', '3', '4', '5', '6'], getdatafromModules(i, files),
        color=getcolor(min(getdatafromModules(i, files))), label=modulesforGraph[count].replace('!', ''))
        ax2[count].legend()
    plt.savefig(GraphicalRepresentationImg, bbox_inches='tight')

def makesubject(description):
    timedeltawithpacific = 12
    nowtemp = datetime.datetime.now() + timedelta(hours=timedeltawithpacific) - timedelta(minutes=int(datetime.datetime.now().minute))
    now = nowtemp.strftime('%B %d, %Y %I:%M %p')
    subject = '[' + now.__str__()+'] ' + description
    return subject

def sendemail(subject, sendFrom, sendTo, sendcc):

    gmail_user = 'youemailaddress@gmail.com'
    gmail_password = 'yourpassword'

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sendFrom
    msg['cc'] = sendcc
    msg['To'] = sendTo

    file1 = open(AllModuleHtmlFile, 'r')
    html1 = ""
    for data in file1:
        html1 = html1 + data

    file2 = open(SwitchResultHtmlFile, 'r')
    html2 = ""
    for data in file2:
        html2 = html2 + data

    fp = open('graphical_representation.png', 'rb')
    part2 = MIMEImage(fp.read())
    fp.close()

    part1 = MIMEText(html1, 'html')
    part3 = MIMEText(html2, 'html')

    msg.attach(part1)
    part2.add_header('Content-ID', '<image1>')
    msg.attach(part2)
    msg.attach(part3)

    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.ehlo()
    s.login(gmail_user, gmail_password)
    toaddrs = [sendTo] + [cc]
    s.sendmail(sendFrom, toaddrs, msg.as_string())
    s.quit()


#--------------------------------- Calling Functions -------------------------------------------#

#files2 = getdatafilenames(Path)
files = ['datafile1','datafile2','datafile3','datafile4','datafile5','datafile6']

createhtmlforAllmodules()

sendFrom = "sendingfrom@gmail.com"
sendTo = "sendingto@outlook.com"
cc = "cc@gmail.com"

sendemail(makesubject("Periodic Monitoring"), sendFrom, sendTo, cc)


#--------------------------------- Calling Functions -------------------------------------------#