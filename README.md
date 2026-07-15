# gjftools

用于gjf文件批量生成、提交、后处理的各类脚本

## gjftools

`gjftools.py`是于自主编程的gjf文件生成工具的源代码，主要用于统一格式的gjf文件生成，具体功能以及使用方式请参考`gjftools_tutorials.ipynb`

## qg09

`qg09`是用于在newconsole上便捷提交任务的脚本，该文件夹中其余脚本都是支持的各类任务的提交子脚本，用于参考

目前该脚本存放在`/usr/bin/qg09`，因此所有用户均可**直接使用**，简要操作说明如下：  
```bash
qg09 -p 8 -f /home/yzh/gjftools/example/models/basic-opt.gjf
```
在命令行中直接输入以下命令，效果为：提交`/home/yzh/gjftools/example/models/basic-opt.gjf`作为gaussian任务输入文件，并使用8核计算  
返回信息应为
```
Input file directory: /home/yzh/gjftools/example/models 
Input file name: /home/yzh/gjftools/example/models/basic-opt.gjf 
Job name: basic-opt 
Number of processors: 8 
Your job 75644 ("basic-opt") has been submitted
```
常用功能还有
```bash
qg09 -p 8 -a
```
即提交当前所在文件夹下所有未被提交（无同前缀.o .po文件）的gjf文件

还可指定任务类型，默认为g09计算，`-x`为gaussian调用xtb计算，`-c`为rpipfmin构象搜索计算，`-t`为CREST构象搜索计算，`-s`为sobEDA能量分解计算。  
如以下命令即为提交当前文件夹下的`gauxtb.gjf`文件进行高斯调用xtb计算：
```bash
qg09 -p 1 -x -f gauxtb.gjf
```

`-q`参数后可接指定host名称，用于指定或避免将任务提交到该host上  
如要指定提交到g0409上，则:
```bash
qg09 -p 8 -a -q g0409
```
如指定不提交到g0409上，则：
```bash
qg09 -p 8 -a -q !g0409
```

## xtb优化
1. 获取初始结构并把想要固定的结构固定。例：在找到过渡态之后，把过渡态的核心结构（如即将成的键或者断的键，金属还原消除的二面角）freeze掉。

2. 修改gjf文件title如下：

    %mem=XGB 

    %nprocshared=1

    #p opt=(modredundant,nomicro) external='./xtb.sh' ugbs
  
执行xtb任务时，一般来讲单核运行，即指定-x时，默认运行核数（不指定-p 核数）就是1

3. 从`gjftools/qg09/xtb_scripts`下获取xtb.sh，genxyz，extderi三个文件到gjf的同一目录下并修改文件权限。修改的命令为
```bash
 chmod 755 $file_name
```
755代表用户可以读、写、执行该文件，组内成员以及其他人只可以读和执行该文件
对该命令感兴趣可以到csdn搜索`Linux用户权限相关命令`阅读相关文章

4. 提交xtb优化任务，命令如下
```bash
  qg09 -p 8 -x -f $file_path
```
输出的log文件即为xtb优化结果。

## rpip构象搜索任务
1. xtb优化

2. 编辑初始结构文件：
将xtb优化后获得的log文件中最后一帧结构再次保存为gjf文件。之后对坐标部分进行如下修改:在元素符号后，具体坐标前输入数字0，之后根据结构，将不愿使之旋转的键（比如甲基，叔丁基等高度对称的基团的成键）两端的原子后的数字改为数字 -1。
在文件末尾增加add bond数据，以保证目标原子间的键连。
具体方法如下：在冻结命令后空一行输入
`addbond：Y`
。Y为数字，且等于要保证键连原子的对数。之后在下一行输入每对原子的序号。如
`B 1 2 F`
具体可参考`gjftools/qg09/rpipmin_scripts/fminstd.gjf`

3. 获取提交任务所需文件：
从`gjftools/qg09/rpipmin_scripts`获取xtb.sh，genxyz，extderi，fmincfg.dat，rpipfmin.exe文件并修改文件权限。

4. 提交构象搜索任务，命令如下
```bash
  qg09 -c -f $file_path
```
执行rpip构象搜索任务时，缺省-p命令的话默认8核运行


## gauprocess（各类后处理脚本）

具体使用方式若有疑问可以查看源码或者问yzh

### gauprocess

通过以下命令调用
```bash
python gauprocess.py
```
功能为将当前文件夹下所有log文件和纯数字文件夹中的log文件集中于一个新的log文件夹中，并生成`gauprocess.csv`，其中包含各log文件的运行状态、关键计算结果。若有fchk文件，则会复制于一个新的fchk文件夹中。

若指定`-c`参数，将会同时删除当前文件夹下所有带有同前缀.po文件而没有.o文件的gjf文件及其对应.po文件。

### run_goodvibes

(需要装有goodvibes的python环境)
调用方式：
```bash
python run_goodvibes.py -d target/dir/ -t 338.15 -c
```
对`target/dir`中的所有（有freq）计算结果进行goodvibe自由能校正，`-t`指定温度为338.15K，`-c`指定删除中间输出dat文件。

### sobedaprocess

调用方式：
```bash
python sobedaprocess.py -d target/dir/
```
对批量sobeda运行输出的log文件进行数据提取，生成`sobedaprocess.csv`

