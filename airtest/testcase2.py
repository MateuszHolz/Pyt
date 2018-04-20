""" import subprocess
batt = subprocess.check_output("adb shell dumpsys battery").decode().split()
def getIndexOfBattery():
    for i in batt:
        if i == 'level:':
            return batt.index(i)+1
print(batt[getIndexOfBattery()]) """


import sys
import imaplib
import getpass
import email
import email.header
import datetime
import email.message

EMAIL_ACCOUNT = "testergamelion66@gmail.com"
EMAIL_FOLDER = "INBOX"
EMAIL_PASS = "dupa1212"


def process_mailbox(M):
    rv, data = M.search(None, "ALL")
    print("RV: {}".format(rv))
    print("DATA: {}".format(data))
    print("DATA (TYPE): {}".format(type(data[0])))
    if rv != 'OK':
        print("No messages found!")
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        
        msg = email.message_from_bytes(data[0][1])
        if msg.is_multipart():
            for payload in msg.get_payload():
                print("#####PAYLOAD#{}\n".format(payload.get_payload(decode=True).decode('utf-8')))
                continue
        else:
            print(msg.get_payload())
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        print('Message %s: %s' % (num, subject))



M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASS)
except imaplib.IMAP4.error:
    print ("LOGIN FAILED!!! ")
    sys.exit(1)

print(rv, data)

rv, mailboxes = M.list()
if rv == 'OK':
    print("Mailboxes:")
    print(mailboxes)

rv, data = M.select(EMAIL_FOLDER)
if rv == 'OK':
    print("Processing mailbox...\n")
    process_mailbox(M)
    M.close()
else:
    print("ERROR: Unable to open mailbox ", rv)

M.logout()