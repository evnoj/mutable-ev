#!/usr/bin/python2.5
#
# Copyright 2015 Emilie Gillet.
#
# Author: Emilie Gillet (emilie.o.gillet@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
# See http://creativecommons.org/licenses/MIT/ for more information.
#
# -----------------------------------------------------------------------------
#
# Lookup table definitions.

import numpy

lookup_tables = []
int16_lookup_tables = []
uint32_lookup_tables = []

SAMPLE_RATE = 32000.0

# give this func a scalar from 0-1
# k is "steepness"
# good steepness range is 0.5-2
def scurve(x, k=1):
  x = x - 0.5
  x = x * 12
  L = 1
  x_0 = 0
  result = L / (1 + numpy.exp(-k * (x - x_0)))
  return result

"""----------------------------------------------------------------------------
Sine table
----------------------------------------------------------------------------"""

WAVETABLE_SIZE = 4096
t = numpy.arange(0.0, WAVETABLE_SIZE + WAVETABLE_SIZE / 4 + 1) / WAVETABLE_SIZE
x = numpy.sin(2 * numpy.pi * t)
lookup_tables += [('sine', x)]



"""----------------------------------------------------------------------------
Coefficients for approximate filter, 32Hz to 16kHz ; Q = 0.5 to 500
----------------------------------------------------------------------------"""

frequency = 32 * (10 ** (2.7 * numpy.arange(0, 257) / 256))
frequency /= SAMPLE_RATE

frequency[frequency >= 0.499] = 0.499

g = numpy.tan(numpy.pi * frequency)
r = 2.0
h = 1.0 / (1.0 + r * g + g * g)
gain = (0.42 / frequency) * (4 ** (frequency * frequency))
r = 1 / (0.5 * 10 ** (3.0 * numpy.arange(0, 257) / 256))

lookup_tables += [
  ('approx_svf_gain', gain),
  ('approx_svf_g', g),
  ('approx_svf_r', r),
  ('approx_svf_h', h)]



"""----------------------------------------------------------------------------
Exponentials covering several decades in 256 steps, with safeguard
----------------------------------------------------------------------------"""

x = numpy.arange(0, 257) / 256.0
lookup_tables += [('4_decades', 10 ** (4 * x))]



"""----------------------------------------------------------------------------
Delay compensation factor for SVF
----------------------------------------------------------------------------"""

ratio = 2.0 ** (numpy.arange(0, 257) / 12.0)
svf_shift = 2.0 * numpy.arctan(1.0 / ratio) / (2.0 * numpy.pi)
lookup_tables += [('svf_shift', svf_shift)]



"""----------------------------------------------------------------------------
Stiffness table.
----------------------------------------------------------------------------"""

structure = numpy.arange(0, 257) / 256.0
stiffness = structure + 0

# .25-.3: 10-11 o clock node originally

# node values experimentally derived for my module:
# .11-.15 exclusive: 9 o' clock node
# .28-.32 exclusive: 10 o' clock node
# .465-.51 exclusive: 12 o' clock node
# .66-.7 exclusive: 2 o' clock node
# .84-.89 exclusive: 3 o' clock node
for i, g in enumerate(structure):
  if g < 0.11:
    g = 0.205 - g
    stiffness[i] = -g * 0.258
  elif g < 0.15:
    # 9 o' clock
    stiffness[i] = -0.025
  elif g < 0.28:
    # .13x = -0.025
    g = 0.28 - g
    stiffness[i] = -g * 0.19
  elif g < 0.32:
    # 10 o' clock
    stiffness[i] = 0.0
  elif g < 0.465:
    p_floor = 0.32
    p_ceil = 0.465
    p_range = p_ceil - p_floor
    scale = (g-p_floor) / p_range
    v_floor = 0
    v_ceil = 0.125
    v_range = v_ceil - v_floor
    stiffness[i] = scurve(scale) * v_range + v_floor
  elif g < 0.51:
    # 12 o' clock
    stiffness[i] = 0.125
  elif g < 0.66:
    p_floor = 0.51
    p_ceil = 0.66
    p_range = p_ceil - p_floor
    scale = (g-p_floor) / p_range
    v_floor = 0.125
    v_ceil = 0.25
    v_range = v_ceil - v_floor
    stiffness[i] = scurve(scale) * v_range + v_floor
  elif g < 0.7:
    # 2 o' clock
    stiffness[i] = 0.25
  elif g < 0.84:
    g -= 0.7
    g /= 0.3
    stiffness[i] = 0.25 + 0.01 * 10 ** (g * 3.005) - 0.01
  elif g < 0.89:
    # 3 o' clock
    stiffness[i] = .5
  else:
    g -= 0.89
    g /= 0.11
    stiffness[i] = 0.5 + 0.01 * 10 ** (g * 1.8) - 0.01

stiffness[0] = -0.05
stiffness[1] = -0.05
stiffness[-1] = 1.0
stiffness[-2] = 1.0

for i, g in enumerate(structure):
  if stiffness[i] > 0:
    stiffness[i] = stiffness[i] * 2

lookup_tables += [('stiffness', stiffness)]



"""----------------------------------------------------------------------------
Quantizer for FM frequencies.
----------------------------------------------------------------------------"""

fm_frequency_ratios = [ 0.5, 0.5 * 2 ** (16 / 1200.0),
  numpy.sqrt(2) / 2, numpy.pi / 4, 1.0, 1.0 * 2 ** (16 / 1200.0), numpy.sqrt(2),
  numpy.pi / 2, 7.0 / 4, 2, 2 * 2 ** (16 / 1200.0), 9.0 / 4, 11.0 / 4,
  2 * numpy.sqrt(2), 3, numpy.pi, numpy.sqrt(3) * 2, 4, numpy.sqrt(2) * 3,
  numpy.pi * 3 / 2, 5, numpy.sqrt(2) * 4, 8]

scale = []
for ratio in fm_frequency_ratios:
  ratio = 12 * numpy.log2(ratio)
  scale.extend([ratio, ratio, ratio])

target_size = int(2 ** numpy.ceil(numpy.log2(len(scale))))
while len(scale) < target_size:
  gap = numpy.argmax(numpy.diff(scale))
  scale = scale[:gap + 1] + [(scale[gap] + scale[gap + 1]) / 2] + \
      scale[gap + 1:]

scale.append(scale[-1])

lookup_tables.append(
    ('fm_frequency_quantizer', scale)
)
