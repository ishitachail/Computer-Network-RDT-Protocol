# SimPy model for the Reliable Data Transport (rdt) Protocol 2.2 (ALTERNATING BIT PROTOCOL)

#
# Sender-side (rdt_Sender)
#	- receives messages to be delivered from the upper layer 
#	  (SendingApplication) 
#	- Implements the protocol for reliable transport
#	  using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#	- receives packets from the unrealible channel via calls to its
#	  rdt_rcv() function.
#	- implements the receiver-side protocol and delivers the collected
#	  data to the receiving application.

# Author: Ishita Chail


import simpy
import random
from Packet import Packet
import sys

# the sender can be in one of these four states:
WAITING_FOR_CALL0 =1
WAITING_FOR_ACK0=2
WAITING_FOR_CALL1=3
WAITING_FOR_ACK1=4

#the receiver can be in any of these states:
WAITING_FOR_0_FROM_BELOW=5
WAITING_FOR_1_FROM_BELOW=6

class rdt_Sender(object):

	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.channel=None
		
		# some state variables
		self.state = WAITING_FOR_CALL0 #initialized state to Waiting for call0
		self.seq_num=0 #initialized the seq number to 0
		self.packet_to_be_sent=None

	
	def rdt_send(self,msg):
		# This function is called by the 
		# sending application.
		# create a packet, and save a copy of this packet
		# for retransmission, if needed

		#can be in two states waiting for call0 or call1
		if self.state==WAITING_FOR_CALL0:
			#create a packet with seq_num=0 and payload with data given by sending app
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			#change seq_num to 1 for alternating bit protocol
			self.seq_num=1
			print("TIME:",self.env.now,"RDT_SENDER: Making packet 0 and sending ", self.packet_to_be_sent)
			#send the packet over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			#after sending packet 0, now wait for ACK0
			self.state=WAITING_FOR_ACK0
			return True
		elif self.state==WAITING_FOR_CALL1:
			#similar logic for this part
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			print("TIME:",self.env.now,"RDT_SENDER: Making packet 1 and sending ", self.packet_to_be_sent)
			self.channel.udt_send(self.packet_to_be_sent)
			self.seq_num=0
			self.state=WAITING_FOR_ACK1
			return True
		else:
			return False
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		#rdt_Sender can receive either an ACK0 or an ACK1 or an corrupted packet
		#handling all cases
		if(packt.payload=="ACK0"):
			if (self.state==WAITING_FOR_ACK0):
				#everything is fine
				print("TIME:",self.env.now,"RDT_SENDER: Received Correct ACK ")
				self.state=WAITING_FOR_CALL1
			elif (self.state==WAITING_FOR_ACK1):
				#received an wrong ACK 
				print("TIME:",self.env.now,"RDT_SENDER: Received Wrong ACK ")
				#resends the packet
				self.channel.udt_send(self.packet_to_be_sent)
		elif(packt.payload=="ACK1"):
			if (self.state==WAITING_FOR_ACK1):
				#everything is fine
				print("TIME:",self.env.now,"RDT_SENDER: Received Correct ACK ")
				self.state=WAITING_FOR_CALL0
			elif (self.state==WAITING_FOR_ACK0):
				#received an wrong ACK 
				print("TIME:",self.env.now,"RDT_SENDER: Received Wrong ACK ")
				#resends the packet
				self.channel.udt_send(self.packet_to_be_sent)
		elif(packt.payload=="$H!T"):
			#if packet corrupted , resend it
			self.channel.udt_send(self.packet_to_be_sent)
			
		

class rdt_Receiver(object):
	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None
		self.state=WAITING_FOR_0_FROM_BELOW
		

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		# check whether the packet is corrupted
	
		#rdt_Receiver can be in two states: Waiting for 0 or 1 from below
		if (self.state==WAITING_FOR_0_FROM_BELOW):
			if(packt.payload=="$H!T" or packt.seq_num==1):
				#packet got corrupted or got an duplicate packet
				response = Packet(seq_num=0, payload="ACK1") #Note: seq_num for the response can be arbitrary. It is ignored.
				#sending an wrong ACK
				# send it over the channel
				print("TIME:",self.env.now,"RDT_RECEIVER: Making ACK1 and sending",packt)
				self.channel.udt_send(response)
			elif(packt.seq_num==0):
				#received an correct packet
				#sending correct ACK
				print("TIME:",self.env.now,"RDT_RECEIVER: Making ACK0 and sending",packt)
				#deliver the data to receiver app
				self.receiving_app.deliver_data(packt.payload)
				response=Packet(seq_num=0, payload="ACK0")
				self.channel.udt_send(response)
				#change the state
				self.state=WAITING_FOR_1_FROM_BELOW
		elif (self.state==WAITING_FOR_1_FROM_BELOW):
			#similar logic as before
			if(packt.payload=="$H!T" or packt.seq_num==0):
				response = Packet(seq_num=0, payload="ACK0") 
				print("TIME:",self.env.now,"RDT_RECEIVER: Making ACK0 and sending",packt)
				self.channel.udt_send(response)
			elif(packt.seq_num==1):
				print("TIME:",self.env.now,"RDT_RECEIVER: Making ACK1 and sending",packt)
				self.receiving_app.deliver_data(packt.payload)
				response=Packet(seq_num=0, payload="ACK1")
				self.channel.udt_send(response)
				self.state=WAITING_FOR_0_FROM_BELOW
				