import os
import can

class can_hat:
	def __init__(self,channel=0,bitrate=100):
		try:
			os.system(f'sudo ifconfig can{channel} down')
			os.system(f'sudo ip link set can{channel} type can bitrate {bitrate}000')
			os.system(f'sudo ifconfig can{channel} up')
		finally:
			self.can = can.interface.Bus(channel = f'can{channel}', bustype='socketcan')
	
	def send(self, id: int, data: list):
		msg = can.Message(arbitration_id=id, data=data, is_extended_id=False)
		self.can.send(msg)
	
	def read(self):
		msg = self.can.recv()
		return msg

	def __del__(self):
		os.system('sudo ifconfig can0 down')
