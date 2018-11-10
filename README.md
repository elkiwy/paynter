# What is PaYnter?

PaYnter is a Python module that let you procedurally generate images with handy features that emulates what you can find in any image editing software like Photoshop, GIMP, Krita, etc...

[![Documentation Status](https://readthedocs.org/projects/paynter/badge/?version=latest)](https://paynter.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/elkiwy/paynter.svg?branch=master)](https://travis-ci.com/elkiwy/paynter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Features

This is a list with what there is currently inside the code:

- Brushes features:
	- Custom brush tip (B/W png images)
	- Supports for multiple brush tips (randomized each dab)
	- Custom brush tip rotation 
	- Custom Brush spacing
	- Custom Brush textures
	- Fuzzy Dab parameters like:
		- Brush size
		- Brush angle
		- Color mix
		- Color Hue
		- Color Saturation
		- Color Value
		- Dab position scattering
- Layer management
	- New layer creation
	- Layer merging with blending modes
- Color management
	- Palette creation
		- Triad palette
		- Separate Hue, Saturation, and Value tweaking
- Brush mirroring
- Drawing functions like:
	- DrawLine(x1, y1, x2, y2)
	- DrawPoint(x, y)
	- DrawRect(x1, y1, x2, y2, angle)
	- DrawPath(pointList)
	- AddBorder(width)
	


# Installation

The recommended way to use Paynter is to download it with pip with the command:
	
    pip3 install paynter

but it can also download the source from GitHub and copy the "paynter" folder inside your project directory.

If you installed it from pip make sure to have all the library requirements by running:

    pip3 install -r requirements.txt


# Usage and Documentation

If you want a brief demostration you can check [example.py](https://github.com/elkiwy/paynter/blob/master/example.py) (NB: To be able to use the brushes created by example.py you also need to download the "res" folder where all the used brushtips are stored).

For advanced instructions and details you can check the project documentation at [paynter.readthedocs.org](https://paynter.readthedocs.org/)



# Dependencies

PaYnter needs **Numpy**, **Numba**, and **PIL** modules. Those can all be installed easily with Pip, anything else should come with the python3 bundle.



# Scope 

This project started October 1th 2018 and its goal is to have a simple yet really powerful interface for all the people who wants to procedurally generate images without letting down all the features that you have inside a real image painting software.

Here are some example of what I was able to create with Paynter:

<img src="https://instagram.fmxp1-1.fna.fbcdn.net/vp/f905c89e7aac3190aabf83eb24c4ece7/5C50D69F/t51.2885-15/e35/s1080x1080/42178085_1903017686660541_5530345369065186468_n.jpg" width="480">

<img src="https://instagram.fmxp1-1.fna.fbcdn.net/vp/3e87abead3dd9cbb056cf52f73901612/5C5D104A/t51.2885-15/sh0.08/e35/s640x640/39380901_716893531976641_8251910851804528640_n.jpg" width="480">

<img src="https://instagram.fmxp1-1.fna.fbcdn.net/vp/04be446f54a90af832b5ac495edf798d/5C44C453/t51.2885-15/sh0.08/e35/s640x640/38495966_303450853537604_5925747759607971840_n.jpg" width="480">

(You can find more here: [@elkiwyart](https://www.instagram.com/elkiwyart/))


