import orcid
import os
import codecs
import multiprocessing
import time


DELIMITER='\t'
ls_attributes=['orcid','lastName','firstName','keywords','biography','title','subtitle','citation','external_ids','url']

# check sum (the last position) calculation
def generateCheckDigit(baseDigits):
    total=0;
    for i in range(len(baseDigits)):
        digit=baseDigits[i]
        total=(total+int(digit))*2
    remainder=total%11;
    result=(12-remainder)%11
    if(result==10): result="x"
    else: result=str(result)
    return baseDigits[0:4]+"-"+baseDigits[4:8]+"-"+baseDigits[8:12]+"-"+baseDigits[12:]+result

def getPubList(strid):
    data=orcid.get(strid)
    ls=data.publications
    print 'Got {0} publications!'.format(len(ls))
    ls_new=[]
    for index in range(len(ls)):
        l=[]
        l.append(replaceNone(ls[index].title))
        l.append(replaceNone(ls[index].subtitle))
        l.append(replaceNone(ls[index].citation))
        l.append(replaceNone("".join(ls[index].external_ids)))
        l.append(replaceNone(ls[index].url))
        ls_pub.append(l)
    return ls_new

# replace None
def replaceNone(string):
    return '' if string is None else string

def getRecords(strid, orcidStart, orcidEnd):
    ls_records=[]
    #print strid
    try:
        author=orcid.get(strid)
        if(author.orcid==None):
            #print strid,' - None'
            return ls_records
        else:
            print 'Pass:{0}'.format(strid)
            if author.biography is not None: biography= author.biography['value']
            else: biography=''
            familyName=author.family_name
            givenName=author.given_name
            name=[familyName,givenName]
            if author.keywords is not None: keywords="".join(author.keywords)
            if author.researcher_urls is not None: urls=author.researcher_urls
            # publications
            ls_pub=[]
            if author.publications !=[]:
                ls=author.publications
                for index in range(len(ls)):
                    l=[]
                    l.append(replaceNone(ls[index].title))
                    l.append(replaceNone(ls[index].subtitle))
                    l.append(replaceNone(ls[index].citation))
                    if(ls[index].external_ids!=None):
                        l.append(replaceNone(str(ls[index].external_ids[0])))
                    else: l.append("None")
                    l.append(replaceNone(ls[index].url))
                    ls_pub.append(l)
            else:
                ls_pub=[""]
            for pub in ls_pub:
                line=strid+DELIMITER+DELIMITER.join(name)
                line=line+DELIMITER+keywords+DELIMITER+repr(biography)+DELIMITER
                line=line+DELIMITER.join(pub)
                ls_records.append(line)
            return ls_records
    except:
        logPath=os.getcwd()+"/"+str(orcidStart)+"_"+str(orcidEnd)+"_log.txt"
        print "Error:{0}".format(strid)
        WriteLog(logPath,strid)
        return None

def WriteFile(filePath, ls_data, ls_attributes):
    f=codecs.open(filePath,mode='w',encoding='utf8')
    f.write(DELIMITER.join(ls_attributes)+"\n")
    for line in ls_data:
        f.write(line+"\n")
    f.close()
    print 'Write file successfully!'

def WriteLog(filePath, strLine):
    f=codecs.open(filePath,mode='a',encoding='utf8')
    f.write(strLine+"\n")
    f.close()
    #print 'Write log {0}'.format(strLine)

# generate a full list of orcids
def GenerateList(orcidStart, orcidEnd):
    listPath=os.getcwd()+"/"+str(orcidStart)+"_"+str(orcidEnd)+"_list.txt"
    f=codecs.open(listPath,'w',encoding='utf8')
    for n in range(int(orcidStart),int(orcidEnd)+1):
        n_str=str(n)
        n_str="0"*(15-len(n_str))+n_str
        orcidReal=generateCheckDigit(n_str)
        f.write(orcidReal+"\n")
    f.close()
    print 'Generate list successfully at {0}'.format(listPath)
    return listPath

def ConvertIntStr(orcid):
    if(type(orcid)==int):
        return "0"*(15-len(str(orcid)))+str(orcid)
    else:return orcid

def Download(orcidStart,orcidEnd, sleepBase):
    st=time.time()
    orcidStart=ConvertIntStr(orcidStart)
    orcidEnd=ConvertIntStr(orcidEnd)
    listPath=GenerateList(orcidStart, orcidEnd)
    f=open(listPath,'rb')
    ls_orcid=[x.strip() for x in f.readlines()]
    f.close()

    ls_whole=[]
    # assign a count for try times (less than 10) & tryid
    count=1
    tryid=''
    while(len(ls_orcid)>0):
        orcidReal=ls_orcid.pop()
        if (len(ls_orcid)+1)%sleepBase==0:
            time.sleep(60) #sleep 1 minute
        ls=getRecords(orcidReal, orcidStart, orcidEnd)
        if ls is not None:
            count=0
            tryid=orcidReal
            for line in ls:
                ls_whole.append(line)
        else:
            if(count<10):
                if(tryid==orcidReal):
                    count+=1
                else:tryid=orcidReal
                print 'Recycle:{0},count:{1}'.format(orcidReal,count)
                ls_orcid.insert(len(ls_orcid),orcidReal)
                time.sleep(1) # sleep 1 second
            else:
                errorPath=os.getcwd()+"/"+str(orcidStart)+"_"+str(orcidEnd)+"_error.txt"
                WriteLog(errorPath,tryid)
                continue
    filePath=os.getcwd()+"/"+str(orcidStart)+"_"+str(orcidEnd)+"_data.txt"
    WriteFile(filePath,ls_whole,ls_attributes)
    et=time.time()
    print "Downloaded. Path: {0}, Cost: {1} mins".format(filePath,float(et-st)/60.0)
        
if __name__=="__main__":
    #test
    #Download('000000020035000','000000020036000',100000)

    #2013-05-10
    #orcidStart='000000015000000'
    #orcidEnd=  '000000020000000'

    #2013-05-14
    #orcidStart='000000020000000'
    #orcidEnd=  '000000025000000'

    #2013-05-16
    #orcidStart='000000025000000'
    #orcidEnd=  '000000030000000'

    #2013-05-18
    orcidStart='000000030000000'
    orcidEnd=  '000000035000000'

    #real end
    #orcidEnd='000000035000000'

    processes=[]
    base=(int(orcidEnd)-int(orcidStart))/10
    for i in range(0,10):
        startIndex=int(orcidStart)+base*i
        endIndex=startIndex+base
        processes.append(multiprocessing.Process(target=Download, args=(startIndex,endIndex,base/10)))
    for p in processes:
        p.start()
    for p in processes:
        p.join      
