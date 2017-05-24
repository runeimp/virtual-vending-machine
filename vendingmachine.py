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
		# print("VendingMachine.channel_handler() | message: {}".format(message))
		data = message['data'].decode()
		print("VendingMachine.channel_handler() | data: {}".format(data))
		data_match = re.search('add_item_(?P<slot>[0-9]+)', data)

		if data == 'add_two_bits':
			# print("  VendingMachine.channel_handler() | amount: {}".format(self.redis.get("vendingmachine001:amount")))
			result = self.redis.incrbyfloat("vendingmachine001:amount", 0.25)
			# print("  VendingMachine.channel_handler() | result: {}".format(result))
			self.display.amount = "${:.2f}".format(result)
		elif data_match:
			slot = data_match.group('slot')
			print("VendingMachine.channel_handler() | data: {} | slot: {}".format(data, slot))
			self.add_item(slot)
		else:
			# print("VendingMachine.channel_handler() | data:", data)
			self.make_purchase()


	def add_item(self, slot):
		ref = "vendingmachine001:slot{}".format(slot)
		print("VendingMachine.add_item() | slot: {} | ref: {}".format(slot, ref))

		count = self.redis.hincrby(ref, 'count', 1)
		# self.redis.hset(ref, 'count', count)

		result = self.redis.hgetall("{}".format(ref))
		name = result[b'name'].decode()
		price = float(result[b'price'].decode())
		print("VendingMachine.add_item() | count: {} | result: {}".format(count, result))

		self.display.slots[int(slot)] = "{}: ${:.2f} × {}".format(name, price, count)


	def make_purchase(self):
		print("VendingMachine.make_purchase()")
		data = self.redis_getall()
		# print("VendingMachine.make_purchase() | data: {}".format(data))
		total_cost = 0.0

		first = True
		for datum in data:
			if first:
				amount = float(datum.decode())
				self.display.amount = "${:.2f}".format(amount)
				first = False
			else:
				name = datum[b'name'].decode()
				price = float(datum[b'price'].decode())
				count = datum[b'count'].decode()
				print("VendingMachine.make_purchase() | datum: {}: ${:.2f} × {}".format(name, price, count))
				if int(count) > 0:
					total_cost += price * count

		print("VendingMachine.make_purchase() | total_cost: ${:.2f}: | amount: ${:.2f}".format(total_cost, amount))


	def redis_getall(self):
		pipe = self.redis.pipeline()
		pipe.get("vendingmachine001:amount")
		pipe.hgetall("vendingmachine001:slot1")
		pipe.hgetall("vendingmachine001:slot2")
		pipe.hgetall("vendingmachine001:slot3")
		pipe.hgetall("vendingmachine001:slot4")
		pipe.hgetall("vendingmachine001:slot5")
		pipe.hgetall("vendingmachine001:slot6")
		data = pipe.execute()

		return data


	def redis_link(self):
		self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
		self.pubsub.subscribe(**{'vendingmachine001-channel': self.channel_handler})
		self.thread = self.pubsub.run_in_thread(sleep_time=0.001)

		data = self.redis_getall()

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

