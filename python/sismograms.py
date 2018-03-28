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
full gui access: select track, mode, update
serial stream data
"""

import cv2
import numpy as np
import random, time, glob
import urllib
import OSC


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


#inicio: x:40, y:80, 
#delta: 172, 305, 437: 15 mins


def read_track(img, ntrack):
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


def draw_sismogram(track):
	# -- canvas
	# colors: http://paletton.com/#uid=74j1u0kllll2H1Ec1bwuEvaS+W4
	val = 3.14
	tim = "-24:66:14"
	lud = "24/4/1420"
	colors = {'white':[202, 177, 166], 'dark': [63, 42, 48], \
				'blue':[243, 6, 78], 'green': [0, 218, 255], \
				'orange':[0, 49, 255], 'yellow': [77, 179, 8]}
	# create windows and canvas once
	w = 480
	h = 320
	window_name = "Ensamble Terrestre"
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
				#cv2.line(nu_can, (40 + 3*b, h/4), (40 + 3*b, -2*val+h/4), colors['orange'], 2)
				#cv2.line(nu_can, (40 + 3*b, h/4), (40 + 3*b, 2*val+h/4), colors['orange'], 2)
				cv2.line(nu_can, (40 + 3*b, (-2*val+h/4)+1), (40 + 3*b, -2*val+h/4), colors['orange'], 1)
				cv2.line(nu_can, (40 + 3*b, ( 2*val+h/4)-1), (40 + 3*b,  2*val+h/4), colors['orange'], 1)
				# send the messahe
				msg = OSC.OSCMessage()
				msg.setAddress(route)
				msg.append(t)
				msg.append(val)
				cOsc.send(msg)
				print msg,
				for i in range(len(str(msg))): print "\r", 
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

def lerp(a, b, s):
	""" lerp(start, stop, amt)"""
	return ((1-s)*a)+((s)*b)



if __name__ == "__main__":
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
	# -- data
	#get_sismograms()
	id_st, sta, data = load_sismogram()
	track = read_track(data, 6)
	#stream_track(cOsc, track, 0.22)
	draw_sismogram(track)

"""
1. intro: interspecifics, select 
	1.1 archive data	, goto 2.2
	1.2 new data		, goto 2.1

2. new data
	2.1 download		, goto 2.2
	2.2 select station  , goto 3.1

3. stream data, select
	3.1 stream itas osc , goto 4
	3.2 stream to serial, goto 4

4. periodic output
	4.1 loop, button to end, refresh periodically
	4.2 once, when end  , goto 1
	4.3 				, goto 1.2
"""