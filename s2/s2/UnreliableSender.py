#coding=utf-8
import sys
import socket
import getopt
import time

import Checksum
import BasicSender

'''
This is an unreliable sender class that reads from a file or STDIN.
'''

#sys.argv =[sys.argv[0],'--help']
sys.argv =[sys.argv[0],'-fD:study\sophomore1\ComputerNetwork\TheFirstProgram\CUG.jpg','-p33123','-a127.0.0.1']
class UnreliableSender(BasicSender.BasicSender):
    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # Main sending loop.
    def start(self):
        size =1000#读取大小
        seqno = 0 #序列号
        msg_type = None #记录消息类型的
        msg = self.infile.read(size)
        
        #新功能
        rtt_estimate = 0.1  # 初始RTT估计值，单位为秒(这里的环路时间是发送端->接收端->发送端的时间)
        base = 0 #窗口第一个的序号
        window_size = 5
        window_max_size = 10
        loss_count = 0 #用来动态调整窗口大小（丢包，错误等情况）
        max_loss = 10#错误超过这个数，说明网络环境不好，就减少窗口数
        window = []
        #temp = 0#拆window用的
        rec_seqno_list =[]
        
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
                #if seqno != 10:
                self.send(packet)
                #self.send(packet)
                print "sent: %s" % seqno
                window.append((packet, time.time(),seqno))
                msg = next_msg
                seqno += 1
                if msg_type == 'end':
                    break
            
            #获取response
            while window:
                response = self.receive(1)
                print "recv: %s" % response
                packet, sent_time, base = window[0] 
                
                #动态调整时间
                rtt_sample = time.time() - window[0][1]  # 计算RTT（环路时间）样本值;window[0][1]=sent_time
        
                if response is not None:
                    if self.handle_response(response):#校对校验码
                        #time.sleep(1)  
                        # rec_seqno_list                      
                        parts = response.split("|")                                               
                        #动态调整滑动窗口
                        if window_size < window_max_size:
                            window_size += 1  # 如果收到新的确认，增大窗口大小
                            #print "window_size: %s" % window_size
                            
                        #清理window
                        #print "int(parts[1]): %s" % int(parts[1])
                        #print "base %s" % base
                        while base < int(parts[1]):
                            if window:
                                #print "base %s" % base
                                base = window[0][2]
                                del window[0]
                            #print"base%s"%base
                            #base += 1
                        if window:
                            packet, sent_time, temp = window[int(parts[1])-base]
                            self.send(packet)
                        '''
                        if int(parts[1])<seqno:
                            for item in window:
                                packet, sent_time, temp = item
                                self.send(packet)
                        '''               
                        #动态调整时间(因为break的原因导致最下面的调整时间没有运行所以在这添加了一个，放在最下面是避免最后收到太多ack而调整了错误的时间)
                        rtt_estimate = 0.875 * rtt_estimate + 0.125 * rtt_sample  # 更新RTT估计值(一种加权移动平均算法，用于平滑网络延迟的变化)
                        #print "rtt_estimate: %s" % rtt_estimate    
                        break #break window
                    
                    else: #校验码不对
                        
                        loss_count += 1  # 如果校验码不对，增加丢包计数
                        if loss_count > max_loss:  # 如果丢包计数超过max_loss，减小窗口大小
                            window_size = max(1,window_size - 1)
                            print "window_size: %s" % window_size
                            loss_count = 0
                        
                        self.send(packet)  # 重传数据包
                        #print "Resent: %s" % packet
                        print "Resent"
                        window[0] = (packet, time.time(),int(packet.split('|')[1]))
                
                elif response is None:  # 超时时间(单位是秒)，0.04是估计值
                    #print "Timeout for packet " 
                    
                    loss_count += 1  # 如果超时，增加丢包计数
                    '''
                    if loss_count > max_loss:  # 如果丢包（超时）计数超过max_loss，减小窗口大小
                        window_size = max(1,window_size - 1)
                        print "window_size: %s" % window_size
                        loss_count = 0
                    '''
                    self.send(packet)  # 重传数据包
                    #print "Resent: %s" % packet
                    print "Resent%s"% base
                    window[0] = (packet, time.time(),int(packet.split('|')[1]))
                
                

                #动态调整时间
                #(0.875旧RTT的权重，0.125新RRT的权重)
                #加权的目的：1.防止新rrt不稳定 2.防止发太多后接收ack太多导致rrt增大而难以纠正
                rtt_estimate = 0.875 * rtt_estimate + 0.125 * rtt_sample  # 更新RTT估计值(一种加权移动平均算法，用于平滑网络延迟的变化)
                #print "rtt_estimate: %s" % rtt_estimate

            if msg_type == 'end' and not window :
                break   
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
