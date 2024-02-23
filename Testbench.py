# Simulation Testbench
#
# Author: Neha Karanjkar


import simpy
from Applications import SendingApplication,ReceivingApplication
from Channel import UnreliableChannel
import random
from Protocol_rdt3_overtake import *

# Create a simulation environment
env=simpy.Environment()

# Populate the simulation environment with objects:
sending_app	  = SendingApplication(env)
receiving_app = ReceivingApplication(env)
rdt_sender	  = rdt_Sender(env)
rdt_receiver  = rdt_Receiver(env)
channel_for_data  = UnreliableChannel(env=env,Pc=0.5,Pl=0.4,delay=random.randint(1,7),name="DATA_CHANNEL")
channel_for_ack	  = UnreliableChannel(env=env,Pc=0.2,Pl=0.36,delay=random.randint(1,4),name="ACK_CHANNEL")

# connect the objects together
# .....forward path...
sending_app.rdt_sender = rdt_sender
rdt_sender.channel = channel_for_data
channel_for_data.receiver = rdt_receiver
rdt_receiver.receiving_app = receiving_app
# ....backward path...for acks
rdt_receiver.channel = channel_for_ack
channel_for_ack.receiver = rdt_sender

# Run simulation
env.run(until=10000)


