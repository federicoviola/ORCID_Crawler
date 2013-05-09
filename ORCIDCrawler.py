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

def getRecords(strid):
    ls_records=[]
    #try:
    author=orcid.get(strid)
    if(author.orcid==None):
        #print strid,' - None'
        return None
    else:
        print strid
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
            line=line+DELIMITER+keywords+DELIMITER+biography+DELIMITER
            line=line+DELIMITER.join(pub)
            ls_records.append(line)
    #except:
    #   print orcid.get(strid)
    return ls_records

def WriteFile(filePath, ls_data, ls_attributes):
    f=codecs.open(filePath,mode='w',encoding='utf8')
    f.write(DELIMITER.join(ls_attributes)+"\n")
    for line in ls_data:
        f.write(line+"\n")
    f.close()
    print 'Write file successfully!'

def Download(orcidStart,orcidEnd, sleepBase):
    st=time.time()
    ls_whole=[]
    for n in range(int(orcidStart),int(orcidEnd)+1):
        #time interval
        if n%sleepBase==0:
            time.sleep(600)
        n_str=str(n)
        n_str="0"*(15-len(n_str))+n_str
        orcidReal=generateCheckDigit(n_str)
        ls=getRecords(orcidReal)
        if ls is not None:
            for line in ls:
                ls_whole.append(line)
    filePath=os.getcwd()+"/"+str(orcidStart)+"_"+str(orcidEnd)+".txt"
    WriteFile(filePath,ls_whole,ls_attributes)
    et=time.time()
    print "Downloaded. Path: {0}, Cost: {1} mins".format(filePath,float(et-st)/60.0)
        
if __name__=="__main__":
    #test
    #Download('000000020035100','000000020045100',100000)

    #2013-05-08
    orcidStart='000000015000000'
    orcidEnd=  '000000020000000'

    #2013-05-01
    #orcidStart='000000020000000'
    #orcidEnd=  '000000025000000'

    #2013-05-02
    #orcidStart='000000025000000'
    #orcidEnd=  '000000030000000'

    #2013-05-03
    #orcidStart='000000030000000'
    #orcidEnd=  '000000035000000'

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
    

        
