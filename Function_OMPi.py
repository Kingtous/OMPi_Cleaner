import re as r
import DataStructure as DS
import os

#################################################################################################
#添加缺失函数

head='void ort_taskwait(int num){}\nvoid ort_taskenv_free(void *ptr, void *(*task_func)(void *)){}\nvoid ort_leaving_single(){}\nvoid * _ompi_crity;\nvoid ort_atomic_begin(){}\nvoid ort_atomic_end(){}\n'

#################################################################################################
#清除注释

def Clean_Mark(data):

    clean_sign_rule = r.compile(u'(\/\*(\s|.)*?\*\/)|(\/\/.*)')
    clean_sign_rule2=r.compile('void\s*\*\s*_task')
    clean_sign_rule3 = r.compile('return\s*\(\(\s*void\s*\*\)')
    txt =r.sub(clean_sign_rule3,'return ((void )',data)
    txt = r.sub(clean_sign_rule2,'void  _task',data)
    #print(r.search(clean_sign_rule2,txt).group())
    #txt = r.sub('void\s*\*\s*_task', 'void * _task', txt)
    txt = r.sub(clean_sign_rule, '', data)

    return data

#################################################################################################
#清除形如 # num "SourceName.c" 的注释

def Clean_Hashtag(data):

    content = data.readlines()

    clean_hashtag = r.compile(u'\s*#\s*\d+\s*')
    edit_static_sign=r.compile(u'static\s+void\s+_taskFunc')
    edit_taskenvFree_sign=r.compile(u'ort_taskenv_free')
    body =''

    for line in content:
        if r.match(clean_hashtag, line):
            body=body+'\n'
        elif r.match(edit_static_sign,line):
            body=body+line[6:]
        elif r.match(edit_taskenvFree_sign,line):
            body=body+'return;\n'
        else:
            body=body+line

    return body


#################################################################################################
#清除ompi处理OpenMP Code后产生的多余的if-else分支

def AnalyzeOpenMPElseClause(elseString):
    #此函数是为了提取出ompi处理task region后生成的if-else代码中else中的task名，并将task函数名以注释的形式返回
    regex = r.compile(u'ort_new_task\(.+;')
    content=r.search(regex,elseString)
    if content:
        name=r.split('[,()]',content.group())
        return name[1]+'(('+name[3]+')'+'0);'
    else:
        #未找到则报错
        return '\n //ERROR Parsing OpenMP Else Clause \n'


def Clean_if_else(data):
    clean_rule= r.compile(u'if\s*\(omp_in_final\(\)\s*\|\|\s*ort_task_throttling\(\)\)')

    content=data

    Pos=[]

    #get if position
    for match_content in r.finditer(clean_rule,content):
        st,ed=match_content.span()
        Pos.append([st,ed])

    #we must deal with if branch from the end pos
    for stPos,edPos in Pos[::-1]:

        s = DS.Stack()
        times=2
        flag=False  #cleared if
        elseClause = ''
        #First we use stack to clean the content of if
        while True:
            PosContent=content[edPos]
            if PosContent=='{':
                s.push(1)
                flag=True
            elif PosContent=='}':
                if(s.isEmpty()):
                    print("ERROR")
                    return
                else:
                    s.pop()
            if(times==1):
                elseClause=elseClause+PosContent
            #判断是否为else语段，是的话则放入一个list中，用函数名为AnalyzeOpenMPClause()返回引用的函数名(注释)
            edPos=edPos+1
            if s.isEmpty() and flag:
                times=times-1
                flag=False
                if times==0:
                    addition=AnalyzeOpenMPElseClause(elseClause)#设置标记
                    stContent=content[:stPos]
                    endContent=content[edPos:]
                    content = stContent+addition+endContent
                    break
    return content


#################################################################################################
#函数入口

def Trim(data_path):
    # 读取文件内容
    File=open(data_path,'r')
    # 处理文件内容
    data = Clean_Hashtag(File)
    data=Clean_Mark(data)
    data=Clean_if_else(data)
    # 写入处理后的文件内容
    (filepath, tempfilename) = os.path.split(data_path)
    (filename, extension) = os.path.splitext(tempfilename)
    Output=open(filename+'_trim'+extension,'w')
    Output.write(head)
    Output.write(data)
    print(data)
    #关闭输入输出流
    File.close()
    Output.close()
