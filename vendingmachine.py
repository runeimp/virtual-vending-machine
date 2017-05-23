#
# @author RuneImp <runeimp@gmail.com>
#

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout

class VendingDisplay(GridLayout):
	pass


class VendingMachine(App):
	def build(self):
		return VendingDisplay()


if __name__ == "__main__":
	VendingMachine().run()

