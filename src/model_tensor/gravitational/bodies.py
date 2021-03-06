#!usr/bin/env python
# -*- coding: utf-8 -*-
#Modified date: 20/05/2016
#Nima 
#

from __future__ import absolute_import

import numpy as np
import scipy as sp

import PyKEP as pk

from src.model_tensor import base_model

class Body():
    """Class defining a celestial body.
  
    Attributes defined here:
    -name: the name of the body.
    -equatorial_radius: equatorial radius of the body
    -mu: gravitational parameter of the body

    Method defined here:
    -acceleration_intensity: gives the acceleration intensity of body
    -relative_position(): defines relative position of spacecraft with 
    respect to body.

    """

    def __init__(self, name, mu = 0.0, equatorial_radius = 0.0):
        """Constructor of the class Body."""
        self._name = name
        self._mu = mu
        self._equatorial_radius = equatorial_radius

    def _get_name(self):
        """Method called when trying to read the attribute 'name'."""
        return self._name
    def _set_name(self, new_name):
        """Method called when trying to modify the attribute 'name'."""
        self._name = new_name

    name = property(_get_name, _set_name)

    def __repr__(self):
        """Method displaying a customized message when an instance of the 
        class BaseModel is called in the command line.
        """
        return "Body: name = '{}', mu = '{}', radius = '{}' m".format(
        self.name, self.mu, self.equatorial_radius)
    def accel_intensity(self, date, satellite_position):
        """Computes the acceleration intensity undergone by spacecraft."""
        rp = self.relative_position(date, satellite_position)
        acc_intens = self.mu / (rp**2)
        return acc_intens
    def relative_position(self, date, satellite_position):
        """Gives the relative position of the spacecraft with respect to 
        a body. Returns a vector position.
        """
        body_position, _ = np.array(self.eph(date))
        r_p = satellite_position - body_position
        return r_p 

class PyKEPBody(Body):
    """Class defining the gravitational model of bodies known from PyKEP.

    This class inherits from class Body.

    Attributes defined here:
    -body_self: instance of class planets with PyKEP library.

    Method defined here:
    -relative_position(): defines relative position of spacecraft with 
    respect to body.

    """
    def __init__(self, name):
        """Constructor of the class PyKEPBody."""
        Body.__init__(self, name)
        self.body_self = pk.planet.jpl_lp("%s" % name)
        self._mu = self.body_self.mu_self
        self._equatorial_radius = self.body_self.radius

    def _get_mu(self):
        """Method called when trying to read the attribute 'mu'."""
        return self._mu
    def _set_mu(self, new_mu):
        """Method called when trying to modify the attribute 'mu'."""
        self._mu = new_mu
    def _get_equatorial_radius(self):
        """Method called when trying to read the attribute 'equatorial_radius'."""
        return self._equatorial_radius
    def _set_equatorial_radius(self, new_equatorial_radius):
        """Method called when trying to modify the attribute 'equatorial_radius'."""
        self._equatorial_radius = new_equatorial_radius

    mu = property(_get_mu, _set_mu)
    equatorial_radius = property(_get_equatorial_radius, _set_equatorial_radius)

    def __repr__(self):
        """Method displaying a customized message when an instance of the 
        class PyKEPBody is called in the command line.
        """
        return "PyKEPBody: name = '{}', mu = {} m³/s², radius = '{}' m".format(
        self._name, self._mu, self._equatorial_radius)
    def relative_position(self, date, satellite_position):
        """Gives the relative position of the spacecraft with respect to 
        known body. Returns a vector position.
        self.body_self.eph(date) is a method from PyKEP library providing the 
        ephemeris of self.body_self: returns a tuple (r, v) respectively 
        the self.body_self position and velocity vectors.
        """
        body_position, _ = np.array(self.body_self.eph(date))
        r_p = satellite_position - body_position
        return r_p

class UnKnownBody(Body):
    """Class defining the gravitational model of bodies unknown from PyKEP.

    This class inherits from class Body.

    Attributes defined here:
    -input_dir: input file directory (class attribute)
    -traj_file: name of trajectory file of the unknown body ephemerides.

    Method defined here:
    -eph(): gives the ephemeris of unknown body with respect to an epoch
  
    """

    input_dir = " "

    def __init__(self, name, mu, radius, traj_file):
        """Constructor of the class UnKnownBody."""
        Body.__init__(self, name)
        self._mu = mu
        self._equatorial_radius = radius
        self._traj_file = traj_file

    def _get_mu(self):
        """Method called when trying to read the attribute 'mu'."""
        return self._mu
    def _set_mu(self, new_mu):
        """Method called when trying to modify the attribute 'mu'."""
        self._mu = new_mu
    def _get_equatorial_radius(self):
        """Method called when trying to read the attribute 'equatorial_radius'."""
        return self._equatorial_radius
    def _set_equatorial_radius(self, new_equatorial_radius):
        """Method called when trying to modify the attribute 'equatorial_radius'."""
        self._equatorial_radius = new_equatorial_radius
    def _get_traj_file(self):
        """Method called when trying to read the attribute 'traj_file'."""
        return self._traj_file
    def _set_traj_file(self, new_traj_file):
        """Method called when trying to modify the attribute 'traj_file'."""
        self._traj_file = new_traj_file
    
    mu = property(_get_mu, _set_mu)
    equatorial_radius = property(_get_equatorial_radius, _set_equatorial_radius)
    traj_file = property(_get_traj_file, _set_traj_file)

    def __repr__(self):
        """Method displaying a customized message when an instance of the 
        class UnKnownBody is called in the command line.
        """
        return "UnKnownBody: name = '{}', mu = {} m³/s², radius = '{}' m".format(
        self._name, self._mu, self._equatorial_radius)
    def eph(self, date):
        """Method providing the ephemeris of unknown body at a given epoch.
        Returns a tuple r, v.
        """
        with open(UnKnownBody.input_dir + self._traj_file) as input_file:
            data = input_file.readlines()
            for i, dt in enumerate(data):
                values = [float(element) for element in data[i].split(' ')]
                time1 = values[0]
                r = np.array([values[1], values[2], values[3]])
                v = np.array([values[4], values[5], values[6]])
                if (i < len(data)-1):
                    next_values = [float(element) for element in data[i+1].split(' ')] 
                time2 = next_values[0]
                r1 = np.array([next_values[1], next_values[2], next_values[3]])
                v1 = np.array([next_values[4], next_values[5], next_values[6]])
                if (time1 > date):
                    raise ValueError("The given epoch is out of range: [2016 - 2050]")
                if (time1 == date):
                    return r, v
                if (time2 == date):
                    return r1, v1
                if (time1 < date < time2):
                    r2 = r * ((time2 - date) / (time2 - time1)) + r1 * ((date - time1) / (time2 - time1))
                    v2 = v * ((time2 - date) / (time2 - time1)) + v1 * ((date - time1) / (time2 - time1))
                    return r2, v2
            if (time2 < date): 
                raise ValueError("The given epoch is out of range: [2016 - 2050]")
