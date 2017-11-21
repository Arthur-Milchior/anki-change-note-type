# -*- coding: utf-8 -*-
#Copyright: Arthur Milchior arthur@milchior.fr
#License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import addHook
from aqt import mw
from aqt.utils import tooltip
from anki.utils import timestampID
import anki.notes
from anki.models import ModelManager

def copyCard(nid):
        """Return the NID of a new card with same field, cards,..."""
        # Copy notes
        note = mw.col.getNote(nid)
        model = note._model
        
        # Create new note
        note_copy = anki.notes.Note(mw.col,model=model)
        # Copy tags and fields (all model fields) from original note
        note_copy.tags = note.tags
        note_copy.fields = note.fields

        # Refresh note and add to database
        note_copy.flush()
        mw.col.addNote(note_copy)

        cards_copy= note_copy.cards()
        cards= note.cards()
        for card_copy in cards_copy:
            ord = card_copy.ord
            (cid, ) = mw.col.db.first("select id from cards where nid = ? and ord = ?",nid, ord)
            card = mw.col.getCard(cid)
            card.id=card_copy.id
            card.nid=card_copy.nid
            card.flush()
        return card_copy.nid


def oldChange(self, m, nids, newModel, fmap, cmap):
        """Change the model of the nodes in nids to newModel

        currently, fmap and cmap are null only for tests.

        keyword arguments
        m -- the previous model of the notes
        nids -- a list of id of notes whose model is m
        newModel -- the model to which the cards must be converted
        fmap -- the dictionnary sending to each fields'ord of the old model a field'ord of the new model
        cmap -- the dictionnary sending to each card type's ord of the old model a card type's ord of the new model
        """
        assert newModel['id'] == m['id'] or (fmap and cmap)
        if fmap:
            self._changeNotes(nids, newModel, fmap)
        if cmap:
            self._changeCards(nids, m, newModel, cmap)
        self.col.genCards(nids)

def newChange(self,m,nids,newModel,fmap,cmap):
    new_nids=map(copyCard,nids)
    oldChange(self,m,new_nids,newModel,fmap,cmap)
    self.col.remNotes(nids)

ModelManager.change =newChange
