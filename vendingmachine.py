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
# Config.set('graphics', 'left', '300')
# Config.set('graphics', 'top', '300')


class VendingDisplay(BoxLayout):
	amount = ObjectProperty('$0.13')
	amount_color = ObjectProperty((0, 0, 0, 1))
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
	total_cost = ObjectProperty('$0.13')


class VendingMachine(App):
	amount = 0.0
	display = None
	pubsub = None
	redis = None
	thread = None
	total_cost = 0.0


	def add_item(self, slot):
		ref = "vendingmachine001:slot{}".format(slot)
		# print("VendingMachine.add_item() | slot: {} | ref: {}".format(slot, ref))

		count = self.redis.hincrby(ref, 'count', 1)

		result = self.redis.hgetall(ref)
		name = result[b'name'].decode()
		price = float(result[b'price'].decode())
		# print("VendingMachine.add_item() | count: {} | result: {}".format(count, result))

		self.display.slots[int(slot)] = "{}: ${:.2f} × {}".format(name, price, count)

		self.update_display()
		self.redis.publish('vendingremote-channel', 'item_added')


	def build(self):
		self.display = VendingDisplay()

		self.redis_link()

		self.update_display()
		
		return self.display


	def channel_handler(self, message):
		data = message['data'].decode()
		data_match = re.search('add_item_(?P<slot>[0-9]+)', data)

		if data == 'add_two_bits':
			result = self.redis.incrbyfloat("vendingmachine001:amount", 0.25)
			self.redis.publish('vendingremote-channel', 'money_added')
		elif data_match:
			slot = data_match.group('slot')
			self.add_item(slot)
		else:
			self.make_purchase()

		self.update_display()


	def check_purchasable(self):
		data = self.redis_getall()
		self.total_cost = 0.0

		first = True
		for datum in data:
			if first:
				self.amount = datum
				first = False
			else:
				name = datum['name']
				price = datum['price']
				count = datum['count']
				if int(count) > 0:
					self.total_cost += price * float(count)

		if self.total_cost == 0.0 or self.total_cost <= self.amount:
			self.display.amount_color = (0, 0, 0, 1)
			result = True
		else:
			self.display.amount_color = (1, 0, 0, 1)
			result = False

		return result


	def make_purchase(self):
		result = self.check_purchasable()

		if result:
			self.amount = self.amount - self.total_cost
			self.total_cost = 0

			pipe = self.redis.pipeline()
			pipe.set("vendingmachine001:amount", self.amount)
			pipe.hset("vendingmachine001:slot1", 'count', 0)
			pipe.hset("vendingmachine001:slot2", 'count', 0)
			pipe.hset("vendingmachine001:slot3", 'count', 0)
			pipe.hset("vendingmachine001:slot4", 'count', 0)
			pipe.hset("vendingmachine001:slot5", 'count', 0)
			pipe.hset("vendingmachine001:slot6", 'count', 0)
			pipe.execute()

			self.redis.publish('vendingremote-channel', 'purchase_complete')
		else:
			self.redis.publish('vendingremote-channel', 'low_funds')


	def on_pause(self):
		self.thread.stop()


	def on_resume(self):
		self.redis_link()


	def on_stop(self):
		self.thread.stop()


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
		result = []

		first = True
		for datum in data:
			if first:
				amount = float(datum.decode())
				result.append(amount)
				first = False
			else:
				obj = {
					'id': datum[b'id'].decode(),
					'name': datum[b'name'].decode(),
					'price': float(datum[b'price'].decode()),
					'count': datum[b'count'].decode()
				}
				result.append(obj)

		return result


	def redis_link(self):
		self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
		self.pubsub.subscribe(**{'vendingmachine001-channel': self.channel_handler})
		self.thread = self.pubsub.run_in_thread(sleep_time=0.001)

		self.update_display()


	def update_display(self):
		self.check_purchasable()

		data = self.redis_getall()

		count = 0
		for datum in data:
			if count == 0:
				self.amount = datum
				self.display.amount = "${:.2f}".format(self.amount)
			else:
				# print("VendingMachine.redis_link() | datum:", datum)
				self.display.slots[count] = "{}: ${:.2f} × {}".format(datum['name'], datum['price'], datum['count'])
			count += 1

		self.display.total_cost = "${:.2f}".format(self.total_cost)


if __name__ == "__main__":
	VendingMachine().run()

