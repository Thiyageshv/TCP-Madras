TCP-Madras : Implementation

Readme

There are two scripts , server and client. The client would request the server to transfer the file and server would then transfer the file pseudo TCP mechanism. Reliable TCP mechanisms over UDP.  The server side (server.py) and receiver side (client.py) are invoked using appropriate commands. 
The server side uses three threads to provide reliable transmissions. 
One thread takes care of the timer , one for just receiving and processing the acks and updating the window according to the acks received , the final thread simply sends chunks by reading from file and once the reading is done and all acks have been received, it sends the FIN packet. 

How packet loss is implemented  ? 
Individual acks have been used in this system instead of cumulative ack.  A sequence window is always maintained and a separate hashmap data structure that contains the the sequence numbers of packets as keys and a flag variable as a value. The flag variable is one if ack has been received, 0 if it is not received. 
In the receiver thread , the receiver checks the ack of the received packet. It then updates the hash map data structure’s flag value of it. On a parallel thread the timer keeps track of the hash map data structure . Timer runs for one element in the sequence window at a time. If ack has been received for that element ( which it knows from referring the hash map data structure) then it will start the timer for the next element. Meanwhile the timeout values are changed as soon as an unambiguous packet is received. ( Karne’s algorithm) .The timeout variable is a global variable. So it is guaranteed that the timer always uses the most recent timeout value. The timer maintains a queue of packets. It checks a packet , if timeout occurs , retransmits it and adds it back to the queue with the new finishing value or otherwise discards it if ack has been received.  In this way whenever there is a loss , the ack will never be received , the timer will eventually timeout for the packet and the packet gets retransmitted until ack has been received. 
In order delivery is guaranteed at the receiver end where the receiver writes the packets in order before updating a sequence window for the next iteration.

Checksum error also triggers retransmission. The chunk size used is 570. 550 bytes of data and 20 bytes of the header.  The checksum is checked by the following method. The receiver assumes the checksum to be 0. Calculates the checksum in the same way sender calculates it and then matches the calculated checksum with the received checksum. Separate hashmaps are maintained to store timeout values of each packet, sent times of each packet to calculate the RTT. We use them just for printing the log otherwise the data is flushed periodically. 


