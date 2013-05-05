from __future__ import print_function
import numpy as np

def LJ(r_0, U_0):
    '''
    Lennard-Jones with minimum at (r_0, -U_0).
    '''
    r_0_6 = r_0 ** 6
    def func(r_sq):
        six_term = r_0_6 / r_sq ** 3
        return U_0 * (six_term ** 2 - 2.0 * six_term)
    return func

def step(r_0, U_0):
    '''
    Potential Well at r with U(r < r_0) = 0, U(r > r_0) = U_0.
    '''
    def func(r_sq):
        return np.where(r_sq < r_0 ** 2, U_0, 0.0)
    return func

def inv_sq(k):
    '''
    Inverse-square law, U(r) = -k / r.
    '''
    def func(r_sq):
        return -k / np.sqrt(r_sq)
    return func

def harm_osc(k):
    '''
    Harmonic oscillator, U(r) = k * (r ** 2) / 2.0.
    '''
    def func(r_sq):
        return 0.5 * k * r_sq ** 2
    return func

def logistic(r_0, U_0, k):
    ''' Logistic approximation to step function. '''
    def func(r_sq):
        return 0.5 * U_0 * (1.0 + np.tanh(k * (np.sqrt(r_sq) - r_0)))
    return func

def polar_rose(n):
    def func(t):
        return np.cos(n * t)
    return func

def polar_rose_sq(n):
    def func(t):
        return 1.5-np.cos(0.5 * n * t) ** 2
    return func