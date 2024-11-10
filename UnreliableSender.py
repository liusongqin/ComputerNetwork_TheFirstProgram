#coding=utf-8
import sys
import socket
import getopt
import collections

import Checksum
import BasicSender

import time
from cryptography.fernet import Fernet

'''
This is an unreliable sender class that reads from a file or STDIN.
'''


#sys.argv =[sys.argv[0],'--help']
sys.argv =[sys.argv[0],'-fD:\study\sophomore1\ComputerNetwork\TheFirstProgram\CUG.jpg','-p33123','-a127.0.0.1']
class UnreliableSender(BasicSender.BasicSender):
    def handle_timeout(self):
        packet, sent_time = self.window[0]  # 获取窗口中的数据包和发送时间
        if packet is not None and time.time() - sent_time > 0.1:  # 如果数据包存在且已经超时
            print "Timeout for packet %s" % packet
            self.send(packet)  # 重传数据包
            #print "Resent: %s" % packet
            self.window[0] = (packet, time.time())  # 更新窗口中的发送时间

    def handle_new_ack(self, ack):
        #print "number: %s" % parts[1]
        base += 1
        del window[0]

    def handle_dup_ack(self, ack):
        self.send(packet)  # 重传数据包
        #print "Resent: %s" % packet
        window[0] = (packet, time.time())

    def log(self, msg):
        '''
        if self.debug:
            print msg
        '''
        print msg
    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            #print "recv: %s" % response_packet
            return True
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet
            return False

    # Main sending loop.
    def start(self):
        start_time = time.time()
        end_time = 0
        size =2990 #读取大小
        seqno = 0 #序列号
        msg_type = None #记录消息类型的
        msg = self.infile.read(size)
        
        #新功能
        rtt_estimate = 0.1  # 初始RTT估计值，单位为秒(这里的环路时间是发送端->接收端->发送端的时间)
        base = 0 #窗口第一个的序号
        window_size = 5
        window_max_size = 10
        loss_count = 0 #用来动态调整窗口大小（丢包，错误等情况）
        max_loss = 2#丢包超过这个数，说明网络环境不好，就减少窗口数
        window = []
        send_time=0
        rec_seqno_list =[]
        rtt_sample =0
        num_elements = 0
        send_count=0
        
        #6Fvkon6hqoiDc0JhOVvxJMBdkLYXY2xKxGrP7BpQ5Z8=
        #irisMX6WX1DoE415qmmVL2igR9EhuH_986vCsVo-zuE=
      
        #密钥
        key = b'6Fvkon6hqoiDc0JhOVvxJMBdkLYXY2xKxGrP7BpQ5Z8='
        # 创建一个Fernet对象
        cipher_suite = Fernet(key)

        while True:
            num_elements = len(window)
            #填充窗口window
            while num_elements < window_size and msg_type != 'end':
                #协议
                next_msg = self.infile.read(size)
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif next_msg == "":
                    msg_type = 'end'
                
                
                # 加密
                msg = cipher_suite.encrypt(msg)  # 需要加密的数据
                packet = self.make_packet(msg_type, seqno, msg)
                self.send(packet)
                print "sent: %s" % seqno
                send_count += 1
                window.append((packet,seqno))
                num_elements = len(window)
                msg = next_msg
                seqno += 1
                if msg_type == 'end':
                    break
            
            send_time = time.time()
            print "window_size: %s" % window_size
            
            #获取response
            while window:
                response = self.receive(rtt_estimate)
                print "recv: %s" % response
                packet, base = window[0]                
                if response is not None:
                    if self.handle_response(response):#校对校验码
                        #time.sleep(1)  
                        # rec_seqno_list                      
                        parts = response.split("|")
                        #动态调整时间
                        rtt_sample = time.time() - send_time  # 计算RTT（环路时间）样本值;window[-1][1]=最后一次发送的sent_time
                        if rtt_sample<2 and rtt_sample>0.005:#防止样本计算的是程序运行时间导致得到特别离谱的结果
                            rtt_estimate = 0.875 * rtt_estimate + 0.125 * rtt_sample  
                            #print "rtt_estimate: %s" % rtt_estimate
                        #动态调整滑动窗口
                        if window_size < window_max_size:
                            window_size += 1  # 如果收到新的确认，增大窗口大小  
                        #清理window
                        if parts[0]=='ack':
                            while base < int(parts[1]) and window:#清ack前面的数据                           
                                if window:
                                    del window[0]
                                    if window:
                                        base = window[0][1]

                        if parts[0]=='buffer':#清buffer所指的数据
                            for index, item in enumerate(window):#enumerate()函数获取元素的索引
                                if item[1] == int(parts[1]):
                                    del window[index]
                                    if window:
                                        base = window[0][1]                            
                        break #break window                    
                    else: #校验码不对                       
                        loss_count += 1  # 如果校验码不对，增加丢包计数
                        if loss_count > max_loss:  # 如果丢包计数超过max_loss，减小窗口大小
                            window_size = max(1,window_size - 1)
                            #print "window_size: %s" % window_size
                            loss_count = 0
                        
                        self.send(packet)  # 重传数据包
                        #print "Resent: %s" % packet
                        print "Resent:%s"% base
                        send_count += 1
                        window[0] = (packet,int(packet.split('|')[1]))
                        send_time = time.time()                
                elif response is None:  # 超时时间(单位是秒)
                    #time.sleep(rtt_estimate)#不知道要不要
                    #print "Timeout for packet "                     
                    loss_count += 1  # 如果超时，增加丢包计数                    
                    if loss_count > max_loss:  # 如果丢包（超时）计数超过max_loss，减小窗口大小
                        window_size = max(1,window_size - 1)
                        #print "window_size: %s" % window_size
                        loss_count = 0                    
                    self.send(packet)  # 重传数据包
                    #print "Resent: %s" % packet
                    print "Resent:%s"% base
                    send_count += 1
                    window[0] = (packet, int(packet.split('|')[1]))
                    send_time = time.time()
            if msg_type == 'end' and not window :
                break
        end_time = time.time()
        finish_time =end_time-start_time
        print "finish_time:%s"%  finish_time
        print "send_count:%s"%  send_count
        volume = (send_count*size)/1024
        print "volume(KB):%s "% volume
        self.infile.close()

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Unreliable Sender"
        print "Sends data unreliably from a file or STDIN."
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:", ["file=", "port=", "address="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
	print filename
	print dest
	print port
    s = UnreliableSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()