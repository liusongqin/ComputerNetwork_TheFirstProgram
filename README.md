# ComputerNetwork_TheFirstProgram
2024/11/11 光棍节呐哈哈，又又又说在最前，这个是我之前大二计算机网络的作业，但是如果要参考代码当然是可以的，但是不能不动脑子就直接搬过去，代码要理解，或者有自己优化或者新增的地方，虽然这样说大家估计不会在意哈哈，因为大家写作业也挺累的。
代码在下面，因为当时写的很嗨，备份了几次，所以有点乱，要不就是备份中的内容，或者当前文件夹中的Receiver.py或者UnreliableSender.py


//说在最前：如老师文件说的，我不可能将代码分享出去，我只限于问题的讨论，具体代码的实现交给各位。
相关问题讨论

问题一：
Traceback (most recent call last):
File "D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Sender.py", line 4, in <module>
import Checksum
File "D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Checksum.py", line 4
SyntaxError: Non-ASCII character '\xbc' in file D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Checksum.py on line 4, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details

解决：1.文件路径不要用中文，改英文。
2.如果你的py文件中出现了中文，请在文件第一行上加上#coding=utf-8