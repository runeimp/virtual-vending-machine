

default:
	@make run


run:
	@term-wipe
	@#clear
	@#make run-remote
	@make run-machine


run-machine:
	@echo
	@echo "python3 vendingmachine.py"
	@echo
	@python3 vendingmachine.py


run-remote:
	@echo
	@echo "python3 vendingremote.py"
	@echo
	@python3 vendingremote.py &


help:
	@echo "help    List all make commands"
	@echo "run     Run the app (defaul)"
	@echo "setup   Setup the local Redis DB"
	@echo "test    Runs several Redis comands"


test:
	redis-cli PUBLISH 'vendingmachine001-channel' 'testing one'
	redis-cli PUBLISH 'vendingmachine001-channel' 'testing two'
	redis-cli PUBSUB NUMSUB 'vendingmachine001-channel'
	redis-cli HGETALL 'vendingmachine001:slot1'


setup:
	@cat redis_setup.aof | redis-cli

