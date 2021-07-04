from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E
from plugins.standard_environment_library._standard_behaviour_mixins.Movable import Movable
from plugins.standard_environment_library._standard_behaviour_mixins.Deletable import Deletable
from functools import cmp_to_key

class Lasso(Deletable, Movable, SIEffect):
	regiontype = PySI.EffectType.SI_CUSTOM
	regionname = "__LASSO__"
	region_display_name = "Lasso"

	def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
		super(Lasso, self).__init__(shape, uuid, E.id.lasso_texture, Lasso.regiontype, Lasso.regionname, kwargs)
		self.set_QML_path("Lasso.qml")
		self.color = E.id.lasso_color

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

	def get_link_sender(self):
		result = self.get_all_lnk_sender()
		for sender in result:
			SIEffect.debug("Lasso.get_link_receiver : sender {}".format(SIEffect.short_uuid(sender)))
		return result

	# add additional points to the set of points of the hull of the bubble.
	# Then recalculate the convex hull
	def recalculate_hull(self, additional_points):
		# The additional_points are in absolute coordinates
		# First they must be changed to relative
		#additional_points_relative = []
		#for p in additional_points:
		#	additional_points_relative.append([p[0]-self.relative_x_pos(),p[1]-self.relative_y_pos()])
		points = PySI.PointVector(additional_points)
		for p in self.shape:
			points.append(p)
		ret = Lasso.graham_scan(points)
		#ret = Lasso.explode(ret, 1.1)
		new_shape = PySI.PointVector()
		for p in ret:
			new_shape.append(p)
		
		self.shape = new_shape
		#recalculate the bounding_box aabb

	@staticmethod
	def explode(points, factor):
		cx,cy = Lasso.calculate_center(points)
		for p in points:
			p.x = cx + (p.x - cx)*factor
			p.y = cy + (p.y - cy)*factor
	
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
