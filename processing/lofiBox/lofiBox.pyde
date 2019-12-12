add_library('serial')
add_library('sound')
# add_library('oscP5')


class capPad(object):
	"""postion of a pad is the center position of its bottom side"""
	def __init__(self, posX, posY, rotate_ang=0):
		super(capPad, self).__init__()
		self.posX = posX
		self.posY = posY
		self.rotate_ang = rotate_ang
		self.upSide = 40
		self.downSide = 110
		self.height = 80
		self.activated = False
		self.soundType = 0

	def display(self):
		noStroke()
		if self.activated:
			color = 0xFFFF968D
		else:
			color = 255
		fill(color)
		pushMatrix()
		translate(self.posX, self.posY)
		rotate(self.rotate_ang)
		quad(-self.upSide/2,-self.height, self.upSide/2, -self.height, self.downSide/2, 0, -self.downSide/2, 0)
		popMatrix()

	def activate(self):
		self.activated = True
		# if self.soundType=='melody':
		# 	if not self.soundfile.isPlaying():
		# 		self.soundfile.play()
		# elif self.soundType=='drum':
		# 	self.soundfile.play()
		if self.soundType:
			if not self.soundfile.isPlaying():
				self.soundfile.loop()

	def deactivate(self):
		self.activated = False
		# if self.soundType=='melody':
		# 	self.activated = self.soundfile.isPlaying()
		# else:
		# 	self.activated = False
		if self.soundfile.isPlaying():
			self.soundfile.stop()

	def addSound(self, soundfile, soundType):
		self.soundfile = soundfile
		self.soundType = soundType
		
def read_touch_from_port(myPort):
    if myPort.available()>0:
    	state_str =  myPort.readStringUntil(10) #10==\n
        if state_str != None and len(state_str) >= 4 and '\t' in state_str:
            # usually state_str == (u'Cn\r\n', 6)
            print(state_str)
            for i in range(8):
            	if capPins[i] in state_str:
            		capPads[i].activate()
            	else:
            		capPads[i].deactivate()

def setup():
	global myPort
	global IF_USE_ARDUINO
	global oct_img
	global capPads
	global capPins
	global fft
	global amp

	fullScreen()
	# for test: 
	# size(640,640)
	background(0,0,0)

	IF_USE_ARDUINO = True
    # print(height, width)

	imageMode(CENTER)
	oct_img = loadImage("octagon.png")
	oct_diameter = 350
	oct_img.resize(0,oct_diameter)
		
	capPads = []
	for i in range(8):
		rad = i*TWO_PI/8 
		posX = width/2 + cos(rad) * oct_diameter/2
		posY = height/2 + sin(rad) * oct_diameter/2
		rotate_ang = 3*PI/2 + rad  
		cap = capPad(posX, posY, rotate_ang)
		capPads.append(cap)

	if IF_USE_ARDUINO:
        	portName = Serial.list()[len(Serial.list()) - 1]
        	# portName = u'/dev/tty.usbmodem14101'
        	myPort = Serial(this, portName, 9600)
       		capPins = ['C4', 'C2', 'C1', 'C3', 'C5', 'C8', 'C7', 'C6']
	
	# drums = [f for f in os.listdir('data/drum') if f[-4:]=='.wav']
	# melodys = [f for f in os.listdir('data/melody') if f[-4:]=='.wav']

	# for i in range(5):
	# 	sf = SoundFile(this, os.path.join('data/drum', drums[i]))
	# 	capPads[i].addSound(sf, 'drum')

	# for i in range(5,8):
	# 	sf = SoundFile(this, os.path.join('data/melody', melodys[i-5]))
	# 	capPads[i].addSound(sf, 'melody')

	wavs = ['bell_shaker.wav', 'top70.wav', 'melody70.wav', 'creek_with_snaps.wav', 'lofi-all-fx.wav', 'lofidrum.wav', 'lofichord.wav', 'lofiVoice.wav']
	for i in range(8):
		sf = SoundFile(this, wavs[i])
		capPads[i].addSound(sf, 'loop')

	bands = 64
	fft = FFT(this, bands)
	inSound = AudioIn(this)
	inSound.start()
	fft.input(inSound)
	amp = Amplitude(this)
	amp.input(inSound)


def mousePressed():
	print(mouseX, mouseY)

def keyPressed():
	# 49~56 == 1~8
	if keyCode in range(49,57):
		capPads[keyCode-49].activate()

def keyReleased():
	# 49~56 == 1~8
	if keyCode in range(49,57):
		capPads[keyCode-49].deactivate()

def draw():
	background(0,0,0)
	if IF_USE_ARDUINO:
		read_touch_from_port(myPort)
	else:
		if not keyPressed:
			for i in range(5,8):
				capPads[i].deactivate()

	image(oct_img, width/2, height/2)
	for capP in capPads:
		capP.display()

	draw_spec_amp()

def draw_spec_amp():
    spectrum = fft.analyze()
    spectrum_2_show = spectrum[:32]
    rectMode(CENTER)
    colorMode(HSB)
    num_bars = len(spectrum_2_show)
    for i in range(num_bars):
        barWidth = width / num_bars
        xPos = barWidth * i
        c = 255 / num_bars * i
        fill(c, 100, 100);
        rect(xPos, height, barWidth-5, spectrum[i]*(height/2*5))
    
    # Get Volume
    vol  = amp.analyze()

    #volume indicator for center, left, right speaker 
    noStroke()
    fill(40)
    ellipse(width/2,height/2, 200*vol,  200*vol)
