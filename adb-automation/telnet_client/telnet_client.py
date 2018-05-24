import telnetlib


telnet = telnetlib.Telnet('192.168.65.181', '1337')
t = True
while t:
	print(telnet.read_until(b'\n', 1))
	t = False
while True:
	print(telnet.read_until(b'\n', 1))
	u = input('writecmd: ')
	telnet.write(u.encode('ascii')+b'\r\n')
	print(telnet.read_until(b'\n', 1))