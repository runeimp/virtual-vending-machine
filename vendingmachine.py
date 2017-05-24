#
# @author RuneImp <runeimp@gmail.com>
#

# import kivy
# kivy.require('1.10.0')

from kivy.app import App
from kivy.config import Config
from kivy.properties import DictProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
import re
import redis


Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')


class VendingDisplay(BoxLayout):
	amount = ObjectProperty('$0.13')
	slots = DictProperty(
		{
			1: '',
			2: '',
			3: '',
			4: '',
			5: '',
			6: '',
		}
	)


class VendingMachine(App):
	display = None
	pubsub = None
	redis = None
	thread = None


	def build(self):
		self.display = VendingDisplay()

		self.redis_link()
		
		return self.display


	def channel_handler(self, message):
		print("VendingMachine.channel_handler() | message: {}".format(message))
		data = message['data'].decode()
		data_match = re.search('add_item_(?P<slot>[0-9]+)', data)
		print("VendingMachine.channel_handler() | data: {} | slot: {}".format(data, data_match.group('slot')))

		if data == 'add_two_bits':
			print("  VendingMachine.channel_handler() | amount: {}".format(self.redis.get("vendingmachine001:amount")))
			result = self.redis.incrbyfloat("vendingmachine001:amount", 0.25)
			print("  VendingMachine.channel_handler() | result: {}".format(result))
			self.display.amount = "${:.2f}".format(result)
		elif data == 'add_item_1':
			self.add_item(1)
		elif data == 'add_item_2':
			self.add_item(2)
		elif data == 'add_item_3':
			self.add_item(3)
		elif data == 'add_item_4':
			self.add_item(4)
		elif data == 'add_item_5':
			self.add_item(5)
		elif data == 'add_item_6':
			self.add_item(6)
		else:
			print("VendingMachine.channel_handler() | data:", data)


	def add_item(self, slot):
		ref = "vendingmachine001:slot{}".format(slot)
		print("VendingMachine.add_item() | slot: {} | ref: {}".format(slot, ref))
		count = self.redis.hincrby("{} count".format(ref), 1)
		result = self.redis.hgetall("{}".format(ref))
		print("VendingMachine.add_item() | count: {} | result: {}".format(count, result))
		self.display.slots[slot] = "{}: ${:.2f} × {}".format(result[b'name'].decode(), float(result[b'price'].decode()), count)


	def redis_link(self):
		self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
		self.pubsub.subscribe(**{'vendingmachine001-channel': self.channel_handler})
		self.thread = self.pubsub.run_in_thread(sleep_time=0.001)

		pipe = self.redis.pipeline()
		pipe.get("vendingmachine001:amount")
		pipe.hgetall("vendingmachine001:slot1")
		pipe.hgetall("vendingmachine001:slot2")
		pipe.hgetall("vendingmachine001:slot3")
		pipe.hgetall("vendingmachine001:slot4")
		pipe.hgetall("vendingmachine001:slot5")
		pipe.hgetall("vendingmachine001:slot6")
		data = pipe.execute()

		count = 0
		for datum in data:
			if count == 0:
				self.display.amount = "${:.2f}".format(float(datum.decode()))
			else:
				print("VendingMachine.redis_link() | datum:", datum)
				self.display.slots[count] = "{}: ${:.2f} × {}".format(datum[b'name'].decode(), float(datum[b'price'].decode()), datum[b'count'].decode())
			count += 1


	def on_resume(self):
		self.redis_link()


	def on_stop(self):
		self.thread.stop()


if __name__ == "__main__":
	VendingMachine().run()

