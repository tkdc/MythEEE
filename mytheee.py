#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

MythEEE
My tiny house electronic & entertainment empire

Copyright (C) 2018 Thomas Katemann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt4 import QtGui, QtCore
import sys
import ctypes
import psutil
from mytheee2core import CoreIf

__title__ = 'MythEEE'
__version__ = '1.1.0'
__author__ = 'Thomas Katemann'
__copyright__ = 'Copyright (C) 2018 Thomas Katemann'
__license__ = 'GPLv3'

print('--- MYthEEE Init ---')
print('PyQt4')
print('python ver: ' + sys.version)


class GuiProps(object):
    def __init__(self):

        # Gui title
        self.gui_title = __title__

        # Gui settings
        self.gui_geometry = [0, 20, 320, 320]
        self.gui_fr_ena = [True, True, True]

        # frame fixed height
        self.gui_fr_fix_height = [240, None, 240]

        # basic font definition
        self.gui_baseFont = QtGui.QFont('Arial', 11)
        self.gui_smallFont = QtGui.QFont('Arial', 10)
        self.gui_baseFont.setBold(False)

        # text string config
        self.gui_ts_height = [20, 40, 70, 20, 20, 30]
        self.gui_ts_width = [70, 60, 200, None, None, None]
        self.gui_ts_wrap = [False, True, True, False, False, False]
        self.gui_ts_font = [self.gui_baseFont, self.gui_baseFont, self.gui_smallFont,
                            self.gui_baseFont, self.gui_baseFont, self.gui_baseFont]
        self.gui_ts_align = [QtCore.Qt.AlignTop, QtCore.Qt.AlignTop, QtCore.Qt.AlignHCenter,
                             QtCore.Qt.AlignHCenter, QtCore.Qt.AlignLeft, QtCore.Qt.AlignBottom]

        # button config
        self.gui_pb_height = [30, 30, 30]
        self.gui_pb_width = [100, 80, 60]

        # check box
        self.gui_cb_width = [80, 75]

        # radio button
        self.gui_rb_width = [200]

        # select box
        self.gui_sb_height = [30, 30, 30, 30]
        self.gui_sb_width = [60, 120, None, 80]

        # text box
        self.gui_tx_height = [30, 30]
        self.gui_tx_width = [60, 80]


class MYthEEE(QtGui.QApplication):
    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)

        str_icon = "/usr/share/icons/gnome/scalable/devices/audio-speakers-symbolic.svg"
        self.setWindowIcon(QtGui.QIcon(str_icon))

        # check for open process
        self.str_proc_name = "mytheee"
        for proc in psutil.process_iter():
            if proc.name() == self.str_proc_name:
                proc.kill()

        # rename process
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
        libc.prctl(15, self.str_proc_name.encode(), 0, 0, 0)

        # init gui layout
        self.sGuiView = GuiView()
        self.sGuiView.idx_actv_zone_prev = 0
        # init core interface
        self.CoreIf = CoreIf(self.sGuiView)
        # set connections
        self.init_connect()
        # show gui
        self.sGuiView.show()
        self.sGuiView.set_frames(0)

        print('--- MYthEEE Init Finished ---')

    def close_event(self):
        print("Close Application")
        for proc in psutil.process_iter():
            if proc.name() == self.str_proc_name:
                print(proc)
                proc.kill()

    def select_zone(self, idx_check):
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if self.sGuiView.idx_actv_zone_prev == idx_actv_zone:
            # zone select equal
            if idx_check == idx_actv_zone:
                if not self.sGuiView.MAIN_CB_Z[idx_actv_zone].isChecked():
                    self.sGuiView.MAIN_CB_Z[idx_actv_zone].setChecked(1)
            else:
                if self.sGuiView.MAIN_CB_Z[idx_check].isChecked():
                    self.CoreIf.gui_select_zone('Join', idx_actv_zone, idx_check)
                else:
                    self.CoreIf.gui_select_zone('UnJoin', idx_actv_zone, idx_check)
        else:
            # zone select not equal
            if self.sGuiView.MAIN_CB_Z[idx_actv_zone].isChecked():
                self.CoreIf.gui_select_zone('CngCo', 0, idx_actv_zone)
            else:
                self.CoreIf.gui_select_zone('SwtZone', 0, idx_actv_zone)
                self.sGuiView.MAIN_CB_Z[idx_actv_zone].setChecked(1)
                self.sGuiView.MAIN_CB_Z[self.sGuiView.idx_actv_zone_prev].setChecked(0)
            self.sGuiView.idx_actv_zone_prev = idx_actv_zone

    def init_connect(self):

        # button actions
        self.sGuiView.MAIN_PB_NEXT.clicked.connect(lambda: self.CoreIf.gui_set_track_next('Next'))
        self.sGuiView.MAIN_PB_PREV.clicked.connect(lambda: self.CoreIf.gui_set_track_next('Prev'))
        self.sGuiView.MAIN_PB_SLEEP.clicked.connect(lambda: self.CoreIf.gui_set_sleep_time())

        self.sGuiView.MAIN_CB_Z[0].clicked.connect(lambda: self.select_zone(0))
        self.sGuiView.MAIN_CB_Z[1].clicked.connect(lambda: self.select_zone(1))
        self.sGuiView.MAIN_RB_Z[0].clicked.connect(lambda: self.select_zone(0))
        self.sGuiView.MAIN_RB_Z[1].clicked.connect(lambda: self.select_zone(1))

        self.sGuiView.MAIN_CB_SHUFFLE.clicked.connect(lambda: self.CoreIf.gui_set_play_mode())
        self.sGuiView.MAIN_TX_LIST.itemDoubleClicked.connect(lambda: self.CoreIf.gui_select_track_idx())
        self.sGuiView.MAIN_SB_MDBTYP.currentIndexChanged.connect(lambda: self.CoreIf.gui_mudb_sel_idx())

        self.sGuiView.MAIN_PB_ADD_PL.clicked.connect(lambda: self.CoreIf.gui_add_mudb_item())
        self.sGuiView.MAIN_PB_REM_PL.clicked.connect(lambda: self.CoreIf.gui_rem_mudb_item())

        self.sGuiView.MAIN_PB_FHEM_SWTON.clicked.connect(lambda: self.CoreIf.gui_fhem_swt('on'))
        self.sGuiView.MAIN_PB_FHEM_SWTOFF.clicked.connect(lambda: self.CoreIf.gui_fhem_swt('off'))
        self.sGuiView.MAIN_PB_FHEM_TEMPD.clicked.connect(lambda: self.CoreIf.gui_fhem_set_temp())

        self.aboutToQuit.connect(self.close_event)

        self.sGuiView.MAIN_ST_VOL[0].installEventFilter(self)
        self.sGuiView.MAIN_ST_VOL[1].installEventFilter(self)
        self.sGuiView.MAIN_ST_BAL[0].installEventFilter(self)
        self.sGuiView.MAIN_ST_INFO[0].installEventFilter(self)
        self.sGuiView.MAIN_ST_INFO[1].installEventFilter(self)
        self.sGuiView.MAIN_TX_LIST.installEventFilter(self)

    def eventFilter(self, widget, event):
        cur_wdg_name = str(widget.windowTitle())

        if event.type() == QtCore.QEvent.Wheel:
            # print('GV-Wheel' + str(event.delta()))
            direction = event.delta()
            if direction > 0:
                if cur_wdg_name == 'MAIN_ST_VOL_0':
                    self.CoreIf.gui_call_vol(0, 'up')
                if cur_wdg_name == 'MAIN_ST_VOL_1':
                    self.CoreIf.gui_call_vol(1, 'up')
                elif cur_wdg_name == 'MAIN_ST_BAL_0':
                    self.CoreIf.gui_call_bal(0, 'right')
            else:
                if cur_wdg_name == 'MAIN_ST_VOL_0':
                    self.CoreIf.gui_call_vol(0, 'dn')
                if cur_wdg_name == 'MAIN_ST_VOL_1':
                    self.CoreIf.gui_call_vol(1, 'dn')
                elif cur_wdg_name == 'MAIN_ST_BAL_0':
                    self.CoreIf.gui_call_bal(0, 'left')

            return False
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if cur_wdg_name == 'MAIN_ST_INFO_0':
                self.CoreIf.gui_play_stop(0)
            if cur_wdg_name == 'MAIN_ST_INFO_1':
                self.CoreIf.gui_play_stop(1)
            return False
        elif event.type() == QtCore.QEvent.KeyRelease:
            if cur_wdg_name == 'MAIN_TX_LIST':
                if event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
                    self.CoreIf.gui_select_track_idx()
            return False
        else:
            return False


# init gui main window
class GuiView(QtGui.QMainWindow):
    # definition of own signals
    signalSelectFirstTableRow = QtCore.pyqtSignal()
    signalGuiClosed = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # get gui data and specification        
        self.s_gui_props = GuiProps()

        # Set gui default size and position
        self.setGeometry(self.s_gui_props.gui_geometry[0],
                         self.s_gui_props.gui_geometry[1],
                         self.s_gui_props.gui_geometry[2],
                         self.s_gui_props.gui_geometry[3])
        self.geometry()
        self.setFixedWidth(self.s_gui_props.gui_geometry[2])

        # set gui title
        self.setWindowTitle(self.s_gui_props.gui_title)

        # create a main widget with grid layout
        self.MAIN_FR_01 = QtGui.QGroupBox()
        self.MAIN_FR_02 = QtGui.QGroupBox()
        self.MAIN_FR_03 = QtGui.QGroupBox()
        self.MAIN_GRID = QtGui.QGridLayout()
        self.MAIN_GRID.addWidget(self.MAIN_FR_01, 1, 0, 1, 3)
        self.MAIN_GRID.addWidget(self.MAIN_FR_02, 2, 0, 1, 3)
        self.MAIN_GRID.addWidget(self.MAIN_FR_03, 3, 0, 1, 3)
        self.MAIN_WIDGET = QtGui.QWidget()
        self.MAIN_WIDGET.setLayout(self.MAIN_GRID)
        # set main widget as central widget of the main window
        self.setCentralWidget(self.MAIN_WIDGET)
        self.MAIN_WIDGET.setMaximumWidth(self.s_gui_props.gui_geometry[2])

        # GUI Elements
        # frame 1 elements
        self.MAIN_ST_VOL = [GuiTextString(0, self.s_gui_props, 'MAIN_ST_VOL_0', 'VOL:', 'Scroll to change the volume'),
                            GuiTextString(0, self.s_gui_props, 'MAIN_ST_VOL_1', 'VOL:', 'Scroll to change the volume')]
        # Balance
        self.MAIN_ST_BAL = [GuiTextString(0, self.s_gui_props, 'MAIN_ST_BAL_0', 'BAL:', 'Scroll to change the balance'),
                            GuiTextString(0, self.s_gui_props, 'MAIN_ST_BAL_1', 'BAL:', 'Scroll to change the balance')]
        # info play status
        self.MAIN_ST_INFO = [GuiTextString(1, self.s_gui_props, 'MAIN_ST_INFO_0', '', 'Click to start/stop playing'),
                             GuiTextString(1, self.s_gui_props, 'MAIN_ST_INFO_1', '', 'Click to start/stop playing')]
        # track display
        self.MAIN_ST_TRACK = [GuiTextString(2, self.s_gui_props, 'MAIN_ST_TRACK_0'),
                              GuiTextString(2, self.s_gui_props, 'MAIN_ST_TRACK_1')]
        self.MAIN_ST_TRACK[0].setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.MAIN_ST_TRACK[1].setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        # Button select player
        self.MAIN_CB_Z = [GuiCheckBox(1, self.s_gui_props, 'LIV1', 'Check for zone grouping', True),
                          GuiCheckBox(1, self.s_gui_props, 'KIT1', 'Check for zone grouping', False)]
        self.MAIN_RB_Z = [GuiRadioBut(0, self.s_gui_props, 'LIV1', 'Select coordinator zone', True),
                          GuiRadioBut(0, self.s_gui_props, 'KIT1', 'Select coordinator zone', False)]

        # frame 1 grid layout
        # addWidget (QWidget, int row, int column, int rowSpan, int columnSpan, Qt.Alignment alignment = 0)
        self.MAIN_GRID_FR01 = QtGui.QGridLayout()
        self.MAIN_GRID_FR01.setSpacing(0)
        self.MAIN_GRID_FR01.setContentsMargins = 0
        self.MAIN_GRID_FR01.setColumnMinimumWidth(0, 70)

        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_TRACK[0], 1, 1, 4, 4)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_TRACK[1], 6, 1, 4, 4)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_VOL[0], 1, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_BAL[0], 2, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_VOL[1], 6, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_INFO[0], 3, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_CB_Z[0], 0, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_CB_Z[1], 5, 0)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_RB_Z[0], 0, 1, 1, 4)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_RB_Z[1], 5, 1, 1, 4)
        self.MAIN_GRID_FR01.addWidget(self.MAIN_ST_INFO[1], 7, 0)

        # FRAME 01
        self.MAIN_FR_01.setVisible(self.s_gui_props.gui_fr_ena[0])
        self.MAIN_FR_01.setStyleSheet("QGroupBox { border: 1px solid;}")
        if self.s_gui_props.gui_fr_fix_height[0] is not None:
            self.MAIN_FR_01.setFixedHeight(self.s_gui_props.gui_fr_fix_height[0])
        fr_obj = getattr(self, 'MAIN_GRID_FR01')
        self.MAIN_FR_01.setLayout(fr_obj)

        # frame 2 elements
        self.MAIN_SB_MDBTYP = GuiSelectBox(3, self.s_gui_props, None, 'Select play source type')
        self.MAIN_SB_MDBITM = GuiSelectBox(2, self.s_gui_props, None, 'Select item of play source type')
        self.MAIN_PB_NEXT = GuiButton(1, self.s_gui_props, 'NEXT', 'Click for next track')
        self.MAIN_PB_PREV = GuiButton(1, self.s_gui_props, 'PREV', 'Click for previous track')
        self.MAIN_PB_ADD_PL = GuiButton(1, self.s_gui_props, 'ADD', 'Play selected source item or add to playlist')
        self.MAIN_PB_REM_PL = GuiButton(1, self.s_gui_props, 'REM', 'Remove tracks from playlist')
        self.MAIN_CB_SHUFFLE = GuiCheckBox(0, self.s_gui_props, 'Shuffle', 'Set shuffle or normal mode',False)
        self.MAIN_ST_NUMTRCK = GuiTextString(3, self.s_gui_props, 'NumTrq', '', 'Number of tracks in playlist')

        self.MAIN_PB_SLEEP = GuiButton(1, self.s_gui_props, 'Sleep', 'Activate sleep timer')
        self.MAIN_TX_SLEEP = GuiTextBox(1, self.s_gui_props, '60', 'Define sleep time in minutes')
        self.MAIN_ST_SLEEP = GuiTextString(3, self.s_gui_props, 'SlpTm', '', 'Sleep timer status')

        self.MAIN_TX_LIST = GuiListBox('MAIN_TX_LIST')

        # FRAME 2 grid layout
        # addWidget (QWidget, int row, int column, int rowSpan, int columnSpan, Qt.Alignment alignment = 0)
        self.MAIN_GRID_FR02 = QtGui.QGridLayout()
        self.MAIN_GRID_FR02.setSpacing(2)
        self.MAIN_GRID_FR02.setContentsMargins = 0
        self.MAIN_GRID_FR02.setColumnMinimumWidth(0, 80)
        self.MAIN_GRID_FR02.setColumnMinimumWidth(4, 80)

        self.MAIN_GRID_FR02.addWidget(self.MAIN_PB_NEXT, 4, 4)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_CB_SHUFFLE, 2, 1, 1, 3, QtCore.Qt.AlignHCenter)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_PB_PREV, 4, 0)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_TX_LIST, 5, 0, 1, 5)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_PB_ADD_PL, 2, 0)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_ST_NUMTRCK, 4, 1, 1, 3, QtCore.Qt.AlignHCenter)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_PB_REM_PL, 2, 4)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_SB_MDBTYP, 1, 0)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_SB_MDBITM, 1, 1, 1, 4)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_PB_SLEEP, 9, 0)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_ST_SLEEP, 9, 1, 1, 3, QtCore.Qt.AlignHCenter)
        self.MAIN_GRID_FR02.addWidget(self.MAIN_TX_SLEEP, 9, 4)

        # FRAME 02
        self.MAIN_FR_02.setVisible(self.s_gui_props.gui_fr_ena[1])
        self.MAIN_FR_02.setStyleSheet("QGroupBox { border: 1px solid;}")
        if self.s_gui_props.gui_fr_fix_height[1] is not None:
            self.MAIN_FR_02.setFixedHeight(self.s_gui_props.gui_fr_fix_height[1])
        fr_obj = getattr(self, 'MAIN_GRID_FR02')
        self.MAIN_FR_02.setLayout(fr_obj)

        # frame 3 elements
        self.MAIN_ST_FHEM = GuiTextString(4, self.s_gui_props, 'FHEM')
        self.MAIN_ST_FHEM_SWT_TIT = GuiTextString(4, self.s_gui_props, '--- Switch ---')
        self.MAIN_SB_FHEM_SWT = GuiSelectBox(2, self.s_gui_props, None, 'Select switch to control')
        self.MAIN_PB_FHEM_SWTON = GuiButton(2, self.s_gui_props, 'ON', 'Set selected switch on')
        self.MAIN_PB_FHEM_SWTOFF = GuiButton(2, self.s_gui_props, 'OFF', 'Set selected switch off')

        self.MAIN_SB_FHEM_TEMP = GuiSelectBox(2, self.s_gui_props, None, 'Select room thermostat to control')
        self.MAIN_SB_FHEM_TEMPD = GuiSelectBox(0, self.s_gui_props, [str(x) for x in list(range(15, 25))],
                                               'Select desired temperature')
        self.MAIN_PB_FHEM_TEMPD = GuiButton(2, self.s_gui_props, 'SET', 'Set desired temperature')

        self.MAIN_ST_FHEM_R_TIT = GuiTextString(5, self.s_gui_props, '--- Temperature ---')
        self.MAIN_ST_FHEM_R = [GuiTextString(3, self.s_gui_props, 'Liv'), GuiTextString(3, self.s_gui_props, 'Bath'),
                            GuiTextString(3, self.s_gui_props, 'Kit'), GuiTextString(3, self.s_gui_props, 'Outdoor')]
        self.MAIN_ST_FHEM_R1 = [GuiTextString(4, self.s_gui_props, 'Liv'), GuiTextString(4, self.s_gui_props, 'Bath'),
                            GuiTextString(4, self.s_gui_props, 'Kit'), GuiTextString(4, self.s_gui_props, 'Outdoor')]
        self.MAIN_ST_FHEM_R2 = [GuiTextString(4, self.s_gui_props, 'Liv'), GuiTextString(4, self.s_gui_props, 'Bath'),
                            GuiTextString(4, self.s_gui_props, 'Kit'), GuiTextString(4, self.s_gui_props, 'Outdoor')]
        self.MAIN_ST_FHEM_R3 = [GuiTextString(4, self.s_gui_props, 'Liv'), GuiTextString(4, self.s_gui_props, 'Bath'),
                            GuiTextString(4, self.s_gui_props, 'Kit'), GuiTextString(4, self.s_gui_props, 'Outdoor')]
        # frame 3 grid layout
        # addWidget (QWidget, int row, int column, int rowSpan, int columnSpan, Qt.Alignment alignment = 0)
        self.MAIN_GRID_FR03 = QtGui.QGridLayout()
        self.MAIN_GRID_FR03.setSpacing(2)
        self.MAIN_GRID_FR03.setContentsMargins = 0
        self.MAIN_GRID_FR03.setColumnMinimumWidth(0, 60)
        self.MAIN_GRID_FR03.setColumnMinimumWidth(1, 40)
        self.MAIN_GRID_FR03.setColumnMinimumWidth(2, 60)
        self.MAIN_GRID_FR03.setColumnMinimumWidth(3, 60)
        self.MAIN_GRID_FR03.setColumnMinimumWidth(4, 60)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_SWT_TIT, 10, 0, 1, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM, 10, 4, 1, 1, QtCore.Qt.AlignRight)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_PB_FHEM_SWTON, 11, 0)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_SB_FHEM_SWT, 11, 1, 1, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_PB_FHEM_SWTOFF, 11, 4, QtCore.Qt.AlignRight)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R_TIT, 12, 0, 1, 5)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_SB_FHEM_TEMP, 13, 0, 1, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_SB_FHEM_TEMPD, 13, 3, 1, 1, QtCore.Qt.AlignHCenter)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_PB_FHEM_TEMPD, 13, 4, QtCore.Qt.AlignRight)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R[0], 14, 0, 1, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R[1], 15, 0, 1, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R[2], 16, 0, 1, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R[3], 17, 0, 1, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R1[0], 14, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R1[1], 15, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R1[2], 16, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R1[3], 17, 2)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R2[0], 14, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R2[1], 15, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R2[2], 16, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R2[3], 17, 3)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R3[0], 14, 4)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R3[1], 15, 4)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R3[2], 16, 4)
        self.MAIN_GRID_FR03.addWidget(self.MAIN_ST_FHEM_R3[3], 17, 4)
        # FRAME 03
        self.MAIN_FR_03.setVisible(self.s_gui_props.gui_fr_ena[2])
        self.MAIN_FR_03.setStyleSheet("QGroupBox { border: 1px solid;}")
        if self.s_gui_props.gui_fr_fix_height[2] is not None:
            self.MAIN_FR_03.setFixedHeight(self.s_gui_props.gui_fr_fix_height[2])
        fr_obj = getattr(self, 'MAIN_GRID_FR03')
        self.MAIN_FR_03.setLayout(fr_obj)

        # Menu bar
        self.menu_fr01 = QtGui.QAction("&Play Status", self, checkable=True)
        self.menu_fr01.setStatusTip('Set Play Status visible')
        self.menu_fr01.isChecked()
        self.menu_fr01.triggered.connect(lambda: self.set_frames(1))

        self.menu_fr02 = QtGui.QAction("&Play Select", self, checkable=True)
        self.menu_fr02.setStatusTip('Set Play Select visible')
        self.menu_fr02.isChecked()
        self.menu_fr02.triggered.connect(lambda: self.set_frames(2))

        self.menu_fr03 = QtGui.QAction("&Fhem Control", self, checkable=True)
        self.menu_fr03.setStatusTip('Set Fhem Control visible')
        self.menu_fr03.isChecked()
        self.menu_fr03.triggered.connect(lambda: self.set_frames(3))

        self.menu_about = QtGui.QAction("&About", self)
        self.menu_about.setStatusTip('About')
        self.menu_about.triggered.connect(lambda: self.show_about_dialog())

        self.statusBar()
        menu_main = self.menuBar()
        menu_sub2 = menu_main.addMenu('&Main')
        menu_sub2.addAction(self.menu_about)
        menu_sub1 = menu_main.addMenu('&View')
        menu_sub1.addAction(self.menu_fr01)
        menu_sub1.addAction(self.menu_fr02)
        menu_sub1.addAction(self.menu_fr03)

        # set default
        if self.s_gui_props.gui_fr_ena[0]:
            self.menu_fr01.setChecked(1)
        if self.s_gui_props.gui_fr_ena[1]:
            self.menu_fr02.setChecked(1)
        if self.s_gui_props.gui_fr_ena[2]:
            self.menu_fr03.setChecked(1)

    def set_frames(self, idx_frame, idx_state=2):
        """

        :param idx_frame:
        """
        if idx_frame > 0:
            str_frame = 'MAIN_FR_0' + str(idx_frame)
            str_menu = 'menu_fr0' + str(idx_frame)

            # visibility of frames
            if idx_state == -1:  # set unavailable
                self.__getattribute__(str_menu).setChecked(False)
                self.__getattribute__(str_menu).setDisabled(True)
                self.__getattribute__(str_frame).setVisible(False)
            elif idx_state == 0:  # set available but disabled
                self.__getattribute__(str_menu).setEnabled(True)
                self.__getattribute__(str_menu).setChecked(False)
                self.__getattribute__(str_frame).setVisible(False)
            elif idx_state == 1:  # set available and enabled
                self.__getattribute__(str_menu).setEnabled(True)
                self.__getattribute__(str_menu).setChecked(True)
                self.__getattribute__(str_frame).setVisible(True)
            elif idx_state == 2:  # change state by gui
                b_is_actv = self.__getattribute__(str_menu).isChecked()
                self.__getattribute__(str_frame).setVisible(b_is_actv)

        b_fr1_is_vis = self.MAIN_FR_01.isVisible()
        b_fr2_is_vis = self.MAIN_FR_02.isVisible()
        b_fr3_is_vis = self.MAIN_FR_03.isVisible()

        if b_fr1_is_vis:
            if self.s_gui_props.gui_fr_fix_height[0] is None:
                d_fr1_h_req = 2000
            else:
                d_fr1_h_req = self.s_gui_props.gui_fr_fix_height[0]
        else:
            d_fr1_h_req = 0

        if b_fr2_is_vis:
            if self.s_gui_props.gui_fr_fix_height[1] is None:
                d_fr2_h_req = 2000
            else:
                d_fr2_h_req = self.s_gui_props.gui_fr_fix_height[1]
        else:
            d_fr2_h_req = 0

        if b_fr3_is_vis:
            if self.s_gui_props.gui_fr_fix_height[2] is None:
                d_fr3_h_req = 2000
            else:
                d_fr3_h_req = self.s_gui_props.gui_fr_fix_height[2]
        else:
            d_fr3_h_req = 0

        # adapt gui height
        d_tot_h_req = d_fr1_h_req + d_fr2_h_req + d_fr3_h_req
        self.setMaximumHeight(d_tot_h_req)

    def get_actv_zone(self):
        """

        :return:
        """
        if self.MAIN_RB_Z[0].isChecked():
            return 0
        elif self.MAIN_RB_Z[1].isChecked():
            return 1

    def set_avail_zone(self, a_zone_avail):
        """

        :param a_zone_avail:
        """
        for idx in range(0, len(self.MAIN_CB_Z)):
            if a_zone_avail[idx]:
                self.MAIN_CB_Z[idx].setEnabled(1)
                self.MAIN_RB_Z[idx].setEnabled(1)
                self.MAIN_RB_Z[idx].dispval = 'Available'
            else:
                self.MAIN_CB_Z[idx].setDisabled(1)
                self.MAIN_RB_Z[idx].setDisabled(1)
                self.MAIN_RB_Z[idx].dispval = 'Not Available'

    def show_about_dialog(self):
        """

        """
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)

        msg.setText(__title__ + '\nVersion: ' + __version__)
        msg.setInformativeText(__copyright__ + '\n'
                                + '\n'
                                + 'This program is free software: you can redistribute it and/or modify \n'
                                + 'it under the terms of the GNU General Public License as published by \n'
                                + 'the Free Software Foundation, either version 3 of the License, or \n'
                                + '(at your option) any later version. \n'
                                + '\n'
                                + 'This program is distributed in the hope that it will be useful, \n'
                                + 'but WITHOUT ANY WARRANTY; without even the implied warranty of \n'
                                + 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  \n'
                                + 'See the GNU General Public License for more details. \n')
        msg.setWindowTitle("About")

        msg.setFont(self.s_gui_props.gui_smallFont)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.setGeometry(20, 100, 30, 30)

        msg.exec_()


class GuiListBox(QtGui.QListWidget):
    def __init__(self, str_name='abc'):
        super(GuiListBox, self).__init__()

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setWindowTitle(str_name)
        self._markline = 0

    @property
    def markline(self):
        return self._markline

    @markline.setter
    def markline(self, value):

        if self._markline > 0 and (self.count() >= self._markline):
            # self.sGuiView.MAIN_TX_LIST.setStyleSheet("QListWidget{ background: white }")
            cur_line = self.item(self._markline - 1)
            cur_line.setBackground(QtCore.Qt.white)

        if value > 0 and (self.count() >= value):
            cur_line = self.item(value - 1)
            cur_line.setBackground(QtCore.Qt.gray)
            # self.setFocus()
        self._markline = value


class GuiTextString(QtGui.QLabel):
    def __init__(self, idx_set, s_gui_props, str_name='abc', str_base='', str_stat_tip=None):
        """

        :type str_base: object
        """
        super(GuiTextString, self).__init__()

        self.setText(str_name)
        self.setAlignment(s_gui_props.gui_ts_align[idx_set])
        self.setFixedHeight(s_gui_props.gui_ts_height[idx_set])
        if s_gui_props.gui_ts_width[idx_set] is not None:
            self.setFixedWidth(s_gui_props.gui_ts_width[idx_set])
        self.setWindowTitle(str_name)  # for event assignment
        self.setWordWrap(s_gui_props.gui_ts_wrap[idx_set])
        self.setFont(s_gui_props.gui_ts_font[idx_set])
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)

        self.str_base_disp = str_base
        self._dispval = 0

    @property
    def dispval(self):
        return self._dispval

    @dispval.setter
    def dispval(self, value):

        if isinstance(value, str) or (str(value.__class__).find('unicode') is not -1):
            str_value = value
        else:
            str_value = str(value)

        self._dispval = str_value
        str_text = str(self.str_base_disp) + ' ' + str_value
        self.setText(str_text)


class GuiButton(QtGui.QPushButton):
    def __init__(self, idx_set, s_gui_props, str_name='abc', str_stat_tip=None):
        super(GuiButton, self).__init__()

        self.setText(str_name)
        self.setFixedHeight(s_gui_props.gui_pb_height[idx_set])
        if s_gui_props.gui_pb_width[idx_set] is not None:
            self.setFixedWidth(s_gui_props.gui_pb_width[idx_set])
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)


class GuiCheckBox(QtGui.QCheckBox):
    def __init__(self, idx_set, s_gui_props, str_name='abc', str_stat_tip=None, b_is_checked=False):
        super(GuiCheckBox, self).__init__()
        self.setFixedWidth(s_gui_props.gui_cb_width[idx_set])
        self.setText(str_name)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setChecked(b_is_checked)
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)


class GuiTextBox(QtGui.QLineEdit):
    def __init__(self, idx_set, s_gui_props, str_text=None, str_stat_tip=None):
        super(GuiTextBox, self).__init__()
        if s_gui_props.gui_tx_width[idx_set] is not None:
            self.setFixedWidth(s_gui_props.gui_tx_width[idx_set])
        self.setFixedHeight(s_gui_props.gui_tx_height[idx_set])
        if str_text is not None:
            self.setText(str_text)
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)


class GuiSelectBox(QtGui.QComboBox):
    def __init__(self, idx_set, s_gui_props, a_list_cont=None, str_stat_tip=None):
        super(GuiSelectBox, self).__init__()
        if s_gui_props.gui_sb_width[idx_set] is not None:
            self.setFixedWidth(s_gui_props.gui_sb_width[idx_set])
        self.setFixedHeight(s_gui_props.gui_sb_height[idx_set])
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        if a_list_cont is not None:
            self.addItems(a_list_cont)
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)


class GuiRadioBut(QtGui.QRadioButton):
    def __init__(self, idx_set, s_gui_props, str_name='abc', str_stat_tip=None, b_is_checked=False):
        super(GuiRadioBut, self).__init__()
        self.setFixedWidth(s_gui_props.gui_rb_width[idx_set])
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setChecked(b_is_checked)
        if str_stat_tip is not None:
            self.setStatusTip(str_stat_tip)
        self._dispval = str_name

    @property
    def dispval(self):
        return self._dispval

    @dispval.setter
    def dispval(self, value):
        self._dispval = value
        self.setText(value)


if __name__ == "__main__":
    application = MYthEEE()
    sys.exit(application.exec_())
