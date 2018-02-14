import numpy as np
import scipy.linalg

from fenics import *
# from functions import FE_function, Snapshot

class HilbertSpace():
	def __init__(self, norm_type):
		self.norm_type = norm_type

	def inner_product(self, fem_function0, fem_function1):
		ip = getattr(self, "inner_product_" + self.norm_type)
		return ip(fem_function0, fem_function1)

	def inner_product_H10(self, fem_function0, fem_function1):
		return assemble( dot(grad(fem_function0), grad(fem_function1))*dx)

	def inner_product_L2(self, fem_function0, fem_function1):
		return assemble( fem_function0 * fem_function1 *dx )

	def linear_combination(self, vecs, c):
		# Build a FE_function from a vector of coefficients
		if len(c) != len(vecs):
			raise Exception('Coefficients and vectors must be of same length!')

		u_p = None
		for i, c_i in enumerate(c):
			if i==0:
				u_p = vecs[i] * c_i
			else:
				if c_i != 0:
					u_p += vecs[i] * c_i
		return u_p

	# vecs: list of snapshots
	# returns list of FE_function
	def orthonormalize(self, vecs, grammian=None):
		if len(vecs) == 0:
			return vecs
		else:
			# We do a cholesky factorisation rather than a Gram Schmidt, as
			# we have a symmetric +ve definite matrix, so this is a cheap and
			# easy way to get an orthonormal basis from our previous basis.
			# Indeed, A = QR = LL^T and A^TA = R^TR = LL^T so L=R^T
			if grammian is None:
				grammian = self.computeGrammian(vecs)
			L = np.linalg.cholesky(grammian)
			L_inv = scipy.linalg.lapack.dtrtri(L.T)[0]
			ortho_vecs = list()
			for i in range(len(vecs)):
				ortho_vecs.append( self.linear_combination(vecs, L_inv[:, i]) )

			return ortho_vecs

	def computeGrammian(self, vecs):
		n = len(vecs)
		G = np.zeros((n, n))
		for i in range(self.dim):
			for j in range(i, n):
				G[i,j] = vecs[i].dot(vecs[j]) # inner product
				G[j,i] = G[i,j]
		return G

class ReducedSpace(HilbertSpace):
	def __init__(self, rbConstructionStrategy):
		self.norm_type, self.basis \
			= rbConstructionStrategy.generateBasis() # List of snapshots
		self.dim   = len(self.basis)
		self.grammian = self.computeGrammian(self.basis)
		self.onb = self.orthonormalize(self.basis, grammian=self.grammian)

	def project(self, fe_function):
		c = np.asarray( [fe_function.dot(basisFun) for basisFun in self.onb] )
		proj = self.linear_combination(self.onb, c)
		return self.linear_combination(self.onb, c)







