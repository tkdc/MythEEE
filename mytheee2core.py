#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

MythEEE core interface
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

import sys
import os

str_this_dir = os.path.dirname(os.path.realpath(__file__))
print(str_this_dir)

# configure the main parts
__b_cosocow_ena__ = True
__b_cofhemif_ena__ = True

if __b_cosocow_ena__:
    try:
        from cosocow import CoSoCoW
    except ImportError:
        print('import CoSoCoW from external path')
        sys.path.append(str_this_dir + '/../CoSoCoW')
        from cosocow import CoSoCoW

if __b_cofhemif_ena__:
    try:
        from cofhemif import CoFhemIf
    except ImportError:
        print('import FhemIf from external path')
        sys.path.append(str_this_dir + '/../CoFhemIf')
        from cofhemif import CoFhemIf

__title__ = 'MythEEE2core'
__version__ = '1.1.0'
__author__ = 'Thomas Katemann'
__copyright__ = 'Copyright 2018 Thomas Katemann'
__license__ = 'GPLv3'

class CoreIf():

    def __init__(self, s_gui_view=None):
        # super(Foo, self).__init__(parent)
        print('--- CoreIf Init ---')

        # Gui class
        self.sGuiView = s_gui_view

        # options
        self.b_print_state = 0

        # Init core module CoSoCoW
        if __b_cosocow_ena__:

            self.sGuiView.set_frames(1, 1)  # enable frame
            self.sGuiView.set_frames(2, 1)  # enable frame

            # source configuration
            self.idx_radio = 0
            self.idx_auxsrc = 1
            self.idx_mudb = [2, 4]
            self.a_mdb_type_list = ['Radio', 'AuxSrc', 'Artist', 'Album', 'Genre', 'ClearAll']
            self.sGuiView.MAIN_SB_MDBTYP.addItems(self.a_mdb_type_list)

            # Init core module CoSoCoW
            self.cosocow = CoSoCoW([['192.168.178.24', '192.168.178.23'], '192.168.178.25'])

            # set zone names
            self.sGuiView.MAIN_CB_Z[0].setText(self.cosocow.a_zone_name[0][0:4])
            self.sGuiView.MAIN_CB_Z[1].setText(self.cosocow.a_zone_name[1][0:5])

            # get and set availability of zones
            self.sGuiView.set_avail_zone(self.cosocow.a_zone_avail)

            # add event callbacks from core to gui
            self.cosocow.ev_volume.append(self.core_call_vol)
            self.cosocow.ev_balance.append(self.core_call_bal)
            self.cosocow.ev_play_state.append(self.core_play_state)
            self.cosocow.ev_play_track_sub.append(self.core_play_track_sub)
            self.cosocow.ev_play_track.append(self.core_play_track)
            self.cosocow.ev_radio_fav.append(self.core_radio_fav)
            self.cosocow.ev_play_mode.append(self.core_get_play_mode)
            self.cosocow.ev_queue_upd.append(self.core_queue_update)
            self.cosocow.ev_play_track_idx.append(self.core_play_track_idx)
            self.cosocow.ev_groups.append(self.core_set_groups)
            self.cosocow.ev_sleep_time_val.append(self.core_upd_sleep_time)

        else:
            # disable frames
            self.sGuiView.set_frames(1, -1)
            self.sGuiView.set_frames(2, -1)

        # Init core module CoFhemIf
        if __b_cofhemif_ena__:
            self.sGuiView.set_frames(3, 1)
            self.cofhemif = CoFhemIf()
            self.core_fhem_init_swt()
            self.cofhemif.ev_send_info.append(self.core_fhem_info)
        else:
            # disable frame
            self.sGuiView.set_frames(3, -1)

        print('--- CoreIf Init Finished ---')

    def core_fhem_init_swt(self):
        """
        initialize fhem device list in gui
        """
        self.sGuiView.MAIN_SB_FHEM_SWT.addItems(self.cofhemif.a_swt_dev)
        self.sGuiView.MAIN_SB_FHEM_TEMP.addItems(self.cofhemif.a_temp_dev)

    def gui_fhem_swt(self, str_action):
        """
        gui callback to set fhem switch action
        :param str_action:
        """
        idx_swt_dev = self.sGuiView.MAIN_SB_FHEM_SWT.currentIndex()
        self.cofhemif.set_fhem_swt(idx_swt_dev, str_action)

    def gui_fhem_set_temp(self):
        """
        gui callback to set desired temperature
        :param str_action:
        """
        idx_dev = self.sGuiView.MAIN_SB_FHEM_TEMP.currentIndex()
        idx_temp = self.sGuiView.MAIN_SB_FHEM_TEMPD.currentIndex()
        str_value = self.sGuiView.MAIN_SB_FHEM_TEMPD.itemText(idx_temp)
        if str_value == '':
            pass
        else:
            d_value = int(str_value)
            self.cofhemif.set_fhem_des_temp(idx_dev, d_value)

    def core_fhem_info(self, idx_room, str_room_cur, str_val1_cur, str_val2_cur, str_val3_cur):
        """
        event callback from core to provide fhem info to gui
        :param idx_room:
        :param str_room_cur:
        :param str_val1_cur:
        :param str_val2_cur:
        :param str_val3_cur:
        """
        self.sGuiView.MAIN_ST_FHEM_R[idx_room].dispval = str_room_cur
        self.sGuiView.MAIN_ST_FHEM_R1[idx_room].dispval = str_val1_cur
        self.sGuiView.MAIN_ST_FHEM_R2[idx_room].dispval = str_val2_cur
        self.sGuiView.MAIN_ST_FHEM_R3[idx_room].dispval = str_val3_cur

    def gui_play_stop(self, idx_zone):
        """
        gui callback to to start or stop playing music
        :param idx_zone:
        """
        self.cosocow.set_play_start_stop(idx_zone)

    def core_upd_sleep_time(self, idx_zone, value):
        """
        event callback from core to provide sleep timer status to gui
        :param idx_zone:
        :param value:
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if idx_actv_zone == idx_zone:
            # print 'Sleep: ' + value
            self.sGuiView.MAIN_ST_SLEEP.dispval = value

    def gui_set_sleep_time(self):
        """
        gui callback to activate sleep timer with desired time
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        d_time = int(self.sGuiView.MAIN_TX_SLEEP.text())
        d_cur_state = self.cosocow.get_sleep_timer(idx_actv_zone)
        if d_cur_state is not None:
            self.cosocow.set_sleep_timer(idx_actv_zone, None)
        else:
            self.cosocow.set_sleep_timer(idx_actv_zone, d_time)

    def core_get_play_mode(self, idx_zone, value):
        """
        event callback from core to provide play mode to gui
        :param idx_zone:
        :param value:
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if idx_zone == idx_actv_zone:
            if value.find('SHUFFLE') != -1:
                self.sGuiView.MAIN_CB_SHUFFLE.setChecked(1)
            else:
                self.sGuiView.MAIN_CB_SHUFFLE.setChecked(0)

    def gui_set_play_mode(self):
        """
        gui callback to change play mode
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if self.sGuiView.MAIN_CB_SHUFFLE.isChecked():
            self.cosocow.set_play_mode(idx_actv_zone, 1)
        else:
            self.cosocow.set_play_mode(idx_actv_zone, 0)

    def core_set_groups(self, a_groups, a_group_co):
        """
        event callback from core to provide zone group status to gui
        :param a_groups:
        :param a_group_co:
        """
        if len(a_groups[0]) > 1:
            self.sGuiView.MAIN_RB_Z[a_group_co[0]].setChecked(1)
            self.sGuiView.MAIN_CB_Z[a_groups[0][0]].setChecked(1)
            self.sGuiView.MAIN_CB_Z[a_groups[0][1]].setChecked(1)
            self.sGuiView.idx_actv_zone_prev = a_group_co[0]
        else:
            idx_actv_zone = self.sGuiView.get_actv_zone()
            if idx_actv_zone == 1:
                self.sGuiView.MAIN_CB_Z[0].setChecked(0)
            else:
                self.sGuiView.MAIN_CB_Z[1].setChecked(0)

    def gui_select_zone(self, str_action, idx_main, idx_join):
        """
        gui callback to change zone selection or configuration
        :param str_action:
        :param idx_main:
        :param idx_join:
        """
        if str_action == 'Join':
            self.cosocow.set_group(str_action, idx_main, idx_join)
        elif str_action == 'UnJoin':
            self.cosocow.set_group(str_action, idx_join)
        elif str_action == 'CngCo':
            self.cosocow.set_group(str_action, idx_main, idx_join)
        elif str_action == 'SwtZone':
            # get list of queue
            self.core_queue_update(idx_join, self.cosocow.a_queue_play_list[idx_join])
            self.core_play_track_idx(idx_join, self.cosocow.a_play_track_idx[idx_join])
            self.core_get_play_mode(idx_join, self.cosocow.a_play_mode[idx_join])

    def gui_add_mudb_item(self):
        """
        gui callback to select source to play
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        idx_type = self.sGuiView.MAIN_SB_MDBTYP.currentIndex()
        idx_item = self.sGuiView.MAIN_SB_MDBITM.currentIndex()
        if idx_type == self.idx_radio:
            # radio
            self.cosocow.set_radio_play(idx_actv_zone, None, idx_item)
        if idx_type == self.idx_auxsrc:
            # aux input
            self.cosocow.set_aux_play(idx_actv_zone, idx_item)
        elif idx_type >= self.idx_mudb[0]:
            # music data base
            self.cosocow.add_mudb_queue_item(idx_actv_zone, idx_type-self.idx_mudb[0], idx_item)

    def gui_rem_mudb_item(self):
        """
        gui callback to remove item from queue
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        idx_items = self.sGuiView.MAIN_TX_LIST.selectedIndexes()
        idx_type = self.sGuiView.MAIN_SB_MDBTYP.currentIndex()

        if idx_type == 5:
            idx_type = -1
        a_idx_items = []

        for item in idx_items:
            #print 'Remove' + str(item.row())
            a_idx_items.append(item.row())

        a_idx_items = sorted(a_idx_items, reverse=True)
        self.cosocow.rem_mudb_queue_item(idx_actv_zone, idx_type, a_idx_items)

    def core_radio_fav(self, idx_zone=0, a_radio_fav=None):
        """
        event callback from core to provide available radios to gui
        :param idx_zone:
        :param a_radio_fav:
        """
        idx_row = self.sGuiView.MAIN_SB_MDBTYP.currentIndex()
        if idx_row == self.idx_radio:
            self.gui_mudb_sel_idx(0)

    def gui_mudb_sel_idx(self, idx_row = None):
        """
        gui callback to select music source and update items of source
        :param idx_row:
        """
        if idx_row is not None:
            idx_row = 0
        else:
            idx_row = self.sGuiView.MAIN_SB_MDBTYP.currentIndex()

        if idx_row > self.idx_mudb[1]:
            self.sGuiView.MAIN_SB_MDBITM.clear()
        elif idx_row == self.idx_radio:
            self.sGuiView.MAIN_SB_MDBITM.clear()
            self.sGuiView.MAIN_SB_MDBITM.addItems(self.cosocow.a_radio_fav_name)
        elif idx_row == self.idx_auxsrc:
            self.sGuiView.MAIN_SB_MDBITM.clear()
            self.sGuiView.MAIN_SB_MDBITM.addItems(self.cosocow.a_aux_avail_name)
        elif idx_row >= self.idx_mudb[0] and idx_row <= self.idx_mudb[1]:
            self.sGuiView.MAIN_SB_MDBITM.clear()
            idx_req = idx_row - self.idx_mudb[0]
            if len(self.cosocow.a_mudb_items_name) is not 0:
                self.sGuiView.MAIN_SB_MDBITM.addItems(self.cosocow.a_mudb_items_name[idx_req])

    def core_play_track_idx(self, idx_zone, idx_track):
        """
        event callback from core to provide current play track index to gui
        :param idx_zone:
        :param idx_track:
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if idx_actv_zone == idx_zone:
            self.sGuiView.MAIN_TX_LIST.markline = idx_track
            if self.b_print_state:
                print('set queue line:' + str(idx_zone) + ' :' + str(idx_track))

    def gui_select_track_idx(self):
        """
        gui callback to select track of queue to play
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        idx_row = self.sGuiView.MAIN_TX_LIST.currentRow()
        self.cosocow.set_queue_track_play(idx_actv_zone, idx_row)

    def gui_set_track_next(self, str_action = 'Next'):
        """
        gui callback to play next track or according str_action
        :param str_action:
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        self.cosocow.set_play_track_next(idx_actv_zone, str_action)

    def core_queue_update(self, idx_zone, a_queue_tracks):
        """
        event callback from core to provide current queue list to gui
        :param idx_zone:
        :param a_queue_tracks:
        """
        idx_actv_zone = self.sGuiView.get_actv_zone()
        if idx_actv_zone == idx_zone:
            while self.sGuiView.MAIN_TX_LIST.count() > 0:
                self.sGuiView.MAIN_TX_LIST.takeItem(0)
            self.sGuiView.MAIN_TX_LIST.insertItems(0, a_queue_tracks)
            self.sGuiView.MAIN_ST_NUMTRCK.dispval = str(self.cosocow.a_play_queue_size[idx_zone])

    def core_play_track_sub(self, idx_zone, value):
        """
        event callback from core to provide current track sub name to gui
        :param idx_zone:
        :param value:
        """
        if idx_zone <= 1:
            self.sGuiView.MAIN_ST_TRACK[idx_zone].dispval = value

    def core_play_track(self, idx_zone, value):
        """
        event callback from core to provide current track source name to gui
        :param idx_zone:
        :param value:
        """
        self.sGuiView.MAIN_RB_Z[idx_zone].dispval = value

    def core_play_state(self, idx_zone, value):
        """
        event callback from core to provide current play state to gui
        :param idx_zone:
        :param value:
        """
        if self.b_print_state:
            print('State:' + str(idx_zone) + ':' + str(value))
        if idx_zone <= 1:
            self.sGuiView.MAIN_ST_INFO[idx_zone].dispval = value

    def core_call_vol(self, idx_zone, value):
        """
        event callback from core to provide current volume value to gui
        :param idx_zone:
        :param value:
        """
        if self.b_print_state:
            print('Vol:' + str(idx_zone) + ':' + str(value))
        if idx_zone <= 1:
            self.sGuiView.MAIN_ST_VOL[idx_zone].dispval = value

    def gui_call_vol(self, idx_zone, str_action):
        """
        gui callback to change required volume
        :param idx_zone:
        :param str_action:
        """
        self.cosocow.set_volume(idx_zone, str_action, 1)

    # get volume change by event
    def core_call_bal(self, idx_zone, value):
        """
        event callback from core to provide current balance value to gui
        :param idx_zone:
        :param value:
        """
        if self.b_print_state:
            print('Bal:' + str(idx_zone) + ':' + str(value))
        if idx_zone == 0:
            self.sGuiView.MAIN_ST_BAL[idx_zone].dispval = value

    def gui_call_bal(self, idx_zone, str_action):
        """
        gui callback to change required volume balance
        :param idx_zone:
        :param str_action:
        """
        self.cosocow.set_balance(idx_zone, str_action, 5)
