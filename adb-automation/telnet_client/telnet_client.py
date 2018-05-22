import telnetlib


telnet = telnetlib.Telnet('192.168.67.195', '1337')
while True:
	telnet.write(b'disconnect\r\n')
	u = input('writecmd: ')
	telnet.write(u.encode('ascii')+b'\r\n')