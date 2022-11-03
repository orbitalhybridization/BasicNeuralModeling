from brian2 import *
import matplotlib.pyplot as plt
from social_bug import Bug
import random

# BUG 1


# BUG 1 


# BUG

# BUG 2



# BUG 3



map_size = 100
global otherbugx, otherbugy, meter_plot, bug_plot, sr_plot, sl_plot, bugs, all_eqs
bug_count = 2
duration=1000
# init bugs with a random location and social limit
limits = [20,5]
locs = [[0,0],[50,50]]
bugs=[Bug(limits[i],locs[i]) for i in range(bug_count)] # a list of bugs in the map

f = figure(1)
bug_plot = [plot(bug.ns.ns.x, bug.ns.ns.y, 'ko')[0] for bug in bugs]
#import pdb; pdb.set_trace()
sr_plot = [plot([0], [0], 'w')[0] for i in range(len(bugs))]   # Just leaving it blank for now but there are sensors for every bug
sl_plot = [plot([0], [0], 'w')[0] for i in range(len(bugs))]
meter_plot = [text([0],[0],'',color='w') for i in range(len(bugs))] # plot the meter for each bug (social_battery / social_limit)


def findClosestBug(bug_index):

	distance = math.inf
	closestBug = None
	
	bug = bugs[bug_index]

	for i,otherbug in enumerate(bugs):

		if i == bug_index:
			continue

		else:
			current_distance = ((bug.ns.ns.x-otherbug.ns.ns.x)**2+(bug.ns.ns.y-otherbug.ns.ns.y)**2)
			#print(current_distance)
			if current_distance[0] < distance:
				closestBug = otherbug

	return closestBug.ns.ns.x,closestBug.ns.ns.y

@network_operation()
def update_positions():

	global otherbugx, otherbugy

	for bug_index,bug in enumerate(bugs):

		# update locations

		bug.ns.sr.x = bug.ns.ns.x + bug.ns.sr.x_disp*sin(bug.ns.ns.angle)+ bug.ns.sr.y_disp*cos(bug.ns.ns.angle) 
		
		bug.ns.sr.y = bug.ns.ns.y + - bug.ns.sr.x_disp*cos(bug.ns.ns.angle) + bug.ns.sr.y_disp*sin(bug.ns.ns.angle) 

		bug.ns.sl.x = bug.ns.ns.x +  bug.ns.sl.x_disp*sin(bug.ns.ns.angle)+bug.ns.sl.y_disp*cos(bug.ns.ns.angle)

		bug.ns.sl.y = bug.ns.ns.y - bug.ns.sl.x_disp*cos(bug.ns.ns.angle)+bug.ns.sl.y_disp*sin(bug.ns.ns.angle) 
	
		# find the closest bug and use that as our stimulus
		otherbugx,otherbugy = findClosestBug(bug_index)

		# update social bars

		# non-social bug far away
		if (bug.color == 'b'):
			if (((bug.ns.ns.x-otherbugx)**2+(bug.ns.ns.y-otherbugy)**2) > 3350): # this might need to be tuned
				bug.update(-1) # recharging

			else:
				bug.update(0)

		# social bug close by
		else:
			if (((bug.ns.ns.x-otherbugx)**2+(bug.ns.ns.y-otherbugy)**2) < 200):
				bug.update(1) # social bar increase
			
			else:
				bug.update(0)

		#else: # social bugs far away and non-social bugs close by just need to move!
		#	bug.update(0)

		# adjust for end of map
		if (bug.ns.ns.x < -map_size):
			bug.ns.ns.x = -map_size
			bug.ns.ns.angle = pi - bug.ns.ns.angle
		if (bug.ns.ns.x > map_size):
			bug.ns.ns.x = map_size
			bug.ns.ns.angle = pi - bug.ns.ns.angle
		if (bug.ns.ns.y < -map_size):
			bug.ns.ns.y = -map_size
			bug.ns.ns.angle = -bug.ns.ns.angle
		if (bug.ns.ns.y > map_size):
			bug.ns.ns.y = map_size
			bug.ns.ns.angle = -bug.ns.ns.angle

		bug.ns.sr.otherbugxx = otherbugx
		bug.ns.sr.otherbugyy = otherbugy
		bug.ns.sl.otherbugxx = otherbugx
		bug.ns.sl.otherbugyy = otherbugy
		
		#print(otherbugx)
	all_eqs = [bug.ns.all_eqs for bug in bugs]

@network_operation(dt=2*ms)
def update_plot(t):
	global bug_plot, meter_plot, sr_plot, sl_plot

	for bug_index,bug in enumerate(bugs):
		#print(bug.ns.ns.x + 5)
		#indx=int(.5*t/ms+1)
		# import pdb; pdb.set_trace()
		bug_plot[bug_index].remove() # remove the bug and sensors from the figure
		sr_plot[bug_index].remove()
		sl_plot[bug_index].remove()
		meter_plot[bug_index].remove()
		bug_x_coords = [bug.ns.ns.x, bug.ns.ns.x-4*cos(bug.ns.ns.angle), bug.ns.ns.x-8*cos(bug.ns.ns.angle)]	# ant-like body
		bug_y_coords = [bug.ns.ns.y, bug.ns.ns.y-4*sin(bug.ns.ns.angle), bug.ns.ns.y-8*sin(bug.ns.ns.angle)]

		bug_plot[bug_index] = plot(bug_x_coords, bug_y_coords, bug.color+'o')[0]	 # Plot the bug's current position
		sr_plot[bug_index] = plot([bug.ns.ns.x, bug.ns.sr.x], [bug.ns.ns.y, bug.ns.sr.y], 'g')[0]	 # Plot sensors
		sl_plot[bug_index] = plot([bug.ns.ns.x, bug.ns.sl.x], [bug.ns.ns.y, bug.ns.sl.y], 'g')[0]
		meter_plot[bug_index] = text(bug.ns.sr.x + 2,bug.ns.sr.y + 2,str(bug.social_bar)+'/'+str(bug.social_limit),color='k',fontsize=8) # plot
		axis([-100,100,-100,100])
	
		draw() # this should update them all at once!
	
	#print(".")

	pause(0.01)

#Monitor motor activity by stim strength
"""
ML = StateMonitor(sbl, ('v','x','y','I','foodxx','foodyy'), record=True)
MR = StateMonitor(sbr, ('v','x','y','I','foodxx','foodyy'), record=True)
SL = StateMonitor(sl, ('v','x','y','I','foodxx','foodyy'), record=True)
SR = StateMonitor(sr, ('v','x','y','I','foodxx','foodyy'), record=True)

MB = StateMonitor(bug, ('motorl', 'motorr', 'speed', 'angle', 'x', 'y'), record = True)
"""
import matplotlib.pyplot as plt
net = Network()
net.run(duration*ms,report='text')
plt.figure()

#import pdb
#pdb.set_trace()


"""
plt.subplot(2,1,1)
plt.plot(sqrt(((SL.x-SL.foodxx)**2+(SL.y-SL.foodyy)**2))[0],SL.I[0]/mV)
title("Left Response by Stimulus Strength")

plt.subplot(2,1,2)
plt.plot(sqrt(((SR.x-SR.foodxx)**2+(SR.y-SR.foodyy)**2))[0],SR.I[0]/mV)
title("Right Response by Stimulus Strength")
plt.subplot_tool()

plt.show()
"""
