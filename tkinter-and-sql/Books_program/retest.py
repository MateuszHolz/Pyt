import re



pattern = r'\d+(\.\d)?:\d+'

while True:
	if re.match(pattern, input("word: ")):
		print("matches")
	else:
		print("doesn't match")