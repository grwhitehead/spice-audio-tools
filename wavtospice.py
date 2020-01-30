#!/usr/bin/env python3
#coding: utf-8

import sys
import wave
import struct
import math
import argparse

formats = (None, '<b', '<h', '<i', '<i')

def read_wav(filename, vrange):
	waveFile = wave.open(filename, 'r')
	data = []
	t = 0

	(nchannels, sampwidth, framerate, nframes, comptype, compname) = waveFile.getparams()
	timestep = 1.0 / framerate

	print('Framerate: %s' % framerate)
	print('Sample width: %s' % sampwidth)
	print('Channels: %s' % nchannels)

	assert sampwidth > 0

	for j in range(nframes):
		waveData = waveFile.readframes(1)

        #Take only the first channel
		waveData = waveData[:sampwidth]
		try:
			waveData = waveData + bytes([0]) if sampwidth == 3 else waveData
			fmt = formats[sampwidth]
		except IndexError:
			raise ValueError('Unsupported sample width')

		temp = struct.unpack_from(fmt, waveData)
		data.append((t * timestep, vrange * float(temp[0]) / (2**(8 * sampwidth - 1) - 1)))
		t += 1

	return data


def write_spice(data, filename):
	with open(filename, 'w') as f:
		for d in data:
			f.write("{:.6e} {:.4f}\n".format(*d))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("wav_file", help="Specify wav file as input")
	parser.add_argument("spice_file", help="Specify output filename for spice data")
	parser.add_argument("--vrange", dest='vrange', default=1, type=float)
	args = parser.parse_args()

	data = read_wav(args.wav_file, args.vrange)

	print('PP voltage: %s' % (max(i[1] for i in data) - min(i[1] for i in data)))
	print('RMS voltage: %s' % math.sqrt(sum(i[1]**2 for i in data)/len(data)))

	write_spice(data, args.spice_file)
