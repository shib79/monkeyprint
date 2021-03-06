# -*- coding: latin-1 -*-

#	Copyright (c) 2015--2016 Paul Bomke
#	Distributed under the GNU GPL v2.
#
#	This file is part of monkeyprint.
#
#	monkeyprint is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	monkeyprint is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You have received a copy of the GNU General Public License
#    along with monkeyprint.  If not, see <http://www.gnu.org/licenses/>.

import re

class stringEvaluator:
	
	def __init__(self, settings, modelCollection):
		self.settings = settings
		self.modelCollection = modelCollection

	def parseCommand(self,command):
		# Find stuff in curly braces.
		# Add () around [...]+ to suppress the curly braces in the result.
		#curlyBraceContents = re.findall(r"\{[A-Za-z\$\+\*\-\/]+\}", command)
		curlyBraceContents = re.findall(r"\{[^\{^\}]+\}", command)
		# Find substrings.
		curlyBraceContentsEvaluated = []
		for expression in curlyBraceContents:
			# Strip the curly braces.
			expressionContent = expression[1:-1]
			print "Found expression: " + expressionContent
			# Test if there are prohibited chars inside.
			# We only want letters, spaces and +-*/.
			# Create a pattern that matches what we don't want.
			allowedPattern = re.compile('[^A-Z^a-z^\+^\-^\*^\/^\$^ ]+')
			# Findall will return a list of prohibited chars if it finds any.
			prohibitedChars = allowedPattern.findall(expressionContent)
			# If not...
			if len(prohibitedChars) == 0:
				print "   Expression valid. Processing..."
				# ... do the processing.
				
				# Replace all $-variables with the corresponding values.
				#values = []
				# First, find all $-variables.
				variables = re.findall(r"\$[A-Za-z]+", expressionContent)
				print "   Found variables: " + str(variables)
				# Iterate through the $-variables...
				for variable in variables:
					# ... and get the corresponding value from the settings.
					#values.append(self.replaceWithValue(variable))
					value = self.replaceWithValue(variable[1:])
					expressionContent = expressionContent.replace(variable, value)
				print "   Replaced variables: " + str(expressionContent)
				# Evaluate the expression.
				result = "0"
				try:
					result = str(eval(expressionContent))
					print "Result: " + result 
				except SyntaxError:
					print "   Something went wrong while parsing G-Code variables. Replacing by \"0\""
				#curlyBraceContentsEvaluated.append(result)
			
				# Replace curly brace expression by result.
				command = command.replace(expression, result)
			
			# If we found prohibited chars...
			else:
				print "Prohibited characters " + str(prohibitedChars) + " found. Check your G-Code string."
				command = command.replace(expression, "0")
		print "Finished G-Code command: " + command
		
		return command
			
	
	def replaceWithValue(self, variable):
		print "      Processing variable: " + variable
		variableValid = True
		if variable == "layerHeight":
			value = str(self.modelCollection.jobSettings['Layer height'].value)
		elif variable == "buildDir":
			if self.settings['Reverse build'].value:
				value = "-1"
			else:
				value = "1"
		elif variable == "tiltDist":
			value = str(self.settings['Tilt distance GCode'].value)
		elif variable == "tiltDir":
			if self.settings['Reverse tilt'].value:
				value = "-1"
			else:
				value = "1"
		elif variable == "shutterPosOpen":
			value = str(self.settings['Shutter position open GCode'].value)
		elif variable == "shutterPosClosed":
			value = str(self.settings['Shutter position closed GCode'].value)
		else:
			value = "0"
			variableValid = False
		
		if variableValid:
			print "      Replacing by " + value + "."
		else:
			print "      Unknown G-Code variable found: \"" + variable + "\". Replacing by \"0\"."
		
		return value
	
