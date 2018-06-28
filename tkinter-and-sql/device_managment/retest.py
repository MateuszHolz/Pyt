import re


^[0-9]{4}$
pattern = r'^\d+(\.\d+)*$'

while True:
	l = input("word: ")
	if len(l) > 0:
		if re.match(pattern, l):
			print("matches")
		else:
			print("doesn't match")

# while True:
# 	print(len(input("test: ")))