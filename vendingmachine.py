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

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')


class VendingDisplay(BoxLayout):
	amount = ObjectProperty('$0.00')
	slot_1 = ObjectProperty('Baby Elephants $1.25 (0)')
	slot_2 = ObjectProperty('Clown Noses $0.25 (0)')
	slot_3 = ObjectProperty('Cotton Candy $0.80 (0)')
	slot_4 = ObjectProperty('Juggling Clubs $4.25 (0)')
	slot_5 = ObjectProperty('Popcorn $0.75 (0)')
	slot_6 = ObjectProperty('Show Tickets $8.25 (0)')


class VendingMachine(App):
	display = None

	def build(self):
		self.display = VendingDisplay()
		# self.display.amount = ObjectProperty('$0.00')
		return self.display


if __name__ == "__main__":
	VendingMachine().run()

