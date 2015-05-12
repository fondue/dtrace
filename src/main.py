#!/usr/bin/python
# v0.1 by Dominik Imhof 03.2015
# 

import time, os
import pickle
# Send
import smtplib
# GPIO
import RPi.GPIO as GPIO  #for GPIO
# Receive
import threading
import picamera, smtplib, sys, time
import email, getpass, imaplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#------------------------------------------------

# GPIO
GPIO.setmode(GPIO.BCM)
print "Welcome to your home"
print "---------------------------------------------"
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT) # for LED
GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # for shutwodn
shutdownSwitch = 25
GPIO.setup(8,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # for quittieren
button = 8

def shutdown(pin):
	print "shutdown"
	os.system("sudo shutdown -h now")
	time.sleep(10)	

GPIO.add_event_detect(shutdownSwitch, GPIO.RISING, callback=shutdown)

# for change detection
openOldKitchen = False
closedOldKitchen = True
openedKitchen = False
closedKitchen = True
hasChangedKitchen = False
lastTimeEntrance = time.time()

openOldEntrance = False
closedOldEntrance = True
openedEntrance = False
closedEntrance = True
hasChangedEntrance = False
lastTimeEntrance = time.time()
#------------------------



# Receive mail

#MailReceiveUSER = 'dominik.imhof@stud.hslu.ch'
MailReceiveUSER = 'bda15-inat@ihomelab-lists.ch'
MailReceivePWD = 'PCnO5CMU'
#MailReceiveSRV = 'imap.hslu.ch'
MailReceiveSRV = 'imap.mail.hostpoint.ch'

MailSendUSER = ''
MailSendPWD = ''
MailSendSRV = 'mail.gmx.net'
MailSendFROM = MailReceiveUSER
MailSendTO = 'dominik.imhof@stud.hslu.ch'

# Send Mail
mailServer = 'pop.gmail.com'
mailPort = 587
mailLogin = 'muster.bewohner@gmail.com'
mailPass = 'braunbaer17'
mailSendFrom = mailLogin
mailSendTo = 'dominik.imhof@stud.hslu.ch'
mailTLS = True
mailDebug = False
#------------------------------------------------------------------

#toleranzSchwelle = 10
warnung = False

#-------------------------------------------------------------------

# Send Mail

def sendemail(from_addr, to_addr, subject, message):
    try:
        header = 'From: %s\n' % from_addr
        header+= 'To: %s\n' % to_addr
        header+= 'Subject: %s\n\n' % subject
        message = header + message
        conn = smtplib.SMTP(mailServer, mailPort)
        if mailDebug:
            conn.set_debuglevel(True) #show communication with the server
        if mailTLS:
            conn.starttls()
        conn.login(mailLogin, mailPass)
        error = conn.sendmail(from_addr, to_addr, message)
        if not error:
            print "Successfully sent email"
    except Exception, e:
        print "\nSMTP Error: " + str(e)
    finally:
        if conn:
            conn.quit()

# check Mails
running = True
newMails = False

def checkMails():
    try:
        print("read mails")
        m = imaplib.IMAP4_SSL(MailReceiveSRV)
        m.login(MailReceiveUSER, MailReceivePWD)
        if running:
            m.select("Inbox")
            status, unreadcount = m.status('INBOX', "(UNSEEN)")
            unreadcount = int(unreadcount[0].split()[2].strip(').,]'))
            if unreadcount > 0:
                items = m.search(None, "UNSEEN")
                items = str(items[1]).strip('[\']').split(' ')
                for index, emailid in enumerate(items):
                    #print "emailid: " + emailid
                    resp, data = m.fetch(emailid, "(RFC822)")
                    email_body = data[0][1]
                    mail = email.message_from_string(email_body)
                    if mail["Subject"] == 'Code':
						print "New mail received: Code-Word accepted"
						global newMails 
						newMails = True
						for part in mail.walk():
							if part.get_content_type() == 'text/plain':
								body = part.get_payload()
								#print "got payload"
                                # For each line in message execute instructions
								for line in body.split('\r\n'):
									if line != " ":
										#print "lese..."
										if line[0:5] == "Mail:":
											address = line[6:len(line)]
											print "Adresse aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/address.txt","w") as f:
												f.write(address+"\n")
												f.close()
												
										if line[0:13] == "Schwelle Tag:":
											schwelleTag = line[14:len(line)]
											print "Schwelle Tag aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/schwelle_tag.txt","w") as f:
												f.write(schwelleTag+"\n")
												f.close()
										
										if line[0:15] == "Schwelle Nacht:":
											schwelleNacht = line[16:len(line)]
											print "Schwelle Nacht aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/schwelle_nacht.txt","w") as f:
												f.write(schwelleNacht+"\n")
												f.close()
										
										if line[0:12] == "Tagesbeginn:":
											tagesbeginn = line[13:len(line)]
											print "Tagesbeginn aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/tages_beginn.txt","w") as f:
												f.write(tagesbeginn+"\n")
												f.close()		
										
										if line[0:12] == "Nachtbeginn:":
											nachtbeginn = line[13:len(line)]
											print "Nachtbeginn aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/nacht_beginn.txt","w") as f:
												f.write(nachtbeginn+"\n")
												f.close()
										
										if line[0:6] == "Status":
											nachtbeginn = line[13:len(line)]
											print "Nachtbeginn aus der Mail gelesen"
											with open("/home/pi/projects/bda/data/nacht_beginn.txt","w") as f:
												f.write(nachtbeginn+"\n")
												f.close()
										
										
                                       
            time.sleep(0.2)
    except Exception, e1:
        print("Error...: " + str(e1))
    except (KeyboardInterrupt, SystemExit):
       exit()


#def writeLastTime():
#    with open('/home/pi/projects/bda/data/last_time.txt','w') as f:
#		value = time.time()
#		f.write(str(value))
#		f.close()

def readLastTime():
	with open('/home/pi/projects/bda/data/last_time.pkl', 'rb') as f:
		t = pickle.load(f)
		print(t)
		return t
        
def writeLastTime():
    with open('/home/pi/projects/bda/data/last_time.pkl','wb') as f:
		value = time.time()
		#print value
		pickle.dump(value,f)
		#lastTime = os.path.getmtime('/home/pi/projects/bda/data/time_zwp.pkl')
		#f.write(str(value))
		#f.close()
	
def readSchwelleTag():
	f = open('/home/pi/projects/bda/data/schwelle_tag.txt')
	while True:
		line = f.readline()
		# Zero length indicates EOF
		if len(line) == 0:
			break
		# The `line` already has a newline
		# at the end of each line
		# since it is reading from a file.
		#print line
		return int(line)
	# close the file
	f.close()	

def readSchwelleNacht():
	f = open('/home/pi/projects/bda/data/schwelle_nacht.txt')
	while True:
		line = f.readline()
		# Zero length indicates EOF
		if len(line) == 0:
			break
		# The `line` already has a newline
		# at the end of each line
		# since it is reading from a file.
		#print line
		return int(line)
	# close the file
	f.close()

def readAddress():
	f = open('/home/pi/projects/bda/data/address.txt')
	while True:
		line = f.readline()
		# Zero length indicates EOF
		if len(line) == 0:
			break
		# The `line` already has a newline
		# at the end of each line
		# since it is reading from a file.
		#print line
		return line
	# close the file
	f.close()
	
def readTagesBeginn():
	f = open('/home/pi/projects/bda/data/tages_beginn.txt')
	while True:
		line = f.readline()
		# Zero length indicates EOF
		if len(line) == 0:
			break
		# The `line` already has a newline
		# at the end of each line
		# since it is reading from a file.
		#print line
		return int(line)
	# close the file
	f.close()
	
def readNachtBeginn():
	f = open('/home/pi/projects/bda/data/nacht_beginn.txt')
	while True:
		line = f.readline()
		# Zero length indicates EOF
		if len(line) == 0:
			break
		# The `line` already has a newline
		# at the end of each line
		# since it is reading from a file.
		#print line
		return int(line)
	# close the file
	f.close()
	
            
def writeOpenKitchen():
    with open('/home/pi/projects/bda/data/time_open_kitchen.pkl','wb') as f:
		value = time.time()
		print "open kitchen: ", value
		pickle.dump(value,f)
		
def writeClosedKitchen():
    with open('/home/pi/projects/bda/data/time_closed_kitchen.pkl','wb') as f:
		value = time.time()
		print "closed kitchen: ", value
		pickle.dump(value,f)
		
            
def writeOpenEntrance():
    with open('/home/pi/projects/bda/data/time_open_entrance.pkl','wb') as f:
		value = time.time()
		print "open entrance: ", value
		pickle.dump(value,f)
		
def writeClosedEntrance():
    with open('/home/pi/projects/bda/data/time_closed_entrance.pkl','wb') as f:
		value = time.time()
		print "closed entrance", value
		pickle.dump(value,f)
		
def getHasChangedKitchen():
	
	time_open = os.path.getmtime('/home/pi/projects/bda/data/time_open_kitchen.pkl')
	time_closed = os.path.getmtime('/home/pi/projects/bda/data/time_closed_kitchen.pkl')
	global openOldKitchen
	global closedOldKitchen
	global openedKitchen
	global closedKitchen
	global hasChangedKitchen

	if time_open >= time_closed:
		openedKitchen = True
		closedKitchen = False

	if time_closed >= time_open:
		openedKitchen = False
		closedKitchen = True

	if openOldKitchen == openedKitchen:
		hasChangedKitchen = False
	else:
		hasChangedKitchen = True

	if closedOldKitchen == closedKitchen:
		hasChangedKitchen = False
	else:
		hasChangedKitchen = True
		
	openOldKitchen = openedKitchen
	closedOldKitchen = closedKitchen
	
	return hasChangedKitchen
	
def getHasChangedEntrance():
	
	time_open = os.path.getmtime('/home/pi/projects/bda/data/time_open_entrance.pkl')
	time_closed = os.path.getmtime('/home/pi/projects/bda/data/time_closed_entrance.pkl')
	global openOldEntrance
	global closedOldEntrance
	global openedEntrance
	global closedEntrance
	global hasChangedEntrance

	if time_open >= time_closed:
		openedEntrance = True
		closedEntrance = False

	if time_closed >= time_open:
		openedEntrance = False
		closedEntrance = True

	if openOldEntrance == openedEntrance:
		hasChangedEntrance = False
	else:
		hasChangedEntrance = True

	if closedOldEntrance == closedEntrance:
		hasChangedEntrance = False
	else:
		hasChangedEntrance = True
		
	openOldEntrance = openedEntrance
	closedOldEntrance = closedEntrance
	
	return hasChangedEntrance
	
# Simulates an activity at the beginning of the programm
writeOpenKitchen()
writeClosedKitchen()
writeOpenEntrance()
writeClosedEntrance()
lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_closed_kitchen.pkl')
lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_closed_entrance.pkl')
# ------------------------------------------------------


while True:
	
	checkMails()
	
	tagStart = readTagesBeginn()
	print "Start des Tages:", tagStart, "Uhr"
	nachtStart = readNachtBeginn()
	print "Start der Nacht:", nachtStart, "Uhr"
	localtime = time.localtime(time.time()).tm_hour
	print "Aktuelle Stunde:", localtime
	
	if localtime >= tagStart and localtime < nachtStart:
		print "It's day"
		tag = True
		nacht = False
		
	else:
		print "It's night"
		tag = False
		nacht = True	
	print "---------------------------------------------"
	
	mailSendTo = readAddress()
	print "Ziel-Adresse:", mailSendTo
	toleranzSchwelleTag = readSchwelleTag() #* 60 # Wert in der Mail muss groesser als 10 sein
	print "Toleranz-Schwelle Tag:", toleranzSchwelleTag, "Sekunden"
	toleranzSchwelleNacht = readSchwelleNacht() #* 60 # Wert in der Mail muss groesser als 10 sein
	print "Toleranz-Schwelle Nacht:", toleranzSchwelleNacht, "Sekunden"
	print "---------------------------------------------"

	# send state
	if newMails == True:
		print "new mails received"
		newMails = False
		if __name__ == '__main__':
			print "Sende Status"
			sendemail(mailSendFrom, mailSendTo, "Status!", "Ziel-Adresse: "+mailSendTo+"\n"+"Schwelle Tag: "+str(toleranzSchwelleTag)+"\n"+"Schwelle Nacht: "+str(toleranzSchwelleNacht)+"\n" + "Tagesbeginn: "+str(tagStart)+"\n"+"Nachtbeginn: "+str(nachtStart))
	else:
		print "no new mails received"
	print "---------------------------------------------"
	
	
	# check: is activity
	if os.path.isfile('/home/pi/projects/bda/data/time_zwave.pkl'):
		# time stamp of file (time when last edited)
		lastTimeZWave = os.path.getmtime('/home/pi/projects/bda/data/time_zwave.pkl')
		print "Time of last activity of ZWave: ", lastTimeZWave
		
	getHasChangedKitchen()
	#global actual_time
	if hasChangedKitchen == True:
		#save timestamp of changed 
		if closedKitchen == True:
			lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_closed_kitchen.pkl')
		if openedKitchen == True:
			lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_open_kitchen.pkl')
	print "Time of last activity in kitchen:", lastTimeKitchen
	
	getHasChangedEntrance()
	#global actual_time
	if hasChangedEntrance == True:
		#save timestamp of changed 
		if closedEntrance == True:
			lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_closed_entrance.pkl')
		if openedKitchen == True:
			lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_open_entrance.pkl')
	print "Time of last activity in entrance:" , lastTimeEntrance
	# ------------------------------------------------------------
			
#Find greatest time:
		
	if lastTimeZWave >= lastTimeEntrance and lastTimeZWave >= lastTimeEntrance:
		print "ZWave registered last activity"
		lastTime = lastTimeZWave
	
	if lastTimeKitchen >= lastTimeEntrance and lastTimeKitchen >= lastTimeZWave:
		print "Kitchen registered last activity"
		lastTime = lastTimeKitchen
		
	if lastTimeEntrance >= lastTimeKitchen and lastTimeEntrance >= lastTimeZWave:
		print "Entrance registered last activity"
		lastTime = lastTimeEntrance
		
	if tag == True: #!!!!!!!!!!!
		if tag == True:
			# check Toleranz
			if time.time() - lastTime >= toleranzSchwelleTag:
				print "Toleranz-Schwelle Tag ueberschritten"
			
				for i in range (1,100):
					GPIO.output(24,GPIO.HIGH)
					
					getHasChangedEntrance()
					if hasChangedEntrance == True:
					#save timestamp of changed 
						if closedEntrance == True:
							lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_closed_entrance.pkl')
						if openedEntrance == True:
							lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_open_entrance.pkl')
					
					getHasChangedKitchen()
					if hasChangedKitchen == True:
					#save timestamp of changed 
						if closedKitchen == True:
							lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_closed_kitchen.pkl')
						if openedKitchen == True:
							lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_open_kitchen.pkl')
					
					
					# Quittieren wenn Schalter oder Sensoren betaetigt werden:
					if ((GPIO.input(button) == True) or (time.time() - os.path.getmtime('/home/pi/projects/bda/data/time_zwave.pkl')) < 5 or (time.time() - lastTimeKitchen)< 5 or (time.time() - lastTimeEntrance) < 5):
						print time.time() - lastTimeKitchen
						print time.time() - lastTimeEntrance
						print time.time() - os.path.getmtime('/home/pi/projects/bda/data/time_zwave.pkl')
						print "Warnung quittiert Tag"
						writeLastTime()
						# !!!!!!!!!!!! noch ergaenzen mit write der anderen
						break
					print i
					if i == 99:
						warnung = True # Sende definitiv eine Warnung
					time.sleep(0.1) 
			
				GPIO.output(24,GPIO.LOW) # Alarm ausschalten
			
				if warnung == True:
					GPIO.output(24,GPIO.LOW) # Alarm ausschalten
					writeLastTime()
					warnung = False 
					if __name__ == '__main__':
						print "Sende Warnung"
						sendemail(mailSendFrom, mailSendTo, 'Warnung!', 'Hallo, zu wenig Aktivitaet in der Wohnung vom Muster Bewohner wurde festgestellt!\nGruesse vom PI')
	if nacht == True: #!!!!!!!!!!!!!!!!!!!!
		if nacht == True:
			if time.time() - lastTime >= toleranzSchwelleNacht:
				print "Toleranz-Schwelle Nacht ueberschritten"
			
				for i in range (1,100):
					GPIO.output(24,GPIO.HIGH)
					
					getHasChangedEntrance()
					if hasChangedEntrance == True:
					#save timestamp of changed 
						if closedEntrance == True:
							lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_closed_entrance.pkl')
						if openedEntrance == True:
							lastTimeEntrance = os.path.getmtime('/home/pi/projects/bda/data/time_open_entrance.pkl')
					
					getHasChangedKitchen()
					if hasChangedKitchen == True:
					#save timestamp of changed 
						if closedKitchen == True:
							lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_closed_kitchen.pkl')
						if openedKitchen == True:
							lastTimeKitchen = os.path.getmtime('/home/pi/projects/bda/data/time_open_kitchen.pkl')
					
					
					# Quittieren wenn Schalter oder Sensoren betaetigt werden:
					if ((GPIO.input(button) == True) or (time.time() - os.path.getmtime('/home/pi/projects/bda/data/time_zwave.pkl')) < 5 or (time.time() - lastTimeKitchen)< 5 or (time.time() - lastTimeEntrance) < 5):
						print time.time() - lastTimeKitchen
						print time.time() - lastTimeEntrance
						print time.time() - os.path.getmtime('/home/pi/projects/bda/data/time_zwave.pkl')
						print "Warnung quittiert nacht"
						writeLastTime()
						break
					print i
					if i == 99:
						warnung = True # Sende definitiv eine Warnung
					time.sleep(0.1) 
			
				GPIO.output(24,GPIO.LOW) # Alarm ausschalten
			
				if warnung == True:
					GPIO.output(24,GPIO.LOW) # Alarm ausschalten
					writeLastTime()
					warnung = False 
					if __name__ == '__main__':
						print "Sende Warnung"
						sendemail(mailSendFrom, mailSendTo, 'Warnung!', 'Hallo, zu wenig Aktivitaet in der Wohnung vom Muster Bewohner wurde festgestellt!\nGruesse vom PI')
	time.sleep(5) 
		


		
