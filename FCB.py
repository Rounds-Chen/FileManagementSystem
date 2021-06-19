
TXTFILE=0 # 文本文件
DIR=1 # 文件夹

class FCB(object):
    def __init__(self,id,filename,type, time,addr,parent=None,size=0):
        self._id=id
        self._filename=filename # 文件（夹）名
        self._type=type # 文件（夹）类型
        self._time=time # 最近一次修改时间
        self._addr=[] # 指向文件（文件夹）地址
        if addr!=None:
            self._addr.append(addr)
        self._size=size # 文件（夹）大小
        self._parent=parent  # 文件（夹）的父文件夹

        
