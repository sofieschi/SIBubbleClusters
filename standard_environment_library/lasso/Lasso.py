from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E
from plugins.standard_environment_library._standard_behaviour_mixins.Movable import Movable
from plugins.standard_environment_library._standard_behaviour_mixins.Deletable import Deletable
from plugins.standard_environment_library._standard_behaviour_mixins.Mergeable import Mergeable
from plugins.standard_environment_library._standard_behaviour_mixins.Lassoable import Lassoable
from functools import cmp_to_key
import math 

class Lasso(Deletable, Movable, Mergeable, SIEffect):
	regiontype = PySI.EffectType.SI_CUSTOM
	regionname = "__LASSO__"
	region_display_name = "Lasso"

	def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
		super(Lasso, self).__init__(shape, uuid, E.id.lasso_texture, Lasso.regiontype, Lasso.regionname, kwargs)
		self.set_QML_path("Lasso.qml")
		self.color = E.id.lasso_color
		self._block_remove_link = False
		self._sb_center_of_circle = []
		self._sb_radius = 0.0
		self._sb_endpoints = []
		self._sb_lassoable_positions = []
		
	@SIEffect.on_enter(E.id.lasso_capabiliy, SIEffect.EMISSION)
	def on_lasso_enter_emit(self, other):
		return self._uuid

	@SIEffect.on_leave(E.id.lasso_capabiliy, SIEffect.EMISSION)
	def on_lasso_leave_emit(self, other):
		return self._uuid

	@SIEffect.on_link(SIEffect.EMISSION, PySI.LinkingCapability.POSITION)
	def position(self):
		#SIEffect.debug('LASSO.position self.x,y={},{}  last={},{}'.format(self.x,self.y, self.last_x, self.last_y))
		#SIEffect.debug('LASSO.position aabb[0]={},{},{}'.format(self.aabb[0].x,self.aabb[0].y, self.aabb[0].z))
		x = self.x - self.last_x
		y = self.y - self.last_y
		self.last_x = self.x
		self.last_y = self.y
		#SIEffect.debug('LASSO.position x,y={},{}  self.x,y={},{}'.format(x,y, self.x, self.y))
		return x, y, self.x, self.y


	def set_block_remove_link(self, block):
		self._block_remove_link = block
		
	def is_remove_link_blocked(self) -> bool:
		return self._block_remove_link
	
	def get_link_sender(self):
		result = self.get_all_lnk_sender()
		for sender in result:
			SIEffect.debug("Lasso.get_link_receiver : sender {}".format(SIEffect.short_uuid(sender)))
		return result

	def get_linked_lassoables(self):
		lassoables = []
		all_lassoable = SIEffect.get_all_objects_extending_class(Lassoable);
		SIEffect.debug("Lasso.get_linked_lassoables : self_uuid={} nr_of_all_lassoable {}".format(SIEffect.short_uuid(self.get_uuid()), len(all_lassoable)))
		for l in all_lassoable:
			SIEffect.debug("Lasso.get_linked_lassoables : lassoable sender={}".format(l.get_all_lnk_sender()))
			if self.get_uuid() in l.get_all_lnk_sender():
				lassoables.append(l)
		SIEffect.debug("Lasso.get_linked_lassoables : nr2 {}".format(lassoables))
		return lassoables
	
	def recalculate_hull(self):
		list_of_linked_lassoables = self.get_linked_lassoables()
		if len(list_of_linked_lassoables) == 0:
			return
		bboxes_points = []
		for l in list_of_linked_lassoables:
			for i in list(range(4)):
				bboxes_points.append([l.x + l.aabb[i].x, l.y + l.aabb[i].y])  
		self.recalculate_hull_with_additional_points(bboxes_points, True)
		
	# add additional points to the set of points of the hull of the bubble.
	# Then recalculate the convex hull
	def recalculate_hull_with_additional_points(self, additional_points, create_new=False):
		SIEffect.debug("recalculate_hull x,y={},{}".format(self.x, self.y))
		# The additional_points are in absolute coordinates
		# First they must be changed to relative coordinates relative to the origin x,y of the bubble,
		# because the shape is defined als PointVector for coordinates relative to the origin x,y
		additional_points_relative = []
		for p in additional_points:
			additional_points_relative.append([p[0]-self.x,p[1]-self.y])
			additional_points_relative.append([p[0]-self.x,p[1]-self.y]) # twice, because the convex hull algorithm has a bug, ignoring points
		points = PySI.PointVector(additional_points_relative)
		if not create_new:
			for p in self.shape:
				points.append(p)
		ret = Lasso.graham_scan(points)
		ret = Lasso.explode(ret, 1.1)
		new_shape = PySI.PointVector()
		minx = 100000.0
		maxx = 0.0
		miny = 100000.0
		maxy = 0.0
		for p in ret:
			new_shape.append(p)
			if p.x < minx:
				minx = p.x
			if p.x > maxx:
				maxx = p.x
			if p.y < miny:
				miny = p.y
			if p.y > maxy:
				maxy = p.y
		self.shape = new_shape
		SIEffect.debug("new bounding box ={},{}  {},{}   {},{}".format(minx, miny, maxx, maxy, maxx-minx, maxy-miny))
		#recalculation of the bounding_box aabb is done automatically

	# method used to enlarge the bubble like an explosion from the center point of the bubble
	@staticmethod
	def explode(points, factor):
		cx,cy = Lasso.calculate_center(points)
		for p in points:
			p.x = cx + (p.x - cx)*factor
			p.y = cy + (p.y - cy)*factor
		return points
	
	@staticmethod
	def calculate_center(points):
		sumx = 0.0
		sumy = 0.0
		nr_of_points = 0.0
		for p in points:
			sumx += p.x
			sumy += p.y
			nr_of_points += 1.0
		return sumx/nr_of_points, sumy/nr_of_points
	
	def spread_bubble_init(self):
		# calculate radius of outer circle
		w = self.get_region_width() 
		h = self.get_region_height()
		self._sb_radius = 0.5*math.sqrt(w*w + h*h)
		self._sb_center_of_circle = [self.absolute_x_pos() + 0.5 * w, self.absolute_y_pos() + 0.5 * h]
		# spread info for a lassoable is a list
		# uuid, startx, starty, endpointx, endpointy
		# create liste of spreadinfos
		self._sb_list_of_linked_lassoables = self.get_linked_lassoables()
		n = len(self._sb_list_of_linked_lassoables)
		if n==0:
			return # This bubble has no objects to spread
		self._sb_endpoints = self.get_circle_points(self._sb_center_of_circle, self._sb_radius, n)
		self._sb_lassoable_positions = []
		for l in self._sb_list_of_linked_lassoables:
			self._sb_lassoable_positions.append([l, l.x, l.y])
		
	# spread the bubble, ie enlarge the bubble by explosion and
	# move objects away from the center
	def spread_bubble(self, factor):
		all_lassoable = SIEffect.get_all_objects_extending_class(Lassoable);	
		for l in all_lassoable:
			l.set_ignore_lasso_capability(True)
		# move lassoables back to initial position
		for lxy in self._sb_lassoable_positions:
			lxy[0].move(lxy[1], lxy[2])		
		self._spread_bubble_internal(factor)
		for l in all_lassoable:
			l.set_ignore_lasso_capability(False)

	def _spread_bubble_internal(self, factor):		
		workinglist_lassoables = self._sb_list_of_linked_lassoables.copy()
		# the moving_list is the list of all objects in the bubble, which intersect with another object in the bubble
		# Only those object should move, so that they do not intersect anymore.
		moving_list = Lasso.get_intersecting_lassoables(workinglist_lassoables)
		for ep in self._sb_endpoints:
			l = Lasso.get_closest(workinglist_lassoables, ep)
			SIEffect.debug("Lasso: workinglist_lassoables l={}, len={}".format(l, len(workinglist_lassoables)))
			workinglist_lassoables.remove(l)
			if l not in moving_list:
				continue
			lcenterx, lcentery = l.get_center()
			# we want to move the center of the lassoable to the point ep, but we have to move the
			# origin x,y of the lassoable. Therefore we have to calculate back from the center.
			dx = lcenterx - l.absolute_x_pos()
			dy = lcentery - l.absolute_y_pos()
			ax,ay = Lassoable.get_absolute_point_on_line(factor, l.absolute_x_pos(), l.absolute_y_pos(), ep[0]-dx, ep[1]-dy)
			l.move(ax - l.aabb[0].x, ay - l.aabb[0].y)
		self.recalculate_hull()
	
	# find the closest lassoable (by its center) in the workinglist_lassoables
	# to the point ep
	@staticmethod	
	def get_closest(workinglist_lassoables, ep):
		if len(workinglist_lassoables) == 1:
			return workinglist_lassoables[0]
		mind2 = 10000000000.0
		lassoable_with_min_distance = None
		for l in workinglist_lassoables:
			## calculate distance between l.get_center() and ep
			lcenterx,lcentery = l.get_center()
			dx = lcenterx-ep[0]
			dy = lcentery-ep[1]
			d2 = dx * dx + dy * dy 
			#d2 = Lasso.distance_sq(l.get_center(),ep)
			if (d2 < mind2):
				lassoable_with_min_distance = l
				mind2 = d2
		return lassoable_with_min_distance
		
	def get_circle_points(self, center_of_circle, radius, n):
		SIEffect.debug("Lasso:get_circle_points {}".format(n))
		sector = (2.0 * math.pi) / n
		points = []
		for i in range(0,n):
			points.append([center_of_circle[0]+radius*math.sin(sector*i), center_of_circle[1]+radius*math.cos(sector*i)])
		return points
		
	@staticmethod
	def get_intersecting_lassoables(workinglist_lassoables):
		moving_list = []
		l = len(workinglist_lassoables)
		for i in range(0,l):
			l1 = workinglist_lassoables[i]
			for j in range(i+1,l):
				l2 = workinglist_lassoables[j]
				if Lassoable.intersect(l1, l2):
					moving_list.append(l1)
					moving_list.append(l2)
		SIEffect.debug("Lasso:get_intersecting_lassoables {} -> {}".format(l, len(moving_list)))			
		return moving_list
	
	# returns the cross product of vector p1p3 and p1p2
	# if p1p3 is clockwise from p1p2 it returns +ve value
	# if p1p3 is anti-clockwise from p1p2 it returns -ve value
	# if p1 p2 and p3 are collinear it returns 0
	@staticmethod
	def direction(p1, p2, p3):
		v1x = p3.x-p1.x
		v1y = p3.y-p1.y
		v2x = p2.x-p1.x
		v2y = p2.y-p1.y
		return v1x * v2y - v2x * v1y #Lasso.cross_product(p3.subtract(p1), p2.subtract(p1))

	# calculates the cross product of vector p1 and p2
	# if p1 is clockwise from p2 wrt origin then it returns +ve value
	# if p2 is anti-clockwise from p2 wrt origin then it returns -ve value
	# if p1 p2 and origin are collinear then it returs 0
	@staticmethod
	def cross_product(p1, p2):
		return p1.x * p2.y - p2.x * p1.y

	# find the point with minimum y coordinate
	# in case of tie choose the point with minimun x-coordinate
	@staticmethod
	def find_min_y(points):
		miny = 999999
		mini = 0
		for i, point in enumerate(points):
			if point.y < miny:
				miny = point.y
				mini = i
			if point.y == miny:
				if point.x < points[mini].x:
					mini = i
		return points[mini], mini

	@staticmethod
	def distance_sq(p1, p2):
		dx = p1.x-p2.x
		dy = p1.y-p2.y
		return dx * dx + dy * dy 

	# comparator for the sorting 
	@staticmethod
	def polar_comparator(p1, p2, p0):
		d = Lasso.direction(p0, p1, p2)
		if d < 0:
			return -1
		if d > 0:
			return 1
		if d == 0:
			if Lasso.distance_sq(p1, p0) < Lasso.distance_sq(p2, p0):
				return -1
			else:
				return 1

	# https://algorithmtutor.com/Computational-Geometry/Convex-Hull-Algorithms-Graham-Scan/
	@staticmethod
	def graham_scan(points):
		# let p0 be the point with minimum y-coordinate,
		# or the leftmost such point in case of a tie
		p0, index = Lasso.find_min_y(points)
		# swap p[0] with p[index]
		points[0], points[index] = points[index], points[0]
		# sort the points (except p0) according to the polar angle
		# made by the line segment with x-axis in anti-clockwise direction
		sorted_polar = sorted(points[1:], key = cmp_to_key(lambda p1, p2: Lasso.polar_comparator(p1, p2, p0)))
		# if more than two points are collinear with p0, keep the farthest
		to_remove = []
		for i in range(len(sorted_polar) - 1):
			d = Lasso.direction(sorted_polar[i], sorted_polar[i + 1], p0)
			if d == 0:
				to_remove.append(i)
		sorted_polar = [i for j, i in enumerate(sorted_polar) if j not in to_remove]
		m = len(sorted_polar)
		if m < 2:
			SIEffect.debug('Convex hull is empty')
		else:
			stack = []
			stack_size = 0
			stack.append(points[0])
			stack.append(sorted_polar[0])
			stack.append(sorted_polar[1])
			stack_size = 3
			for i in range(2, m):
				while (True):
					d = Lasso.direction(stack[stack_size - 2], stack[stack_size - 1], sorted_polar[i])
					if d < 0: # if it makes left turn
						break
					else: # if it makes non left turn
						stack.pop()
						stack_size -= 1
				stack.append(sorted_polar[i])
				stack_size += 1
			return stack

