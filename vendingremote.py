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
import redis


Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')


class VendingDisplay(BoxLayout):
	amount = ObjectProperty('$0.13')
	redis = None
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


	def add_item(self, item):
		print("VendingDisplay.add_item() | item: {}".format(item))
		self.redis.publish('vendingmachine001-channel', "add_item_{}".format(item))


	def add_two_bits(self):
		self.redis.publish('vendingmachine001-channel', 'add_two_bits')


	def make_purchase(self):
		self.redis.publish('vendingmachine001-channel', 'make_purchase')


	def redis_link(self):
		self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
		self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

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
				self.amount = "${}".format(datum.decode())
			else:
				self.slots[count] = "Order {}: ${}".format(datum[b'name'].decode(), datum[b'price'].decode())
			count += 1


class VendingRemote(App):
	display = None

	def build(self):
		self.display = VendingDisplay()

		self.display.redis_link()
		
		return self.display


if __name__ == "__main__":
	VendingRemote().run()

