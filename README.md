# 文件管理——文件系统

## 项目目的

* 熟悉文件存储空间的管理和文件系统管理实现
* 熟悉文件的物理结构、目录结构和文件操作
* 加深对文件系统内部功能和实现过程的理解

## 开发环境

* 开发工具：**PyCharm** *2020.1.3  PC-201.8538.36*

* 开发语言：python


## 运行方式

1. 双击`dist`文件夹中`MainWindow.exe`运行

2. ```python
   python MainWindow.py
   ```

## 项目需求

在内存中开辟一个空间作为文件存储器，在其上实现一个简单的文件系统。

退出系统时，需将该文件系统的内容保存到磁盘上，以便下次可以将其恢复到内存中来。

## 项目功能

* 在<u>工作区</u><u>右键</u> **新建文件/文件夹**，或<u>点击</u>左上角`📁`**新建文件夹**
* <u>双击文本文件行</u> **打开文件**，可在记事本中**修改文件**，并选择是否保存修改内容
* <u>双击文件夹</u><u>行</u> **进入文件夹**
* 在<u>文件/文件夹行右键</u> **打开、删除、重命名**
* <u>左侧文件树</u>显示当前文件系统的**文件夹树形结构**
* <u>顶部文本框</u>显示当前**工作区的文件路径**
* <u>点击左上角</u>`⬆` **回退到上一级**文件夹
* <u>点击右上角</u>`格式化`按钮**格式化文件系统**

## 页面展示

<img src="\display\结构展示.png" alt="结构展示" style="zoom:50%;" />

### 新建文件/文件夹

<img src="\display\新建.png" alt="新建" style="zoom: 33%;" />

### 删除文件/文件夹

<img src="\display\删除.png" alt="删除" style="zoom: 33%;" />

### 查看文件/文件夹

<img src="\display\修改.png" alt="修改" style="zoom: 33%;" />

### 修改文件

<img src="\display\修改 (2).png" alt="修改 (2)" style="zoom: 33%;" />

### 重命名文件/文件夹

<img src="\display\重命名.png" alt="重命名" style="zoom: 33%;" />



## 设计

### 系统设计

####  文件存储空间管理

使用**显示链接**的方法，文件中的内容存放在磁盘不同的块中，每次创建文件时为文件分配数量合适的空闲块。每次写文件时按顺序将文件内容写在相应块中; 删除文件时将原先有内容的位置置为空即可。

#### 空闲空间管理

在**位图**的基础上进行改造，将存放磁盘上文件位置信息的**FAT表**与传统的位图进行结合，磁盘空闲的位置使用`EMPTY = -2`标识，放有文件的盘块存放文件所在的下一个盘块的位置，文件存放结束的盘块位置使用`EOF = -1`标识。

#### 文件目录

使用**多级目录结构**，文件夹`fcb`中的`_addr`项存储文件夹中的文件及子文件夹的`fcb`。

### 常量设计

| TXTFILE         | DIR          | EMPTY             | EOF                       |
| --------------- | ------------ | ----------------- | ------------------------- |
| 0, 表示文本文件 | 1,表示文件夹 | -2,表示磁盘块为空 | -1,表示磁盘块为文件结尾块 |

### 类设计

#### FCB

`FCB`类的数据结构如下：

| _id       | fcb标识符(唯一)                                           |
| --------- | --------------------------------------------------------- |
| _filename | 文件/文件夹名称                                           |
| _type     | 文件(TXTFILE), 文件夹(DIR)                                |
| _time     | 最近一次修改时间(%Y-%m-%d %H:%M:%S)                       |
| _addr     | 文本文件：物理地址的起始块; 文件夹：其中文件及文件夹的fcb |
| _size     | 文件/文件夹的大小(KB)                                     |
| _parent   | 文件/文件夹的父文件夹                                     |

#### 虚拟磁盘VirtualDisk

`Disk`类的数据结构如下：

| _fcbNums   | 磁盘中fcb数量            |
| ---------- | ------------------------ |
| _size      | 磁盘初始容量(1024KB)     |
| _blockSize | 磁盘块大小(1KB)          |
| _remainer  | 磁盘剩余块数             |
| _bitmap    | 位图                     |
| _memory    | 数据区，存储文本文件内容 |
| _root      | 虚拟根目录(Root)         |

## 功能实现

### 创建文件/文件夹

通过`disk._bitmap`判断当前磁盘是否有容量，

* 若当前磁盘空间不足，则创建失败，并弹出提示框
* 若当前磁盘空间充足，为该文件/文件夹创建对应的`fcb`，并将`fcb`加入该新文件/文件夹所在父文件夹的`_addr`列表中，同时修改当前UI界面

### 删除文件/文件夹

* 删除文件：根据该文件对应`fcb`中的磁盘存放起始块号`_addr[0]`，将其对应的`_bitmap`项置为`EMPTY`，回收虚拟磁盘的空间

* 删除文件夹：递归地将该文件夹中所有文件以及文件夹删除

* 删除文件/文件夹中内容后，均需将其`fcb`从父文件夹的`_addr`中删除

  ```python
  # 删除文本文件内容
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
          if fileFcb._addr==[]:
              return
          if fileFcb._type==TXTFILE:
              self.rmFile(fileFcb)
              return
          for f in fileFcb._addr:
              self.rm(f)
          fileFcb._addr=[]
          self._fcbNums-=1
  ```

### 读写文件

* 写文件：

  * 将待写入文件的内容`content`从`str`转为`bytes`,根据虚拟磁盘每块容量`1KB`计算所需块数`blockNums`
  * 判断文本文件写前空间<`blockNums`，需要继续分配磁盘块；否则回收多余的磁盘块
  * 将`content`对应的字节按顺序写入响应的磁盘块中

* 读文件：根据该文件对应`fcb`中的`_addr`以及虚拟磁盘的`_bitmap`依次查找拼接文件所在磁盘块的内容，将其由`bytes`转为`str`后显示到UI中

  ```python
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
  ```

### 重命名文件/文件夹

若用户确认修改文件/文件夹名称，进行新名称的重名检测修改后，修改该文件/文件夹的`fcb`中的`_filename`，同时修改UI界面。

### 格式化虚拟磁盘

重置虚拟磁盘的`_bitmap`, `_memory`等数据，同时修改UI界面。

```python
# 格式化虚拟磁盘
self._fcbNums=1
self._remainer = self._size // self._blockSize  # 磁盘余量
self._bitmap = [EMPTY] * self._remainer  # 位图（初始为空）
self._memory = [''] * self._remainer  # 数据空间
self._root = FCB(self._fcbNums,'Root', DIR, None, None)  # 虚拟根目录
self._ui._parentFcb = self._disk._root
self._ui._fcbs = self._disk._root._addr
# 重置UI
self.setupTableWidget() #重置页面的tableWwidget
self.fileTree.clear() # 重置页面的treeWidget
self.pathText.setText('Root>') # 重置pathText
```

### 回退上一级

* 若当前处于根目录，不进行操作

* 反之，将UI页面对应的文件夹置为当前UI文件夹的父文件夹，同时修改UI界面

  ```python
  self._parentFcb=self._parentFcb._parent
  self._fcbs=self._parentFcb._addr
  oldPath=self.pathText.displayText()
  newPath=oldPath.split('>')
  newPath='>'.join(newPath[:-2])+'>'
  self.pathText.setText(newPath)
  self._treeItem=self._treeItem.parent()
  ```

### 文件重名检测

使用模糊检测算法，首先获取当前文件夹目录中所有文件或文件夹名称列表`nameList`，遍历`nameList`，判断若有重名文件，应新添加的后缀数字`dupName`。检测完成后返回修正后的文件名。

```python
for f in self._ui._fcbs:
    if f._id!=id and f._type==type:
        nameList.append(f._filename)
for name in nameList:
    if name.startswith(fileName):
        dupNum+=1
if dupNum!=0:
    while fileName+'('+str(dupNum)+')' in nameList:
        dupNum+=1
    return fileName+'('+str(dupNum)+')'
return fileName
```

### 数据持久化

使用`python`内置`shelve`模块进行系统数据的存储。

关闭程序时，将虚拟磁盘的数据存储到`test_shelf.db`中；打开程序时读取`test_shelf.db`中的数据以初始化虚拟磁盘对象。

```python
# 存储
s['fcbNums']=self._ctrl._disk._fcbNums
s['remainer']=self._ctrl._disk._remainer
s['bitmap']=self._ctrl._disk._bitmap
s['memory']=self._ctrl._disk._memory
s['fcb']=self._ctrl._disk._root
# 读取
self._disk._fcbNums=s['fcbNums']
self._disk._remainer=s['remainer']
self._disk._bitmap=s['bitmap']
self._disk._memory=s['memory']
self._disk._root=s['fcb']
```

## 改进方向

* 可使用索引结构改进文件在磁盘中的存储方式，实现随机存取
* 可将`FCB`分解成符号目录项和基本目录项，减少磁盘访问次数
* UI界面可进一步美化，增加更多功能和快捷键

