

default:
	@make help


run:
	@./term-wipe
	@
	make run-remote
	@make run-machine


run-machine:
	@echo
	@echo "python3 vendingmachine.py"
	@echo
	@python3 vendingmachine.py &


run-remote:
	@echo
	@echo "python3 vendingremote.py"
	@echo
	@python3 vendingremote.py &


help:
	@./term-wipe
	@echo "help        List all make commands"
	@echo "run         Run the machine and remote apps"
	@echo "run-machine Run the machine app"
	@echo "run-remote  Run the remote app"
	@echo "reset       Reset (WIPE OUT) the local Redis DB"
	@echo "setup       Setup the local Redis DB"
	@echo "test        Runs several Redis comands"


test:
	@./term-wipe
	redis-cli PUBLISH 'vendingmachine001-channel' 'testing one'
	redis-cli PUBLISH 'vendingmachine001-channel' 'testing two'
	redis-cli PUBSUB NUMSUB 'vendingmachine001-channel'
	redis-cli PUBSUB NUMSUB 'vendingremote-channel'
	redis-cli HGETALL 'vendingmachine001:slot1'


reset:
	@./term-wipe
	redis-cli FLUSHDB


setup:
	@./term-wipe
	@cat redis_setup.aof | redis-cli

