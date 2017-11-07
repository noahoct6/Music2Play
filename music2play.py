import numpy as np
import scipy.io.wavfile
import matplotlib.pyplot as plt

keys = {} #dictionary with keys of frequencies leading to letter values
note_freqs = []
for n in range(1,89):
	i_note = float((2.**((n-49.)/12.))*440.)
	note_freqs.append(i_note) #calculate all frequencies in the range of the piano keys, 88 values
	if(n%12 == 1):keys[i_note]='A'
	elif(n%12 == 2):keys[i_note]='A#'
	elif(n%12 == 3):keys[i_note]='B'
	elif(n%12 == 4):keys[i_note]='C'
	elif(n%12 == 5):keys[i_note]='C#'
	elif(n%12 == 6):keys[i_note]='D'
	elif(n%12 == 7):keys[i_note]='D#'
	elif(n%12 == 8):keys[i_note]='E'
	elif(n%12 == 9):keys[i_note]='F'
	elif(n%12 == 10):keys[i_note]='F#'
	elif(n%12 == 11):keys[i_note]='G'
	elif(n%12 == 12):keys[i_note]='G#'


def fourier(amps,dt,nt): #pass specific section of soudwave, give amplitude section array, number of samples, and sampling period - this function outputs the the top 10 frequencies with largest magnitudes
	fourier_coeffs = np.absolute(np.fft.fft(amps))
	fourier_freqs = np.fft.fftfreq(nt,d=dt)

	freq_amps = [] #will store max amplitude of each frequency

	for freq in note_freqs:
		f_L = freq - .015*freq #create lower bound error frequency
		f_H = freq + .015*freq #create upper bound error frequency

		for i,c in enumerate(fourier_freqs):
			if(c > f_L): #finds the index of the frequency closest to the lower bound
				i_L = i
				break
		for i,c in enumerate(fourier_freqs):
			if(c > f_H): #finds the index of the frequency closest to the upper bound
				i_H = i
				break

		try:freq_amps.append(np.amax(np.array(fourier_coeffs[i_L:i_H]))) #try to append the maximum amplitude in the selected frequency range
		except:freq_amps.append(0) #if it amax fails, append zero

	freq_arr = np.array(freq_amps) / np.amax(freq_amps) #normalize all amplitudes to the max amplitude, new range is from 0-1

	max_freqs = []
	for i,c in enumerate(freq_arr): #go through the list of amplitudes and find the max amplitude and its corresponding frequency
		if(c>.35):
			max_freqs.append(note_freqs[i])

	#uncomment to view fourier graph
	plt.bar(note_freqs, freq_arr, align='center', alpha=0.5, hold=True) #discrete plot
	plt.xlim(0,4200) #limit to only the frequencies we care about
	plt.show()

	final_arr = []
	for freq in max_freqs:final_arr.append((freq,keys[freq])) #find the notes associated with frequencies and enter into a final list, keys[freq]
	return(final_arr) #return the array final_arr


cmajor = scipy.io.wavfile.read('daijiro_riff.wav') #read entire sound file
snd = cmajor[1] #parse
height = snd[:,0] #get amplitudes
dt = 1./cmajor[0] #sample period = 1/f_s
nt = height.shape[0] #number of samples

magnitudes = np.absolute(height) #create an array of the magnitude of the signal
samples = [] #initialize the x-domain as sample number starting at 0
for i in range(0,nt): #create x-domain
	samples.append(i)

envelope = []
envelope_sample = []
marg_i = 400 #marginal index
jump = marg_i
while(marg_i<nt):
	curr_max = 0
	for i in range(marg_i-jump,marg_i): #approximate by finding max over a given interval
		if(magnitudes[i]>curr_max):
			curr_max = magnitudes[i]
			curr_samp = i
	envelope.append(curr_max) #add local maximum
	envelope_sample.append(curr_samp) #add sample number of local maximum
	marg_i = marg_i + jump

spikes = []
spike_depth = 1100 #depth of spike, play with to get right spikes
for i in range(3,len(envelope_sample)): #find spikes in envolope array
	if(((envelope[i]-envelope[i-1])>spike_depth) or ((envelope[i]-envelope[i-2])>spike_depth) or ((envelope[i]-envelope[i-3])>spike_depth)):
		spikes.append(envelope_sample[i])

clean_spikes = [] #initialize list of spike coordinates without redundancy
cutoff = 1600 #redundancy width specified
for i in range(1,len(spikes)): #get rid of redundancy in spikes, enter into new array clean_spikes
	if(((spikes[i]-spikes[i-1])<cutoff) and (spikes[i-1] not in clean_spikes)):
		clean_spikes.append(spikes[i])
	elif(((spikes[i]-spikes[i-1])<cutoff) and (spikes[i-1] in clean_spikes)):
		del(clean_spikes[-1])
		clean_spikes.append(spikes[i])
	else:
		clean_spikes.append(spikes[i])

#uncomment to see magnitude with spike lines
# for spike in clean_spikes:
#     plt.axvline(x=spike,color='r')
# plt.plot(envelope_sample,envelope)
# #plt.xlim(0,200000)
# plt.show()

# print(spikes)
# print(clean_spikes)

results = []
lower = 0 #lower bound of slice
upper = 7000 #upper bound of slice

#use just below to look at indivual spike results on fourier graph, uncomment bar graph in fourier function
index = 1
try:
	results.append(fourier(height[clean_spikes[index]-lower:clean_spikes[index]+lower],dt,lower+upper))
except:
	try:
		results.append(fourier(height[0:clean_spikes[index]+upper],dt,clean_spikes[index]+upper))
	except:
		results.append(fourier(height[clean_spikes[index]-lower:nt],dt,nt+lower-clean_spikes[index]))

# for spike in clean_spikes: #send portions of original file to fourier function and store return into results list
# 	try:
# 		results.append(fourier(height[spike-lower:spike+upper],dt,lower+upper))
# 	except:
# 		try:
# 			results.append(fourier(height[0:spike+uppper],dt,spike+upper))
# 		except:
# 			results.append(fourier(height[spike-lower:nt],dt,nt+lower-spike))
print(results, clean_spikes[1]) #display result as list of lists
