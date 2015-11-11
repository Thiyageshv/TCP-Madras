import socket
import os
import sys
import time 
import  Queue
from struct import *
import threading 
from threading import Thread
from SocketServer import ThreadingMixIn

class sendthread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        print "New thread started"
    def run(self):
        global ackmark
        global fintimeout
        global source_ip
        global dest_ip 
        global tcp_source
        global tcp_dest   
        global tcp_seq
        global tcp_ack_seq
        global tcp_doff
        global tcp_fin
        global tcp_syn
        global tcp_rst
        global tcp_psh
        global tcp_ack
        global tcp_urg
        global tcp_window
        global tcp_check
        global tcp_urg_ptr 
        global tcp_offset_res
        global tcp_flags
        global ackdict
        global expectedseq
        global seqwindow
        global pktdata
        global timeoutdata
        global rttdata
        global packetsize
        global stopflag 
        global winsize
        global filename
        global datatimeout
        global retran
        global senttimedata
        global lastack 
        senttimedata = {}
        packetsize = 570
        
        
        
        for i in range(1,winsize+1):
            item = i*packetsize + 1
            seqwindow.append(item)
        
          
        self.socket.settimeout(datatimeout)
        
        
        sendingseq = 1
        i=1
        tcp_seq = 1
       
        
        for message in iter(lambda: fin.read(550), ''):
            tcp_check = 0
            while sendingseq + packetsize not in seqwindow:
                
                continue 
            
                    
            #print i 
            #print "chunk:" , sendingseq 
            tcp_seq = sendingseq
            tcp_ack = 0
            tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
            tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
            


            source_address = socket.inet_aton( source_ip )
            dest_address = socket.inet_aton(dest_ip)
            placeholder = 0
            protocol = socket.IPPROTO_TCP
            
            tcp_length = len(tcp_header) + len(message)
      
 
            #psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
            psh = tcp_header + message  
           
            tcp_check = checksum(psh)  
            #print "checksum for chunk:", sendingseq , "is ", tcp_check
           
            tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
            packet = tcp_header + message
           # print "len of packet is " , len(packet)
            
            #print tcp_header
    
            print "sending packet" , tcp_seq 
            ackmark = 0
            sendingseq = sendingseq  + packetsize 
            expectedseq = sendingseq  #nextseq that is to be sent
            ackdict[expectedseq] = 0 # 0 indicates ack has not yet been received 
                #l = i-1
                #seqwindow[l] = sendingseq
            i=(i+1)
            senttime = time.time()    
            self.socket.sendto(packet, (source_ip, clientport))
            pktdata[tcp_seq] = packet 
            timeoutdata[tcp_seq] = senttime + datatimeout #datatimeout is retransmission timeout
           # print seqwindow 
            rttdata[tcp_seq] = senttime 
            senttimedata[tcp_seq] = senttime
            
            
            
                  
                
           # print " first" , i , "packets sent"
           
           # print ackdict.keys()
       # print seqwindow    
        finflag = 1
        b = 0
        
        
        while 0 in ackdict.values():
            continue
        stopflag = 1 
        
        
                              
            
        print "data done , sending fin packet"
       # print ackdict.keys()
        #print ackdict.values()
        tcp_fin = 1
        tcp_syn = 0
        tcp_ack = 0   
        tcp_seq = tcp_seq+1
        ITER = 0
        while True:
            
            tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
            FINpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
            stime = time.time()
            if ITER == 0:
                writelogsyn(FINpacket,"FIN packet sent ",0)
                rttdata[tcp_seq] = stime
                senttimedata[tcp_seq] = stime
            ITER = ITER + 1
            # time.sleep(7.0)  used this to check syn ack delay response at the client side
           
            self.socket.sendto(FINpacket, (source_ip, clientport))  
           
            #time.sleep(RTT)   
            while fintimeout == 0:
                pass  #wait till fintimeout values is update by the other thread
            
            if fintimeout == 1:
            #retransmit
                continue 
            elif fintimeout == 2:
                #exit
                print "received fin ack , connection terminated"
                
                print "Data transfer succesfful"
                print "Number of segments transmitted: ",len(ackdict)
                print "Number of retransmitted segments: ",retran
                print "Number of bytes transmitted" , os.stat(filename).st_size
                
                fin.close()
                self.socket.close()
                sys.exit()
                
        
              
        
            
        

class receiverthread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        print "New thread started"
    
    def run(self):
        global ackmark
        global fintimeout
        global ackdict
        global expectedseq
        global winsize 
        global seqwindow
        global timeoutdata
        global pktdata
        global packetsize
        global lastack 
        global stopflag 
        global changeflag
        global filename
        global datatimeout
        global rttdata
        global lastack
        changeflag = 0
        stopflag = 0
       
       
        while True:
            try: 
                ack, addr = self.socket.recvfrom(1024)
                receivedtime = time.time()
                acktcp_source, acktcp_dest, acktcp_seq, acktcp_ack_seq, acktcp_offset_res, acktcp_flags,  acktcp_window, acktcp_check, acktcp_urg_ptr = unpack('!HHLLBBHHH',ack)
                if acktcp_seq == lastack - packetsize + 2:
                    fintimeout = 2 
                if evaluateflag(acktcp_flags) == "ACK": 
                    print "Received ack" , acktcp_seq
                    timeoutdata[(acktcp_seq - packetsize)] = receivedtime
                    ackdict[acktcp_seq] = 1
                    thisseq = acktcp_seq - packetsize
                    if rttdata[thisseq]!= 0:
                        sampleRTT = receivedtime - rttdata[thisseq]
                        calculatetimeout(sampleRTT) 
                        rttdata[thisseq] = sampleRTT
                    else:
                        rttdata[thisseq] = receivedtime - senttimedata[thisseq]
                    
                    #print "setting ackmark " , ackmark
                    lock.acquire()
                   
                    if seqwindow[0] == acktcp_seq and stopflag == 0:  #if first element of window has been acked , let us change the window 
                        j=0
                        i=1
                        while i < winsize and (ackdict[seqwindow[i]] == 1):
                            i= i+1
                            
                        k=0
                        while k < i:
                            writelog((seqwindow[k]-packetsize))
                            k=k+1
                                
                        while i < winsize:    
                            seqwindow[j] = seqwindow[i]
                            j = j+1
                            i = i + 1
                     
                        while j < winsize:
                            
                            if expectedseq + packetsize <= lastack:
                                seqwindow[j] = expectedseq + packetsize 
                                ackdict[seqwindow[j]] = 0
                                expectedseq = expectedseq + packetsize
                                j = j+1
                            else:
                               # print "seqwindow done"
                                #stopflag=1
                                break
                       
                    lock.release()
                                          
                   # print seqwindow , "after receiving ack" , acktcp_seq
                   # print ackdict.keys()
                elif evaluateflag(acktcp_flags) == "ACKFIN":
                   
                    fintimeout = 2 # indicates finack has been received , no retranmission needed
                    finrtt = receivedtime - rttdata[(acktcp_seq-1)] 
                    rttdata[(acktcp_seq-1)] = finrtt
                    if changeflag == 0:
                        writelogsyn(ack,"FIN ACK received",finrtt)
                    changeflag = changeflag + 1
                    self.socket.close()
                    sys.exit()
            except socket.timeout:
                print "No packet has been received for the past 30 seconds "
                fintimeout = 1 #indicates timeout needed
                
                
class timerthread(Thread):
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        print "New thread started"
        
    def run(self):
        global ackmark
        global fintimeout
        global ackdict
        global expectedseq
        global winsize 
        global seqwindow
        global pktdata
        global timeoutdata
        global timerqueue
        global packetsize 
        global lastack 
        global changeflag
        global rttdata
        global datatimeout
        global retran
        
       
        seqwindow2 = []
        prev = 0 
        timerqueue = Queue.Queue()
        a = packetsize + 1
        for i in range(0,winsize):
            seq = seqwindow[i]-packetsize
            seqwindow2.append(seqwindow[i])  #duplicate seqwindow
            timerqueue.put(seq)
        endwin = seqwindow[winsize-1] - packetsize 
        dupseq = endwin + packetsize  
       # print "dulicate seqwindow ", seqwindow2 
        
        
        while seqwindow[0] not in ackdict.keys(): 
            pass
        
        pkt = timerqueue.get()
        ackpkt = pkt + packetsize 
            
        while True:
            while ackpkt in ackdict.keys() and pkt in timeoutdata.keys() and pkt in pktdata.keys():
                   
                if ackdict[ackpkt] != 1:
                   # print "timer dealing with packet " , pkt
                    while ackdict[ackpkt] == 0 and time.time() < timeoutdata[pkt]:
                        pass
                    if ackdict[ackpkt] == 0 and time.time() >= timeoutdata[pkt]:
                        print "retrasnmitting packet " , pkt
                        retran = retran + 1
                        senttime = time.time()
                        #ackdict[ackpkt] = 2
                        self.socket.sendto(pktdata[pkt], (source_ip, clientport))
                        timeoutdata[pkt] = senttime + datatimeout
                        rttdata[pkt] = 0 #karne's algorithm : marking retrasnmitted packets to avoid them for next rtt calculation
                        timerqueue.put(pkt)
                            
                    elif ackdict[ackpkt] == 1:
                        lock.acquire()
                        if seqwindow2[0] == ackpkt:
                            j=0
                            i=1
                            while i < winsize and (ackdict[seqwindow2[i]] == 1):
                                i= i+1
                                
                            while i < winsize:    
                                seqwindow2[j] = seqwindow2[i]
                                j = j+1
                                i = i + 1
                            #  acknext = seqwindow[i-1]
                            #  print "acknext is" , acknext
                            while j < winsize:
                            
                                if dupseq + packetsize <= lastack:
                                    seqwindow2[j] = dupseq + packetsize 
                                     
                                    dupseq = dupseq + packetsize
                                    endwin = endwin + packetsize 
                                    timerqueue.put(endwin)
                                    j = j+1
                                  
                                else:
                                      #stopflag=1
                                      break 
                            
                        lock.release()
                       
               
                elif (ackdict[ackpkt] == 1):
                         lock.acquire()
                        
                         if seqwindow2[0] == ackpkt:
                            
                             j=0
                             i=1
                             while i < winsize and (ackdict[seqwindow2[i]] == 1):
                                 i= i+1
                                
                             while i < winsize:    
                                 seqwindow2[j] = seqwindow2[i]
                                 j = j+1
                                 i = i + 1
                             #  acknext = seqwindow[i-1]
                             #  print "acknext is" , acknext
                             while j < winsize:
                            
                                 if dupseq + packetsize <= lastack:
                                     seqwindow2[j] = dupseq + packetsize 
                                     
                                     dupseq = dupseq + packetsize
                                     endwin = endwin + packetsize 
                                     timerqueue.put(endwin)
                                     j = j+1
                                  
                                 else:
                                       #stopflag=1
                                       break
                         lock.release()
                
                            
                    
                pkt = timerqueue.get()
                ackpkt = pkt + packetsize
                #  print "waiting for packet" , pkt
                
                
        
            
        
        #sending process has started
                 
def writelog(seqnum):
    global pktdata
    global senttimedata
    global rttdata
    global filename 
    
    rtt = rttdata[seqnum]
    packet = pktdata[seqnum]
    tcpheader = packet[:20]
    tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr = unpack('!HHLLBBHHH',tcpheader)
    packettype = "DATA "
    writemsg = "Packet Type: " + packettype + "Timestamp: " + str(senttimedata[seqnum]) + "\n"
    
    acktcp_seq = tcp_seq + 1
    writemsg = writemsg + " seq number of packet sent: " + str(tcp_seq) + "\n"
    writemsg = writemsg + " header details: " + "\n"
    
    writemsg =  writemsg + " source: " + str(tcp_source) + " "
    writemsg = writemsg + " destination: " + str(tcp_dest) + " " + "FLAGS: " + str(tcp_flags) + " " +  "windowsize: " + str(tcp_window) + " " + "checksum: " + str(tcp_check) + "\n"
    
    writemsg = writemsg + " Recieved ack details: " + " ack sequence number: " + str(acktcp_seq) + "\n"
   
    writemsg = writemsg + " Roundtrip time for the segment was: " + str(rtt) + "\n"
    if filename != "stdout":
        log.write(writemsg)
        log.write("\n\n")
    elif filename=="stdout":
        sys.stdout.write(writemsg + "\n\n")

def writelogsyn(packet,packettype,rtt):
    
    tcpheader = packet[:20]
    tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr = unpack('!HHLLBBHHH',tcpheader)
    packettype = packettype
    if tcp_seq in rttdata:
        writemsg = "Packet Type: " + packettype + "Timestamp: " + str(rttdata[tcp_seq]) + "\n"
    else:
        writemsg = "Packet Type: " + packettype + "\n"
        
    log.write(writemsg)
    acktcp_seq = tcp_seq + 1
    writemsg = "seq number of packet sent: " + str(tcp_seq) + "\n" 
    writemsg = writemsg + "header details: " + "\n"
    
    writemsg = writemsg + " source: " + str(tcp_source) + " "
    writemsg = writemsg + " destination: " + str(tcp_dest) + " " + "FLAGS: " + str(tcp_flags) + " " +  "windowsize: " + str(tcp_window) + " " + "checksum: " + str(tcp_check) + "\n"
    log.write(writemsg)
    writemsg = writemsg + " Recieved ack: " + " ack sequence number: " + str(acktcp_seq) + "\n"
    
    if rtt!=0:
        writemsg = writemsg + " Roundtrip time of the segment was: " + str(rtt) + "\n"
        log.write(writemsg)
        log.write("\n\n")
    if filename != "stdout":
        log.write(writemsg)
        log.write("\n\n")
    elif filename=="stdout":
        sys.stdout.write(writemsg + "\n\n")
    
    
    
                 
               
def calculatetimeout(sampleRTT):
    global estimatedRTT
    global devRTT
    global datatimeout
    estimatedRTT = 0.875*estimatedRTT + 0.125*sampleRTT
    if sampleRTT > estimatedRTT:
        devRTT = 0.75*devRTT + 0.25*(sampleRTT-estimatedRTT)
    else:
        devRTT = 0.75*devRTT + 0.25*(estimatedRTT-sampleRTT)
    datatimeout = estimatedRTT + 4*devRTT
    print "new timneout value is" , datatimeout
    
            

def checksum(data):
    s = 0
   
    if len(data)%2==1:
        data = data + "\0"   #padding
   
        # loop taking 2 characters at a time
    for i in range(0, len(data), 2):
        w = ord(data[i]) + (ord(data[i+1]) << 8 )
       
        s = s + w
       
        
    s = (s>>16) + (s & 0xffff);
   
    s = s + (s >> 16);
   
    #complement and mask to 4 byte short
    s = ~s & 0xffff
    
  
    return s
    
def evaluateflag(flags):
    num = 6
    bits = [(flags >> bit) & 1 for bit in range(num -1, -1 , -1)]
    
   
    flagval = ""
    for position,bit in enumerate(bits):
        if position == 1 and bit == 1:
            flagval = flagval + "ACK"
        if position == 5 and bit == 1:
            flagval = flagval + "FIN" 
    print flagval        
    if flagval == "":
        return "data" 
    else:       
        return flagval
        
        
        
        
lock = threading.Lock() 
global retran
retran = 0
global estimatedRTT 
estimatedRTT = 0 
global devRTT 
devRTT = 0  
global senttimedata 
global datatimeout
global lastack   
global packetsize 
packetsize = 570    
global seqwindow   
seqwindow = []     
global winsize 
if int(sys.argv[6])%570 == 0:
    winsize = int(sys.argv[6])/570  
else:
    winsize = int(sys.argv[6])/570  + 1
global filename 
filename = sys.argv[1]
global expectedseq
global fintimeout 
fintimeout = 0 # to indicate if FIN Ahas been transmitted successfully   
global ackmark 
ackmark = 0 
global ackdict   
ackdict = {} 
global pktdata
pktdata = {}  
global timeoutdata
timeoutdata = {}  
global timerqueue
timerqueue = Queue.Queue
global source_ip  
source_ip = "127.0.0.1"
global dest_ip
dest_ip = sys.argv[2]
global UDP_PORT
UDP_PORT = int(sys.argv[4]) #5005
global clientport 
clientport = int(sys.argv[3])  #6000
global changeflag 
global rttdata
rttdata = {}   
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((source_ip, int(UDP_PORT)))
# tcp header fields
global tcp_source
tcp_source = UDP_PORT # source port
global tcp_dest   
tcp_dest = clientport   # destination port
global tcp_seq 
tcp_seq = 0
global tcp_ack_seq
tcp_ack_seq = 0
global tcp_doff
tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
#tcp flags
global tcp_fin
tcp_fin = 0
global tcp_syn
tcp_syn = 1
global tcp_rst
tcp_rst = 0
global tcp_psh
tcp_psh = 0
global tcp_ack
tcp_ack = 0
global tcp_urg
tcp_urg = 0
global tcp_window
    #   maximum allowed window size
global tcp_check
tcp_check = 0
global tcp_urg_ptr 
tcp_urg_ptr = 0
global tcp_offset_res
 
tcp_offset_res = (tcp_doff << 4) + 0
global tcp_flags 
tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

# the ! in the pack format string means network order
logfilename = sys.argv[5]
log = open(logfilename, 'w+')
error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
try:
    fin = open(filename, 'rb')
except error_to_catch:
    print "file not found"
    sys.exit()
except (OSError, IOError) as e:
    print "File IO error"
    sys.exit()

filesize = os.stat(filename).st_size
print "filesize is ", filesize 
if filesize%550 == 0:
    chunknum = filesize/550
else:
    chunknum = (filesize/550) + 1
print "number of chunks is '", chunknum , "'"

lastack = chunknum * packetsize + 1
print "'",lastack,"'"
if chunknum < winsize:
    winsize = chunknum

tcp_window = winsize
while True:
    i=1
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    rtcp_source, rtcp_dest, rtcp_seq, rtcp_ack_seq, rtcp_offset_res, rtcp_flags,  rtcp_window, rtcp_check, rtcp_urg_ptr = unpack('!HHLLBBHHH',data)
    writelogsyn(data,"SYN received",0)
    print "received a SYN packet", rtcp_flags
    
    tcp_ack = 1
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
    print tcp_flags 
    SYNACKpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
    SYNACKpacket = SYNACKpacket + filename
    # time.sleep(7.0)  used this to check syn ack delay response at the client side
    writelogsyn(SYNACKpacket,"SYNACK sent",0) 
    flag = 0
    while flag != 1:
        sock.sendto(SYNACKpacket, (source_ip, clientport))
        senttime = time.time()
        print "sent ack for SYN"
        while time.time() - senttime < 6.0:
            ack, addr = sock.recvfrom(1024)
            acktcp_source, acktcp_dest, acktcp_seq, acktcp_ack_seq, acktcp_offset_res, acktcp_flags,  acktcp_window, acktcp_check, acktcp_urg_ptr = unpack('!HHLLBBHHH',ack)
            if evaluateflag(acktcp_flags) != "ACK" or acktcp_seq != 1: 
                print "this is not ack , waiting for ack still" 
            else:
                rcvtime = time.time()
                R = rcvtime - senttime #initial roundtriptime
                writelogsyn(ack,"ACK received for SYNACK",R) 
                estimatedRTT = R
                devRTT = R/2 
                datatimeout = 3*R
                flag = 1
                break    
    
    print "ack received ,three way handshake complete ,  can now start sending data" , acktcp_flags
    break
    
    
    
threads = [] 

try:
    
    newthread = sendthread(sock)
    newthread.daemon = True
    newthread2 = receiverthread(sock)
    newthread2.daemon = True
    newthread3 = timerthread(sock)
    newthread3.daemon = True
    newthread.start()
    newthread2.start()
    newthread3.start()
    threads.append(newthread)
    threads.append(newthread2)
    threads.append(newthread3)
    while True:
        for t in threads:
            t.join(600)
            if not t.isAlive():
                break
        break        
            
            
except KeyboardInterrupt:
    sys.exit()
    
  
sys.exit()    