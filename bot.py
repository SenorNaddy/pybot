#!/usr/bin/env python
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import time, sys
import datetime, os, re, stat

class MessageLogger:
	def __init__(self, file):
		self.file = file
	def log(self, message):
		timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
		self.file.write('%s %s\n' % (timestamp, message))
		self.file.flush()

	def close(self):
		self.file.close()

class LogBot(irc.IRCClient):

	def __init__(self):
		self.nickname = "naddybot"
		self.realname = "naddybot"
		self.username = "naddybot"

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.filename, "a"))
		self.logger.log("[connected at %s]" % time.asctime(time.localtime(time.time())))

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" % time.asctime(time.localtime(time.time())))
		self.logger.close()
	
	def signedOn(self):
		self.join(self.factory.channel)

	def joined(self, channel):
		self.logger.log("[I have joined %s]" % channel)
	
	def privmsg(self, user, channel, msg):
		user = user.split('!', 1)[0]
		self.logger.log("<%s> %s" % (user, msg))

	def action(self, user, channel, msg):
		user = user.split('!', 1)[0]
		self.logger.log("* %s %s" % (user, msg))

	def irc_NICK(self, prefix, params):
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))

	def alterCollidedNick(self, nickname):
		return nickname + '^'

class LogBotFactory(protocol.ClientFactory):
	protocol = LogBot
	def __init__(self, channel, filename):
		self.channel = channel
		self.filename = filename
		protocol.factory = self
#	def buildProtocol(self, addr):
#		p = Logbot()
#		p.factory = self
#		return p

	def ClientConnectionLost(self, connector, reason):
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()

if __name__ == '__main__':
	log.startLogging(sys.stdout)
	f = LogBotFactory(sys.argv[1], sys.argv[2])
	reactor.connectTCP("irc.freenode.net",6667, f)

	reactor.run()
