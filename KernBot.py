#MenuTitle: KernBot
# -*- coding: utf-8 -*-
__doc__="""
KernBot.IO is a GlyphsApp plugin that will improve your productivity and save you time during the metric spacing and kerning phases of your font development workflow.

Out of the box, KernBotIO displays an interface aiming to center your focus on the space between your letterforms. GlyphsApp is a fantastic tool, but it emphasizes the current glyph and does not give justice to the context surrounding your glyph-shapes. KernBotIO re-centers the space between your letterforms, allowing you to quickly view any letter combination that uses your chosen kerning pair combination.

KernBotIO helps you by displaying lists of all the kerning-keys within your font. It then lists every letter and all possible letter combinations that utilize the selected kerning-key-pair. It also makes use of optional buttons to display your kerning in context, including a spacing string sequence maker, a word generator, and even more under-development!

To contribute, please create a branch on the GitHub repository:
https://github.com/joeygrable94/KernBot.io

Created by Joey Grable
@JoeyGrable94
www.JoeyGrable.com
"""

# ---------------------------------------------------------------------------------------------------------
# DEV HELP DOCS
# https://docu.glyphsapp.com/
# https://ts-vanilla.readthedocs.io/en/latest/objects/List.html#list-item-cells

# PATH TO GLYPHS APP SCRIPT FILES
# ~/Library/Application Support/Glyphs/Scripts

# ---------------------------------------------------------------------------------------------------------
# IMPORTS
import os
import math
import json
import random
# & DEPENDENCIES
from vanilla import FloatingWindow, TextBox, List, RadioGroup, EditText, CheckBox, Button, VerticalLine, HorizontalLine
from vanilla.test.testAll import Test

# ---------------------------------------------------------------------------------------------------------
# GLOBAL DATA SETS

# return a dictionary of over 300,000 words from the Oxford English Dictionary
ALL_WORDS = []
OXFORD_SRC = "./resources/OxfordEnglishDictionary.txt"
with open(OXFORD_SRC) as json_words:
	ALL_WORDS = json.load(json_words)

# ---------------------------------------------------------------------------------------------------------
# GLOBAL FUNCTIONS

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
		if "@MMK_R_" in kGroupKey:
			if kGroupKey in g2g1:
				print("Double glyph in RIGHT kern groups", kGroupKey, kGroupGlyphs, g2g1[kGroupKey] )
			else:
				g2g1[kGroupKey] = kGroupGlyphs
		elif "@MMK_L_" in kGroupKey:
			if kGroupKey in g2g2:
				print("Double glyph in LEFT kern groups", kGroupKey, kGroupGlyphs, g2g2[kGroupKey] )
			else:
				g2g2[kGroupKey] = kGroupGlyphs
	# return tuple of Left and Right Kern Groups
	return g2g1, g2g2

# ---------------------------------------------------------------------------------------------------------
# KERNBOT CLASS
class KernBot:

	# Object Globals
	mtrcUnit = 4
	kernUnit = 4

	# constructor
	def __init__(self):
		w = 300 # window width
		h = 700 # window height
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
		self.initComplete = False

		# Highly Used Letter in Draw F(x)s
		self.spaceLetter = self._getCurrentLayerForLetter(cGlyph=self.font.glyphs["space"])

		# Vanilla Window Obj
		self.w = FloatingWindow(
			(50,100,w,h),
			"KernBot.io",
			autosaveName="com.joeygrable.kernbot.ui"
		)
		# Vanilla Element Styles
		KgValueStyle = dict(alignment="center", sizeStyle="regular")
		KgLabelStyle = dict(alignment="center", sizeStyle="mini")
		KgBtnStyles = dict(sizeStyle="regular")

		# -------------------------------------------------------------------------------------------------
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

		# -------------------------------------------------------------------------------------------------
		# populate List elements with initial font data
		self.leftKernKeysList = self._getCleanKernKeysAsList( self.glyph2Group1.keys() )
		self.leftKernKeysList.sort(key=lambda x:(x.islower(), x))
		self.rightKernKeysList = self._getCleanKernKeysAsList( self.glyph2Group2.keys() )
		self.rightKernKeysList.sort(key=lambda x:(x.islower(), x))

		# -------------------------------------------------------------------------------------------------
		# display buttons for outputing kern/glyph strings to screen
		# divider line
		self.w.listsHorizontalDvd = HorizontalLine( (m, tbh*3+lsh*2+m*2.5, w-m-m, 1) )
		# label text for this section of the app
		self.w.drawGlyphsActionsLabel = TextBox( (m, tbh*3+lsh*2+m*3.5, w-m-m, tbh), "Draw To Window Actions:" )
		# show current letter pair
		self.w.showCurrentLetterPair = Button( (m, tbh*4+lsh*2+m*3.5, col_1_of_2, bth), "current letter pair", callback=self.drawCurrentLetterPair, **KgBtnStyles )
		# label text for possible kern pairs list
		self.w.allPossibleLetterPairsLabel = TextBox( (m, tbh*5+lsh*2+m*4.25, col_1_of_2, tbh), "all possible letter pairs:", sizeStyle="mini" )
		# show all letter pairs with kern pair
		self.w.showAllLetterPairsWithKerning = List( (m, tbh*5+lsh*2+m*6, col_1_of_2, lsh*0.76), [], selectionCallback=self.drawSelectedAllPossibleLetterPairsWithKerning)
		# show a randomly selected word from list
		self.w.showRandomSelectedWordBtn = Button( (col_2_of_2, tbh*4+lsh*2+m*3.5, -m, bth), "show random word", callback=self.drawRandomSelectedMatchingWord )
		# label text for matching words list
		self.w.allMatchingWordsLabel  = TextBox( (col_2_of_2, tbh*5+lsh*2+m*4.25, -m, tbh), "all words conaining pair:", sizeStyle="mini" )
		# show list of all matching words
		self.w.showAllMatchingWords = List( (col_2_of_2, tbh*5+lsh*2+m*6, -m, lsh*0.76), [], selectionCallback=self.drawNewSelectedMatchingWord )
		# divider line
		self.w.drawGlyphsActionsHorizontalDvd = HorizontalLine( (m, -pb-m, w-m-m, 1) )

		# -------------------------------------------------------------------------------------------------
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
		self.w.LgRmBtnPlus = Button( (w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), "+", callback=self.leftGlyphRightMetricPlus, **KgBtnStyles )
		self.w.LgRmBtnMinus = Button( (w/5, -pb+tbh*1.75, (w/5)/2, bth), "-", callback=self.leftGlyphRightMetricMinus, **KgBtnStyles )
		# LEFT+RIGHT Kerning Pair Value
		self.w.KernPairBtnPlus = Button( (w/5+w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), "+", callback=self.glyphsKerningPairPlus, **KgBtnStyles )
		self.w.KernPairBtnMinus = Button( (w/5+w/5, -pb+tbh*1.75, (w/5)/2, bth), "-", callback=self.glyphsKerningPairMinus, **KgBtnStyles )
		# RIGHT Glyph LEFT Metric Value
		self.w.RgLmBtnPlus = Button( (-w/5-w/5+((w/5)/2), -pb+tbh*1.75, (w/5)/2, bth), "+", callback=self.rightGlyphLeftMetricPlus, **KgBtnStyles )
		self.w.RgLmBtnMinus = Button( (-w/5-w/5, -pb+tbh*1.75, (w/5)/2, bth), "-", callback=self.rightGlyphLeftMetricMinus, **KgBtnStyles )

		# -------------------------------------------------------------------------------------------------
		# addCallbacks and listen to CONSTANTS
		Glyphs.addCallback( self.documentWasSaved, DOCUMENTWASSAVED )
		Glyphs.addCallback( self.drawBackground, DRAWBACKGROUND )
		
		# load initial ALL_WORDS dataset
		self.allMatchingWords = []
		self.allPossibleGlyphPairs = []
		self.allPossibleLetterPairs = []
		self.currentLetterPair = None

		# run initializing functions
		self.w.bind("close", self.closeCleanUp) # call if window closes
		self.updating = False # Flag to avoid recursive Updating

		# fill the controls with real values (ie. Lists)
		self.updateAppUI()
		self.initComplete = True
		
		self.w.open() # open window
		self.w.makeKey() # focus window

	# ----------------------------------------------------------------------------------------------------
	# KERN BOT USER INTERFACE updater

	# update the app each time the user clicks one of the glyphs list
	def updateAppUI(self, sender=None):
		if not self.updating: # only act if not already updating
			self.updating = True # set updating Flag check
			
			# ----- GET LEFT Kern Keys -------------------------------------------------------------------
			# fill the left kern list with kern keys (unfiltered)
			self.w.leftKerns.set( self.leftKernKeysList )
			# select top item in list if item not already selected
			if not self.w.leftKerns.getSelection():
				self.w.leftKerns.setSelection([0])
				lk_KeySelect = 0
			else:
				lk_KeySelect = self.w.leftKerns.getSelection()[0]

			# ----- GET LEFT Glyphs w/ key ---------------------------------------------------------------
			lk_KeyFind = self.w.leftKerns[lk_KeySelect]
			lk_glyphs = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey("L", lk_KeyFind) )
			lk_glyphs.sort(key=lambda x:(x.islower(), x))
			# fill the left glyphs list with glyphs with matching kern key (unfiltered)
			self.w.leftGlyphsList.set( lk_glyphs )
			# select top item in list of item is not already selected
			if not self.w.leftGlyphsList.getSelection():
				self.w.leftGlyphsList.setSelection([0])
				leftCharSelect = 0
			else:
				leftCharSelect = int(self.w.leftGlyphsList.getSelection()[0])
			
			# ----- GET RIGHT Kern Keys -------------------------------------------------------------------
			# fill the right kern list with kern keys (unfiltered)
			self.w.rightKerns.set( self.rightKernKeysList )
			# select top item in list if item not already selected
			if not self.w.rightKerns.getSelection():
				self.w.rightKerns.setSelection([0])
				rk_KeySelect = 0
			else:
				rk_KeySelect = self.w.rightKerns.getSelection()[0]

			# ----- GET RIGHT Glyphs w/ key ---------------------------------------------------------------
			rk_KeyFind = self.w.rightKerns[rk_KeySelect]
			rk_glyphs = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey("R", rk_KeyFind) )
			rk_glyphs.sort(key=lambda x:(x.islower(), x))
			# fill the right glyphs list with glyphs with matching kern key (unfiltered)
			self.w.rightGlyphsList.set( rk_glyphs )
			# select top item in list of item is not already selected
			if not self.w.rightGlyphsList.getSelection():
				self.w.rightGlyphsList.setSelection([0])
				rightCharSelect = 0
			else:
				rightCharSelect = int(self.w.rightGlyphsList.getSelection()[0])

			# ----- LEFT Glyph ----------------------------------------------------------------------------
			leftGlyph = self._getGlyphFromCharStr( lk_glyphs[leftCharSelect] )
			leftGlyphLayer = leftGlyph.layers[self.selectedMaster.id]
			leftGlyphName = str(leftGlyph.name)
			leftGlyphUC = "U+%s" % leftGlyph.unicode
			leftGlyphRightSB = "+ %d" % leftGlyphLayer.RSB
			leftGlyphRightMetricKey = str(leftGlyph.rightMetricsKey) if not "None" == str(leftGlyph.rightMetricsKey) else "=%d" % leftGlyphLayer.RSB
			self.actvGlyphLeft = leftGlyph
			self.actvLeftKernKey = lk_KeyFind

			# ----- RIGHT Glyph ---------------------------------------------------------------------------
			rightGlyph = self._getGlyphFromCharStr( rk_glyphs[rightCharSelect] )
			rightGlyphLayer = rightGlyph.layers[self.selectedMaster.id]
			rightGlyphName = str(rightGlyph.name)
			rightGlyphUC = "U+%s" % rightGlyph.unicode
			rightGlyphLeftSB = "+ %d" % rightGlyphLayer.LSB
			rightGlyphLeftMetricKey = str(rightGlyph.leftMetricsKey) if not "None" == str(rightGlyph.leftMetricsKey) else "=%d" % rightGlyphLayer.LSB
			self.actvGlyphRight = rightGlyph
			self.actvRightKernKey = rk_KeyFind

			# ----- KERNING PAIR Information --------------------------------------------------------------
			kernPairKey = "%s | %s" % (lk_KeyFind, rk_KeyFind)
			kernAmt = Glyphs.font.kerningForPair( self.selectedMaster.id, "@MMK_L_%s" % lk_KeyFind, "@MMK_R_%s" % rk_KeyFind )
			if kernAmt > 100:
				kernAmt = 0
			if kernAmt > 0:
				kernPairVal = "+ %d" % kernAmt
			elif kernAmt == 0:
				kernPairVal = "= %d" % kernAmt
			elif kernAmt < 0:
				kernPairVal = "- %s" % str(kernAmt)[1:]

			# ----- SET Glyphs Metric & Kerning Information -----------------------------------------------
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

			# ----- UPDATE DATA SETS ----------------------------------------------------------------------
			# if initComplete = False, first time running updater
			if not self.initComplete:
				# set current letter pair
				self.currentLetterPair = leftGlyphName+rightGlyphName
				# set all possible glyph pairs
				self.allPossibleGlyphPairs = self._determineAllPossibleLetterPairsWithKerning()
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
					# set all possible glyph pairs
					self.allPossibleGlyphPairs = self._determineAllPossibleLetterPairsWithKerning()
					# recalc all matching words list
					self.allMatchingWords = self._determineMatchingWordsContaining( leftGlyphName, rightGlyphName )

			# ----- POPULATE ALL POSSIBLE LETTER PAIRS ----------------------------------------------------
			# check to see if all possble pairs already populated
			if not self.allPossibleGlyphPairs:
				self.allPossibleGlyphPairs = self._determineAllPossibleLetterPairsWithKerning()
			# make sure there's at least one possible letter pair
			else:
				# get a list of the glyph pairs and show in list
				self.allPossibleLetterPairs = self._getCleanPossibleGlyphPairs( self.allPossibleGlyphPairs )
				self.w.showAllLetterPairsWithKerning.set( self.allPossibleLetterPairs )

			# ----- POPULATE ALL MATCHING WORDS WITH LETTER PAIR ------------------------------------------
			# check to see if we've already searched for all matching words
			if not self.allMatchingWords:
				self.allMatchingWords = self._determineMatchingWordsContaining( leftGlyphName, rightGlyphName )
			# make sure there are at least some words to show
			else:
				# fill the list of matching words (unfiltered)
				self.w.showAllMatchingWords.set( self.allMatchingWords )

			# ----- Redraw & Finish Glyphs App updating ---------------------------------------------------
			Glyphs.redraw()
			# set Flag update complete
			self.updating = False

	# -----------------------------------------------------------------------------------------------------
	# CALLBACKS: GENERAL APP callbacks

	# every time the Glyphs App saves
	def documentWasSaved(self, passedobject):
		# update app for now
		self.updateAppUI()

	# every time the Glyphs App tries to reload
	def drawBackground(self, layer, info):
		# pass for now
		pass

	# when the window closes, unsubscribe from events
	def closeCleanUp(self, sender):
		Glyphs.removeCallback( self.documentWasSaved, DOCUMENTWASSAVED )
		Glyphs.removeCallback( self.drawBackground, DRAWBACKGROUND )

	# -----------------------------------------------------------------------------------------------------
	# CALLBACKS: UPDATE TAB to display strings of letters

	# open new tab with current letter pair
	def drawCurrentLetterPair(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# get layer of current glyphs
		currentLeftLetter = self._getCurrentLayerForLetter(side="left")
		currentRightLetter = self._getCurrentLayerForLetter(side="right")
		# make list of all letters to draw
		allLetters = [currentLeftLetter, currentRightLetter]
		# draw letters to current tab open
		self._drawGlyphLayersToScreen( allLetters )

	# open new tab with current letter pair in a WORD
	def drawNewSelectedMatchingWord(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# pull from all matching words list
		if self.allMatchingWords:
			# all letters to draw
			allLetters = []
			selectedWordLetters = None
			selectionMax = 5
			# select top item in list if item not already selected
			if not sender.getSelection():
				sender.setSelection([0])
				possibleMatchesSelection = [0]
			else:
				possibleMatchesSelection = sender.getSelection()[:selectionMax]
			# multiple selection
			if len(possibleMatchesSelection) > 1:
				# get subset of selected words
				for sWordIndex in possibleMatchesSelection:
					selectedWord = self.allMatchingWords[ sWordIndex ]
					selectedWordLetters = self._getWordLettersToDraw( selectedWord )
					# add all word letters to end of letters list, then add space
					allLetters += selectedWordLetters
					allLetters += [self.spaceLetter]

			# single selection
			else:
				# get the word selected to be drawn
				selectedWord = self.allMatchingWords[ possibleMatchesSelection[0] ]
				selectedWordLetters = self._getWordLettersToDraw( selectedWord )
				# add all word letters to end of letters list, then add space
				allLetters += selectedWordLetters
				allLetters += [self.spaceLetter]
			# draw letters to current tab open
			self._drawGlyphLayersToScreen( allLetters )

	# get a random word from list of all matching words and draw to tab
	def drawRandomSelectedMatchingWord(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# pull from all matching words list
		if self.allMatchingWords:
			# randomly get one word out of list
			selectedWord = random.choice(self.allMatchingWords)
			selectedWordLetters = self._getWordLettersToDraw(selectedWord)
			# draw letters to current tab open
			self._drawGlyphLayersToScreen( selectedWordLetters )
			# get & set cursor position to position of letter pair in word
			cursorPos = self._getCursorPositionOfPair( selectedWord )
			self._setCursorPositionOfPair(cursorPos)
	
	# open new tab with all possible letter combinations that use the current kerning pair 	
	def drawSelectedAllPossibleLetterPairsWithKerning(self, sender):
		# first make sure the UI state is current
		self.updateAppUI()
		# pull from all possible glyph pairs
		if self.allPossibleGlyphPairs:
			# all letters to draw
			allLetters = []
			# select top item in list if item not already selected
			if not sender.getSelection():
				sender.setSelection([0])
				possiblePairsSelection = [0]
			else:
				possiblePairsSelection = sender.getSelection()
			# multiple selection
			if len(possiblePairsSelection) > 1:
				# loop through each selected pair
				multipleGlyphPairs = self.allPossibleGlyphPairs[ possiblePairsSelection[0]:possiblePairsSelection[-1]+1 ]
				for gPair in multipleGlyphPairs:
					# add pair and space to all letters
					allLetters.append( self._getCurrentLayerForLetter(cGlyph=gPair[0]) )
					allLetters.append( self._getCurrentLayerForLetter(cGlyph=gPair[1]) )
					allLetters.append( self.spaceLetter )
			# single selection
			else:
				# get current pair glyph info
				snglPair = self.allPossibleGlyphPairs[ possiblePairsSelection[0] ]
				allLetters.append( self._getCurrentLayerForLetter(cGlyph=snglPair[0]) )
				allLetters.append( self._getCurrentLayerForLetter(cGlyph=snglPair[1]) )
				allLetters.append( self.spaceLetter )
			# draw letters to current tab open
			self._drawGlyphLayersToScreen( allLetters )

	# -----------------------------------------------------------------------------------------------------
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
		self._adjustLeftGlyphRightMetric(direction="-")
		self.updateAppUI()

	# LEFT GLYPH increase right metric multiplier
	def leftGlyphRightMetricPlus(self, sender):
		self._adjustLeftGlyphRightMetric(direction="+")
		self.updateAppUI()

	# RIGHT GLYPH decrease left metric multiplier
	def rightGlyphLeftMetricMinus(self, sender):
		self._adjustRightGlyphLeftMetric(direction="-")
		self.updateAppUI()

	# RIGHT GLYPH increase left metric multiplier
	def rightGlyphLeftMetricPlus(self, sender):
		self._adjustRightGlyphLeftMetric(direction="+")
		self.updateAppUI()

	# LEFT+RIGHT GLYPH decrease kerning for pair
	def glyphsKerningPairMinus(self, sender):
		self._adjustKerningForPair(direction="-")
		self.updateAppUI()

	# LEFT+RIGHT GLYPH increase kerning for pair
	def glyphsKerningPairPlus(self, sender):
		self._adjustKerningForPair(direction="+")
		self.updateAppUI()

	# -----------------------------------------------------------------------------------------------------
	# METRIC & KERNING METHODS ––> sets new glyph value

	# ADJUST left glyph right metric +/-
	def _adjustLeftGlyphRightMetric(self, direction="-"):
		# get left glyph layer information
		leftGlyphLayer = self.actvGlyphLeft.layers[self.selectedMaster.id]
		leftGlyphRMK = str(self.actvGlyphLeft.rightMetricsKey) if not None == self.actvGlyphLeft.rightMetricsKey else leftGlyphLayer.RSB
		# if is a mltp of another glyph
		if type(leftGlyphRMK) == str:
			# check metric key has mltp attached
			if "*" in leftGlyphRMK:
				leftGlyphMMltp = float(leftGlyphRMK.rsplit("*", 1)[-1])
			else:
				leftGlyphMMltp = 1.0
			# INCREASE OR DECREASE
			if direction == "-":
				NEWleftGlyphMMltp = leftGlyphMMltp - 0.05
			elif direction == "+":
				NEWleftGlyphMMltp = leftGlyphMMltp + 0.05
			NEWleftGlyphRMK = unicode((leftGlyphRMK.rsplit("*", 1)[0] + "*" + str(NEWleftGlyphMMltp))[1:], "UTF-8")
			# set new RMK for Glyph
			self.actvGlyphLeft.rightMetricsKey = self.actvGlyphLeft.rightMetricsKey.replace( leftGlyphRMK[1:], NEWleftGlyphRMK )
		# if is a multiple of the metric spacing unit
		elif type(leftGlyphRMK) == float:
			# INCREASE OR DECREASE
			if direction == "-":
				# set new RSB for Glyph
				leftGlyphLayer.RSB = leftGlyphLayer.RSB - self.mtrcUnit
			elif direction == "+":
				# set new RSB for Glyph
				leftGlyphLayer.RSB = leftGlyphLayer.RSB + self.mtrcUnit
		# sync metrics
		if self.SyncGlyphMetrics:
			for thisLeftGlyphLayer in self.actvGlyphLeft.layers:
				thisLeftGlyphLayer.syncMetrics()

	# ADJUST right glyph left metric +/-
	def _adjustRightGlyphLeftMetric(self, direction="-"):
		# get right glyph layer information
		rightGlyphLayer = self.actvGlyphRight.layers[self.selectedMaster.id]
		rightGlyphLMK = str(self.actvGlyphRight.leftMetricsKey) if not None == self.actvGlyphRight.leftMetricsKey else rightGlyphLayer.LSB
		# if is a mltp of another glyph
		if type(rightGlyphLMK) == str:
			# check metric key has mltp attached
			if "*" in rightGlyphLMK:
				rightGlyphMMltp = float(rightGlyphLMK.rsplit("*", 1)[-1])
			else:
				rightGlyphMMltp = 1.0
			# INCREASE OR DECREASE
			if direction == "-":
				NEWrightGlyphMMltp = rightGlyphMMltp - 0.05
			elif direction == "+":
				NEWrightGlyphMMltp = rightGlyphMMltp + 0.05
			NEWrightGlyphLMK = unicode((rightGlyphLMK.rsplit("*", 1)[0] + "*" + str(NEWrightGlyphMMltp))[1:], "UTF-8")
			# set new LMK for Glyph
			self.actvGlyphRight.leftMetricsKey = self.actvGlyphRight.leftMetricsKey.replace( rightGlyphLMK[1:], NEWrightGlyphLMK )
		# if is a multiple of the metric spacing unit
		elif type(rightGlyphLMK) == float:
			# INCREASE OR DECREASE
			if direction == "-":
				# set new LSB for Glyph
				rightGlyphLayer.LSB = rightGlyphLayer.LSB - self.mtrcUnit
			elif direction == "+":
				# set new LSB for Glyph
				rightGlyphLayer.LSB = rightGlyphLayer.LSB + self.mtrcUnit
		# sync metrics
		if self.SyncGlyphMetrics:
			for thisRightGlyphLayer in self.actvGlyphRight.layers:
				thisRightGlyphLayer.syncMetrics()

	# ADJUST kerning value for right+left glyph pair +/-
	def _adjustKerningForPair(self, direction="-"):
		# set kern direction
		if direction == "-":
			kdVal = -1
		elif direction == "+":
			kdVal = 1
		# get current kerning
		kpVal = Glyphs.font.kerningForPair( self.selectedMaster.id, "@MMK_L_%s" % self.actvLeftKernKey, "@MMK_R_%s" % self.actvRightKernKey )
		if kpVal > 100:
			kpVal = -1
		# calculate the next kernunit interval +/-
		NEWkpVal = float(int(round(kpVal/self.kernUnit + kdVal ))*self.kernUnit)
		# set new value for kern pair
		Glyphs.font.setKerningForPair( self.selectedMaster.id, "@MMK_L_%s" % self.actvLeftKernKey, "@MMK_R_%s" % self.actvRightKernKey, NEWkpVal )

	# -----------------------------------------------------------------------------------------------------
	# UTILITY METHODS ——> return something
	
	# returns a list of all glyphs that has the desired kerning group on the specified side
	def _getGlyphsWithKernKey(self, side, searchForKey):
		for kGroup in self.kernGroups.keys():
			findMMK = "@MMK_"+side+"_"+searchForKey
			if findMMK in kGroup:
				return self.kernGroups[kGroup]

	# returns the kern key letter as a string (from a unicode u"@MMK_L_v" string ——> "v")
	def _getCleanKernKeysAsList(self, uListItems):
		cleanList = []
		for lItem in uListItems:
			cleanList.append( str(lItem.rsplit("_", 1)[-1]) )
		return cleanList

	# returns a list of letter-pairs give a list of glyph pairs
	def _getCleanPossibleGlyphPairs(self, gListItems):
		cleanList = []
		for gItem in gListItems:
			cleanList.append( str(gItem[0].name+gItem[1].name) )
		return cleanList

	# returns s list of letter names given a list of GSGlyph obj
	def _getGlyphNamesListFromObj(self, gListItems):
		cleanList = []
		for gItem in gListItems:
			cleanList.append( str(gItem.name) )
		return cleanList

	# returns a single glyph Obj given a specific letter
	def _getGlyphFromCharStr(self, letter):
		for glyph in Glyphs.font.glyphs:
			if glyph.name == letter:
				return glyph

	# returns the current layer of the active left glyph
	def _getCurrentLayerForLetter(self, side="left", cGlyph=None):
		# if want a specific glyph
		if not None == cGlyph:
			cGlyphLayer = cGlyph.layers[ self.selectedMaster.id ]
		else:
			# default get the current active left glyph
			if side == "left":
				cGlyphLayer = self.actvGlyphLeft.layers[ self.selectedMaster.id ]
			# otherwise get the current active right glyph
			elif side == "right":
				cGlyphLayer = self.actvGlyphRight.layers[ self.selectedMaster.id ]
		# return the letter
		return cGlyphLayer

	# search for a word in ALL_WORDS list containing chars Left and Right
	def _determineMatchingWordsContaining(self, cLeft, cRight):
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
					# check both matches exist
					if wordSet1 and wordSet2:
						# make NEW word camelCase ——> "camel"+"Case" = word1 + word2.uppercase()
						newWord = str(random.choice(wordSet1)) + str(random.choice(wordSet2)).capitalize()
						foundWords.append( newWord )
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
			print("improper C1 or C2 values")
		# return random word that matches input
		return foundWords

	# iterate through list of glyph names in word and
	# return list of all letters glyph layer to draw
	def _getWordLettersToDraw(self, inputWord):
		# format all chars glyphs in word
		allChars = []
		for currentChar in inputWord:
			allChars.append( self.font.glyphs[currentChar] )
		# get all letter glyph layers to draw
		allLetters = []
		for cGlyph in allChars:
			# get current glyph layer
			currentLetter = self._getCurrentLayerForLetter(cGlyph=cGlyph)
			allLetters.append( currentLetter )
		# return the list of all letter layers to draw
		return allLetters

	# return a list of all possible combinations of the current left/right kern key pair
	def _determineAllPossibleLetterPairsWithKerning(self):
		# gather char information
		allLeftChars = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey("L", self.actvLeftKernKey) )
		allLeftChars.sort(key=lambda x:(x.islower(), x))
		allRightChars = self._getGlyphNamesListFromObj( self._getGlyphsWithKernKey("R", self.actvRightKernKey) )
		allRightChars.sort(key=lambda x:(x.islower(), x))
		# make list of all possible chars
		allCombinations = []
		for leftChar in allLeftChars:
			for rightChar in allRightChars:
				allCombinations.append( (self.font.glyphs[leftChar], self.font.glyphs[rightChar]) )
		# return list of all pairs
		return allCombinations

	# -----------------------------------------------------------------------------------------------------
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
		Glyphs.font.currentTab.textCursor = posIndex
		return True

	# -----------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------
# RUN KERNBOT.IO
KernBot()