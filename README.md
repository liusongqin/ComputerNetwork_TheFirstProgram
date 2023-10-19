# ComputerNetwork_TheFirstProgram
相关问题讨论

问题一：
Traceback (most recent call last):
File "D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Sender.py", line 4, in <module>
import Checksum
File "D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Checksum.py", line 4
SyntaxError: Non-ASCII character '\xbc' in file D:\正经事\学习\大二上课程内容\计算机网络\bears-tp\Checksum.py on line 4, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details

解决：1.文件路径不要用中文，改英文。
2.如果你的py文件中出现了中文，请在文件第一行上加上#coding=utf-8