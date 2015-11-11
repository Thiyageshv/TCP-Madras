import socket
import sys
import time 
from struct import *
import threading 
from threading import Thread
from SocketServer import ThreadingMixIn




class sendthread(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        print "New thread started"
    def run(self):
        print "entering 1"
        
def sendack(stcp_seq):
    global UDP_IP
    global receiverport
    global ackmark
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

    print "Sending ack for chunk" , stcp_seq
    tcp_seq = stcp_seq + 1
    tcp_ack = 1
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
    ackpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
    #time.sleep(3.0)
    sock.sendto(ackpacket, (UDP_IP, UDP_PORT))
    

class receivethread(Thread):
    def __init__(self):
        Thread.__init__(self)
        print "New thread started"
    
    def run(self):
        global UDP_IP
        global receiverport
        global ackmark
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
        global packetsize
        global pktdata
        global filename
        global winsize
        global receiveddata
        receiveddata = {}
        stopflag = 0
        seqwindow = []
        rcvdict = {}
        pktdict = {}
        sock.settimeout(60.0)
       
        file = open(filename, 'w+')
        
        print "entering"
        
      
        packetsize = 570
        k=1
        for i in range (1,winsize+1):
            seqwindow.append(k)
            k = k + packetsize
        expectedseq = seqwindow[winsize-1]
        for t in seqwindow:
            rcvdict[t] = 0
        
        while True:
            
            try:
                packet, addr = sock.recvfrom(2048)
                rcvtime = time.time()
                tcp_check = 0
                tcp_header = packet[:20]
                message = packet[20:]
                #print tcp_header
                #print message 
                
                
                stcp_source, stcp_dest, stcp_seq, stcp_ack_seq, stcp_offset_res, stcp_flags,  stcp_window, stcp_check, stcp_urg_ptr = unpack('!HHLLBBHHH',tcp_header)
                clienttcp_header = pack('!HHLLBBHHH' , stcp_source, stcp_dest, stcp_seq, stcp_ack_seq, stcp_offset_res, stcp_flags,  stcp_window, tcp_check, stcp_urg_ptr)
                psh = clienttcp_header + message 
                clienttcp_check = checksum(psh)
                pktdata[stcp_seq] = packet
                receiveddata[stcp_seq] = rcvtime
               
               # print "received tcp_check is ", stcp_check
                #print "client tcp_check" , clienttcp_check 
                
                    
                # print "chunk checksum received:", i ,stcp_check
                #print evaluateflag(stcp_flags)
                if evaluateflag(stcp_flags) == "data" and stcp_seq in seqwindow:
                  
                    if clienttcp_check == stcp_check:
                        print "checksums match"
                        if seqwindow[0] == stcp_seq:  #if first element of window has been acked , let us change the window 
                            pktdict[stcp_seq] = message 
                            rcvdict[seqwindow[0]] = 1 
                            j=0
                            i=1
                            while i < winsize and rcvdict[seqwindow[i]]==1:
                                i= i+1
                            
                            k=0
                            while k < i:
                                item = pktdata[seqwindow[k]]
                                file.write(item[20:]) 
                                writelog(item,seqwindow[k])
                                k=k+1
                            
                            while i < winsize:    
                                seqwindow[j] = seqwindow[i]
                                j = j+1
                                i = i + 1
                          #  acknext = seqwindow[i-1]
                          #  print "acknext is" , acknext
                          
                            while j < winsize:
                                seqwindow[j] = expectedseq + packetsize 
                                rcvdict[seqwindow[j]] = 0
                                expectedseq = expectedseq + packetsize
                                j = j+1
                               
                        else:
                            rcvdict[stcp_seq] = 1 #1 indicates packet is received
                            pktdict[stcp_seq] = message
                            
                        acknum = stcp_seq - 1 + packetsize
                        print "Seqwindow after receiving packet " , stcp_seq , "is " ,seqwindow
                        sendack(acknum)
                    else:
                        print "checksums don't match"
                        continue
                    
               
                elif evaluateflag(stcp_flags) == "FIN":
                    print "connection is going to be terminated , sending FIN ACK"
                    tcp_seq = stcp_seq + 1
                    tcp_ack = 1
                    tcp_fin = 1
                    tcp_syn = 0
                    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
                    finackpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
                    sock.sendto(finackpacket, (UDP_IP, UDP_PORT))
                    sock.close() 
                    sys.exit()
            except socket.error:
                print "socket error"
              
            
def writelog(packet,seqnum):
    global pktdata
    global receiveddata
    packet = pktdata[seqnum]
    tcpheader = packet[:20]
    tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr = unpack('!HHLLBBHHH',tcpheader)
    packettype = "DATA "
    writemsg = "Packet Type: " + packettype + "Timestamp: " + str(receiveddata[seqnum]) + "\n"
 
    acktcp_seq = tcp_seq + 1
    writemsg = writemsg + " seq number of packet received: " + str(tcp_seq) + "\n"
    writemsg = writemsg + "header details: " + "\n"
   
    writemsg = writemsg + " source: " + str(tcp_source) + " "
    writemsg = writemsg + " destination: " + str(tcp_dest) + " " + "FLAGS: " + str(tcp_flags) + " " +  "windowsize: " + str(tcp_window) + " " + "checksum: " + str(tcp_check) + "\n"
    log.write(writemsg)
    writemsg = writemsg + " Sending ack details: " + " ack sequence number: " + str(tcp_seq+1) + "\n"
    
    if filename != "stdout":
        log.write(writemsg)
        log.write("\n\n")
    elif filename=="stdout":
        sys.stdout.write(writemsg + "\n\n")
    
"""    
def writelogsyn(packet,packettype):
    
    tcpheader = packet[:20]
    tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr = unpack('!HHLLBBHHH',tcpheader)
    packettype = packettype
    if tcp_seq in rttdata:
        writemsg = "Packet Type: " + packettype + "Timestamp: " + " "+ "\n"
    else:
        writemsg = "Packet Type: " + packettype + "\n"
        
    log.write(writemsg)
    acktcp_seq = tcp_seq + 1
    writemsg = "seq number of packet sent: " + str(tcp_seq) + "\n" 
    writemsg = writemsg + "header details: " + "\n"
    log.write(writemsg)
    writemsg = "source: " + str(tcp_source) + " "
    writemsg = writemsg + " destination: " + str(tcp_dest) + " " + "FLAGS: " + str(tcp_flags) + " " +  "windowsize: " + str(tcp_window) + " " + "checksum: " + str(tcp_check) + "\n"
    log.write(writemsg)
    writemsg = "Sent ack: " + " ack sequence number: " + str(tcp_seq + 1) + "\n"
    log.write(writemsg)
    log.write("\n\n")     
"""       
        
        
        
        
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
    
    for position,bit in enumerate(bits):
        if position == 1 and bit == 1:
            return "ACK"
        if position == 5 and bit == 1:
            print "FIN pack"
            return "FIN"    
    return "data" 
    
    
    
    
       
global UDP_IP
UDP_IP = sys.argv[3]#"127.0.0.1"
global server_ip
server_ip = "192.168.73.1"
global UDP_PORT
UDP_PORT = int(sys.argv[4])#5005
global receiverport 
receiverport = int(sys.argv[2])#5000
global pktdata
pktdata={}
global receiveddata
receiveddata = {}
print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

    

# tcp header fields
global tcp_source
tcp_source = receiverport   # source port
global tcp_dest
tcp_dest = UDP_PORT   # destination port
global tcp_Seq
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
global tcp_Ack
tcp_ack = 0
global tcp_urg
tcp_urg = 0
global tcp_window
tcp_window = 3   #   maximum allowed window size
global tcp_check
tcp_check = 0
global tcp_urg_ptr
tcp_urg_ptr = 0
global tcp_offset
global filename
filename = sys.argv[1]
global winsize
 
tcp_offset_res = (tcp_doff << 4) + 0
tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
i = 0
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, int(receiverport))) 
sock.settimeout(5.0)  # Timeout in case SYN,ACK gets lost
while True:
    SYNpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
    try:
        sock.sendto(SYNpacket, (UDP_IP, UDP_PORT))
        print "SYN to server " , tcp_flags
    except socket.error:
        print "not able to connect , trying again after", 1 << i , "seconds"
        if i <= 5:
            time.sleep(1 << i)
            i=i+1
            continue
        else:
            print "error , not able to eastablish connection"
            break   
    try:
        synack, addr = sock.recvfrom(2048)
        header = synack[:20]
        
    except socket.timeout:
        print " syn ack not received yet , sending syn again" 
        continue   
        
    stcp_source, stcp_dest, stcp_seq, stcp_ack_seq, stcp_offset_res, stcp_flags,  stcp_window, stcp_check, stcp_urg_ptr = unpack('!HHLLBBHHH',header)
    if evaluateflag(stcp_flags) != "ACK" or stcp_seq!=0:
        print "packet received is not syn ack , resending syn ", stcp_flags
    else:
        
        print "syn ack received"
        winsize = stcp_window
        break
tcp_seq = 1
tcp_ack = 1
tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
SYNACKpacket = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)
sock.sendto(SYNACKpacket, (UDP_IP, UDP_PORT))
print "ack packet sent " , tcp_flags 


print "Can now start receiving data"
logfile = sys.argv[5]
log = open(logfile,'w+')


threads = [] 

try:
    newthread = sendthread()
    newthread.daemon = True
    newthread2 = receivethread()
    newthread2.daemon = True
    newthread.start()
    newthread2.start()
    threads.append(newthread)
    threads.append(newthread2)
    
    for t in threads:
        t.join(600)
      
            
            
except KeyboardInterrupt:
    sys.exit()
    
  
sys.exit() 
