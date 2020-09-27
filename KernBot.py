#MenuTitle: KernBot
# -*- coding: utf-8 -*-
__doc__="""
A Kerning Tool
"""
# imports
import os
import math
import json
import random
from vanilla import FloatingWindow, TextBox, List, RadioGroup, EditText, CheckBox, Button, VerticalLine, HorizontalLine
from vanilla.test.testAll import Test

# return a dictionary of all english words
ALL_WORDS = []
WORD_SRC = './resources/words_dictionary.txt'
with open(WORD_SRC) as json_words:
	ALL_WORDS = json.load(json_words)

# returns dictionary of all Kerning Group Keys and a list of associated glyphs
def makeKerningGroups(fGlyphs):
	returnKernGroups = {}
	for glyph in fGlyphs:
		#print(glyph.leftKerningKey, glyph, glyph.rightKerningKey)
		# Left
		if not glyph.leftKerningKey in returnKernGroups.keys():
			returnKernGroups[glyph.leftKerningKey] = []
		returnKernGroups[glyph.leftKerningKey].append( glyph )
		# Right
		if not glyph.rightKerningKey in returnKernGroups.keys():
			returnKernGroups[glyph.rightKerningKey] = []
		returnKernGroups[glyph.rightKerningKey].append( glyph )
	# return sorted groups
	return returnKernGroups

# returns dictionary of glyphNames --> (kernGroupOnRight, kernGroupOnLeft)
def glyphToKerningGroups(kGroups):
	g2g1 = {}
	g2g2 = {}	
	for kGroupKey, kGroupGlyphs in kGroups.items():
		if '@MMK_R_' in kGroupKey:
			if kGroupKey in g2g1:
				print('Double glyph in RIGHT kern groups', kGroupKey, kGroupGlyphs, g2g1[kGroupKey] )
			else:
				g2g1[kGroupKey] = kGroupGlyphs
		elif '@MMK_L_' in kGroupKey:
			if kGroupKey in g2g2:
				print('Double glyph in LEFT kern groups', kGroupKey, kGroupGlyphs, g2g2[kGroupKey] )
			else:
				g2g2[kGroupKey] = kGroupGlyphs
	# return tuple of Left and Right Kern Groups
	return g2g1, g2g2


# KERNBOT CLASS
class KernBot:

	# Object Globals
	mtrcUnit = 4
	kernUnit = 4

	# constructor
	def __init__(self):
		w = 300 # window width
<<<<<<< HEAD
		h = 700 # window height
=======
		h = 600 # window height
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		m = 8 # margin spacer
		s = 0.25 # scale to draw glyphs
		pb = 100 # padding bottom to space controls
		lsh = 150 # list height
		tbh = 24 # text box height
		cbh = 20 # checkbox height
		btw = 140 # button width
		bth = 24 # button height
		col_1_of_2 = w/2-m-m/2
		col_2_of_2 = w/2+m/2

		# GSFont obj
		self.font = Glyphs.font # current Font obj
		self.selectedMaster = Glyphs.font.selectedFontMaster # current Master obj
		self.KBtab = Glyphs.font.tabs[0] # current GSEditViewController obj tabs
		self.actvglyphleft = None
		self.actvglyphright = None
		self.SyncGlyphMetrics = True
<<<<<<< HEAD
		self.initComplete = False

		# Highly Used Letter in Draw F(x)s
		self.spaceLetter = self._getCurrentLayerForLetter(cGlyph=self.font.glyphs['space'])
=======

		# Highly Used Letter in Draw F(x)s
		self.spaceLetter = self.getCurrentLayerForLetter(cGlyph=self.font.glyphs['space'])
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad

		# Vanilla Window Obj
		self.w = FloatingWindow(
			(50,100,w,h),
			'KernBot.io',
			autosaveName="com.joeygrable.kernbot.ui"
		)
		# Vanilla Element Styles
		KgValueStyle = dict(alignment="center", sizeStyle="regular")
		KgLabelStyle = dict(alignment="center", sizeStyle="mini")
		KgBtnStyles = dict(sizeStyle="regular")

		# ------------------------------------------------------------------------------------------------
		# create Left and Right list of Kerning Groups keys
		self.w.leftKernTxt = TextBox( (m, m, col_1_of_2, tbh), "Right KERN KEY" )
		self.w.rightKernTxt = TextBox( (col_2_of_2, m, -m, tbh), "Left KERN KEY" )
		self.w.leftKerns = List( (m, tbh+m, col_1_of_2, lsh), [], selectionCallback=self.updateKernGroupsList )
		self.w.rightKerns = List( (col_2_of_2, tbh+m, -m, lsh), [], selectionCallback=self.updateKernGroupsList )

		# (below KGroupsList) create Left and Right list of glyphs that share the selected Kerning Group Key
		self.w.leftGlyphsListTxt = TextBox( (m, tbh+lsh+m*2, col_1_of_2, tbh), "Left GLYPH" )
		self.w.leftGlyphsListTxtSub = TextBox( (m, tbh*2+lsh+m*2, col_1_of_2, tbh), "w/ Right Kern Group", sizeStyle="mini" )
		self.w.rightGlyphsListTxt = TextBox( (col_2_of_2, tbh+lsh+m*2, -m, tbh), "Right GLYPH" )
		self.w.rightGlyphsListTxtSub = TextBox( (col_2_of_2, tbh*2+lsh+m*2, -m, tbh), "w/ Left Kern Group", sizeStyle="mini" )

		self.w.leftGlyphsList = List( (m, tbh*3+lsh+m+m/2, col_1_of_2, lsh), [], selectionCallback=self.updateGlyphWithKernGroupList)
		self.w.rightGlyphsList = List( (col_2_of_2, tbh*3+lsh+m*1.5, -m, lsh), [], selectionCallback=self.updateGlyphWithKernGroupList )

		# make kerning groups and cache them in the App --> list of kern groups
		self.kernGroups = makeKerningGroups( Glyphs.font.glyphs )
		# make a cross reference for glyphName --> (kernGroupOnLeft, kernGroupOnRight)
		self.glyph2Group1, self.glyph2Group2 = glyphToKerningGroups( self.kernGroups )

		# ------------------------------------------------------------------------------------------------
		# populate List elements with initial font data
<<<<<<< HEAD
		self.leftKernKeysList = self._getCleanKernKeysAsList( self.glyph2Group1.keys() )
		self.leftKernKeysList.sort(key=lambda x:(x.islower(), x))
		self.rightKernKeysList = self._getCleanKernKeysAsList( self.glyph2Group2.keys() )
=======
		self.leftKernKeysList = self.cleanKeysList( self.glyph2Group1.keys() )
		self.leftKernKeysList.sort(key=lambda x:(x.islower(), x))
		self.rightKernKeysList = self.cleanKeysList( self.glyph2Group2.keys() )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.rightKernKeysList.sort(key=lambda x:(x.islower(), x))

		# ------------------------------------------------------------------------------------------------
		# display buttons for outputing kern/glyph strings to screen
		# divider line
		self.w.listsHorizontalDvd = HorizontalLine( (m, tbh*3+lsh*2+m*2.5, w-m-m, 1) )
		# label text for this section of the app
		self.w.openNewTabToDisplayLabel = TextBox( (m, tbh*3+lsh*2+m*3.5, w-m-m, tbh), "Open New Tab and Display:" )
		# show current letter pair
<<<<<<< HEAD
		self.w.showCurrentLetterPair = Button( (m, tbh*4+lsh*2+m*3.5, col_1_of_2, bth), 'show letter pair', callback=self.drawCurrentLetterPair, **KgBtnStyles )
		# show current letter pair in word
		#self.w.showCurrentLetterPairInWord = Button( (col_2_of_2, tbh*4+lsh*2+m*3.5, -m, bth), 'show pair in word', callback=self.drawCurrentLetterPairInWord, **KgBtnStyles )
		# show list of all matching words
		self.w.showCurrentLetterPairWords = List( (col_2_of_2, tbh*4+lsh*2+m*3.5, -m, bth), [], selectionCallback=self.drawNewSelectedMatchingWord )
		# show current letter pair in spacing string (nnnonn, nonono)
		self.w.showCurrentLetterPairSpacingString = Button( (m, tbh*5+lsh*2+m*4.5, col_1_of_2, bth), 'spacing string', callback=self.drawCurrentPairInSpacingString, **KgBtnStyles )
		# show all letter pairs with kern pair
		self.w.showAllLetterPairsWithKerning = Button( (col_2_of_2, tbh*5+lsh*2+m*4.5, -m, bth), 'all kerning pairs', callback=self.drawAllPossibleLetterPairsWithKerning, **KgBtnStyles )
=======
		self.w.showCurrentLetterPair = Button( (m, tbh*4+lsh*2+m*3.5, col_1_of_2, bth), 'show letter pair', callback=self.newTabWithCurrentLetterPair, **KgBtnStyles )
		# show current letter pair in word
		self.w.showCurrentLetterPairInWord = Button( (col_2_of_2, tbh*4+lsh*2+m*3.5, -m, bth), 'show pair in word', callback=self.newTabWithCurrentLetterPairInWord, **KgBtnStyles )
		# show current letter pair in spacing string (nnnonn, nonono)
		self.w.showCurrentLetterPairSpacingString = Button( (m, tbh*5+lsh*2+m*4.5, col_1_of_2, bth), 'spacing string', callback=self.newTabWithCurrentSpacingString, **KgBtnStyles )
		# show all letter pairs with kern pair
		self.w.showAllLetterPairsWithKerning = Button( (col_2_of_2, tbh*5+lsh*2+m*4.5, -m, bth), 'all kerning pairs', callback=self.newTabWithAllLetterPairs, **KgBtnStyles )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# divider line
		self.w.currentGlyphsHorizontalDvd = HorizontalLine( (m, -pb-m, w-m-m, 1) )

		# ------------------------------------------------------------------------------------------------
		# display the current selected GLYPHS, their METRIC Keys/Values, and KERNING Pair/Value 
		# show the current left glyph
		self.w.currentLeftGlyph = TextBox( (0, -pb, w/5, tbh), "H", **KgValueStyle )
		self.w.currentLeftGlyphUC = TextBox( (0, -pb+tbh, w/5, tbh), "U+0048", **KgLabelStyle )
		self.w.currentLeftGlyphUClabel = TextBox( (0, -pb+tbh*1.8, w/5, tbh), "LEFT GLYPH", **KgLabelStyle )
		# divider line
		self.w.LeftGlyphDvdr = VerticalLine( (w/5, -pb, 1, tbh*2.5) )
		# show the current left glyph right metric
		self.w.currentLeftGlyphRightMetricVal = TextBox( (w/5, -pb, w/5, tbh), "+0", **KgValueStyle )
		self.w.currentLeftGlyphRightMetricKey = TextBox( (w/5, -pb+tbh, w/5, tbh), "=[value]", **KgLabelStyle )
		self.w.currentLeftGlyphRightMetricLabel = TextBox( (w/5, -pb+tbh*3, w/5, tbh), "RGT MTRC", **KgLabelStyle )
		# divider line--------
		self.w.LeftGlyphRightMetricDvd = VerticalLine( (w/5+w/5, -pb, 1, tbh*2.5) )
		# show the active kern pair
		self.w.currectKernPairVal = TextBox( (w/5+w/5, -pb, w/5, tbh), "-0", **KgValueStyle )
		self.w.currectKernPairKey = TextBox( (w/5+w/5, -pb+tbh, w/5, tbh), "V|V", **KgLabelStyle )
		self.w.currectKernPairLabel = TextBox( (w/5+w/5, -pb+tbh*3, w/5, tbh), "KERN PAIR", **KgLabelStyle )
		# divider line
		self.w.RightGlyphLeftMetricDvdr = VerticalLine( (w/5+w/5+w/5, -pb, 1, tbh*2.5) )
		# show the current right glyph left metric
		self.w.currentRightGlyphLeftMetricVal = TextBox( (-w/5-w/5, -pb, w/5, tbh), "+0", **KgValueStyle )
		self.w.currentRightGlyphLeftMetricKey = TextBox( (-w/5-w/5, -pb+tbh, w/5, tbh), "=[value]", **KgLabelStyle )
		self.w.currentRightGlyphLeftMetricLabel = TextBox( (-w/5-w/5, -pb+tbh*3, w/5, tbh), "LFT MTRC", **KgLabelStyle )
		# divider line
		self.w.RightGlyphDvdr = VerticalLine( (-w/5, -pb, 1, tbh*2.5) )
		# show the current right glyph
		self.w.currentRightGlyph = TextBox( (-w/5, -pb, -0, tbh), "I", **KgValueStyle )
		self.w.currentRightGlyphUC = TextBox( (-w/5, -pb+tbh, -0, tbh), "U+0049", **KgLabelStyle )
		self.w.currentRightGlyphUClabel = TextBox( (-w/5, -pb+tbh*1.8, -0, tbh), "RIGHT GLYPH", **KgLabelStyle )
		# buttons for kerning in steps. Round if kerning is not a multiple of a step.
		# LEFT Glyph RIGHT Metric Value
		self.w.LgRmBtnPlus = Button( (w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), '+', callback=self.leftGlyphRightMetricPlus, **KgBtnStyles )
		self.w.LgRmBtnMinus = Button( (w/5, -pb+tbh*1.75, (w/5)/2, bth), '-', callback=self.leftGlyphRightMetricMinus, **KgBtnStyles )
		# LEFT+RIGHT Kerning Pair Value
		self.w.KernPairBtnPlus = Button( (w/5+w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), '+', callback=self.glyphsKerningPairPlus, **KgBtnStyles )
		self.w.KernPairBtnMinus = Button( (w/5+w/5, -pb+tbh*1.75, (w/5)/2, bth), '-', callback=self.glyphsKerningPairMinus, **KgBtnStyles )
		# RIGHT Glyph LEFT Metric Value
		self.w.RgLmBtnPlus = Button( (-w/5-w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), '+', callback=self.rightGlyphLeftMetricPlus, **KgBtnStyles )
		self.w.RgLmBtnMinus = Button( (-w/5-w/5, -pb+tbh*1.75, (w/5)/2, bth), '-', callback=self.rightGlyphLeftMetricMinus, **KgBtnStyles )

		# ----------------------------------------------------------------------------------------
		# addCallbacks and listen to CONSTANTS
		#Glyphs.addCallback( self.documentwassaved, DOCUMENTWASSAVED )
		#Glyphs.addCallback( self.drawbackground, DRAWBACKGROUND )
		
		# load initial ALL_WORDS dataset
		self.allMatchingWords = []
<<<<<<< HEAD
		self.currentLetterPair = None
=======
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad

		# run initializing functions
		self.w.bind('close', self.closeCleanUp) # call if window closes
		self.updating = False # Flag to avoid recursive Updating

		# fill the controls with real values (ie. Lists)
		self.updateAppUI()
<<<<<<< HEAD
		self.initComplete = True
=======
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		
		self.w.open() # open window
		self.w.makeKey() # focus window

	# ----------------------------------------------------------------------------------------------------
<<<<<<< HEAD
	# KERN BOT USER INTERFACE updater

=======
	
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
	# update the app each time the user clicks one of the glyphs list
	def updateAppUI(self, sender=None):
		if not self.updating: # only act if not already updating
			self.updating = True # set updating Flag check
			
			# ----- GET LEFT Kern Keys ----------------------------------------------
			# fill the left kern list with kern keys (unfiltered)
			self.w.leftKerns.set( self.leftKernKeysList )
			# select top item in list if item not already selected
			if not self.w.leftKerns.getSelection():
				self.w.leftKerns.setSelection([0])
				lk_KeySelect = 0
			else:
				lk_KeySelect = self.w.leftKerns.getSelection()[0]

			# ----- GET LEFT Glyphs w/ key ------------------------------------------
			lk_KeyFind = self.w.leftKerns[lk_KeySelect]
<<<<<<< HEAD
			lk_glyphs = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey('L', lk_KeyFind) )
=======
			lk_glyphs = self.cleanGlyphsList( self.getGlyphsWithKernKey('L', lk_KeyFind) )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
			lk_glyphs.sort(key=lambda x:(x.islower(), x))
			# fill the left glyphs list with glyphs with matching kern key (unfiltered)
			self.w.leftGlyphsList.set( lk_glyphs )
			# select top item in list of item is not already selected
			if not self.w.leftGlyphsList.getSelection():
				self.w.leftGlyphsList.setSelection([0])
				leftCharSelect = 0
			else:
				leftCharSelect = int(self.w.leftGlyphsList.getSelection()[0])
			
			# ----- GET RIGHT Kern Keys ----------------------------------------------
			# fill the right kern list with kern keys (unfiltered)
			self.w.rightKerns.set( self.rightKernKeysList )
			# select top item in list if item not already selected
			if not self.w.rightKerns.getSelection():
				self.w.rightKerns.setSelection([0])
				rk_KeySelect = 0
			else:
				rk_KeySelect = self.w.rightKerns.getSelection()[0]

			# ----- GET RIGHT Glyphs w/ key ------------------------------------------
			rk_KeyFind = self.w.rightKerns[rk_KeySelect]
<<<<<<< HEAD
			rk_glyphs = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey('R', rk_KeyFind) )
=======
			rk_glyphs = self.cleanGlyphsList( self.getGlyphsWithKernKey('R', rk_KeyFind) )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
			rk_glyphs.sort(key=lambda x:(x.islower(), x))
			# fill the right glyphs list with glyphs with matching kern key (unfiltered)
			self.w.rightGlyphsList.set( rk_glyphs )
			# select top item in list of item is not already selected
			if not self.w.rightGlyphsList.getSelection():
				self.w.rightGlyphsList.setSelection([0])
				rightCharSelect = 0
			else:
				rightCharSelect = int(self.w.rightGlyphsList.getSelection()[0])

			# ----- LEFT Glyph -------------------------------------------------------
<<<<<<< HEAD
			leftGlyph = self._getGlyphFromCharStr( lk_glyphs[leftCharSelect] )
=======
			leftGlyph = self.getGlyphFromChar( lk_glyphs[leftCharSelect] )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
			leftGlyphLayer = leftGlyph.layers[self.selectedMaster.id]
			leftGlyphName = str(leftGlyph.name)
			leftGlyphUC = "U+%s" % leftGlyph.unicode
			leftGlyphRightSB = "+ %d" % leftGlyphLayer.RSB
			leftGlyphRightMetricKey = str(leftGlyph.rightMetricsKey) if not "None" == str(leftGlyph.rightMetricsKey) else "=%d" % leftGlyphLayer.RSB
			self.actvGlyphLeft = leftGlyph
			self.actvLeftKernKey = lk_KeyFind

			# ----- RIGHT Glyph ------------------------------------------------------
<<<<<<< HEAD
			rightGlyph = self._getGlyphFromCharStr( rk_glyphs[rightCharSelect] )
=======
			rightGlyph = self.getGlyphFromChar( rk_glyphs[rightCharSelect] )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
			rightGlyphLayer = rightGlyph.layers[self.selectedMaster.id]
			rightGlyphName = str(rightGlyph.name)
			rightGlyphUC = "U+%s" % rightGlyph.unicode
			rightGlyphLeftSB = "+ %d" % rightGlyphLayer.LSB
			rightGlyphLeftMetricKey = str(rightGlyph.leftMetricsKey) if not "None" == str(rightGlyph.leftMetricsKey) else "=%d" % rightGlyphLayer.LSB
			self.actvGlyphRight = rightGlyph
			self.actvRightKernKey = rk_KeyFind

			# ----- KERNING PAIR Information -----------------------------------------
			kernPairKey = "%s | %s" % (lk_KeyFind, rk_KeyFind)
			kernAmt = Glyphs.font.kerningForPair( self.selectedMaster.id, '@MMK_L_%s' % lk_KeyFind, '@MMK_R_%s' % rk_KeyFind )
			if kernAmt > 100:
				kernAmt = 0
			if kernAmt > 0:
				kernPairVal = "+ %d" % kernAmt
			elif kernAmt == 0:
				kernPairVal = "= %d" % kernAmt
			elif kernAmt < 0:
				kernPairVal = "- %s" % str(kernAmt)[1:]

			# ----- SET Glyphs Metric & Kerning Information --------------------------
			# LEFT Glyph 
			self.w.currentLeftGlyph.set( leftGlyphName )
			self.w.currentLeftGlyphUC.set( leftGlyphUC )
			self.w.currentLeftGlyphRightMetricVal.set( leftGlyphRightSB )
			self.w.currentLeftGlyphRightMetricKey.set( leftGlyphRightMetricKey )
			# LEFT+RIGHT Kerning
			self.w.currectKernPairVal.set( kernPairVal )
			self.w.currectKernPairKey.set( kernPairKey )
			# RIGHT Glyph
			self.w.currentRightGlyph.set( rightGlyphName )
			self.w.currentRightGlyphUC.set( rightGlyphUC )
			self.w.currentRightGlyphLeftMetricVal.set( rightGlyphLeftSB )
			self.w.currentRightGlyphLeftMetricKey.set( rightGlyphLeftMetricKey )

<<<<<<< HEAD
			# ----- UPDATE WORD DATA SET ---------------------------------------------
			# if initComplete = False, first time running updater
			if not self.initComplete:
				# set current letter pair
				self.currentLetterPair = leftGlyphName+rightGlyphName
				# calculate initial matching words list
				self.allMatchingWords = self._determineMatchingWordsContaining( leftGlyphName, rightGlyphName )
			# not our first rodeo in the updater
			else:
				# ONLY RERUN MATCHING WORDS DETERMINER IF THE LETTER PAIR CHANGES
				# check if pair changed
				oldPair = self.currentLetterPair
				newPair = leftGlyphName+rightGlyphName
				# check if either letter in pair changed
				if not oldPair == newPair:
					# set new current letter pair
					self.currentLetterPair = newPair
					# recalc all matching words list
					self.allMatchingWords = self._determineMatchingWordsContaining( leftGlyphName, rightGlyphName )
			
			# check to see if we've already searched for all matching words
			if not self.allMatchingWords:
				self.allMatchingWords = self._determineMatchingWordsContaining( leftGlyphName, rightGlyphName )

			# make sure there are at least some words to show
			if self.allMatchingWords:
				# fill the list of matching words (unfiltered)
				self.w.showCurrentLetterPairWords.set( self.allMatchingWords )
=======
			# ----- UPDATE GLOBAL DATA SETS ------------------------------------------
			self.currentLetterPair = leftGlyphName+rightGlyphName
			self.allMatchingWords = self.findWordContaining( leftGlyphName, rightGlyphName )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad

			# ----- Redraw & Finish Glyphs App updating ------------------------------
			Glyphs.redraw()
			# set Flag update complete
			self.updating = False

	# ----------------------------------------------------------------------------------------------------
<<<<<<< HEAD
	# CALLBACKS: GENERAL APP callbacks
=======
	# GENERAL APP callbacks
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad

	# every time the Glyphs App saves
	def documentWasSaved(self, passedobject):
		self.updateAppUI()

	# every time the Glyphs App tries to reload
	def drawBackground(self, layer, info):
		pass

	# when the window closes, unsubscribe from events
	def closeCleanUp(self, sender):
		Glyphs.removeCallback( self.documentWasSaved, DOCUMENTWASSAVED )
		Glyphs.removeCallback( self.drawBackground, DRAWBACKGROUND )
		print 'KernBot Window Closed'

	# ----------------------------------------------------------------------------------------------------
<<<<<<< HEAD
	# CALLBACKS: UPDATE TAB to display strings of letters

	# open new tab with current letter pair
	def drawCurrentLetterPair(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# get layer of current glyphs
		currentLeftLetter = self._getCurrentLayerForLetter(side='left')
		currentRightLetter = self._getCurrentLayerForLetter(side='right')
		# make list of all letters to draw
		allLetters = [currentLeftLetter, currentRightLetter]
		# draw letters to current tab open
		self._drawGlyphLayersToScreen( allLetters )

	# open new tab with current letter pair in a WORD
	def drawNewSelectedMatchingWord(self, sender):
=======
	# UPDATE TAB to display strings of letters
	def displayGlyphsInTab(self, allGlyphs):
		# empty tab to display new string
		self.KBtab.layers = []
		# loop all chars in string
		for gChar in allGlyphs:
			# add char to tab string
			self.KBtab.layers.append( gChar )

	# open new tab with current letter pair
	def newTabWithCurrentLetterPair(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# get layer of current glyphs
		currentLeftLetter = self.getCurrentLayerForLetter(side='left')
		currentRightLetter = self.getCurrentLayerForLetter(side='right')
		# make list of all letters to draw
		allLetters = [currentLeftLetter, currentRightLetter]
		# draw letters to current tab open
		self.displayGlyphsInTab( allLetters )

	# open new tab with current letter pair in a WORD
	def newTabWithCurrentLetterPairInWord(self, sender):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# first make sure the UI state is current
		self.updateAppUI()
		# pull from all matching words list
		if self.allMatchingWords:
<<<<<<< HEAD
			# select top item in list if item not already selected
			if not sender.getSelection():
				sender.setSelection([0])
				matchingWordSelect = 0
			else:
				matchingWordSelect = sender.getSelection()[0]
			# randomly get one word out of list
			#selectedWord = random.choice(self.allMatchingWords)
			# get the word selected to be drawn
			selectedWord = self.allMatchingWords[ matchingWordSelect ]
			# format all chars glyphs
			allChars = []
			for currentChar in selectedWord:
=======
			# randomly get one word out of list
			randMatch = random.choice(self.allMatchingWords)
			# format all chars glyphs
			allChars = []
			for currentChar in randMatch:
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
				allChars.append( self.font.glyphs[currentChar] )
			# get all letter glyph layers to draw
			allLetters = []
			for cGlyph in allChars:
				# get current glyph layer
<<<<<<< HEAD
				currentLetter = self._getCurrentLayerForLetter(cGlyph=cGlyph)
				allLetters.append( currentLetter )
			# draw letters to current tab open
			self._drawGlyphLayersToScreen( allLetters )
			# get & set cursor position to position of letter pair in word
			cursorPos = self._getCursorPositionOfPair( selectedWord )
			self._setCursorPositionOfPair(cursorPos)

	# open new tab with a spacing string that uses the kerning pair
	def drawCurrentPairInSpacingString(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# get layer of current glyphs
		currentLeftLetter = self._getCurrentLayerForLetter(side='left')
		currentRightLetter = self._getCurrentLayerForLetter(side='right')
		# make list of all letters to draw
		allLetters = []
		numTimes = 10
=======
				currentLetter = self.getCurrentLayerForLetter(cGlyph=cGlyph)
				allLetters.append( currentLetter )
			# draw letters to current tab open
			self.displayGlyphsInTab( allLetters )
			# get & set cursor position to position of letter pair in word
			cursorPos = self.getCursorPosition( randMatch )
			self.setCursorPosition(cursorPos)

	# open new tab with a spacing string that uses the kerning pair
	def newTabWithCurrentSpacingString(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# get layer of current glyphs
		currentLeftLetter = self.getCurrentLayerForLetter(side='left')
		currentRightLetter = self.getCurrentLayerForLetter(side='right')
		# make list of all letters to draw
		allLetters = []
		numTimes = 4
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		for cIndex in range(1, numTimes):
			allLetters.append( currentLeftLetter )
			allLetters.append( currentRightLetter )
		# draw letters to current tab open
<<<<<<< HEAD
		self._drawGlyphLayersToScreen( allLetters )

	# open new tab with all possible letter combinations that use the current kerning pair 
	def drawAllPossibleLetterPairsWithKerning(self, sender):
		# gather char information
		allLeftChars = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey('L', self.actvLeftKernKey) )
		allLeftChars.sort(key=lambda x:(x.islower(), x))
		allRightChars = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey('R', self.actvRightKernKey) )
=======
		self.displayGlyphsInTab( allLetters )

	# open new tab with all possible letter combinations that use the current kerning pair 
	def newTabWithAllLetterPairs(self, sender):
		# gather char information
		allLeftChars = self.cleanGlyphsList( self.getGlyphsWithKernKey('L', self.actvLeftKernKey) )
		allLeftChars.sort(key=lambda x:(x.islower(), x))
		allRightChars = self.cleanGlyphsList( self.getGlyphsWithKernKey('R', self.actvRightKernKey) )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		allRightChars.sort(key=lambda x:(x.islower(), x))
		# make list of all possible chars
		allChars = []
		for leftChar in allLeftChars:
			for rightChar in allRightChars:
				allChars.append( self.font.glyphs[leftChar] )
				allChars.append( self.font.glyphs[rightChar] )
		# make list of all possible kern pair combination
		LPcount = 1
		spaceEvery = 2
		allLetters = []
		for cGlyph in allChars:
			# get current glyph layer
<<<<<<< HEAD
			currentLetter = self._getCurrentLayerForLetter(cGlyph=cGlyph)
=======
			currentLetter = self.getCurrentLayerForLetter(cGlyph=cGlyph)
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
			allLetters.append( currentLetter )
			# add glyph spacer every
			if LPcount == spaceEvery:
				allLetters.append( self.spaceLetter )
				LPcount = 1
			else:
				LPcount += 1
		# draw letters to current tab open
<<<<<<< HEAD
		self._drawGlyphLayersToScreen( allLetters )
=======
		self.displayGlyphsInTab( allLetters )
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad

	# ----------------------------------------------------------------------------------------------------
	# KERN GROUP & GLYPHS ——> callback functions for Lists, Buttons, and TextBox (oh my!)

	# every time either kern group list changes
	def updateKernGroupsList(self, sender):
		# update App UI
		self.updateAppUI()

	# every time the glyph w/ kern group list changes
	def updateGlyphWithKernGroupList(self, sender):
		# update App UI
		self.updateAppUI()

	# LEFT GLYPH decrease right metric multiplier
	def leftGlyphRightMetricMinus(self, sender):
<<<<<<< HEAD
		self._adjustLeftGlyphRightMetric(direction='-')
=======
		self.adjustLeftGlyphRightMetric(direction='-')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# LEFT GLYPH increase right metric multiplier
	def leftGlyphRightMetricPlus(self, sender):
<<<<<<< HEAD
		self._adjustLeftGlyphRightMetric(direction='+')
=======
		self.adjustLeftGlyphRightMetric(direction='+')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# RIGHT GLYPH decrease left metric multiplier
	def rightGlyphLeftMetricMinus(self, sender):
<<<<<<< HEAD
		self._adjustRightGlyphLeftMetric(direction='-')
=======
		self.adjustRightGlyphLeftMetric(direction='-')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# RIGHT GLYPH increase left metric multiplier
	def rightGlyphLeftMetricPlus(self, sender):
<<<<<<< HEAD
		self._adjustRightGlyphLeftMetric(direction='+')
=======
		self.adjustRightGlyphLeftMetric(direction='+')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# LEFT+RIGHT GLYPH decrease kerning for pair
	def glyphsKerningPairMinus(self, sender):
<<<<<<< HEAD
		self._adjustKerningForPair(direction='-')
=======
		self.adjustKerningForLeftRightPair(direction='-')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# LEFT+RIGHT GLYPH increase kerning for pair
	def glyphsKerningPairPlus(self, sender):
<<<<<<< HEAD
		self._adjustKerningForPair(direction='+')
=======
		self.adjustKerningForLeftRightPair(direction='+')
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		self.updateAppUI()

	# ----------------------------------------------------------------------------------------------------
	# METRIC & KERNING METHODS ––> sets new glyph value

	# ADJUST left glyph right metric +/-
<<<<<<< HEAD
	def _adjustLeftGlyphRightMetric(self, direction='-'):
=======
	def adjustLeftGlyphRightMetric(self, direction='-'):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# get left glyph layer information
		leftGlyphLayer = self.actvGlyphLeft.layers[self.selectedMaster.id]
		leftGlyphRMK = str(self.actvGlyphLeft.rightMetricsKey) if not None == self.actvGlyphLeft.rightMetricsKey else leftGlyphLayer.RSB
		# if is a mltp of another glyph
		if type(leftGlyphRMK) == str:
			# check metric key has mltp attached
			if '*' in leftGlyphRMK:
				leftGlyphMMltp = float(leftGlyphRMK.rsplit('*', 1)[-1])
			else:
				leftGlyphMMltp = 1.0
			# INCREASE OR DECREASE
			if direction == '-':
				NEWleftGlyphMMltp = leftGlyphMMltp - 0.05
			elif direction == '+':
				NEWleftGlyphMMltp = leftGlyphMMltp + 0.05
			NEWleftGlyphRMK = unicode((leftGlyphRMK.rsplit('*', 1)[0] + '*' + str(NEWleftGlyphMMltp))[1:], 'UTF-8')
			# set new RMK for Glyph
			self.actvGlyphLeft.rightMetricsKey = self.actvGlyphLeft.rightMetricsKey.replace( leftGlyphRMK[1:], NEWleftGlyphRMK )
		# if is a multiple of the metric spacing unit
		elif type(leftGlyphRMK) == float:
			# INCREASE OR DECREASE
			if direction == '-':
				# set new RSB for Glyph
				leftGlyphLayer.RSB = leftGlyphLayer.RSB - self.mtrcUnit
			elif direction == '+':
				# set new RSB for Glyph
				leftGlyphLayer.RSB = leftGlyphLayer.RSB + self.mtrcUnit
		# sync metrics
		if self.SyncGlyphMetrics:
			for thisLeftGlyphLayer in self.actvGlyphLeft.layers:
				thisLeftGlyphLayer.syncMetrics()

	# ADJUST right glyph left metric +/-
<<<<<<< HEAD
	def _adjustRightGlyphLeftMetric(self, direction='-'):
=======
	def adjustRightGlyphLeftMetric(self, direction='-'):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# get right glyph layer information
		rightGlyphLayer = self.actvGlyphRight.layers[self.selectedMaster.id]
		rightGlyphLMK = str(self.actvGlyphRight.leftMetricsKey) if not None == self.actvGlyphRight.leftMetricsKey else rightGlyphLayer.LSB
		# if is a mltp of another glyph
		if type(rightGlyphLMK) == str:
			# check metric key has mltp attached
			if '*' in rightGlyphLMK:
				rightGlyphMMltp = float(rightGlyphLMK.rsplit('*', 1)[-1])
			else:
				rightGlyphMMltp = 1.0
			# INCREASE OR DECREASE
			if direction == '-':
				NEWrightGlyphMMltp = rightGlyphMMltp - 0.05
			elif direction == '+':
				NEWrightGlyphMMltp = rightGlyphMMltp + 0.05
			NEWrightGlyphLMK = unicode((rightGlyphLMK.rsplit('*', 1)[0] + '*' + str(NEWrightGlyphMMltp))[1:], 'UTF-8')
			# set new LMK for Glyph
			self.actvGlyphRight.leftMetricsKey = self.actvGlyphRight.leftMetricsKey.replace( rightGlyphLMK[1:], NEWrightGlyphLMK )
		# if is a multiple of the metric spacing unit
		elif type(rightGlyphLMK) == float:
			# INCREASE OR DECREASE
			if direction == '-':
				# set new LSB for Glyph
				rightGlyphLayer.LSB = rightGlyphLayer.LSB - self.mtrcUnit
			elif direction == '+':
				# set new LSB for Glyph
				rightGlyphLayer.LSB = rightGlyphLayer.LSB + self.mtrcUnit
		# sync metrics
		if self.SyncGlyphMetrics:
			for thisRightGlyphLayer in self.actvGlyphRight.layers:
				thisRightGlyphLayer.syncMetrics()

	# ADJUST kerning value for right+left glyph pair +/-
<<<<<<< HEAD
	def _adjustKerningForPair(self, direction='-'):
=======
	def adjustKerningForLeftRightPair(self, direction='-'):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# set kern direction
		if direction == "-":
			kdVal = -1
		elif direction == "+":
			kdVal = 1
		# get current kerning
		kpVal = Glyphs.font.kerningForPair( self.selectedMaster.id, '@MMK_L_%s' % self.actvLeftKernKey, '@MMK_R_%s' % self.actvRightKernKey )
		if kpVal > 100:
			kpVal = -1
		# calculate the next kernunit interval +/-
		NEWkpVal = float(int(round(kpVal/self.kernUnit + kdVal ))*self.kernUnit)
		# set new value for kern pair
		Glyphs.font.setKerningForPair( self.selectedMaster.id, '@MMK_L_%s' % self.actvLeftKernKey, '@MMK_R_%s' % self.actvRightKernKey, NEWkpVal )

	# ----------------------------------------------------------------------------------------------------
	# UTILITY METHODS ——> return something
	
	# returns a list of all glyphs that has the desired kerning group on the specified side
<<<<<<< HEAD
	def _getGlyphsWithKernKey(self, side, searchForKey):
=======
	def getGlyphsWithKernKey(self, side, searchForKey):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		for kGroup in self.kernGroups.keys():
			findMMK = '@MMK_'+side+'_'+searchForKey
			if findMMK in kGroup:
				return self.kernGroups[kGroup]

<<<<<<< HEAD
	# returns the kern key letter as a string (from a unicode u'@MMK_L_v' string ——> 'v')
	def _getCleanKernKeysAsList(self, uListItems):
=======
	# returns the kern key as a string (from a unicode u'@MMK_L_v' string)
	def cleanKeysList(self, uListItems):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		cleanList = []
		for lItem in uListItems:
			cleanList.append( str(lItem.rsplit('_', 1)[-1]) )
		return cleanList

<<<<<<< HEAD
	# returns s list of letter names given a list of GSGlyph obj
	def _getGlyphNamesListFromObj(self, gListItems):
=======
	# returns the glyphs list as letters list
	def cleanGlyphsList(self, gListItems):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		cleanList = []
		for gItem in gListItems:
			cleanList.append( str(gItem.name) )
		return cleanList

	# returns a single glyph Obj given a specific letter
<<<<<<< HEAD
	def _getGlyphFromCharStr(self, letter):
=======
	def getGlyphFromChar(self, letter):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		for glyph in Glyphs.font.glyphs:
			if glyph.name == letter:
				return glyph

	# returns the current layer of the active left glyph
<<<<<<< HEAD
	def _getCurrentLayerForLetter(self, side='left', cGlyph=None):
		# if want a specific glyph
		if not None == cGlyph:
			cGlyphLayer = cGlyph.layers[ self.selectedMaster.id ]
		else:
			# default get the current active left glyph
			if side == 'left':
				cGlyphLayer = self.actvGlyphLeft.layers[ self.selectedMaster.id ]
			# otherwise get the current active right glyph
			elif side == 'right':
				cGlyphLayer = self.actvGlyphRight.layers[ self.selectedMaster.id ]
		# return the letter
		return cGlyphLayer

	# search for a word in ALL_WORDS list containing chars Left and Right
	def _determineMatchingWordsContaining(self, cLeft, cRight):
=======
	def getCurrentLayerForLetter(self, side='left', cGlyph=None):
		# if want a specific glyph
		if not None == cGlyph:
			returnLetter = cGlyph.layers[ self.selectedMaster.id ]
		else:
			# default get the current active left glyph
			if side == 'left':
				returnLetter = self.actvGlyphLeft.layers[ self.selectedMaster.id ]
			# otherwise get the current active right glyph
			elif side == 'right':
				returnLetter = self.actvGlyphRight.layers[ self.selectedMaster.id ]
		# return the letter
		return returnLetter

	# search for a word in ALL_WORDS list containing chars Left and Right
	def findWordContaining(self, cLeft, cRight):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# get a word list that matches the possible word cases
		L_CAP = cLeft.isupper()
		R_CAP = cRight.isupper()
		# get list of found words
		foundWords = []
		# CASE #1: CAP-CAP word --------------------------------------
		if L_CAP and R_CAP:
			# find any matching word
			findString = str( (cLeft+cRight).lower() )
			for cWord in ALL_WORDS:
				if findString in cWord:
					# make entire work uppercase
					# add word to found list
					foundWords.append( cWord.upper() )
		# CASE #2: CAP-lower word ------------------------------------
		elif L_CAP and not R_CAP:
			# find any first car is CAP and second car is lower
			for cWord in ALL_WORDS:
				check1 = str(cLeft.lower())
				check2 = str(cRight)
				# word must have at least two characters
				if len(cWord) > 2:
					if cWord[0] == check1 and cWord[1] == check2:
						# convert first letter in every word to CAP
						cWordCap1 = str(cWord).capitalize()
						# add word to found list
						foundWords.append( cWordCap1 )
		# CASE #3: lower-CAP word ------------------------------------
		elif not L_CAP and R_CAP:
			# find two matching words
			findLeft = str(cLeft).lower()
			findRight = str(cRight).lower()
			wordSet1 = []
			wordSet2 = []
			for cWord in ALL_WORDS:
				# word must have at least two characters
				if len(cWord) > 2:
					# word1 match if last char match cLeft
					if cWord[-1] == findLeft:
						wordSet1.append( cWord )
					# word2 match if first char match cRight
					if cWord[0] == findRight:
						wordSet2.append( cWord )
<<<<<<< HEAD
=======
					
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
					# check both matches exist
					if wordSet1 and wordSet2:
						# make NEW word camelCase ——> "camel"+"Case" = word1 + word2.uppercase()
						newWord = str(random.choice(wordSet1)) + str(random.choice(wordSet2)).capitalize()
						foundWords.append( newWord )
<<<<<<< HEAD
=======

>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		# CASE #4: lower-lower word ----------------------------------
		elif not L_CAP and not R_CAP:
			# find any matching word
			findString = str(cLeft+cRight)
			for cWord in ALL_WORDS:
				if findString in cWord:
					# add word to found list
					foundWords.append( cWord.upper() )
		# CASE #ERROR: improper C1 or C2 values
		else:
			print('improper C1 or C2 values')
		# return random word that matches input
		return foundWords

<<<<<<< HEAD
	# ----------------------------------------------------------------------------------------------------
	# DRAW METHODS ——> does something with the GlyphsApp EditViewController

	# draw a list of GSLayer objs with the current active KernBot TAB
	def _drawGlyphLayersToScreen(self, allGlyphs):
		# empty tab to display new string
		self.KBtab.layers = []
		# loop all chars in string
		for gChar in allGlyphs:
			# add char to tab string
			self.KBtab.layers.append( gChar )

	# returns an index postiont between the current letter pairs within a given word
	def _getCursorPositionOfPair(self, word):
		foundCharsIndex = word.find(self.currentLetterPair)
		return foundCharsIndex+1

	# sets current Glyphs App tab cursor position with a given index position
	def _setCursorPositionOfPair(self, posIndex):
=======
	# returns an index postiont between the current letter pairs within a given word
	def getCursorPosition(self, word):
		foundCharsIndex = word.find(self.currentLetterPair)
		return foundCharsIndex+1

	# sets current Glyphs App tab cursor position to a given index position
	def setCursorPosition(self, posIndex):
>>>>>>> b4895a139c130ad25add5ed192a9cce5a28156ad
		Glyphs.font.currentTab.textCursor = posIndex
		return True

	# ----------------------------------------------------------------------------------------------------

# run
KernBot()