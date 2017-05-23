

default:
	@make run


run:
	@term-wipe
	@echo
	@echo "python3 vendingmachine.py"
	@echo
	@python3 vendingmachine.py


help:
	@echo "help    List all make commands"
	@echo "run     Run the app (defaul)"
	@echo "setup   Setup the local Redis DB"


setup:
	@cat redis_setup.aof | redis-cli

