import numpy as np

from fenics import *
from solver import DiffusionCheckerboard
import copy

class FE_function():
	"""
		This is a function living in an ambient Hilbert space.
		Basic operations like +, -, *(scalar), /(scalar), inner product and norm are supported
		We can also plot them for visualization.
	"""
	# Remark: We assume that self and other have the same ambient_space and fem function_space

	def __init__(self, ambient_space, function):
		self.ambient_space = ambient_space
		self.fun = function

	# Addition of two FE_functions
	def __add__(self, other):
		V = self.fun.function_space()
		u = Function(V)
		u.vector()[:] = self.fun.vector().get_local() + other.fun.vector().get_local()
		return FE_function(self.ambient_space, u)

	def __iadd__(self, other):
		self.fun.vector()[:] = self.fun.vector().get_local() + other.fun.vector().get_local()
		return self

	# Subtraction of two FE_functions
	def __sub__(self, other):
		V = self.fun.function_space()
		u = Function(V)
		u.vector()[:] = self.fun.vector().get_local() - other.fun.vector().get_local()
		return FE_function(self.ambient_space, u)

	def __isub__(self, other):
		self.fun.vector()[:] = self.fun.vector().get_local() - other.fun.vector().get_local()
		return self

	# Multiplication by scalar
	def __mul__(self, other):
		""" other must be a scalar here """
		V = self.fun.function_space()
		u = Function(V)
		c = interpolate( Constant(other), V )
		u.vector()[:] = self.fun.vector().get_local() * c.vector().get_local()
		return FE_function(self.ambient_space, u)

	def __imul__(self, other):
		""" other must be a scalar here """
		V = self.fun.function_space()
		c = interpolate( Constant(other), V )
		self.fun.vector()[:] = self.fun.vector().get_local() * c.vector().get_local()
		return self

	__rmul__ = __mul__

	# Division by scalar
	def __truediv__(self, other):
		""" other must be a scalar here """
		V = self.fun.function_space()
		u = Function(V)
		c = interpolate( Constant(other), V )
		u.vector()[:] = self.fun.vector().get_local() / c.vector().get_local()
		return FE_function(self.ambient_space, u)

	def __itruediv__(self, other):
		""" other must be a scalar here """
		V = self.fun.function_space()
		c = interpolate( Constant(other), V )
		self.fun.vector()[:] = self.fun.vector().get_local() / c.vector().get_local()
		return self

	# Inner product
	def dot(self, other):
		return self.ambient_space.inner_product(self.fun, other.fun)

	def norm(self):
		return norm(self.fun, norm_type=self.ambient_space.norm_type)

	def plot(self, seeOnScreen= True, save=False, seeMesh = False):
		# Visualize plot and mesh
		if seeOnScreen:
			plot(self.fun)
			if seeMesh:
				plot(self.fun.function_space().self.mesh())
			import matplotlib.pyplot as plt
			plt.show()
		# Save snapshot to file in VTK format
		if save:
			filename = 'img/fe_function.pvd'
			vtkfile = File(filename)
			vtkfile << self.fun

	def _new_helper(self, filename, kw):
		return cls.__new__(cls, value, **kw)

class Snapshot(FE_function):
	"""
		We assume that these functions are solutions of a PDE.
	"""
	def __init__(self, ambient_space, function, param):
		super().__init__(ambient_space, function)
		self.param = param
		# self.measure = np.array([0.]) # TODO: measures of solution
		# self.filename = "_".join(np.char.mod('%14.8E', self.param))

class Sensor(FE_function):
	"""
		A function of type Sensor is the Riesz representer of a linear functional.
	"""
	def __init__(self, ambient_space, function, param):
		super().__init__(ambient_space, function)
		self.param = param

