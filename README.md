# Computer-Network-RDT-Protocol

There are four protocols: Protocol_rdt2, Protocol_rdt22, Protocol_rdt3, Protocol_rdt31


The file Channel.py implements a model for an unreliable channel over which packets can be corrupted or lost. This model has the following parameters: Pc: The probability of a packet being corrupted, Pl: The probability of a packet being lost, Delay: The time it takes for a packet to travel over the channel and reach the receiver.


The file Protocol_rdt2.py implements the simple ACK/NAK based protocol rdt2.0 that can work when data packets can get corrupted. Check that this protocol indeed works by setting Pc>0 for the data-channel.
[Note: The protocol to be used can be specified in the file Testbench.py by modifying the linefrom Protocol_rdt<version> import *]


File Protocol_rdt22.py :  Developed an alternating-bit protocol which can work even when both the data and ack packets can get corrupted. Tested that the protocol works by simulating for a large amount of time or a large number of packets sent, with Pc>0 for both the data and ack channels.  


File  Protocol_rdt3.py : Implemented an alternating-bit protocol with Timeouts (rdt3.0) that can work when data or ack packets can be corrupted or lost. Tested that your protocol indeed works by simulating for a large amount of time or a large number of packets sent, with Pc>0 and Pl>0 for both the data and ack channels.
