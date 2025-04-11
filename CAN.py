import os
import can
import subprocess

class can_hat:
	def __init__(self, channel=0, bitrate=100):
		self.channel = channel
		try:
			# Check if the channel is already up
			result = subprocess.run(['ip', 'link', 'show', f'can{channel}'], capture_output=True, text=True)
			if 'UP' in result.stdout:
				subprocess.run(['sudo', 'ifconfig', f'can{channel}', 'down'], check=True)
			
			subprocess.run(['sudo', 'ip', 'link', 'set', f'can{channel}', 'type', 'can', f'bitrate', f'{bitrate}000'], check=True)
			subprocess.run(['sudo', 'ifconfig', f'can{channel}', 'up'], check=True)
		finally:
			self.can = can.interface.Bus(channel=f'can{channel}', bustype='socketcan')
	
	def send(self, id: int, data: list):
		try:
			msg = can.Message(arbitration_id=id, data=data, is_extended_id=False)
			self.can.send(msg)
		except can.CanError as e:
			print(f"Error sending CAN message: {e}")
	
	def read(self):
		try:
			msg = self.can.recv()
			return msg
		except can.CanError as e:
			print(f"Error reading CAN message: {e}")
			return None

	def close(self):
		subprocess.run(['sudo', 'ifconfig', f'can{self.channel}', 'down'], check=True)

	def __del__(self):
		self.close()
