import matplotlib.pyplot as plt
import numpy as np
import sys

from fealpy.mesh.meshio import load_mat_mesh, write_mat_mesh, write_mat_linear_system
from fealpy.mesh.simple_mesh_generator import rectangledomainmesh  
from fealpy.mesh.simple_mesh_generator import triangle, unitsquaredomainmesh

from fealpy.functionspace.tools import function_space 
from fealpy.femmodel.BiharmonicFEMModel import BiharmonicRecoveryFEM  
from fealpy.boundarycondition.BoundaryCondition import DirichletBC
from fealpy.solver import solve1
from fealpy.functionspace.function import FiniteElementFunction
from fealpy.erroranalysis.PrioriError import L2_error, div_error, H1_semi_error
from fealpy.model.BiharmonicModel2d import SinSinData, BiharmonicData2, BiharmonicData3, BiharmonicData4, BiharmonicData5 

m = int(sys.argv[1]) 
sigma = int(sys.argv[2])  

meshtype = int(sys.argv[3])

if m == 1:
    model = SinSinData()
    box = [0, 1, 0, 1]
elif m == 2:
    model = BiharmonicData2(1.0,1.0)
    box = [0, 1, 0, 1]
elif m == 3:
    model = BiharmonicData3()
    box = [0, 1, 0, 1]
elif m == 4:
    model = BiharmonicData4()
    box = [0, 1, 0, 1]
elif m == 5:
    model = BiharmonicData5()
    box = [-1, 1, -1, 1]

maxit = 4
degree = 1
error = np.zeros((maxit,), dtype=np.float)
derror = np.zeros((maxit,), dtype=np.float)
gerror = np.zeros((maxit,), dtype=np.float)
H1Serror = np.zeros((maxit,), dtype=np.float)
Ndof = np.zeros((maxit,), dtype=np.int)

h0 = 0.025
if (meshtype == 3):
    mesh = load_mat_mesh('../data/square'+str(1)+'.mat')

for i in range(maxit):
    if meshtype == 1: # uniform mesh 
        n = 20*2**i
        mesh = rectangledomainmesh(box, nx=n, ny=n)  
    elif meshtype == 2: # CVT mesh
        mesh = load_mat_mesh('../data/square'+str(i+2)+'.mat')
    elif meshtype == 3: # Delaunay uniform refine mesh 
        mesh.uniform_refine()
    elif meshtype == 4: # Delaunay mesh
        mesh = triangle(box, h0/2**i)
    elif meshtype == 5:
        mesh = load_mat_mesh('../data/sqaureperturb'+str(i+2)+'.'+str(0.5) + '.mat')

    V = function_space(mesh, 'Lagrange', degree)
    V2 = function_space(mesh, 'Lagrange_2', degree)
    uh = FiniteElementFunction(V)
    ruh = FiniteElementFunction(V2)

    fem = BiharmonicRecoveryFEM(V, model, sigma=sigma, rtype='inv_area')
    bc = DirichletBC(V, model.dirichlet, model.is_boundary_dof)
    solve1(fem, uh, dirichlet=bc, solver='direct')
    fem.recover_grad(uh, ruh)

    Ndof[i] = V.number_of_global_dofs() 
    error[i] = L2_error(model.solution, uh, order=4)
    derror[i] = div_error(model.laplace, ruh, order=4)
    gerror[i] = L2_error(model.gradient, ruh, order=5)
    H1Serror[i] = H1_semi_error(model.gradient, uh, order=5)

print(Ndof)
print('L2 error:\n', error)
order = np.log(error[0:-1]/error[1:])/np.log(2)
print('order:\n', order)

print('div error:\n', derror)
order = np.log(derror[0:-1]/derror[1:])/np.log(2)
print('order:\n', order)

print('revover gradient error:\n', gerror)
order = np.log(gerror[0:-1]/gerror[1:])/np.log(2)
print('order:\n', order)

print('gradient error:\n', H1Serror)
order = np.log(H1Serror[0:-1]/H1Serror[1:])/np.log(2)
print('order:\n', order)