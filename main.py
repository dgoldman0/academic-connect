from server import ATBotServer

# It might be a good idea to fine-tune GPT-3.5-turbo and use that to generate posts that will better fit the format of the system.

server = ATBotServer('settings.json')
server.loop()