#!/usr/bin/python
#filename: udo_pushto_api.py
from collections import defaultdict
import telnetlib,json,urllib
import os,sys,commands,multiprocessing
import smtplib  
import time
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
import sys
if not "/root/labroom" in sys.path:
    sys.path.append("/root/labroom")
import messageMode
#-------config------------------
devicefile = '/root/udt_pushto_API/udt_pushto_api.ini'              #Attention use full path 
#allarpmacfile =  '/root/udt/allarpmac.html-c'
allarpmacfile_1 =  '/root/udt/allarpmac.html'
allarpmacfile_2 =  '/root/udt/allarpmac_input.html'
pythonlog =  '/root/mylog.txt'
API_url = 'http://cmdb/find/updateSwitchIpPort.do'
linecount = 0
MAX_process = 100         #mutiprocessing

receiver = 'yihf@liepin.com'


def func(_index,_allarpmacfile):
    #print 'num:',_index
    line_list = []

    linesearch_cmd = "awk  -vbb="+str(_index)+" '{if ($1==bb){print }}' "+_allarpmacfile
    #print macsearch_cmd
    allresult =  os.popen(linesearch_cmd,'r').read()
    allresult_count =  allresult.count('\n')
    if (allresult_count == 1):
        #print "no mac-address infomation!"+'</p>'
        #os.system("echo "+begintime+' unknow1:'+allresult.split()[2] \
        #           +' '+allresult.split()[1]+"  no interface info"+" >> "+pythonlog)
        #print allresult.split()[2],allresult.split()[1],'unknow1'
        #api function...........
        return 'ok-error'
    if (allresult_count > 1):
        arpline = allresult.split('\n')[0]
        macline = allresult.split('\n')[int(allresult_count)-1]
        #find Agg interface
        if(macline.find('Bridge.Agg') != -1):
            #print "no if detail  info!"+'</p>'
            #os.system("echo "+begintime+' unknow2:'+allresult.split()[2]  \
            #       +' '+allresult.split()[1]+"  no interface detail info"+" >> "+pythonlog)
            #print arpline.split()[2],arpline.split()[1],'unknow2'
            #api function...........
            #print 'filter  this line'
            return 'ok-error'
        #general interface
        if_flag = macline.split()[4].find('/') 
        if_slot = macline.split()[4][if_flag-1:if_flag]
        if_num_e = macline.split()[4].find('<') 
        if_num = macline.split()[4][if_flag+3:if_num_e]
        src_ipif = macline.split()[1][6:] +'-'+if_slot
        search_sn_cmd = "awk -vdd="+src_ipif+" '{if ($1==dd){print $3 }}' "+ devicefile
        snresult =  os.popen(search_sn_cmd,'r').read()
        #print snresult
        snresult_count =  snresult.count('\n')
        if (snresult_count != 1):
            #print ' sn error!'
            os.system("echo "+begintime+' '+str(_index)+' '+search_sn_cmd+':'+"  find sn error"+" >> "+pythonlog)
            return 'sn error'
        #print arpline.split()[2],arpline.split()[1],if_num
        os.system("echo "+begintime+' data:'+allresult.split()[2] +' ' \
                   +allresult.split()[1]+' '+snresult.split()[0]+' '+if_num+' ' \
                   +macline.split()[1][6:]+'-'+macline.split()[4].replace('</p>','').replace('/','-')[10:]+" >> "+pythonlog)
        #api function...........
        one_line_list = []
        one_ip = allresult.split()[2]
        one_mac= allresult.split()[1]
        one_sn = snresult.split()[0]
        one_port_num = if_num
        one_description = macline.split()[1][6:]+'-'+macline.split()[4].replace('</p>','').replace('/','-')[10:]
        #transfrom_mac 
        newmac_t = one_mac[4:]
        if newmac_t.count('.') != 2:
            os.system("echo "+begintime+' '+"  mac format  error"+" >> "+pythonlog)
            return 'mac error!'
        newmac =  newmac_t[:2]+':'+newmac_t[2:4]+':'+newmac_t[5:7]+':'+newmac_t[7:9]+':'+newmac_t[10:12]+':'+newmac_t[12:14]
        one_result = {
            "server_ip"	: one_ip[3:],
            "server_sn"	: '',
            "server_network_mac"   : newmac,
            "switch_sn"	: one_sn,
            "switch_port"	: one_port_num,
            "switch_port_mac"	: '',
            #"descrip":one_description
        } 

        return one_result


    return 'other count error!'


if __name__ == "__main__":

    #---init paramater------
    begintime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    device_idct = defaultdict(lambda:defaultdict(dict))
    line_list = []
    os.system("echo "+begintime+"   udt_pushto_API  begin !  >> "+pythonlog)  # log to mylog.txt 


    #determine whether the two  file  exists 
    if(str(os.path.exists(allarpmacfile_1)).find('True') != 0):
        print 'allarpmac file not find!'
        os.system("echo "+ begintime +" arpmacfile not find!"+" >> "+pythonlog)  # log to mylog.txt
        sys.exit()
    if(str(os.path.exists(allarpmacfile_2)).find('True') != 0):
        print 'allarpmac file not find!'
        os.system("echo "+ begintime +" arpmacfile not find!"+" >> "+pythonlog)  # log to mylog.txt
        sys.exit()


    #append the first file to line_list
    numsearch_cmd_1 = "tail -n 1 "+ allarpmacfile_1
    tagidstr =  os.popen(numsearch_cmd_1,'r').read()
    allids_1 =  int(tagidstr.split()[0])+1
    #print allids
    os.system("echo "+ begintime +" file1 id num:"+str(allids_1)+" >> "+pythonlog)  # log to mylog.txt
    
    #main(allids)
    for index in range (0,allids_1):
        func_ret =  func(index,allarpmacfile_1)
        if str(func_ret).find('error') == -1:
            #print func_ret
            line_list.append(func_ret) 



    #append the second file to line_list
    numsearch_cmd_2 = "tail -n 1 "+ allarpmacfile_2
    tagidstr =  os.popen(numsearch_cmd_2,'r').read()
    allids_2 =  int(tagidstr.split()[0])+1
    #print allids
    os.system("echo "+ begintime +" file2 id num:"+str(allids_2)+" >> "+pythonlog)  # log to mylog.txt
    
    #main(allids)
    for index in range (0,allids_2):
        func_ret =  func(index,allarpmacfile_2)
        if str(func_ret).find('error') == -1:
            #print func_ret
            line_list.append(func_ret) 



    allline = len(line_list)
    print 'push to cmdb all line count:',allline
    temp_list = 'Data='+'{'+'infoList'+':'+str(line_list)+'}'
    print "hong->->",temp_list

        
    u = urllib.urlopen(API_url, temp_list)
    cmdb_ret =  u.read()
    print cmdb_ret
    cmdb_result =  str(cmdb_ret)[11:12]
    if int(cmdb_result) == 1:
        print 'push to API successful!'
        #os.system("echo "+begintime+"   push to API successful!   >> "+pythonlog)  
    else:
        print 'push to API error!'
        os.system("echo "+begintime+"   push to API error - -!  >> "+pythonlog)  

    # result report
    messageMode.sendtxtmail(str(allline)+" Udt data Push to API",0,'push to cmdb successful!',receiver,begintime)
    endtime =  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    os.system("echo "+endtime+"  udt_pushto_API over !  >> "+pythonlog)  # log to mylog.txt 
