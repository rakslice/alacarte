# -*- coding: utf-8 -*-
#   Alacarte Menu Editor - Simple fd.o Compliant Menu Editor
#   Copyright (C) 2006  Travis Watkins
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Library General Public
#   License as published by the Free Software Foundation; either
#   version 2 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import gtk, gmenu
from ConfigParser import ConfigParser

class DesktopParser(ConfigParser):
	def __init__(self, filename=None):
		ConfigParser.__init__(self)
		if filename:
			self.read(filename)
		self._list_separator = ';'

	def optionxform(self, option):
		#makes keys not be lowercase
		return option

	def get(self, option, locale=None):
		if locale:
			option = option + '[%s]' % locale
		value = ConfigParser.get(self, 'Desktop Entry', option)
		if self._list_separator in value:
			value = value.split(self._list_separator)
		if value == 'true':
			value = True
		if value == 'false':
			value = False
		return value

	def set(self, option, value, locale=None):
		if locale:
			option = option + '[%s]' % locale
		if value == True:
			value = 'true'
		if value == False:
			value = 'false'
		if isinstance(value, tuple) or isinstance(value, list):
			value = self._list_seperator.join(value) + ';'
		ConfigParser.set(self, 'Desktop Entry', option, value)

	def write(self, file_object):
		file_object.write('[Desktop Entry]\n')
		items = []
		for item in self.items('Desktop Entry'):
			items.append(item)
		items.sort()
		for item in items:
			file_object.write(item[0] + '=' + item[1] + '\n')

def getUserMenuPath():
	menu_dir = None
	if os.environ.has_key('XDG_CONFIG_HOME'):
		menu_dir = os.path.join(os.environ['XDG_CONFIG_HOME'], 'menus')
	else:
		menu_dir = os.path.join(os.environ['HOME'], '.config', 'menus')
	if not os.path.isdir(menu_dir):
		os.makedirs(menu_dir)
	return menu_dir

def getUserItemPath():
	item_dir = None
	if os.environ.has_key('XDG_DATA_HOME'):
		item_dir = os.path.join(os.environ['XDG_DATA_HOME'], 'share', 'applications')
	else:
		item_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'applications')
	if not os.path.isdir(item_dir):
		os.makedirs(item_dir)
	return item_dir

def getDirectoryPath(file_id):
	home = getUserDirectoryPath()
	file_path = os.path.join(home, file_id)
	if os.path.isfile(file_path):
		return file_path
	if os.environ.has_key('XDG_DATA_DIRS'):
		for system_path in os.environ['XDG_DATA_DIRS'].split(':'):
			file_path = os.path.join(system_path, 'desktop-directories', file_id)
			if os.path.isfile(file_path):
				return file_path
	file_path = os.path.join('/', 'usr', 'share', 'desktop-directories', file_id)
	return file_path

def getUserDirectoryPath():
	menu_dir = None
	if os.environ.has_key('XDG_DATA_HOME'):
		menu_dir = os.path.join(os.envrion['XDG_DATA_HOME'], 'share', 'desktop-directories')
	else:
		menu_dir = os.path.join(os.environ['HOME'], '.local', 'share', 'desktop-directories')
	if not os.path.isdir(menu_dir):
		os.makedirs(menu_dir)
	return menu_dir

def getSystemMenu(file_name):
	if os.environ.has_key('XDG_CONFIG_DIRS'):
		for system_path in os.environ['XDG_CONFIG_DIRS'].split(':'):
			if os.path.isfile(os.path.join(system_path, 'menus', file_name)):
				return os.path.join(system_path, file_name)
	return os.path.join('/', 'etc', 'xdg', 'menus', file_name)

def getUserMenuXml(tree):
	system_file = getSystemMenu(tree.get_menu_file())
	name = tree.root.get_menu_id()
	menu_xml = "<!DOCTYPE Menu PUBLIC '-//freedesktop//DTD Menu 1.0//EN' 'http://standards.freedesktop.org/menu-spec/menu-1.0.dtd'>\n"
	menu_xml += "<Menu>\n  <Name>" + name + "</Name>\n  "
	menu_xml += "<MergeFile type=\"parent\">" + system_file +	"</MergeFile>\n</Menu>\n"
	return menu_xml

def getIcon(item, for_properties=False):
	if isinstance(item, str):
		iconName = item
	else:
		iconName = item.get_icon()
	if iconName and not '/' in iconName and iconName[-3:] in ('png', 'svg', 'xpm'):
		iconName = iconName[:-4]
	icon_theme = gtk.icon_theme_get_default()
	try:
		if for_properties:
			return icon_theme.load_icon(iconName, 24, 0), icon_theme.lookup_icon(iconName, 24, 0).get_filename()
		return icon_theme.load_icon(iconName, 24, 0)
	except:
		if iconName and '/' in iconName:
			try:
				if for_properties:
					return gtk.gdk.pixbuf_new_from_file_at_size(iconName, 24, 24), iconName
				return gtk.gdk.pixbuf_new_from_file_at_size(iconName, 24, 24)
			except:
				pass
		print "Can't find " + str(iconName)
		if for_properties:
			return None
		if item.get_type() == gmenu.TYPE_DIRECTORY:
			iconName = 'gnome-fs-directory'
		elif item.get_type() == gmenu.TYPE_ENTRY:
			iconName = 'application-default-icon'
		try:
			return icon_theme.load_icon(iconName, 24, 0)
		except:
			return None
