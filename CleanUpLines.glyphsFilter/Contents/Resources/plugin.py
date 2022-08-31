# encoding: utf-8

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from math import degrees, atan2

def angle(firstPoint, secondPoint):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return degrees(atan2(yDiff,xDiff))


class CleanUpLines(FilterWithDialog):

	# Definitions of IBOutlets

	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()

	# Text field in dialog
	angleThresholdField = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Clean Up Lines',
			'de': 'Linien aufräumen',
			'fr': 'Nettoyer les lignes',
			'es': 'Limpiar líneas',
			'pt': 'Limpar linhas retas',
			'jp': 'ラインをクリーンアップ',
			'ko': '라인 정리',
			'zh': '清理线路',
			})
		
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize({
			'en': 'Clean Up',
			'de': 'Aufräumen',
			'fr': 'Nettoyer',
			'es': 'Limpiar',
			'pt': 'Limpar',
			'jp': '掃除',
			'ko': '청소',
			'zh': '清理',
			})
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)

	# On dialog show
	@objc.python_method
	def start(self):
		
		# Set default value
		Glyphs.registerDefault('com.mekkablue.CleanUpLines.threshold', 10.0)
		
		# Set value of text field
		self.angleThresholdField.setStringValue_(Glyphs.defaults['com.mekkablue.CleanUpLines.threshold'])
		
		# Set focus to text field
		self.angleThresholdField.becomeFirstResponder()

	# Action triggered by UI
	@objc.IBAction
	def setThreshold_(self, sender):
		
		# Store value coming in from dialog
		if isinstance(sender, float):
			Glyphs.defaults['com.mekkablue.CleanUpLines.threshold'] = sender
		elif hasattr(sender,"floatValue"):
			Glyphs.defaults['com.mekkablue.CleanUpLines.threshold'] = sender.floatValue()
			
		# Trigger redraw
		self.update()

	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		
		# Called on font export, get value from customParameters
		if "threshold" in customParameters:
			threshold = customParameters['threshold']
		
		# Called through UI, use stored value
		else:
			threshold = float(Glyphs.defaults['com.mekkablue.CleanUpLines.threshold'])
		
		# Delete all nodes that are on an angle smaller than the theshold
		for i in range(len(layer.shapes))[::-1]:
			thisShape = layer.shapes[i]
			if isinstance(thisShape, GSPath):
				nodeCount = len(thisShape.nodes)
				for j in range(nodeCount)[::-1]:
					thisNode = thisShape.nodes[j]
					if thisNode.type == GSLINE:
						prevNode = thisShape.nodes[(j-1)%nodeCount] 
						nextNode = thisShape.nodes[(j+1)%nodeCount]
						if nextNode.type == GSLINE and prevNode.type != GSOFFCURVE:
							prevAngle = angle(prevNode, thisNode) % 360
							nextAngle = angle(thisNode, nextNode) % 360
							if abs(nextAngle-prevAngle) < threshold:
								del thisShape.nodes[j]
								nodeCount = len(thisShape.nodes)

	@objc.python_method
	def generateCustomParameter(self):
		return "%s; threshold:%s;" % (self.__class__.__name__, Glyphs.defaults['com.mekkablue.CleanUpLines.threshold'])

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
