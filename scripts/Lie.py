# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 18:25:49 2024

@author: hibad
"""
import numpy as np
from numpy import arccos, sin, cos, trace, arctan2
from numpy.linalg import norm, matrix_power, inv
class SO2:
    @staticmethod
    def hat(theta):
       return np.array([[0, -theta],
                        [theta, 0]])
    @staticmethod
    def Log(M):
        return arctan2(M[1,0], M[0,0])
    
    @staticmethod
    def Exp(theta):
        c = cos(theta)
        s = sin(theta)
        return np.array([[c, -s],
                         [s, c]])
class SE2:
    @staticmethod
    def V(theta):
        if theta==0:
            return np.eye(2)
        return sin(theta)/theta* np.eye(2) +(1-cos(theta))/theta * SO2.hat(1)
    
    @staticmethod
    def Log(M):
        tau = np.zeros(3)
        theta = SO2.Log(M[0:2,0:2])
        v = SE2.V(theta)
        rho = inv(v)@M[0:2,2]
        tau[0:2]=rho
        tau[2] = theta
        return tau

    
    @staticmethod
    def Exp(tau):
        M=np.eye(3)
        M[0:2,0:2]=SO2.Exp(tau[2])
        v = SE2.V(tau[2])
        M[0:2,2] = v@tau[0:2]
        return M
    
    @staticmethod
    def Jr(tau):
        Jr = np.eye(3)
        if tau[2]==0:
            return Jr
        
        s = sin(tau[2])
        c = cos(tau[2])
        
        Jr[0,0] = sin(tau[2])/tau[2]
        Jr[0,1] = (1-c)/tau[2]
        Jr[0,2] = (tau[2]*tau[0]-tau[1]+tau[1]*c-tau[0]*s)/tau[2]**2
        Jr[1,0] = (c-1)/tau[2]
        Jr[1,1] = sin(tau[2])/tau[2]
        Jr[1,2] = (tau[0]+tau[2]*tau[1]-tau[0]*c-tau[1]*s)/tau[2]**2
        return Jr
    
    @staticmethod
    def Jl(tau):
        Jl = SE2.Jr(-np.array(tau))
        return Jl
    
    @staticmethod
    def Jl_inv(tau):
        Jl = SE2.Jl(tau)
        return inv(Jl)
    
    def Jr_inv(tau):
        Jr = SE2.Jl_inv(-np.array(tau))
        return inv(Jr)
    
    def Ad(M):
        ad=np.eye(3)
        R=M[0:2, 0:2]
        t=M[0:2,2]
        ad[0:2,0:2]=R
        ad[0:2,2] = -SO2.hat(1)@t
        return ad

class SO3:
    @staticmethod
    def vee(W):
        return np.array([W[2,1], W[0,2], W[1,0]]).copy()
    @staticmethod
    def hat(w):
        return np.array([[0, -w[2], w[1]],
                         [w[2], 0, -w[0]],
                         [-w[1], w[0], 0]])
    @staticmethod
    def Log(R):
        theta=arccos((trace(R)-1)/2)
        if theta == 0:
            return np.zeros(3)
        u=theta*SO3.vee((R-R.T))/(2*sin(theta))
        return u.copy()
    
    @staticmethod
    def Exp(u):
        theta=np.linalg.norm(u)
        if theta==0: 
            return np.eye(3)
        u=u/theta
        R=np.eye(3)+sin(theta)*SO3.hat(u)+(1-cos(theta))*SO3.hat(u)@SO3.hat(u)
        return R.copy()
    
    @staticmethod
    def Jl(w):
        t=norm(w)
        if t==0:
            return np.eye(3)
        w_x=SO3.hat(w)
        J=np.eye(3)+(1-cos(t))/t**2*w_x + (t-sin(t))/t**3*w_x @w_x 
        return J.copy()
    
    @staticmethod
    def Jl_inv(w):
        t=norm(w)
        if t==0:
            return np.eye(3)
        w_x=SO3.hat(w)
        J=np.eye(3)-1/2*w_x+(1/t**2-(1+cos(t))/(2*t*sin(t)))*w_x@w_x
        return J.copy()
    
    
    @staticmethod
    def Jr(theta):
        t= norm(theta)
        if t==0:
            return np.eye(3)
        c = cos(t)
        s = sin(t)
        theta_x = SO3.hat(theta)
        J = np.eye(3) - ((1-c)/t**2)*theta_x + (t-s)/t**3* theta_x@theta_x 
        return J.copy()
    
    @staticmethod
    def Jr_inv(w):
        t=norm(w)
        if t==0:
            return np.eye(3)
        w_x = SO3.hat(w)
        J=np.eye(3) + 1/2*w_x + (1/t**2-(1+cos(t))/(2*t*sin(t))) * (w_x@w_x)
        return J.copy()
    
class SE3:
    @staticmethod 
    def Ad(M):
        J = np.zeros((6,6))
        J[0:3,0:3] = M[0:3,0:3]
        J[3:6,3:6] = M[0:3,0:3]
        J[0:3,3:6] = SO3.hat(M[0:3,3])@M[0:3,0:3]
        return J.copy()
        
    @staticmethod
    def V(theta):
        t = norm(theta)
        theta_cross = SO3.hat(theta)
        if t == 0:
            return np.eye(3)
        else:
            v= np.eye(3) + (1-cos(t))/t**2 * theta_cross + (t-sin(t))/t**3 * theta_cross@theta_cross       
        return v.copy()
    
    @staticmethod
    def Log(M):
        theta = SO3.Log(M[0:3, 0:3])
        v = SE3.V(theta)
        rho = inv(v)@M[0:3,3]
        return np.concatenate((rho,theta))
    
    @staticmethod
    def Exp(tau):
        R = SO3.Exp(tau[3:6])
        t = SE3.V(tau[3:6])@tau[0:3]
        M = np.eye(4)
        M[0:3,0:3] = R
        M[0:3, 3] = t
        return M.copy()
            
    @staticmethod
    def Jl_inv(tau):
        theta = tau[3:6]
        jl_inv = SO3.Jl_inv(theta)
        Q = SE3.Q(tau)
        J = np.zeros((6,6))
        J[0:3, 0:3] = jl_inv
        J[3:6,3:6] = jl_inv
        J[0:3,3:6] = -jl_inv@Q@jl_inv
        return J.copy()
        
    @staticmethod
    def Jr_inv(tau):
        return SE3.Jl_inv(-tau)    
            
    @staticmethod
    def Q(tau):
        rho_x = SO3.hat(tau[0:3])
        theta_x = SO3.hat(tau[3:6])
        theta_x_sq = theta_x@theta_x
        t = norm(tau[3:6])
        if t==0:
            return np.zeros((3,3)) 
        s = sin(t)
        c = cos(t)
        trt =  theta_x@rho_x@theta_x
        Q = 1/2*rho_x + (t-s)/t**3*(theta_x@rho_x + rho_x@theta_x + trt) \
            - (1-(t**2)/2-c)/t**4 * (theta_x_sq@rho_x + rho_x@theta_x_sq - 3*trt) \
                -1/2*((1-(t**2)/2-c)/t**4 - 3*(t-s-(t**3)/6)/t**5) \
                    * (trt@theta_x + theta_x @trt)
        return Q.copy()
    
    @staticmethod
    def Jr(tau):
        tau=np.array(tau)
        J = SO3.Jr(tau[3:6])
        q = SE3.Q(-tau)
        Jr = np.zeros((6,6))
        Jr[0:3,0:3] = J
        Jr[3:6, 3:6] = J
        Jr[0:3,3:6] = q
        return Jr.copy()
    
if __name__ == "__main__":
    import manifpy
    M1 = manifpy.SE3.Random()
    M1np = np.eye(4)
    M1np[0:3,0:3] = M1.rotation()
    M1np[0:3,3] = M1.translation()
    tau1np = SE3.Log(M1np)
    tau1 = M1.log().coeffs()
    e = np.max(tau1 - tau1np)
    assert e<0.00000001
    print("SE3 log passed")
    
    assert np.max(SE3.Exp(tau1np) -M1np)<0.00000001
    print("SE3 exp passed")
    
    assert np.max(M1.adj() - SE3.Ad(M1np))<0.00000001
    print("SE3 adj passed")
    
    M2 = manifpy.SE3.Random()
    M2np = np.eye(4)
    M2np[0:3,0:3] = M2.rotation()
    M2np[0:3,3] = M2.translation()
    tau2 = M2.log()
    tau2np = tau2.coeffs()
    J1 = np.zeros((6,6))
    J2 = np.zeros((6,6))
    
    M1.plus(tau2, J1, J2)
    J1np = SE3.Ad(inv(M2np))
    assert np.max(J1np - J1)<0.00000001
    J2np = SE3.Jr(tau2np)
    assert np.max(J2np - J2)<0.00000001
    print("SE3 O-plus Jacobian passed")
    
    J1 = np.zeros((6,6))
    J2 = np.zeros((6,6))
    tau = M2.minus(M1, J2,J1).coeffs()
    taunp = SE3.Log(inv(M1np)@(M2np))
    
    J1np = -SE3.Jl_inv(tau)
    J2np = SE3.Jr_inv(tau)
    assert np.max(J1np - J1)<0.00000001
    assert np.max(J2np - J2)<0.00000001
    print("SE3 O-minus Jacobian passed")
