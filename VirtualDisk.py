import datetime

EMPTY=-2 # 位图中表示空
EOF=-1 # 位图中表示文件结尾

from FCB import *
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

from icos import *

class Disk(object):
    def __init__(self,size,blocksize):
        self._fcbNums=1 # 总的fcb数
        self._size=size # 磁盘总容量(KB)
        self._blockSize=blocksize # 每个盘块的大小(KB)
        self._remainer=self._size//self._blockSize #磁盘余量
        self._bitmap=[EMPTY]*self._remainer  # 位图（初始为空）
        self._memory=['']*self._remainer # 数据空间
        self._root=FCB(self._fcbNums,'Root',DIR,None,None) # 虚拟根目录


    # 格式化磁盘
    def format(self):
        self._fcbNums=1
        self._remainer = self._size // self._blockSize  # 磁盘余量
        self._bitmap = [EMPTY] * self._remainer  # 位图（初始为空）
        self._memory = [''] * self._remainer  # 数据空间
        self._root = FCB(self._fcbNums,'Root', DIR, None, None)  # 虚拟根目录

    # 创建新的空文件
    def newFile(self,parent):
        start=-1
        for i in range(0,len(self._bitmap)):
            if self._bitmap[i]==EMPTY:
                start=i
                self._bitmap[start]=EOF
                break
        if start==-1:
            print('创建文件失败！磁盘空间不足！')
            return []
        else:
            self._remainer-=1
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._fcbNums+=1
            newFcb=FCB(self._fcbNums,'新建文本文档',TXTFILE,now,start,parent)
            return newFcb

    # 读取文件
    def readFile(self,fileFcb:FCB):
        addr=fileFcb._addr[0]
        content=str.encode('',encoding='utf8')
        while self._bitmap[addr]!=EOF:
            content+=self._memory[addr]
            addr=self._bitmap[addr]

        content+=self._memory[addr]
        return content


    # 删除文本文件内容
    def rmFile(self,fileFcb:FCB):
        addr = fileFcb._addr[0]
        while self._bitmap[addr] != EOF:
            t = self._bitmap[addr]
            self._bitmap[addr] = EOF
            addr = t
            self._remainer += 1
        self._bitmap[addr] = EOF
        self._remainer += 1
        self._fcbNums-=1

    # 删除文件（夹）
    def rm(self,fileFcb:FCB):
        if fileFcb._addr==[]:
            return
        if fileFcb._type==TXTFILE:
            self.rmFile(fileFcb)
            return
        for f in fileFcb._addr:
            self.rm(f)
        fileFcb._addr=[]
        self._fcbNums-=1
        return


    # 将文件数据重新写入磁盘
    def writeMemory(self, start, content):
        content=str.encode(content,encoding='utf8') # 字符串转为字节串
        i=0
        while self._bitmap[start]!=EOF:
            self._memory[start]=content[i*1000:i*1000+1001]
            print('memeory[{}]:{}'.format(start,self._memory[start]))
            i+=1
            start=self._bitmap[start]
        self._memory[start]=content[i*1000:]

    # 新建文件夹
    def mkdir(self,parent):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._fcbNums+=1
        newFcb=FCB(self._fcbNums,'新建文件夹',DIR,now,None,parent)
        return newFcb

    # 修改文件
    def modify(self,fileFcb:FCB,content):
        byteNums=len(str.encode(content, encoding='utf8'))
        blockNums=byteNums//1000+(1 if byteNums%1000 else 0)
        fileFcb._size = blockNums

        blocks=int(fileFcb._size)
        if blocks==0:
            blocks+=1
        if blocks+self._remainer<blockNums:
            print('磁盘空间不足，无法保存!')
            msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '磁盘空间不足')
            msg_box.setWindowIcon(QIcon(':/icos/warn.ico'))
            msg_box.exec_()
        else:
            addr=fileFcb._addr[0]
            blockNums-=1
            while blockNums>0 and self._bitmap[addr]!=EOF:
                addr=self._bitmap[addr]
                blockNums-=1
            if blockNums==0 and self._bitmap[addr]!=EOF:
                t=0
                while self._bitmap[addr]!=EOF:
                    t=self._bitmap[addr]
                    self._bitmap[addr] = EMPTY
                    self._remainer +=1
                    addr=t
                self._bitmap[addr]=EMPTY
                self._remainer += 1
            else:
                for i in range(addr+1, len(self._bitmap)):
                    if blockNums<=0:
                        break
                    if self._bitmap[i]==EMPTY:
                        self._bitmap[addr]=i
                        self._remainer -= 1
                        addr=i
                        blockNums-=1
                self._bitmap[addr]=EOF
                self._remainer -= 1

        self.writeMemory(fileFcb._addr[0], content)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 文件新的修改时间
        fileFcb._time=now


