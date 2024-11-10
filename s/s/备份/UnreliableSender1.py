#coding=utf-8
import sys
import socket
import getopt
import time
import collections

import Checksum
import BasicSender

'''
This is an unreliable sender class that reads from a file or STDIN.
'''


#sys.argv =[sys.argv[0],'--help']
sys.argv =[sys.argv[0],'-fD:study\sophomore1\ComputerNetwork\TheFirstProgram\CUG.jpg','-p33123','-a127.0.0.1']
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
        size =1000#读取大小
        seqno = 0 #序列号
        msg_type = None #记录消息类型的
        msg = self.infile.read(size)
        
        #新功能
        rtt_estimate = 0.1  # 初始RTT估计值，单位为秒(这里的环路时间是发送端->接收端->发送端的时间)
        base = 0
        window_size = 5
        window_max_size = 10
        loss_count = 0 #用来动态调整窗口大小（丢包，错误等情况）
        max_loss = 10#错误超过这个数，说明网络环境不好，就减少窗口数
        window = []
        
        #responses = []  # 创建一个空列表来存储所有的 response
        while True:
            
            #填充窗口window
            while seqno < base + window_size and msg_type != 'end':
                #协议
                next_msg = self.infile.read(size)
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif next_msg == "":
                    msg_type = 'end'
                packet = self.make_packet(msg_type, seqno, msg)
                self.send(packet)
                #print "sent: %s" % packet
                window.append((packet, time.time()))
                msg = next_msg
                seqno += 1
                if msg_type == 'end':
                    break
            
            #获取response
            while window:
                response = self.receive()
                print "recv: %s" % response
                packet, sent_time = window[0] 
                
                #动态调整时间
                rtt_sample = time.time() - window[0][1]  # 计算RTT（环路时间）样本值;window[0][1]=sent_time
                
                if response is not None:
                    if self.handle_response(response):#校对校验码
                        #time.sleep(1)                        
                        parts = response.split("|")
                        if base == int(parts[1]):#序列号重复
                            
                            loss_count += 1  # 如果重复，增加丢包计数
                            if loss_count > max_loss:  # 如果丢包计数超过max_loss，减小窗口大小
                                window_size = max(1,window_size - 1)
                                print "window_size: %s" % window_size
                                loss_count = 0
                            
                            print "same seqno"
                            self.send(packet)  # 重传数据包
                            print "Resent"
                            window[0] = (packet, time.time())
                        
                        else:#序列号未重复（也是唯一正确传输的代码）
                            #print "number: %s" % parts[1]
                            
                            #动态调整滑动窗口
                            if window_size < window_max_size:
                                window_size += 1  # 如果收到新的确认，增大窗口大小
                                print "window_size: %s" % window_size
                            
                            #清理window
                            while base != int(parts[1]):
                                base += 1
                                del window[0]
                            break 
                    
                    else: #校验码不对
                        
                        loss_count += 1  # 如果校验码不对，增加丢包计数
                        if loss_count > max_loss:  # 如果丢包计数超过max_loss，减小窗口大小
                            window_size = max(1,window_size - 1)
                            print "window_size: %s" % window_size
                            loss_count = 0
                        
                        self.send(packet)  # 重传数据包
                        #print "Resent: %s" % packet
                        print "Resent"
                        window[0] = (packet, time.time())
                
                elif rtt_sample > (rtt_estimate + 0.04):  # 超时时间(单位是秒)，0.04是估计值
                    print "Timeout for packet %s" % packet
                    
                    loss_count += 1  # 如果超时，增加丢包计数
                    if loss_count > max_loss:  # 如果丢包（超时）计数超过max_loss，减小窗口大小
                        window_size = max(1,window_size - 1)
                        print "window_size: %s" % window_size
                        loss_count = 0
                    
                    self.send(packet)  # 重传数据包
                    #print "Resent: %s" % packet
                    print "Resent"
                    window[0] = (packet, time.time())
                
                elif response is None:#未响应
                    #print "no response %s" % packet
                    print "no respons"
                    
                    loss_count += 1  # 如果未响应，增加丢包计数
                    if loss_count > max_loss:  # 如果丢包计数超过max_loss，减小窗口大小
                        window_size = max(1,window_size - 1)
                        print "window_size: %s" % window_size
                        loss_count = 0
                    
                    #等待一个环路的时间
                    time.sleep(rtt_estimate)
                    print "Resent"
                    self.send(packet)  # 重传数据包
                    #print "Resent: %s" % packet
                    window[0] = (packet, time.time())

                #动态调整时间
                #(0.875旧RTT的权重，0.125新RRT的权重)
                #加权的目的：1.防止新rrt不稳定 2.防止发太多后接收ack太多导致rrt增大而难以纠正
                rtt_estimate = 0.875 * rtt_estimate + 0.125 * rtt_sample  # 更新RTT估计值(一种加权移动平均算法，用于平滑网络延迟的变化)
                print "rtt_estimate: %s" % rtt_estimate

            if msg_type == 'end' and not window :
                break   
        self.infile.close()
'''               
                if time.time() - sent_time > 0.1:  # 超时时间(单位是秒)
                    print "Timeout for packet %s" % packet
                    self.send(packet)  # 重传数据包
                    print "Resent: %s" % packet
                    response = self.receive()
                    window[0] = (packet, time.time(),response)
                else:
                    if response is not None and self.handle_response(response):
                        base += 1
                        del window[0]
                    else:
                        print "No response received."
                        break
'''

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
