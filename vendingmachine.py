#
# @author RuneImp <runeimp@gmail.com>
#

# import kivy
# kivy.require('1.10.0')

from kivy.app import App
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
import redis


Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')


class VendingDisplay(BoxLayout):
	amount = ObjectProperty('$0.13')
	slots = ObjectProperty(
		{
			1: '',
			2: '',
			3: '',
			4: '',
			5: '',
			6: '',
		}
	)
	# slot_1 = ObjectProperty('Baby Elephants $1.25 (0)')
	# slot_2 = ObjectProperty('Clown Noses $0.25 (0)')
	# slot_3 = ObjectProperty('Cotton Candy $0.80 (0)')
	# slot_4 = ObjectProperty('Juggling Clubs $4.25 (0)')
	# slot_5 = ObjectProperty('Popcorn $0.75 (0)')
	# slot_6 = ObjectProperty('Show Tickets $8.25 (0)')


class VendingMachine(App):
	display = None
	redis = None

	def build(self):
		self.display = VendingDisplay()
		self.display.amount = '$0.00'

		self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

		pipe = self.redis.pipeline()
		pipe.hgetall("vendingmachine001:slot1")
		pipe.hgetall("vendingmachine001:slot2")
		pipe.hgetall("vendingmachine001:slot3")
		pipe.hgetall("vendingmachine001:slot4")
		pipe.hgetall("vendingmachine001:slot5")
		pipe.hgetall("vendingmachine001:slot6")
		data = pipe.execute()

		count = 1
		for datum in data:
			print("  VendingMachine.build() | count: {} | name: {:15} | price: {}".format(count, datum[b'name'].decode(), datum[b'price'].decode()))
			self.display.slots[count] = "{} ${}".format(datum[b'name'].decode(), datum[b'price'].decode())
			count += 1
		
		return self.display


if __name__ == "__main__":
	VendingMachine().run()

