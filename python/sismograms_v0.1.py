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
stream data

v0.2
----
graphic ui
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
	id_st = id_st[id_st.find('\\')+1:id_st.rfind('.')]
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
		print "<x: %i> [%i : %i]: %i" % (ix, y_top, y_bottom, delta_y)
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


def stream_track(cOSc, track, per):
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
		print msg
		time.sleep(per)
	print "<-- stream endpoint -->"
	return 0


if __name__ == "__main__":
	send_period = 1
	osc_host = "127.0.0.1" 
	osc_port = 8000
	try:
		send_addr = osc_host, osc_port
		cOsc = OSC.OSCClient()
		cOsc.connect(send_addr)
		print "<osc>: ok"
	except:
		print "<osc>: x.x"
	
	# -- data
	id_st, sta, data = load_sismogram()
	track = read_track(data, 8)
	stream_track(cOsc, track, 0.66)
