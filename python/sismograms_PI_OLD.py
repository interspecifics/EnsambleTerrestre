#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
sismograms
----------
Dowload sismogram plots from Servicio Sismologico Nacional,
Reads them as a track and generate OSC messages accordingly.
mecanosaurio // 22.mzo.2018

v0.1
----
get sismograms,
select, read and parse tracks
osc stream data

v0.2
----
graphic ui: draw signal, 
show data and names

v0.3
-----
lerping values
full gui access:
 	wilkomen
	select track, mode, update + [screens]
v0.4
-----
i2c stream data

v0.5
-----
send encoded data
adjust timming
keep it going forever
"""


# ----------------------------------------------------------------\\ L I B S
import cv2
import numpy as np
import random, time, glob
import urllib
#import OSC
import smbus


# ----------------------------------------------------------------\\ utils

w = 480
h = 320
state = 0
# colors: http://paletton.com/#uid=52P0U0kDDll-D2jHnbjKWuWJIYd
colors = {'white':[222, 211, 222], 'dark': [12, 5, 1], \
			'blue':[248, 96, 13], 'green': [0, 251, 0], \
			'other':[113, 45, 8], 'yellow': [0, 255, 245], \
			'red':[0, 0, 255], 'purp':[248, 6, 175]}
bus = smbus.SMBus(1)
address_NE = 0x6A
address_SW = 0x3A


def change_state(s):
	global state
	state = s
	return

def lerp(a, b, s):
	""" lerp(start, stop, amt)"""
	return ((1-s)*a)+((s)*b)

def write_I2C(val):
	#bus.write_byte_data(address, 0, val)
	return -1

def write_list_I2C(string_data):
	lis = [ord(c) for c in string_data]
	bus.write_i2c_block_data(address_NE, 0, lis[:2])
	bus.write_i2c_block_data(address_SW, 0, lis[2:])
	#print ">> "+ string_data
	#for c in string_data:
	#	bus.write_byte(address, ord(c))
	return -1


# ----------------------------------------------------------------\\ sismogram functs
def get_sismograms():
	# 1. download images
	urls = {"cuig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCU.gif",\
			"caig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCA.gif",\
			"cmig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCM.gif",\
			"huig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaHU.gif",\
			"oxig_a": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismograma_OX.gif",\
			"oxig_v": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaOX.gif",\
			"plig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaPL.gif",\
			"lpig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaLP.gif",\
			"spig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaSP.gif",\
			"ppig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaPP.gif",\
		}
	try:
		for u in urls.keys():
			print u, urls[u]
			urllib.urlretrieve(urls[u], "data/"+u+".gif")
	except:
		return False
	return 0


def load_sismogram():
	# 2. show list, load an image, return state and array
	img_fns = glob.glob("data/*.gif")
	print "sismogramas disponibles: "
	for i, fn in enumerate(img_fns):
		print "\t",i,". ",fn
	print "*: --- *** --- *** ---- :*"
	selec = None
	while (selec==None and selec!=''):
		print "teclea y numero y presiona intro: "
		try:
			selec = int(raw_input('<Opt>: '))
		except ValueError:
			print "x.X Not a number"
	# but when it is
	print "[get]: ", selec
	gif = cv2.VideoCapture(img_fns[selec])
	id_st = img_fns[selec]
	if id_st.find('\\')>0: id_st = id_st[id_st.find('\\')+1:id_st.rfind('.')]
	else: id_st = id_st[id_st.find('/')+1:id_st.rfind('.')]
	state, data = gif.read()
	return id_st, state, data


def read_track(img, ntrack):
	# inicio: x:40, y:80, #delta: 172, 305, 437: 15 mins
	# looks for top and bottom colored pixels over a trail,
	# return array with values
	start_point = [40, 80+ntrack*20]
	end_point = [570, 80+ntrack*20]
	max_amp_y = 20

	track = []
	for ix in range(start_point[0], end_point[0]):
		if (ix==172 or ix==305 or ix==437): continue
		past_pixel= []
		act_pixel = [None, None, None]
		y_top = 0
		# change this for a while
		for iy in range(start_point[1]-max_amp_y, start_point[1] + max_amp_y/2):
			past_pixel = list(act_pixel)
			act_pixel = list(img[iy][ix])
			if act_pixel[2]==0 and past_pixel[2]==255:
				y_top = iy
				break
		past_pixel= []
		act_pixel = [None, None, None]
		y_bottom = 0
		for iy in range(start_point[1]-max_amp_y/2, start_point[1]+max_amp_y):
			past_pixel = list(act_pixel)
			act_pixel = list(img[iy][ix])
			if act_pixel[2]==255 and past_pixel[2]==0:
				y_bottom = iy
				break
		if (y_top==0 and y_bottom==0 and list(img[80+ntrack*20][ix])[2]==255):
			delta_y = 0
		else:
			if (y_top==0): y_top = start_point[1]-max_amp_y
			if (y_bottom==0): y_bottom=start_point[1]+max_amp_y
			delta_y = abs(y_top-y_bottom)
		#print "<x: %i> [%i : %i]: %i" % (ix, y_top, y_bottom, delta_y)
		track.append([delta_y, y_top, y_bottom])
	return track


def read_tracks(img):
	# like read_track but for all at once, return matrix
	tracks = []
	for jj in range(24):
		start_point = [40, 80+jj*20]
		end_point = [570, 80+jj*20]
		max_amp_y = 20
		track = []
		for ix in range(start_point[0], end_point[0]):
			if (ix==172 or ix==305 or ix==437): continue
			past_pixel= []
			act_pixel = [None, None, None]
			y_top = 0
			# change this for a while
			for iy in range(start_point[1]-max_amp_y, start_point[1] + max_amp_y/2):
				past_pixel = list(act_pixel)
				act_pixel = list(img[iy][ix])
				if act_pixel[2]==0 and past_pixel[2]==255:
					y_top = iy
					break
			
			past_pixel= []
			act_pixel = [None, None, None]
			y_bottom = 0
			for iy in range(start_point[1]-max_amp_y/2, start_point[1]+max_amp_y):
				past_pixel = list(act_pixel)
				act_pixel = list(img[iy][ix])
				if act_pixel[2]==255 and past_pixel[2]==0:
					y_bottom = iy
					break
			if (y_top==0 and y_bottom==0 and list(img[80+jj*20][ix])[2]==255):
				delta_y = 0
			else:
				if (y_top==0): y_top = start_point[1]-max_amp_y
				if (y_bottom==0): y_bottom=start_point[1]+max_amp_y
				delta_y = abs(y_top-y_bottom)
			#print "<x: %i> [%i : %i]: %i" % (ix, y_top, y_bottom, delta_y)
			track.append([delta_y, y_top, y_bottom])
		tracks.append(track)
	return tracks


'''
def stream_track(cOsc, track, per):
	"""send data via osc periodically"""
	print "<-- streaming track -->"
	route = "/sismogram/data"
	index = 0
	for t,d in enumerate(track):
		val = d[index]
		msg = OSC.OSCMessage()
		msg.setAddress(route)
		msg.append(t)
		msg.append(val)
		cOsc.send(msg)
		print msg,
		for i in range(len(str(msg))): print "\r", 
		time.sleep(per)
	print "\n<-- stream endpoint -->"
	return 0
'''


# ----------------------------------------------------------------\\ drawing functions
def draw_sismogram(track):
	# -- canvas
	val = 3.14
	tim = "-24:66:14"
	lud = "24/4/1420"
	# create windows and canvas once
	def on_mouse(event, x, y, flags, param):
		return
	window_name = "Ensamble Terrestre"
	cv2.namedWindow(window_name)
	cv2.setMouseCallback(window_name, on_mouse)
	# fill the canvas with color
	canvas = np.zeros((h, w, 3), np.uint8)
	for j in range(h):
		for i in range(w):
			canvas[j][i]=colors['dark']
	# draw the boxes
	box_main = [(5,5), (w-5, h-5), colors['blue'], 1]
	box_plot = [(10,10), (w-15, h/2), colors['blue'], 1]
	cv2.rectangle(canvas, box_main[0], box_main[1], box_main[2], box_main[3])
	cv2.rectangle(canvas, box_plot[0], box_plot[1], box_plot[2], box_plot[3])
	# put some labels
	cv2.putText(canvas, "<Ensamble Terrestre>" ,(-85+w/2, 20), cv2.FONT_HERSHEY_PLAIN, 1, colors['yellow'])
	cv2.putText(canvas, "Last uPdate: " ,(270, h-15), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['yellow'])
	cv2.putText(canvas, lud , (380, h-15), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['white'])
	cv2.putText(canvas, ">Estacion:", 	(20, 30+h/2),  cv2.FONT_HERSHEY_SIMPLEX, 	1, colors['white'])
	cv2.putText(canvas, ">Tiempo:", 	(20, 60+h/2),  cv2.FONT_HERSHEY_SIMPLEX, 	1, colors['white'])
	cv2.putText(canvas, ">Intensidad:", (20, 90+h/2),  cv2.FONT_HERSHEY_SIMPLEX, 	1, colors['white'])
	cv2.putText(canvas, ">Mssg:", 		(20, 120+h/2), cv2.FONT_HERSHEY_SIMPLEX, 	1, colors['white'])
	# duplicate
	nu_can =canvas.copy()
	route = "/sismogram/data/"+id_st
	print "<-- streaming track -->"
	for a in range(4):
		for b in range(132):
			indek = a*132 + b
			if indek<4*132-1:
				dd = track[indek]
				val = dd[0]
				t = a*132 + b
				# do the plot, first, overwrite
				cv2.rectangle(nu_can, (40 + 3*b, -50+h/4), (40 + 3*b +20, 50+h/4),  colors['dark'],  -1)
				cv2.line(nu_can, (43 + 3*b, -50+h/4), (43 + 3*b, 50+h/4), colors['blue'], 1)
				cv2.line(nu_can, (40 , -50+h/4), (40, 50+h/4), colors['yellow'], 1)
				cv2.line(nu_can, (40 + 3*132, -50+h/4), (40+3*132, 50+h/4), colors['yellow'], 1)
				# this is the data
				#cv2.line(nu_can, (40 + 3*b, h/4), (40 + 3*b, -2*val+h/4), colors['other'], 2)
				#cv2.line(nu_can, (40 + 3*b, h/4), (40 + 3*b, 2*val+h/4), colors['other'], 2)
				cv2.line(nu_can, (40 + 3*b, (-2*val+h/4)+1), (40 + 3*b, -2*val+h/4), colors['other'], 1)
				cv2.line(nu_can, (40 + 3*b, ( 2*val+h/4)-1), (40 + 3*b,  2*val+h/4), colors['other'], 1)
				'''
				# send the messahe
				msg = OSC.OSCMessage()
				msg.setAddress(route)
				msg.append(t)
				msg.append(val)
				cOsc.send(msg)
				print msg,
				for i in range(len(str(msg))): print "\r", 
				'''
				# overwrite the data values in it
				cv2.rectangle(nu_can, (250, 30+h/2),  (450, 5+h/2),  colors['dark'],  -1)
				cv2.rectangle(nu_can, (250, 60+h/2),  (450, 30+h/2), colors['dark'],  -1)
				cv2.rectangle(nu_can, (250, 90+h/2),  (450, 60+h/2), colors['dark'],  -1)
				cv2.rectangle(nu_can, (180, 125+h/2), (450, 100+h/2), colors['dark'],  -1)
				cv2.putText(nu_can, id_st ,		(250, 30+h/2),  cv2.FONT_HERSHEY_DUPLEX, 1, colors['yellow'])
				cv2.putText(nu_can, str(t) ,	(250, 60+h/2),  cv2.FONT_HERSHEY_DUPLEX, 0.7, colors['yellow'])
				cv2.putText(nu_can, str(val) ,	(250, 90+h/2),  cv2.FONT_HERSHEY_DUPLEX, 0.7, colors['yellow'])
				cv2.putText(nu_can, str(msg) ,	(180, 120+h/2), cv2.FONT_HERSHEY_PLAIN,  1, colors['yellow'])
				# show it
				cv2.imshow(window_name, nu_can)
				k = cv2.waitKey(50) & 0xFF
				if k == 27:
					cv2.destroyAllWindows()
					break
	print ""
	print "\n<-- stream endpoint -->"
	# at last wait for a button
	while(1):
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			cv2.destroyAllWindows()
			break
	# end draw sismogram



# ----------------------------------------------------------------\\ neu functions
# ----------------------------------------------------------------\\ NEU functions
def draw_willkommen():
	# create mouse callback for window
	def on_mouse_01(event, x, y, flags, param):
		if event==cv2.EVENT_LBUTTONDOWN:
			# cheq alt button
			if (x>btn_alt[0][0] and x<btn_alt[1][0] and \
				y>btn_alt[0][1] and y<btn_alt[1][1]):
				print "[btn_ALT]: "+str(x)+","+str(y)
				cv2.rectangle(canvas, btn_alt[0], btn_alt[1], colors['green'], -2)
				change_state(4)
				print "[ST]: I"
				time.sleep(0.3)
			# cheq photo button
			if (x>btn_neu[0][0] and x<btn_neu[1][0] and \
				y>btn_neu[0][1] and y<btn_neu[1][1]):
				print "[btn_NEU]: "+str(x)+","+str(y)
				cv2.rectangle(canvas, btn_neu[0], btn_neu[1], colors['green'], -2)
				change_state(2)
				print "[ST]: II"
				time.sleep(0.3)
		elif event==cv2.EVENT_RBUTTONDOWN:
			print "<R>: "+str(x)+","+str(y)
		return
	# create windows and canvas once
	window_name = "Ensamble Terrestre"
	cv2.namedWindow(window_name)
	cv2.setMouseCallback(window_name, on_mouse_01)
	# fill the canvas with color
	canvas = np.zeros((h, w, 3), np.uint8)
	for j in range(h):
		for i in range(w):
			canvas[j][i]=colors['dark']
	# draw the boxes titles
	box_main = [(5,5), (w-5, h-5), colors['other'], 2]
	cv2.rectangle(canvas, box_main[0], box_main[1], box_main[2], box_main[3])
	cv2.putText(canvas, "Ensamble" ,(-110+w/2, -10+h/4), cv2.FONT_HERSHEY_DUPLEX, 1.4, colors['green'])
	cv2.putText(canvas, "Terrestre" ,(-110+w/2, 40+h/4), cv2.FONT_HERSHEY_SIMPLEX, 1.5, colors['green'])
	# buttons
	btn_neu = [(w*1/10, h*4/6), (w*4/10, h*5/6), colors['blue'], 2]
	btn_alt = [(w*6/10, h*4/6), (w*9/10, h*5/6), colors['blue'], 2]
	cv2.rectangle(canvas, btn_neu[0], btn_neu[1], btn_neu[2], btn_neu[3])
	cv2.rectangle(canvas, btn_alt[0], btn_alt[1], btn_alt[2], btn_alt[3])
	cv2.putText(canvas, "<New Data>" ,(20+w*1/10, 30+h*4/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.putText(canvas, "<Records>" ,(20+w*6/10, 30+h*4/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	# wait for a change
	while (state==0):
		cv2.imshow(window_name, canvas)
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
	cv2.destroyAllWindows()
	return


def draw_updating():
	urls = {"cuig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCU.gif",\
		"caig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCA.gif",\
		"cmig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaCM.gif",\
		"huig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaHU.gif",\
		"oxig_a": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismograma_OX.gif",\
		"oxig_v": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaOX.gif",\
		"plig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaPL.gif",\
		"lpig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaLP.gif",\
		"spig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaSP.gif",\
		"ppig": "http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaPP.gif",\
	}
	# create windows and canvas once
	window_name = "Ensamble Terrestre"
	#cv2.namedWindow(window_name)
	cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_AUTOSIZE)
	# fill the canvas with color
	canvas = np.zeros((h, w, 3), np.uint8)
	for j in range(h):
		for i in range(w):
			canvas[j][i]=colors['dark']
	# draw the boxes titles
	box_main = [(5,5), (w-5, h-5), colors['other'], 1]
	cv2.rectangle(canvas, box_main[0], box_main[1], box_main[2], box_main[3])
	cv2.putText(canvas, "i n t e r s p e c i f i c s" ,(-72+w/2, 20), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['blue'])
	cv2.putText(canvas, "Ensamble" ,(-110+w/2,  10+h/4), cv2.FONT_HERSHEY_DUPLEX, 1.4, colors['green'])
	cv2.putText(canvas, "Terrestre" ,(-105+w/2, 60+h/4), cv2.FONT_HERSHEY_SIMPLEX, 1.5, colors['green'])
	# buttons
	cv2.putText(canvas, "[Actualizando DB]: " ,(20+w*3/10, h*4/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, canvas)
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		cv2.destroyAllWindows()

	# wait for a change
	i=0
	try:
		for u in urls.keys():
			print u, urls[u]
			urllib.urlretrieve(urls[u], "data/"+u+".gif")
			box_10 = [(25+i*(w-50)/10, 4*h/5), (25+(i+1)*(w-50)/10, 10+4*h/5), colors['other'], -2]
			cv2.rectangle(canvas, box_10[0], box_10[1], box_10[2], box_10[3])
			cv2.rectangle(canvas, box_10[0], box_10[1], colors['green'], 2)
			cv2.imshow(window_name, canvas)
			k = cv2.waitKey(5) & 0xFF
			if k == 27:
				break
			i+=1
	except:
		return False
	print "[UPDAtE]: complete at: " + time.asctime()
	time.sleep(2)
	if i==len(urls):
		change_state(4)
		print "[ST]: IV"

	cv2.destroyAllWindows()
	return


def load_track(f_in):
	# like select_track + read_tracks
	gif = cv2.VideoCapture(f_in)
	id_st = f_in
	if id_st.find('\\')>0: id_st = id_st[id_st.find('\\')+1:id_st.rfind('.')]
	else: id_st = id_st[id_st.find('/')+1:id_st.rfind('.')]
	print "[loading]: "+id_st

	state, img = gif.read()

	# ex-return id_st, state, data (img)
	tracks = []
	for jj in range(24):
		start_point = [40, 80+jj*20]
		end_point = [570, 80+jj*20]
		max_amp_y = 20
		track = []
		for ix in range(start_point[0], end_point[0]):
			if (ix==172 or ix==305 or ix==437): continue
			# this checks for top value
			past_pixel= []
			act_pixel = [None, None, None]
			y_top = 0
			for iy in range(start_point[1]-max_amp_y, start_point[1] + max_amp_y/2):
				past_pixel = list(act_pixel)
				act_pixel = list(img[iy][ix])
				if act_pixel[2]==0 and past_pixel[2]==255:
					y_top = iy
					break
			# this checks for bottom value
			past_pixel= []
			act_pixel = [None, None, None]
			y_bottom = 0
			for iy in range(start_point[1]-max_amp_y/2, start_point[1]+max_amp_y):
				past_pixel = list(act_pixel)
				act_pixel = list(img[iy][ix])
				if act_pixel[2]==255 and past_pixel[2]==0:
					y_bottom = iy
					break
			# if empty
			if (y_top==0 and y_bottom==0 and list(img[80+jj*20][ix])[2]==255):
				delta_y = 0
			# if not empty
			else:
				if (y_top==0): y_top = start_point[1]-max_amp_y
				if (y_bottom==0): y_bottom=start_point[1]+max_amp_y
				delta_y = abs(y_top-y_bottom)
			#print "<x: %i> [%i : %i]: %i" % (ix, y_top, y_bottom, delta_y)
			track.append([delta_y, y_top, y_bottom])
		tracks.append(track)
	return tracks



def draw_sismograms():
	def on_mouse(event, x, y, flags, param):
		return
	# create window and canvas once
	lud = "24/4/1420"
	window_name = "Ensamble Terrestre"
	# uncomment for fullscreen
	# cv2.namedWindow(window_name)
	cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(window_name,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_AUTOSIZE)
	
	cv2.setMouseCallback(window_name, on_mouse)
	canvas = np.zeros((h, w, 3), np.uint8)
	for j in range(h):
		for i in range(w):
			canvas[j][i]=colors['dark']

	# draw the boxes
	box_main = [(2,2), (w-2, h-2), colors['blue'], 1]
	box_plot = [(10,10), (w-15, h/2), colors['blue'], 1]
	nu_canvas = canvas.copy()
	cv2.rectangle(nu_canvas, box_main[0], box_main[1], box_main[2], box_main[3])
	cv2.putText(nu_canvas, "i n t e r s p e c i f i c s" ,(-72+w/2, 20), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['blue'])
	cv2.putText(nu_canvas, "Ensamble" ,(-110+w/2,  10+h/4), cv2.FONT_HERSHEY_DUPLEX, 1.4, colors['green'])
	cv2.putText(nu_canvas, "Terrestre" ,(-105+w/2, 60+h/4), cv2.FONT_HERSHEY_SIMPLEX, 1.5, colors['green'])
	cv2.putText(nu_canvas, "[Analizando] " ,(40+w*3/10, h*4/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])

	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(5) & 0xFF

	# read the data:
	# N - spig : san pedro martir, BC 	[31.046, -115.466]	negro, cuchillo obs
	# E - ppig : popocatepetl, MX		[19.067, -98.628]	rojo, caña
	# S - huig : huatulco, OA 			[15.769, -96.108]	azul, conejo
	# W - caig : el cayaco, GE 			[17.048, -100.267]  blanco, casa
	data = {}
	cv2.putText(nu_canvas, " . " ,(40+w*3/10, h*5/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(10) & 0xFF
	data["N"] = load_track("./data/lpig.gif")
	cv2.putText(nu_canvas, " . " ,(60+w*3/10, h*5/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(10) & 0xFF
	data["E"] = load_track("./data/ppig.gif")
	cv2.putText(nu_canvas, " . " ,(80+w*3/10, h*5/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(10) & 0xFF
	data["S"] = load_track("./data/huig.gif")
	cv2.putText(nu_canvas, " . " ,(100+w*3/10, h*5/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(10) & 0xFF
	data["W"] = load_track("./data/caig.gif")
	cv2.putText(nu_canvas, " . " ,(120+w*3/10, h*5/6), cv2.FONT_HERSHEY_PLAIN, 1, colors['green'])
	cv2.imshow(window_name, nu_canvas)
	k = cv2.waitKey(10) & 0xFF


	# each data is an array
	# show it continously over time
	# ------------------- ---------- ---------------------/ ///
	last_hour = -2
	first_hour = 0
	change = False
	now_hour = int(time.asctime()[11:13])
	if int(time.asctime()[14:16])<16: 
		now_hour=now_hour-1
		change = True

	samples = {}
	buff = {k:[] for k in data.keys()}
	x_off = {'N':10, 'E':w/2+5, 'S':w/2+5, 'W':10}
	y_off = {'N':h/4+20, 'E':h/4+20, 'S':3*h/4, 'W':3*h/4}
	stations = {'N':'Norte', 'E':'Este', 'S':'Sur', 'W':'Oeste'}
	st_wi = 100
	step = (w-30)/(2.0*st_wi)
	print "<-- streaming track -->"
	for hour in range(last_hour, first_hour):
		for i in range(0, 4*132-1):
			samples = {k:data[k][hour][i][0] for k in data.keys()}
			#add data to buffers
			for k in data.keys():
				buff[k].append(samples[k])
				if len(buff[k])>st_wi: buff[k] = buff[k][-st_wi:]
			# clone canvas
			nu_canvas = canvas.copy()
			cv2.rectangle(nu_canvas, (5, 45), ((w/2)-2, (h/2)-7),  colors['dark'],  -1)
			cv2.rectangle(nu_canvas, (5, 45), ((w/2)-2, (h/2)-7),  colors['other'],  1)
			cv2.rectangle(nu_canvas, (w/2+2, 45), (w-5, (h/2)-7),  colors['dark'],  -1)
			cv2.rectangle(nu_canvas, (w/2+2, 45), (w-5, (h/2)-7),  colors['other'],  1)
			cv2.rectangle(nu_canvas, (5, h/2+27), (w/2-2, h-25),  colors['dark'],  -1)
			cv2.rectangle(nu_canvas, (5, h/2+27), (w/2-2, h-25),  colors['other'],  1)
			cv2.rectangle(nu_canvas, (w/2+2, h/2+27), (w-5, h-25),  colors['dark'],  -1)
			cv2.rectangle(nu_canvas, (w/2+2, h/2+27), (w-5, h-25),  colors['other'],  1)
			for k in data.keys():
				# draoe scopes
				for j,b in enumerate(range(-len(buff[k]), 0)):
					if (j>0):
						#print abs(j), step, abs(j)*step
						cv2.rectangle(nu_canvas, (int(x_off[k]+(j-1)*step), y_off[k]+np.clip(buff[k][b-1], 0, 40)), \
									(int(x_off[k]+abs(j)*step), y_off[k]+np.clip(buff[k][b],0,40)), colors["green"], 1)
						cv2.rectangle(nu_canvas, (int(x_off[k]+(j-1)*step), y_off[k]-np.clip(buff[k][b-1], 0, 40)), \
									(int(x_off[k]+abs(j)*step), y_off[k]-np.clip(buff[k][b],0,40)), colors["green"], 1)
				# draw titles
				cv2.putText(canvas, "i n t e r s p e c i f i c s" ,(-72+w/2, 15), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['blue'])
				cv2.putText(canvas, "[Ensamble Terrestre]" ,(-85+w/2, 30), cv2.FONT_HERSHEY_PLAIN, 1, colors['white'])
				# draw labels
				cv2.putText(nu_canvas, "[S]:" ,(x_off[k]+10, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['red'])
				cv2.putText(nu_canvas, stations[k] ,(x_off[k]+35, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['white'])
				cv2.putText(nu_canvas, "[A]:" ,(x_off[k]+82, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['red'])
				cv2.putText(nu_canvas, str(buff[k][b]) ,(x_off[k]+105, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['white'])
				data_hour = now_hour+(hour+1)
				data_min = int( 60 - (60/528.0) * (4*132-1-i) )
				#data_sec = int( (60*(4*132-1-i)%528 ) )
				cv2.putText(nu_canvas, "[T]:" ,(x_off[k]+130, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['red'])
				cv2.putText(nu_canvas, str(data_hour).zfill(2)+':'+str(data_min).zfill(2)+' hrs' ,(x_off[k]+150, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['white'])
				#cv2.putText(nu_canvas, str(hour+1)+'h '+str((4*132-1)-i)+'ss' ,(x_off[k]+150, y_off[k]-10+h/4), cv2.FONT_HERSHEY_PLAIN, 0.7, colors['white'])
			data_str = ""
			# add data to buffer
			for i,k in enumerate(data.keys()):
				data_str += chr(65+buff[k][b])
			#print data_str
			# send data
			write_list_I2C(data_str)
			# show it
			cv2.imshow(window_name, nu_canvas)
			k = cv2.waitKey(400) & 0xFF
			if k == 27:
				cv2.destroyAllWindows()
				break
			# if going beyond now, break
			if data_hour>=int(time.asctime()[11:13]) and data_min >= int(time.asctime()[14:16]) and not change: break
	print "\n<-- stream endpoint -->"
	cv2.destroyAllWindows()

	'''
	# at last wait for a button
	while(1):
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			cv2.destroyAllWindows()
			change_state(5);
			break
	# end draw sismogram
	'''


# ----------------------------------------------------------------\\ M A I N
if __name__ == "__main__":
	'''
	# -- osc
	send_period = 1
	osc_host = "192.168.1.73" 
	osc_port = 16000
	send_addr = osc_host, osc_port
	cOsc = OSC.OSCClient()
	try:
		cOsc.connect(send_addr)
		print "<osc>: ok"
	except:
		print "<osc>: x.x"
	'''
	print "[ interspecifics // ensamble terrrestre ]"
	# --timing
	t0 = 0
	t1 = 0

	# -- data
	change_state(2)
	print "[ST]: Q0Q0"
	#get_sismograms()
	#id_st, sta, data = load_sismogram()
	##track = read_track(data, 1)
	#draw_sismogram(track)
	#stream_track(cOsc, track, 0.22)
	
	while(True):
		if time.time()-t0 > 900:
			try:
				draw_updating()
			except:
				continue
			t0 = time.time()
		else:
			try:
				draw_sismograms()
			except:
				continue
		"""
		if state==0:
			draw_willkommen()
		elif state==2:
			draw_updating()
			t0 = time.time()
		elif state==4:
			draw_sismograms()
		else:
			break
		"""

"""
0. select modo

1. new data
	a. download
	b. read + assign
	c. start streaming
	d. periodically refresh

2. old data
	a. select
	b. read + assign
	c. start streamming
"""
