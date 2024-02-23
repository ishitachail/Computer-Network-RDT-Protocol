# SimPy model for the Reliable Data Transport (rdt) Protocol 2.2 (ALTERNATING BIT PROTOCOL)

#
# Sender-side (rdt_Sender)
#	- receives messages to be delivered from the upper layer 
#	  (SendingApplication) 
#	- Implements the protocol for reliable transport
#	 using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#	- receives packets from the unrealible channel via calls to its
#	rdt_rcv() function.
#	- implements the receiver-side protocol and delivers the collected
#	data to the receiving application.

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
		self.state = WAITING_FOR_CALL0
		self.seq_num=0
		self.packet_to_be_sent=None
	
		#additional timer-related variables
		self.timeout_value = 10
		self.timer_is_running = False
		self.timer = None
	
	# This function models a Timer's behavior.
	def timer_behavior(self):
		try:
			# Start
			self.timer_is_running=True
			yield self.env.timeout(self.timeout_value)
			# Stop
			self.timer_is_running=False
			# take some actions
			self.timeout_action()
		except simpy.Interrupt:
			# upon interrupt, stop the timer
			self.timer_is_running=False
	
	# This function can be called to start the timer
	def start_timer(self):
		assert(self.timer_is_running==False)
		self.timer=self.env.process(self.timer_behavior())

	# This function can be called to stop the timer
	def stop_timer(self):
		assert(self.timer_is_running==True)
		self.timer.interrupt()

	def timeout_action(self):
		# add here the actions to be performed
		# upon a timeout
		self.channel.udt_send(self.packet_to_be_sent)
		self.start_timer()	

	
	def rdt_send(self,msg):

		if self.state==WAITING_FOR_CALL0:
			# This function is called by the 
			# sending application.
			
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
			
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			# send it over the channel
			print("TIME:",self.env.now,"RDT_SENDER: making packet 0 and sending", self.packet_to_be_sent)
			self.channel.udt_send(self.packet_to_be_sent)
			self.start_timer()
			self.seq_num=1
			self.state=WAITING_FOR_ACK0
			return True
		elif self.state==WAITING_FOR_CALL1:
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			# send it over the channel
			print("TIME:",self.env.now,"RDT_SENDER: making packet 1 and sending", self.packet_to_be_sent)
			self.channel.udt_send(self.packet_to_be_sent)
			self.start_timer()
			self.seq_num=0
			self.state=WAITING_FOR_ACK1
			return True
		else:
			return False
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		if(self.timer_is_running==False):
			self.timeout_action()
		else:
			if(packt.payload=="ACK0"):
				if (self.state==WAITING_FOR_ACK0):
					#everything is fine
					self.stop_timer()
					self.state=WAITING_FOR_CALL1
				
				elif (self.state==WAITING_FOR_ACK1):
					#self.channel.udt_send(self.packet_to_be_sent)
					print("TIME:",self.env.now,"ACK_CHANNEL : Wrong ACK Received", self.packet_to_be_sent)
			
			elif(packt.payload=="ACK1"):
			
				if (self.state==WAITING_FOR_ACK1):
					self.stop_timer()
					self.state=WAITING_FOR_CALL0
			
				elif (self.state==WAITING_FOR_ACK0):
					#self.channel.udt_send(self.packet_to_be_sent)
					print("TIME:",self.env.now,"ACK_CHANNEL : Wrong ACK Received", self.packet_to_be_sent)
				
			elif(packt.payload=="$H!T"):
				#self.channel.udt_send(self.packet_to_be_sent)
				print("TIME:",self.env.now,"ACK_CHANNEL : ACK got corrupted",self.packet_to_be_sent)
			
		

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
		#print("TIME:",self.env.now,"RDT_RECEIVER: Received packet", packt.payload)
		
		if (self.state==WAITING_FOR_0_FROM_BELOW):
			if(packt.payload=="$H!T" or packt.seq_num==1):
				response1 = Packet(seq_num=0, payload="ACK1") #Note: seq_num for the response can be arbitrary. It is ignored.
				# send it over the channel
				print("TIME:",self.env.now,"RDT_RECEIVER: making ACK1 and sending",packt)
				self.channel.udt_send(response1)
			elif(packt.seq_num==0):
				print("TIME:",self.env.now,"RDT_RECEIVER: making ACK0 and sending",packt)
				self.receiving_app.deliver_data(packt.payload)
				response2=Packet(seq_num=0, payload="ACK0")
				
				self.channel.udt_send(response2)
				self.state=WAITING_FOR_1_FROM_BELOW

		elif (self.state==WAITING_FOR_1_FROM_BELOW):
			if(packt.payload=="$H!T" or packt.seq_num==0):
				response3 = Packet(seq_num=0, payload="ACK0") #Note: seq_num for the response can be arbitrary. It is ignored.
				# send it over the channel
				print("TIME:",self.env.now,"RDT_RECEIVER: making ACK0 and sending",packt)
				self.channel.udt_send(response3)
			elif(packt.seq_num==1):
				print("TIME:",self.env.now,"RDT_RECEIVER: making ACK1 and sending",packt)
				self.receiving_app.deliver_data(packt.payload)
				response4=Packet(seq_num=0, payload="ACK1")
				
				self.channel.udt_send(response4)
				self.state=WAITING_FOR_0_FROM_BELOW
				