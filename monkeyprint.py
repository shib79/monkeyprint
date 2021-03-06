#!/usr/bin/python
# -*- coding: latin-1 -*-

#	Copyright (c) 2015 Paul Bomke
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
import sys, getopt # Needed to parse command line arguments.
import time
import monkeyprintModelHandling
import monkeyprintSettings
import monkeyprintGui
import monkeyprintGuiHelper
import monkeyprintPiServer



	
def main(argv):

	if __name__ == "__main__":
		# Test if this file is executed as the main application contrary to being executed as a model from inside another file.
		# Check command line arguments to see if this is a standalone or gui instance.
		# -h: print usage instructions.
		# -f: specify mkp file to open on startup.
		# -p, --print: run print process without gui. You have to pass the file name of an mkp file to print.
		try:
			opts, args = getopt.getopt(argv,"hdsf:p:",["server", "file=", "print="])
		except getopt.GetoptError:
			usage()
			sys.exit(2)

		# Act according to commandline options.
		if len(opts) != 0:
		
			# Check if debug option was given.
			debugOption = False
			for opt, arg in opts:
				if (opt=="-d"):
					debugOption = True
					
			# If debug flag was the only option...
			if len(opts) == 1 and debugOption:
				# ...start with debug flag.
				runGui(debug=debugOption)
			# If there are more options...
			else:
				# ...evaluate them.
				for opt, arg in opts:
					if (opt=="-h"):
						# Display help.
						usage()
						sys.exit(2)
					elif (opt in ("-f", "--file")):
						# Run Gui with project file.
						runGui(filename=arg, debug=debugOption)
					elif (opt in ("-p", "--print")):
						# Run non gui with project file and start print.
						runNoGui(filename=arg, debug=debugOption)
					elif (opt in ("-s", "--server")):
						# Start server that listens for commands via socket.
						runServerNoGui(debug=debugOption)
					
		# If no options present, just run with GUI.
		else:
			runGui()
	

def runGui(filename=None, debug=False):

	print "Starting Monkeyprint with GUI."
	# Create a debug console text buffer.
	console = monkeyprintGuiHelper.consoleText()

	# Create settings dictionary object for machine and program settings.
	programSettings = monkeyprintSettings.programSettings(console)
	
	# Create version message.
	console.addLine("You are using Monkeyprint " + str(programSettings['versionMajor'].value) + "." + str(programSettings['versionMinor'].value) + "." + str(programSettings['revision'].value))

	# Update settings from file.	
	programSettings.readFile()
	
	# Set debug mode if specified.
	if debug:
		print "Debug mode active."
		programSettings['Debug'].value = True
	else:
		programSettings['Debug'].value = False

	# Create model collection object.
	# This object contains model data and settings data for each model.
	# Pass program settings.
	modelCollection = monkeyprintModelHandling.modelCollection(programSettings, console)

	# Create splash screen for given interval.
	# Get version string first.
	versionString = "Monkeyprint version " + str(programSettings['versionMajor'].value) + "." + str(programSettings['versionMinor'].value) + "." + str(programSettings['revision'].value)
	splash = monkeyprintGuiHelper.splashWindow(imageFile='./logo.png', duration=1, infoString = versionString)
	
	# Create gui.
	gui = monkeyprintGui.gui(modelCollection, programSettings, console, filename)

	# Start the gui main loop.
	gui.main()



def runNoGui(filename=None, debug=False):

	print "Starting without Gui."
	# Create settings dictionary object for machine and program settings.
	programSettings = monkeyprintSettings.programSettings()
	
	# Update settings from file.	
	programSettings.readFile()

	# Set debug mode if specified.
	if debug==True:
		programSettings['Debug'].value = debug
		print "Debug mode active."
	else:
		programSettings['Debug'].value = False
	
	# Create model collection object.
	# This object contains model data and settings data for each model.
	# Pass program settings.
	modelCollection = monkeyprintModelHandling.modelCollection(programSettings)
	
	
	#TODO disable this...
	modelCollection.jobSettings['Exposure time'].value = 0.1
	print ("Exposure time: " + str(modelCollection.jobSettings['Exposure time'].value) + ".")
	
	
	# Load project file.
	# TODO: test if file is mkp.
	modelCollection.loadProject(filename)
	print ("Project file: " + str(filename) + " loaded successfully.")
	print "Found the following models:"
	for model in modelCollection:
		if model != 'default':
			print ("   " + model)
	
	# Start the slicer.
	modelCollection.updateSliceStack()
	print ("Starting slicer.")

	# Wait for all slicer threads to finish.
	while(modelCollection.slicerRunning()):
		modelCollection.checkSlicerThreads()
		time.sleep(.2)
		sys.stdout.write('.')
		sys.stdout.flush()
	
	# Start print process when slicers are done.
	print "\nSlicer done. Starting print process."
	
	# Create the projector window.
	gui = monkeyprintGui.noGui(programSettings, modelCollection)	
	
	
	print "Print process done. Thank you for using Monkeyprint."


def runServerNoGui(port="5553", debug=False):
	printerServer = monkeyprintPiServer.monkeyprintPiServer(port, debug)
	

def usage():
	print "\nCommand line option not recognized.\n"
	print "Usage: monkeyprint.py <options>\n"

	print "<no option>:                     Start GUI."
	print "-h:                              Show this help text."
	print "-f or --file <filename.mkp>:     Start GUI and load project file."
	print "-p or --print <filename.mkp>:    Start without GUI and run a print job."
	print "-s or --server				Start a monkeyprint server that prints incoming files."
	print "-d:                              Run in debug mode without stepper motion"
	print "                                 and shutter servo. This will overwrite"
	print "                                 the debug option in the settings menu."

main(sys.argv[1:])
