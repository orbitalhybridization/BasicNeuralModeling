from brian2 import *
start_scope()

class Bug():

	def __init__(self,social_limit,loc,recharge_rate=1):
		
		"""
		Every bug starts off with a social limit
		"""
		
		# Init

		self.social_limit = social_limit
		self.social_bar = 0 # start out with an empty social bar
		self.recharge_rate = recharge_rate

		self.color = 'r' # start off social means start off red
		self.ns = NervousSystem('agg') # social means start as an agg

		self.ns.ns.x = loc[0]
		self.ns.ns.y = loc[1]

		# init base conditions
		self.ns.ns.motorl = 1 # 0
		self.ns.ns.motorr = 1 # 0
		self.ns.ns.angle = pi/2
		
		#import pdb; pdb.set_trace()

	def update(self,amount):
		"""
		Update bug's temperament based on social bar
		"""

		# update social bar
		self.social_bar += amount

		# change color if needed
		if ((self.social_bar >= self.social_limit) and (self.color == 'r')): # non-social if we've hit limit
			self.changeTemperament()

		elif ((self.social_bar == 0) and (self.social_limit != 0) and (self.color == 'b')): # become social if recharged
			self.changeTemperament()

		#dist = sqrt(((self.ns.sr.x-self.ns.sr.otherbugxx)**2+(self.ns.sr.y-self.ns.sr.otherbugyy)**2))
		#print(self.ns.sr.u)
		#print(dist)

	def changeTemperament(self):
		
		if self.color == 'b': # formerly coward
			self.ns = NervousSystem('agg') # change neuronal connections to agg
			self.color = 'r' # change colour to red to indicate

		else:
			self.ns = NervousSystem('cow') # change neuronal connections to cow
			self.color = 'b'


class NervousSystem(): # nervous system

	def __init__(self,temperament):

		"""
		Here the brian2 neurons are defined.
		"""

		self.sr = None
		self.sl = None
		self.temperament = temperament
		self.all_eqs = []
		
		if temperament == 'agg':
			
			self.ns = self.makeAggressor()

		else:
			self.ns = self.makeCoward()


	def makeAggressor(self):
		a = 0.02
		b = 0.2
		c = -65
		d = 2
		g_synpk=5
		tau_ampa=0.5*ms
		g_synmaxval=(g_synpk/(tau_ampa/ms*exp(-1)))

		sensor_eqs = '''
		# Sensor neurons
		a = 0.02 :1
		b = 0.2 : 1
		c = -65: 1
		d = 2:1

		I0 = 1250:1
		tau_ampa=0.5*ms:second
		g_synpk=5:1
		g_synmaxval=(g_synpk/(tau_ampa/ms*exp(-1))):1


		# equations for neurons
		    dv/dt = ((0.04 * v**2 + 5 * v + 140 - u + I) + (s *(0 - v)))/ms  : 1
		    du/dt = (a * (b * v - u))/ms : 1
		    x : 1
		    y : 1
		    x_disp : 1
		    y_disp : 1
		    otherbugxx : 1
		    otherbugyy : 1
		    mag :1
		    I = I0 / sqrt(((x-otherbugxx)**2+(y-otherbugyy)**2)): 1
		    s : 1
		'''

		sensor_reset = '''
		    v = c
		    u = u + d
		'''


		# right sensor
		sr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sr.v = c
		sr.u = c*b
		sr.x_disp = 5
		sr.y_disp = 5
		sr.x = sr.x_disp
		sr.y = sr.y_disp
		sr.otherbugxx = 1
		sr.otherbugyy = 1
		sr.mag=1

		# left sensor
		sl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sl.v = c
		sl.u = c*b
		sl.x_disp = -5
		sl.y_disp = 5
		sl.x = sl.x_disp
		sl.y = sl.y_disp
		sl.otherbugxx = 1
		sl.otherbugyy = 1
		sl.mag=1

		# right bug motor neuron
		sbr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sbr.v = c
		sbr.u = c*b
		sbr.otherbugxx = 1
		sbr.otherbugyy = 1
		sbr.mag=0

		# left bug motor neuron
		sbl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sbl.v = c
		sbl.u = c*b
		sbl.otherbugxx = 1
		sbl.otherbugyy = 1
		sbl.mag=0

		# The virtual bug
		bug_eqs = '''
		taum = 4.5*ms:second
		base_speed = 1:1
		turn_rate = 25*Hz:Hz
		alpha = 0.1:1


		#equations for movement here
		    dx/dt = (alpha * speed * cos(angle))/ms : 1
		    dy/dt = (alpha * speed * sin(angle))/ms : 1
		    speed = ((motorl + motorr)/2) + base_speed : 1
		    dangle/dt = (motorr - motorl) * turn_rate : 1
		    dmotorl/dt = -motorl/taum : 1
		    dmotorr/dt = -motorr/taum : 1
		'''
		#These are the equation  for the motor and speed

		bug = NeuronGroup(1, bug_eqs, clock=Clock(0.2*ms),method='euler')
	
		w = 10
		syn_rr=Synapses(sr, sbl, clock=Clock(0.2*ms), model='''
				taum = 4.5*ms:second
				g_synmax : 1
				dg_syn/dt = -g_syn/taum + z : 1
				dz/dt = -z/taum : Hz
				s_post = g_syn :1 (summed)
				''',
			    on_pre='''
				z+= g_synmax * Hz
			    ''')
		syn_rr.connect(i=[0],j=[0])
		syn_rr.g_synmax=g_synmaxval

		syn_ll=Synapses(sl, sbr, clock=Clock(0.2*ms), model='''
				taum = 4.5*ms:second
				g_synmax : 1
				dg_syn/dt = -g_syn/taum + z : 1
				dz/dt = -z/taum : Hz
				s_post = g_syn :1 (summed)
				''',
			    on_pre='''
				z+= g_synmax * Hz
			    ''')
		syn_ll.connect(i=[0],j=[0])
		syn_ll.g_synmax=g_synmaxval

		syn_r = Synapses(sbr, bug, clock=Clock(0.2*ms), on_pre='motorr += 10')
		syn_r.connect(i=[0],j=[0])
		syn_l = Synapses(sbl, bug, clock=Clock(0.2*ms), on_pre='motorl += 10')
		syn_l.connect(i=[0],j=[0])

		self.sr = sr
		self.sl = sl
	
		self.all_eqs = [syn_r,syn_l,syn_rr,syn_ll,sr,sl,sbr,sbl,bug]
		return bug


	def makeCoward(self):
		a = 0.02
		b = 0.2
		c = -65
		d = 2
		g_synpk=5
		tau_ampa=0.5*ms
		g_synmaxval=(g_synpk/(tau_ampa/ms*exp(-1)))

		sensor_eqs = '''
		# Sensor neurons
		a = 0.02:1
		b = 0.2:1
		c = -65:1
		d = 2:1

		I0 = 1250:1
		tau_ampa=0.5*ms:second
		g_synpk=5:1
		g_synmaxval=(g_synpk/(tau_ampa/ms*exp(-1))):1


		# equations for neurons
		    dv/dt = ((0.04 * v**2 + 5 * v + 140 - u + I) + (s *(0 - v)))/ms  : 1
		    du/dt = (a * (b * v - u))/ms : 1
		    x : 1
		    y : 1
		    x_disp : 1
		    y_disp : 1
		    otherbugxx : 1
		    otherbugyy : 1
		    mag :1
		    I = I0 / sqrt(((x-otherbugxx)**2+(y-otherbugyy)**2)): 1
		    s : 1
		'''

		sensor_reset = '''
		    v = c
		    u = u + d
		'''


		# right sensor
		sr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sr.v = c
		sr.u = c*b
		sr.x_disp = 5
		sr.y_disp = 5
		sr.x = sr.x_disp
		sr.y = sr.y_disp
		sr.otherbugxx = 1
		sr.otherbugyy = 1
		sr.mag=1

		# left sensor
		sl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sl.v = c
		sl.u = c*b
		sl.x_disp = -5
		sl.y_disp = 5
		sl.x = sl.x_disp
		sl.y = sl.y_disp
		sl.otherbugxx = 1
		sl.otherbugyy = 1
		sl.mag=1

		# right bug motor neuron
		sbr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sbr.v = c
		sbr.u = c*b
		sbr.otherbugxx = 1
		sbr.otherbugyy = 1
		sbr.mag=0

		# left bug motor neuron
		sbl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
		sbl.v = c
		sbl.u = c*b
		sbl.otherbugxx = 0
		sbl.otherbugyy = 0
		sbl.mag=0


		# The virtual bug
		bug_eqs = '''
		taum = 4.5*ms:second
		base_speed = 1:1
		turn_rate = 25*Hz:Hz
		alpha = 0.1:1


		#equations for movement here
		    dx/dt = (alpha * speed * cos(angle))/ms : 1
		    dy/dt = (alpha * speed * sin(angle))/ms : 1
		    speed = ((motorl + motorr)/2) + base_speed : 1
		    dangle/dt = (motorr - motorl) * turn_rate : 1
		    dmotorl/dt = -motorl/taum : 1
		    dmotorr/dt = -motorr/taum : 1
		'''
		#These are the equation  for the motor and speed

		bug = NeuronGroup(1, bug_eqs, clock=Clock(0.2*ms),method='euler')

		w = 10
		syn_rr=Synapses(sr, sbr, clock=Clock(0.2*ms), model='''
				taum = 4.5*ms:second
				g_synmax : 1
				dg_syn/dt = -g_syn/taum + z : 1
				dz/dt = -z/taum : Hz
				s_post = g_syn :1 (summed)
				''',
			    on_pre='''
				z+= g_synmax * Hz
			    ''')
		syn_rr.connect(i=[0],j=[0])
		syn_rr.g_synmax=g_synmaxval

		syn_ll=Synapses(sl, sbl, clock=Clock(0.2*ms), model='''
				taum = 4.5*ms:second
				g_synmax : 1
				dg_syn/dt = -g_syn/taum + z : 1
				dz/dt = -z/taum : Hz
				s_post = g_syn :1 (summed)
				''',
			    on_pre='''
				z+= g_synmax * Hz
			    ''')
		syn_ll.connect(i=[0],j=[0])
		syn_ll.g_synmax=g_synmaxval

		syn_r = Synapses(sbr, bug, clock=Clock(0.2*ms), on_pre='motorr += 10')
		syn_r.connect(i=[0],j=[0])
		syn_l = Synapses(sbl, bug, clock=Clock(0.2*ms), on_pre='motorl += 10')
		syn_l.connect(i=[0],j=[0])

		self.sr = sr
		self.sl = sl
		self.all_eqs = [syn_r,syn_l,syn_rr,syn_ll,sr,sl,sbr,sbl,bug]
		return bug
