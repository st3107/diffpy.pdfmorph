#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""class MorphSphere -- apply a spherical shape function to the objective
class MorphSpheroid -- apply a spheroidal shape function to the objective
"""


import numpy
from numpy import sqrt
from numpy import arctan as atan
from numpy import arctanh as atanh

from diffpy.pdfmorph.morphs.morph import *

class MorphSphere(Morph):
    '''Apply a spherical characteristic function to the objective

    Configuration variables:

    radius  --  The radius of the sphere

    '''

    # Define input output types
    summary = 'Apply spherical characteristic function to objective'
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["radius"]

    def morph(self, xobj, yobj, xref, yref):
        """Apply a scale factor."""
        Morph.morph(self, xobj, yobj, xref, yref)
        f = _sphericalCF(xobj, 2 * self.radius)
        self.yobjout *= f
        return self.xyallout

# End of class MorphSphere

class MorphSpheroid(Morph):
    '''Apply a spherical characteristic function to the objective

    Configuration variables:

    radius   --  The equatorial radius of the spheroid
    pradius  --  The polar radius of the spheroid

    '''

    # Define input output types
    summary = 'Apply spheroidal characteristic function to objective'
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["radius", "pradius"]

    def morph(self, xobj, yobj, xref, yref):
        """Apply a scale factor."""
        Morph.morph(self, xobj, yobj, xref, yref)
        f = _spheroidalCF(xobj, self.radius, self.pradius)
        self.yobjout *= f
        return self.xyallout

# End of class MorphSpheroid

def _sphericalCF(r, psize):
    """Spherical nanoparticle characteristic function.
    
    r       --  distance of interaction
    psize   --  The particle diameter
    
    From Kodama et al., Acta Cryst. A, 62, 444-453 
    (converted from radius to diameter)

    """
    f = numpy.zeros_like(r)
    if psize > 0: 
        x = r/psize
        g = (1.0 - 1.5*x + 0.5*x*x*x)
        g[x > 1] = 0
        f += g
    return f

def _spheroidalCF(r, erad, prad):
    """Spheroidal characteristic function specified using radii.

    Spheroid with radii (erad, erad, prad)

    prad    --  polar radius
    erad    --  equatorial radius

    erad < prad equates to a prolate spheroid
    erad > prad equates to a oblate spheroid
    erad == prad is a sphere

    """
    psize = 2*erad
    pelpt = prad / erad
    return _spheroidalCF2(r, psize, pelpt)

def _spheroidalCF2(r, psize, axrat):
    """Spheroidal nanoparticle characteristic function.

    Form factor for ellipsoid with radii (psize/2, psize/2, axrat*psize/2)
    
    r      --  distance of interaction
    psize  --  The equatorial diameter
    axrat  --  The ratio of axis lengths

    From Lei et al., Phys. Rev. B, 80, 024118 (2009)
    
    """
    pelpt = axrat

    if psize <= 0 or pelpt <= 0: 
        return numpy.zeros_like(r)

    # to simplify the equations
    v = pelpt
    d = psize
    d2 = d*d
    v2 = v*v

    if v == 1: 
        return _sphericalCF(r, psize)

    rx = r
    if v < 1:

        r = rx[rx <= v*psize]
        r2 = r*r
        f1 = 1 - 3*r/(4*d*v)*(1-r2/(4*d2)*(1+2.0/(3*v2))) \
                - 3*r/(4*d)*(1-r2/(4*d2))*v/sqrt(1-v2)*atanh(sqrt(1-v2))

        r = rx[numpy.logical_and(rx > v*psize, rx <= psize)]
        r2 = r*r
        f2 = (3*d/(8*r)*(1+r2/(2*d2))*sqrt(1-r2/d2) \
                - 3*r/(4*d)*(1-r2/(4*d2))*atanh(sqrt(1-r2/d2)) \
                ) * v/sqrt(1-v2)

        r = rx[rx > psize]
        f3 = numpy.zeros_like(r)

        f = numpy.concatenate((f1,f2,f3))

    elif v > 1:

        r = rx[rx <= psize]
        r2 = r*r
        f1 = 1 - 3*r/(4*d*v)*(1-r2/(4*d2)*(1+2.0/(3*v2))) \
                - 3*r/(4*d)*(1-r2/(4*d2))*v/sqrt(v2-1)*atan(sqrt(v2-1))

        r = rx[numpy.logical_and(rx > psize, rx <= v*psize)]
        r2 = r*r
        f2 = 1 - 3*r/(4*d*v)*(1-r2/(4*d2)*(1+2.0/(3*v2))) \
            - 3.0/8*(1+r2/(2*d2))*sqrt(1-d2/r2)*v/sqrt(v2-1) \
            - 3*r/(4*d)*(1-r2/(4*d2))*v/sqrt(v2-1) \
            * (atan(sqrt(v2-1)) - atan(sqrt(r2/d2-1)))

        r = rx[rx > v*psize]
        f3 = numpy.zeros_like(r)

        f = numpy.concatenate((f1,f2,f3))

    return f


