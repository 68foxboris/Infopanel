from Plugins.Plugin import PluginDescriptor
from Screens.PluginBrowser import *
from Screens.Ipkg import Ipkg
from Components.SelectionList import SelectionList
from Screens.NetworkSetup import *
from enigma import *
from enigma import getBoxType
from Screens.Standby import *
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Screens.Screen import Screen
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.ChoiceBox import ChoiceBox
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS, fileExists, pathExists
from Components.MenuList import MenuList
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.config import ConfigSubsection, ConfigInteger, ConfigText, getConfigListEntry, ConfigSelection, ConfigIP, ConfigYesNo, ConfigSequence, ConfigNumber, NoSave, ConfigEnableDisable, configfile
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Sources.Progress import Progress
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.SystemInfo import SystemInfo
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
import os
import sys
import re
font = 'Regular;16'
import ServiceReference
import time
import datetime
inINFOPanel = None
config.softcam = ConfigSubsection()
config.softcam.actCam = ConfigText(visible_width=200)
config.softcam.actCam2 = ConfigText(visible_width=200)
config.softcam.waittime = ConfigSelection([('0', _('dont wait')),
 ('1', _('1 second')),
 ('5', _('5 seconds')),
 ('10', _('10 seconds')),
 ('15', _('15 seconds')),
 ('20', _('20 seconds')),
 ('30', _('30 seconds'))], default='15')
config.plugins.infopanel_redpanel = ConfigSubsection()

def Check_Softcam():
    found = False
    if fileExists('/etc/enigma2/noemu'):
        found = False
    else:
        for x in os.listdir('/etc'):
            if x.find('.emu') > -1:
                found = True
                break

    return found


def Check_SysSoftcam():
    if os.path.isfile('/etc/init.d/softcam'):
        if os.path.islink('/etc/init.d/softcam') and not os.readlink('/etc/init.d/softcam').lower().endswith('none'):
            try:
                syscam = None
                syscam = os.readlink('/etc/init.d/softcam').rsplit('.', 1)[1]
                if syscam.lower().startswith('oscam'):
                    return 'oscam'
            except:
                pass

        if pathExists('/usr/bin/'):
            softcams = os.listdir('/usr/bin/')
            for softcam in softcams:
                if softcam.lower().startswith('oscam'):
                    return 'oscam'

    return


if Check_Softcam():
    redSelection = [('0', _('Default (Instant Record)')),
     ('1', _('Infopanel')),
     ('2', _('Timer List')),
     ('3', _('Show Movies')),
     ('4', _('Softcam Panel'))]
else:
    redSelection = [('0', _('Default (Instant Record)')),
     ('1', _('Infopanel')),
     ('2', _('Timer List')),
     ('3', _('Show Movies'))]

def timerEvent():
    pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
    for p in pluginlist:
        redSelection.append((p.name, _(p.name)))

    if getBoxType() == 'dm800':
        config.plugins.infopanel_redpanel.selection = ConfigSelection(redSelection, default='0')
        config.plugins.infopanel_redpanel.selectionLong = ConfigSelection(redSelection, default='1')
    else:
        config.plugins.infopanel_redpanel.selection = ConfigSelection(redSelection, default='1')
        config.plugins.infopanel_redpanel.selectionLong = ConfigSelection(redSelection, default='2')


timer = eTimer()
timer.timeout.get().append(timerEvent)
timer.startLongTimer(1)
choicelist = [('0', _('Audio Selection')),
 ('1', _('Default (Timeshift)')),
 ('2', _('Toggle Pillarbox <> Pan&Scan')),
 ('3', _('Teletext'))]
config.plugins.infopanel_yellowkey = ConfigSubsection()
if getBoxType() == 'dm800':
    config.plugins.infopanel_yellowkey.list = ConfigSelection(default='1', choices=choicelist)
    config.plugins.infopanel_yellowkey.listLong = ConfigSelection(default='1', choices=choicelist)
else:
    config.plugins.infopanel_yellowkey.list = ConfigSelection(default='0', choices=choicelist)
    config.plugins.infopanel_yellowkey.listLong = ConfigSelection(default='0', choices=choicelist)
config.plugins.showinfopanelextensions = ConfigYesNo(default=False)
config.plugins.infopanel_frozencheck = ConfigSubsection()
config.plugins.infopanel_frozencheck.list = ConfigSelection([('0', _('Off')),
 ('1', _('1 min.')),
 ('5', _('5 min.')),
 ('10', _('10 min.')),
 ('15', _('15 min.')),
 ('30', _('30 min.'))])
if os.path.isfile('/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo') is True:
    try:
        from Plugins.Extensions.MultiQuickButton.plugin import *
    except:
        pass

from Screens.CronTimer import *
from Plugins.Extensions.Infopanel.ScriptRunner import *
from Plugins.Extensions.Infopanel.MountManager import *
from Plugins.Extensions.Infopanel.SoftcamPanel import *
from Plugins.Extensions.Infopanel.CamStart import *
from Plugins.Extensions.Infopanel.CamCheck import *
from Plugins.Extensions.Infopanel.SwapManager import Swap, SwapAutostart
from Plugins.Extensions.Infopanel.SoftwarePanel import SoftwarePanel
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import InitConfig as BackupRestore_InitConfig
SystemInfo['SoftCam'] = Check_Softcam()
if not Check_Softcam() and config.plugins.showinfopanelextensions.value:
    config.plugins.showinfopanelextensions.value = False
    config.plugins.showinfopanelextensions.save()
    config.plugins.infopanel_redpanel.save()
if config.usage.keymap.value != eEnv.resolve('${datadir}/enigma2/keymap.xml'):
    if not os.path.isfile(eEnv.resolve('${datadir}/enigma2/keymap.usr')) and config.usage.keymap.value == eEnv.resolve('${datadir}/enigma2/keymap.usr'):
        setDefaultKeymap()
    if not os.path.isfile(eEnv.resolve('${datadir}/enigma2/keymap.ntr')) and config.usage.keymap.value == eEnv.resolve('${datadir}/enigma2/keymap.ntr'):
        setDefaultKeymap()
    if not os.path.isfile(eEnv.resolve('${datadir}/enigma2/keymap.u80')) and config.usage.keymap.value == eEnv.resolve('${datadir}/enigma2/keymap.u80'):
        setDefaultKeymap()

def setDefaultKeymap():
    print '[Info-Panel] Set Keymap to Default'
    config.usage.keymap.value = eEnv.resolve('${datadir}/enigma2/keymap.xml')
    config.save()


def command(comandline, strip = 1):
    comandline = comandline + ' >/tmp/command.txt'
    os.system(comandline)
    text = ''
    if os.path.exists('/tmp/command.txt') is True:
        file = open('/tmp/command.txt', 'r')
        if strip == 1:
            for line in file:
                text = text + line.strip() + '\n'

        else:
            for line in file:
                text = text + line
                if text[-1:] != '\n':
                    text = text + '\n'

        file.close()
    if text[-1:] == '\n':
        text = text[:-1]
    comandline = text
    os.system('rm /tmp/command.txt')
    return comandline


boxversion = getBoxType()
machinename = getMachineName()
INFO_Panel_Version = 'Info-Panel V1.2'
print '[Info-Panel] machinename: %s' % machinename
print '[Info-Panel] boxtype: %s' % boxversion
panel = open('/tmp/infopanel.ver', 'w')
panel.write(INFO_Panel_Version + '\n')
panel.write('Machinename: %s ' % machinename + '\n')
panel.write('Boxtype: %s ' % boxversion + '\n')
try:
    panel.write('Keymap: %s ' % config.usage.keymap.value + '\n')
except:
    panel.write('Keymap: keymap file not found !!' + '\n')

panel.close()
ExitSave = '[Exit] = ' + _('Cancel') + '              [Ok] =' + _('Save')

class ConfigPORT(ConfigSequence):

    def __init__(self, default):
        ConfigSequence.__init__(self, seperator='.', limits=[(1, 65535)], default=default)


def main(session, **kwargs):
    session.open(Infopanel)


def Apanel(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Info Panel'),
          main,
          'Infopanel',
          3)]
    else:
        return []


def camstart(reason, **kwargs):
    global timerInstance
    if not config.plugins.infopanel_frozencheck.list.value == '0':
        CamCheck()
    try:
        f = open('/proc/stb/video/alpha', 'w')
        f.write(str(config.osd.alpha.value))
        f.close()
    except:
        print '[Info-Panel] failed to write /proc/stb/video/alpha'

    try:
        if config.softcam.camstartMode.value == '0':
            if timerInstance is None:
                timerInstance = CamStart(None)
            timerInstance.startTimer()
    except:
        print '[Info-Panel] failed to run CamStart'

    return


def Plugins(**kwargs):
    return [PluginDescriptor(name=_('Info Panel'), description='Info panel GUI 27/12/2013', where=PluginDescriptor.WHERE_MENU, fnc=Apanel),
     PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=camstart),
     PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=SwapAutostart),
     PluginDescriptor(name=_('Info Panel'), description='Info panel GUI 27/12/2013', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]


MENU_SKIN = '<screen position="center,center" size="500,370" title="INFO Panel" >\n\t<widget source="global.CurrentTime" render="Label" position="0, 340" size="500,24" font="Regular;20" foregroundColor="#FFFFFF" halign="right" transparent="1" zPosition="5">\n\t\t<convert type="ClockToText">>Format%H:%M:%S</convert>\n\t</widget>\n\t<eLabel backgroundColor="#56C856" position="0,330" size="500,1" zPosition="0" />\n\t<widget name="Mlist" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="#251e1f20" transparent="1" />\n\t<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="#f2e000" halign="left" />\n</screen>'
CONFIG_SKIN = '<screen position="center,center" size="600,440" title="PANEL Config" >\n\t<widget name="config" position="10,10" size="580,377" enableWrapAround="1" scrollbarMode="showOnDemand" />\n\t<widget name="labelExitsave" position="90,410" size="420,25" halign="center" font="Regular;20" transparent="1" foregroundColor="#f2e000" />\n</screen>'
INFO_SKIN = '<screen name="Panel-Info"  position="center,center" size="730,400" title="PANEL-Info" >\n\t<widget name="label2" position="0,10" size="730,25" font="Regular;20" transparent="1" halign="center" foregroundColor="#f2e000" />\n\t<widget name="label1" position="10,45" size="710,350" font="Console;20" zPosition="1" backgroundColor="#251e1f20" transparent="1" />\n</screen>'
INFO_SKIN2 = '<screen name="PANEL-Info2"  position="center,center" size="530,400" title="PANEL-Info" backgroundColor="#251e1f20">\n\t<widget name="label1" position="10,50" size="510,340" font="Regular;15" zPosition="1" backgroundColor="#251e1f20" transparent="1" />\n</screen>'

class PanelList(MenuList):

    def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 50, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', int(font0 * 1.5)))
            self.l.setFont(1, gFont('Regular', int(font1 * 1.5)))
            self.l.setItemHeight(int(itemHeight * 1.5))
        else:
            self.l.setFont(0, gFont('Regular', font0))
            self.l.setFont(1, gFont('Regular', font1))
            self.l.setItemHeight(itemHeight)


def MenuEntryItem(entry):
    res = [entry]
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(15, 8), size=(60, 60), png=entry[0]))
        res.append(MultiContentEntryText(pos=(90, 15), size=(810, 60), font=0, text=entry[1]))
    else:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(40, 40), png=entry[0]))
        res.append(MultiContentEntryText(pos=(60, 10), size=(540, 40), font=0, text=entry[1]))
    return res


from Screens.PiPSetup import PiPSetup
from Screens.InfoBarGenerics import InfoBarPiP

def InfoEntryComponent(file):
    png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'icons/' + file + '.png'))
    if png == None:
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/' + file + '.png')
        if png == None:
            png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'icons/default.png'))
            if png == None:
                png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/default.png')
    res = png
    return res


class Infopanel(Screen, InfoBarPiP, ProtectedScreen):
    servicelist = None

    def __init__(self, session, services = None):
        global menu
        global inINFOPanel
        global pluginlist
        global INFOCONF
        Screen.__init__(self, session)
        config.plugins.configurationbackup = BackupRestore_InitConfig()
        if config.ParentalControl.configured.value:
            ProtectedScreen.__init__(self)
        self.session = session
        self.skin = MENU_SKIN
        self.onShown.append(self.setWindowTitle)
        ProtectedScreen.__init__(self)
        self.service = None
        INFOCONF = 0
        pluginlist = 'False'
        try:
            print '[INFO-Panel] SHOW'
            inINFOPanel = self
        except:
            print '[INFO-Panel] Error Hide'

        if services is not None:
            self.servicelist = services
        else:
            self.servicelist = None
        self.list = []
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {'cancel': self.Exit,
         'upUp': self.up,
         'downUp': self.down,
         'ok': self.ok}, 1)
        self['label1'] = Label(INFO_Panel_Version)
        self['summary_description'] = StaticText('')
        self.Mlist = []
        if Check_Softcam():
            self.Mlist.append(MenuEntryItem((InfoEntryComponent('SoftcamPanel'), _('SoftcamPanel'), 'SoftcamPanel')))
            self.Mlist.append(MenuEntryItem((InfoEntryComponent('SoftcamPanelSetup'), _('Softcam-Panel Setup'), 'Softcam-Panel Setup')))
        if Check_SysSoftcam() is 'oscam':
            self.Mlist.append(MenuEntryItem((InfoEntryComponent('OScamInfo'), _('OScamInfo'), 'OScamInfo')))
        self.Mlist.append(MenuEntryItem((InfoEntryComponent('SoftwareManager'), _('Software Manager'), 'software-manager')))
        self.Mlist.append(MenuEntryItem((InfoEntryComponent('KeymapSel'), _('Keymap Selection'), 'KeymapSel')))
        self.Mlist.append(MenuEntryItem((InfoEntryComponent('Plugins'), _('Plugins'), 'Plugins')))
        self.Mlist.append(MenuEntryItem((InfoEntryComponent('Infos'), _('Infos'), 'Infos')))
        self.onChangedEntry = []
        if getDesktop(0).size().width() == 1280:
            self['Mlist'] = PanelList([])
        else:
            self['Mlist'] = PanelList([], font0=24, font1=15, itemHeight=50)
        self['Mlist'].l.setList(self.Mlist)
        menu = 0
        self['Mlist'].onSelectionChanged.append(self.selectionChanged)
        return

    def isProtected(self):
        return config.ParentalControl.setuppinactive.value and not config.ParentalControl.config_sections.main_menu.value and config.ParentalControl.config_sections.infopanel.value

    def createSummary(self):
        pass

    def getCurrentEntry(self):
        if self['Mlist'].l.getCurrentSelection():
            selection = self['Mlist'].l.getCurrentSelection()[0]
            self['summary_description'].text = selection[1]
            if selection[0] is not None:
                return selection[0]
        return

    def selectionChanged(self):
        item = self.getCurrentEntry()

    def setWindowTitle(self):
        self.setTitle(_('Info Panel'))
        self.selectionChanged()

    def up(self):
        pass

    def down(self):
        pass

    def left(self):
        pass

    def right(self):
        pass

    def Red(self):
        self.showExtensionSelection1(Parameter='run')

    def Green(self):
        pass

    def yellow(self):
        pass

    def blue(self):
        pass

    def Exit(self):
        global menu
        global inINFOPanel
        if menu == 0:
            try:
                self.service = self.session.nav.getCurrentlyPlayingServiceReference()
                service = self.service.toCompareString()
                servicename = ServiceReference.ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
                print '[INFO-Panel] HIDE'
                inINFOPanel = None
            except:
                print '[INFO-Panel] Error Hide'

            self.close()
        elif menu == 1:
            self['Mlist'].moveToIndex(0)
            self['Mlist'].l.setList(self.oldmlist)
            menu = 0
            self['label1'].setText(INFO_Panel_Version)
        elif menu == 2:
            self['Mlist'].moveToIndex(0)
            self['Mlist'].l.setList(self.oldmlist1)
            menu = 1
            self['label1'].setText('Infos')
        return

    def ok(self):
        menu = self['Mlist'].l.getCurrentSelection()[0][2]
        print '[INFO-Panel] MenuItem: ' + menu
        if menu == 'Plugins':
            self.Plugins()
        elif menu == 'Pluginbrowser':
            self.session.open(PluginBrowser)
        elif menu == 'Infos':
            self.Infos()
        elif menu == 'InfoPanel':
            self.session.open(Info, 'InfoPanel')
        elif menu == 'Info':
            self.session.open(Info, 'SystemInfo')
        elif menu == 'ImageVersion':
            self.session.open(Info, 'ImageVersion')
        elif menu == 'FreeSpace':
            self.session.open(Info, 'FreeSpace')
        elif menu == 'Network':
            self.session.open(Info, 'Network')
        elif menu == 'Mounts':
            self.session.open(Info, 'Mounts')
        elif menu == 'Kernel':
            self.session.open(Info, 'Kernel')
        elif menu == 'Ram':
            self.session.open(Info, 'Free')
        elif menu == 'Cpu':
            self.session.open(Info, 'Cpu')
        elif menu == 'Top':
            self.session.open(Info, 'Top')
        elif menu == 'MemInfo':
            self.session.open(Info, 'MemInfo')
        elif menu == 'Module':
            self.session.open(Info, 'Module')
        elif menu == 'Mtd':
            self.session.open(Info, 'Mtd')
        elif menu == 'Partitions':
            self.session.open(Info, 'Partitions')
        elif menu == 'Swap':
            self.session.open(Info, 'Swap')
        elif menu == 'SystemInfo':
            self.System()
        elif menu == 'CronTimer':
            self.session.open(CronTimers)
        elif menu == 'JobManager':
            self.session.open(ScriptRunner)
        elif menu == 'OScamInfo':
            from Screens.OScamInfo import OscamInfoMenu
            self.session.open(OscamInfoMenu)
        elif menu == 'SoftcamPanel':
            self.session.open(SoftcamPanel)
        elif menu == 'software-manager':
            self.Software_Manager()
        elif menu == 'software-update':
            self.session.open(SoftwarePanel)
        elif menu == 'backup-settings':
            self.session.openWithCallback(self.backupDone, BackupScreen, runBackup=True)
        elif menu == 'restore-settings':
            self.backuppath = getBackupPath()
            self.backupfile = getBackupFilename()
            self.fullbackupfilename = self.backuppath + '/' + self.backupfile
            if os_path.exists(self.fullbackupfilename):
                self.session.openWithCallback(self.startRestore, MessageBox, _('Are you sure you want to restore your STB backup?\nSTB will restart after the restore'), default=False)
            else:
                self.session.open(MessageBox, _('Sorry no backups found!'), MessageBox.TYPE_INFO, timeout=10)
        elif menu == 'backup-files':
            self.session.open(BackupSelection, title=_('Default files/folders to backup'), configBackupDirs=config.plugins.configurationbackup.backupdirs_default, readOnly=True)
        elif menu == 'backup-files-additional':
            self.session.open(BackupSelection, title=_('Additional files/folders to backup'), configBackupDirs=config.plugins.configurationbackup.backupdirs, readOnly=False)
        elif menu == 'backup-files-excluded':
            self.session.open(BackupSelection, title=_('Files/folders to exclude from backup'), configBackupDirs=config.plugins.configurationbackup.backupdirs_exclude, readOnly=False)
        elif menu == 'MultiQuickButton':
            self.session.open(MultiQuickButton)
        elif menu == 'MountManager':
            self.session.open(HddMount)
        elif menu == 'SwapManager':
            self.session.open(Swap)
        elif menu == 'Softcam-Panel Setup':
            self.session.open(ShowSoftcamPanelExtensions)
        elif menu == 'KeymapSel':
            self.session.open(KeymapSel)

    def Plugins(self):
        global menu
        menu = 1
        self['label1'].setText(_('Plugins'))
        self.tlist = []
        self.oldmlist = []
        self.oldmlist = self.Mlist
        self.tlist.append(MenuEntryItem((InfoEntryComponent('MountManager'), _('MountManager'), 'MountManager')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('CronTimer'), _('CronManager'), 'CronTimer')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('JobManager'), _('JobManager'), 'JobManager')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('SwapManager'), _('SwapManager'), 'SwapManager')))
        if os.path.isfile('/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo') is True:
            self.tlist.append(MenuEntryItem((InfoEntryComponent('MultiQuickButton'), _('MultiQuickButton'), 'MultiQuickButton')))
        self['Mlist'].moveToIndex(0)
        self['Mlist'].l.setList(self.tlist)

    def Infos(self):
        global menu
        menu = 1
        self['label1'].setText(_('Infos'))
        self.tlist = []
        self.oldmlist = []
        self.oldmlist1 = []
        self.oldmlist = self.Mlist
        self.tlist.append(MenuEntryItem((InfoEntryComponent('InfoPanel'), _('InfoPanel'), 'InfoPanel')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('ImageVersion'), _('Image-Version'), 'ImageVersion')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('FreeSpace'), _('FreeSpace'), 'FreeSpace')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Kernel'), _('Kernel'), 'Kernel')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Mounts'), _('Mounts'), 'Mounts')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Network'), _('Network'), 'Network')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Ram'), _('Ram'), 'Ram')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('SystemInfo'), _('SystemInfo'), 'SystemInfo')))
        self['Mlist'].moveToIndex(0)
        self['Mlist'].l.setList(self.tlist)
        self.oldmlist1 = self.tlist

    def System(self):
        global menu
        menu = 2
        self['label1'].setText(_('System Info'))
        self.tlist = []
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Cpu'), _('Cpu'), 'Cpu')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('MemInfo'), _('MemInfo'), 'MemInfo')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Mtd'), _('Mtd'), 'Mtd')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Module'), _('Module'), 'Module')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Partitions'), _('Partitions'), 'Partitions')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Swap'), _('Swap'), 'Swap')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Top'), _('Top'), 'Top')))
        self['Mlist'].moveToIndex(0)
        self['Mlist'].l.setList(self.tlist)

    def System_main(self):
        global menu
        menu = 1
        self['label1'].setText(_('System'))
        self.tlist = []
        self.oldmlist = []
        self.oldmlist = self.Mlist
        self.tlist.append(MenuEntryItem((InfoEntryComponent('Info'), _('Info'), 'Info')))
        self['Mlist'].moveToIndex(0)
        self['Mlist'].l.setList(self.tlist)

    def Software_Manager(self):
        global menu
        menu = 1
        self['label1'].setText(_('Software Manager'))
        self.tlist = []
        self.oldmlist = []
        self.oldmlist = self.Mlist
        self.tlist.append(MenuEntryItem((InfoEntryComponent('SoftwareManager'), _('Software update'), 'software-update')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('BackupSettings'), _('Backup Settings'), 'backup-settings')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('RestoreSettings'), _('Restore Settings'), 'restore-settings')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('BackupFiles'), _('Show default backup files'), 'backup-files')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('BackupFilesAdditional'), _('Select additional backup files'), 'backup-files-additional')))
        self.tlist.append(MenuEntryItem((InfoEntryComponent('BackupFilesExcluded'), _('Select excluded backup files'), 'backup-files-excluded')))
        self['Mlist'].moveToIndex(0)
        self['Mlist'].l.setList(self.tlist)

    def backupDone(self, retval = None):
        if retval is True:
            self.session.open(MessageBox, _('Backup done.'), MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.open(MessageBox, _('Backup failed.'), MessageBox.TYPE_INFO, timeout=10)

    def startRestore(self, ret = False):
        if ret == True:
            self.exe = True
            self.session.open(RestoreScreen, runRestore=True)


class KeymapSel(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = ['SetupInfo', 'Setup']
        Screen.setTitle(self, _('Keymap Selection') + '...')
        self.setup_title = _('Keymap Selection') + '...'
        self['HelpWindow'] = Pixmap()
        self['HelpWindow'].hide()
        self['status'] = StaticText()
        self['footnote'] = Label()
        self['description'] = Label('')
        usrkey = eEnv.resolve('${datadir}/enigma2/keymap.usr')
        ntrkey = eEnv.resolve('${datadir}/enigma2/keymap.ntr')
        u80key = eEnv.resolve('${datadir}/enigma2/keymap.u80')
        self.actkeymap = self.getKeymap(config.usage.keymap.value)
        keySel = [('keymap.xml', _('Default  (keymap.xml)'))]
        if os.path.isfile(usrkey):
            keySel.append(('keymap.usr', _('User  (keymap.usr)')))
        if os.path.isfile(ntrkey):
            keySel.append(('keymap.ntr', _('Neutrino  (keymap.ntr)')))
        if os.path.isfile(u80key):
            keySel.append(('keymap.u80', _('UP80  (keymap.u80)')))
        if self.actkeymap == usrkey and not os.path.isfile(usrkey):
            setDefaultKeymap()
        if self.actkeymap == ntrkey and not os.path.isfile(ntrkey):
            setDefaultKeymap()
        if self.actkeymap == u80key and not os.path.isfile(u80key):
            setDefaultKeymap()
        self.keyshow = ConfigSelection(keySel)
        self.keyshow.value = self.actkeymap
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keySave,
         'cancel': self.keyCancel,
         'red': self.keyCancel,
         'green': self.keySave,
         'menu': self.keyCancel}, -2)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))
        if self.selectionChanged not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.selectionChanged)
        self.selectionChanged()

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Use Keymap'), self.keyshow))
        self['config'].list = self.list
        self['config'].setList(self.list)
        if config.usage.sort_settings.value:
            self['config'].list.sort()
        return

    def selectionChanged(self):
        self['status'].setText(self['config'].getCurrent()[0])

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

        self.selectionChanged()

    def getCurrentEntry(self):
        return self['config'].getCurrent()[0]

    def getCurrentValue(self):
        return str(self['config'].getCurrent()[1].getText())

    def getCurrentDescription(self):
        return self['config'].getCurrent() and len(self['config'].getCurrent()) > 2 and self['config'].getCurrent()[2] or ''

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def saveAll(self):
        config.usage.keymap.value = eEnv.resolve('${datadir}/enigma2/' + self.keyshow.value)
        config.usage.keymap.save()
        configfile.save()
        if self.actkeymap != self.keyshow.value:
            self.changedFinished()

    def keySave(self):
        self.saveAll()
        self.close()

    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()

        self.close()

    def keyCancel(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving settings?'))
        else:
            self.close()

    def getKeymap(self, file):
        return file[file.rfind('/') + 1:]

    def changedFinished(self):
        self.session.openWithCallback(self.ExecuteRestart, MessageBox, _('Keymap changed, you need to restart the GUI') + '\n' + _('Do you want to restart now?'), MessageBox.TYPE_YESNO)
        self.close()

    def ExecuteRestart(self, result):
        if result:
            quitMainloop(3)
        else:
            self.close()


class ShowSoftcamPanelExtensions(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'Setup'
        Screen.setTitle(self, _('Softcam-Panel Setup') + '...')
        self.setup_title = _('Softcam-Panel Setup') + '...'
        self['HelpWindow'] = Pixmap()
        self['HelpWindow'].hide()
        self['status'] = StaticText()
        self['footnote'] = Label()
        self['description'] = Label('')
        self['labelExitsave'] = Label('[Exit] = ' + _('Cancel') + '              [Ok] =' + _('Save'))
        CamCheckStop()
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keySave,
         'cancel': self.keyCancel,
         'red': self.keyCancel,
         'green': self.keySave,
         'menu': self.keyCancel}, -2)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))
        if self.selectionChanged not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.selectionChanged)
        self.selectionChanged()

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Show Softcam-Panel in Extensions Menu'), config.plugins.showinfopanelextensions))
        self.list.append(getConfigListEntry(_('Start Mode'), config.softcam.camstartMode))
        if config.softcam.camstartMode.value == '0':
            self.list.append(getConfigListEntry(_('Start attempts'), config.softcam.restartAttempts))
            self.list.append(getConfigListEntry(_('Time between start attempts (sec.)'), config.softcam.restartTime))
            self.list.append(getConfigListEntry(_('Stop check when cam is running'), config.softcam.restartRunning))
        self.list.append(getConfigListEntry(_('Show CCcamInfo in Extensions Menu'), config.cccaminfo.showInExtensions))
        self.list.append(getConfigListEntry(_('Show OscamInfo in Extensions Menu'), config.oscaminfo.showInExtensions))
        self.list.append(getConfigListEntry(_('Frozen Cam Check'), config.plugins.infopanel_frozencheck.list))
        self.list.append(getConfigListEntry(_('Wait time before start Cam 2'), config.softcam.waittime))
        self['config'].list = self.list
        self['config'].setList(self.list)
        if config.usage.sort_settings.value:
            self['config'].list.sort()
        return

    def selectionChanged(self):
        self['status'].setText(self['config'].getCurrent()[0])

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

        self.selectionChanged()
        self.createSetup()

    def getCurrentEntry(self):
        return self['config'].getCurrent()[0]

    def getCurrentValue(self):
        return str(self['config'].getCurrent()[1].getText())

    def getCurrentDescription(self):
        return self['config'].getCurrent() and len(self['config'].getCurrent()) > 2 and self['config'].getCurrent()[2] or ''

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def saveAll(self):
        if config.softcam.camstartMode.value == '0':
            if os.path.exists('/etc/rc2.d/S20softcam.cam1'):
                print 'Delete Symbolink link'
                self.container = eConsoleAppContainer()
                self.container.execute('update-rc.d -f softcam.cam1 defaults')
            if os.path.exists('/etc/init.d/softcam.cam1'):
                print 'Delete softcam init script cam1'
                os.system('rm /etc/init.d/softcam.cam1')
            if os.path.exists('/etc/rc2.d/S20softcam.cam2'):
                print 'Delete Symbolink link'
                self.container = eConsoleAppContainer()
                self.container.execute('update-rc.d -f softcam.cam2 defaults')
            if os.path.exists('/etc/init.d/softcam.cam2'):
                print 'Delete softcam init script cam2'
                os.system('rm /etc/init.d/softcam.cam2')
        for x in self['config'].list:
            x[1].save()

        configfile.save()

    def keySave(self):
        self.saveAll()
        self.doClose()

    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()

        self.doClose()

    def keyCancel(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving settings?'))
        else:
            self.doClose()

    def doClose(self):
        if not config.plugins.infopanel_frozencheck.list.value == '0':
            CamCheck()
        self.close()


class Info(Screen):

    def __init__(self, session, info):
        self.service = None
        Screen.__init__(self, session)
        self.skin = INFO_SKIN
        self['label2'] = Label('INFO')
        self['label1'] = ScrollLabel()
        if info == 'InfoPanel':
            self.InfoPanel()
        if info == 'SystemInfo':
            self.SystemInfo()
        elif info == 'ImageVersion':
            self.ImageVersion()
        elif info == 'FreeSpace':
            self.FreeSpace()
        elif info == 'Mounts':
            self.Mounts()
        elif info == 'Network':
            self.Network()
        elif info == 'Kernel':
            self.Kernel()
        elif info == 'Free':
            self.Free()
        elif info == 'Cpu':
            self.Cpu()
        elif info == 'Top':
            self.Top()
        elif info == 'MemInfo':
            self.MemInfo()
        elif info == 'Module':
            self.Module()
        elif info == 'Mtd':
            self.Mtd()
        elif info == 'Partitions':
            self.Partitions()
        elif info == 'Swap':
            self.Swap()
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'cancel': self.Exit,
         'ok': self.ok,
         'up': self.Up,
         'down': self.Down}, -1)
        return

    def Exit(self):
        self.close()

    def ok(self):
        self.close()

    def Down(self):
        self['label1'].pageDown()

    def Up(self):
        self['label1'].pageUp()

    def InfoPanel(self):
        try:
            self['label2'].setText('INFO')
            info1 = self.Do_cmd('cat', '/etc/motd', None)
            if info1.find('wElc0me') > -1:
                info1 = info1[info1.find('wElc0me'):len(info1)] + '\n'
                info1 = info1.replace('|', '')
            else:
                info1 = info1[info1.find('INFO'):len(info1)] + '\n'
            info2 = self.Do_cmd('cat', '/etc/image-version', None)
            info3 = self.Do_cut(info1 + info2)
            self['label1'].setText(info3)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def SystemInfo(self):
        try:
            self['label2'].setText(_('Image Info'))
            info1 = self.Do_cmd('cat', '/etc/version', None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def ImageVersion(self):
        try:
            self['label2'].setText(_('Image Version'))
            now = datetime.now()
            info1 = 'Date = ' + now.strftime('%d-%B-%Y') + '\n'
            info2 = 'Time = ' + now.strftime('%H:%M:%S') + '\n'
            info3 = self.Do_cmd('uptime', None, None)
            tmp = info3.split(',')
            info3 = 'Uptime = ' + tmp[0].lstrip() + '\n'
            info4 = self.Do_cmd('cat', '/etc/image-version', ' | head -n 1')
            info4 = info4[9:]
            info4 = 'Imagetype = ' + info4 + '\n'
            info5 = 'Load = ' + self.Do_cmd('cat', '/proc/loadavg', None)
            info6 = self.Do_cut(info1 + info2 + info3 + info4 + info5)
            self['label1'].setText(info6)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def FreeSpace(self):
        try:
            self['label2'].setText(_('FreeSpace'))
            info1 = self.Do_cmd('df', None, '-h')
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Mounts(self):
        try:
            self['label2'].setText(_('Mounts'))
            info1 = self.Do_cmd('mount', None, None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Network(self):
        try:
            self['label2'].setText(_('Network'))
            info1 = self.Do_cmd('ifconfig', None, None) + '\n'
            info2 = self.Do_cmd('route', None, '-n')
            info3 = self.Do_cut(info1 + info2)
            self['label1'].setText(info3)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Kernel(self):
        try:
            self['label2'].setText(_('Kernel'))
            info0 = self.Do_cmd('cat', '/proc/version', None)
            info = info0.split('(')
            info1 = 'Name = ' + info[0] + '\n'
            info2 = 'Owner = ' + info[1].replace(')', '') + '\n'
            info3 = 'Mainimage = ' + info[2][0:info[2].find(')')] + '\n'
            info4 = 'Date = ' + info[3][info[3].find('SMP') + 4:len(info[3])]
            info5 = self.Do_cut(info1 + info2 + info3 + info4)
            self['label1'].setText(info5)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Free(self):
        try:
            self['label2'].setText(_('Ram'))
            info1 = self.Do_cmd('free', None, None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Cpu(self):
        try:
            self['label2'].setText(_('Cpu'))
            info1 = self.Do_cmd('cat', '/proc/cpuinfo', None, " | sed 's/\t\t/\t/'")
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Top(self):
        try:
            self['label2'].setText(_('Top'))
            info1 = self.Do_cmd('top', None, '-b -n1')
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def MemInfo(self):
        try:
            self['label2'].setText(_('MemInfo'))
            info1 = self.Do_cmd('cat', '/proc/meminfo', None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Module(self):
        try:
            self['label2'].setText(_('Module'))
            info1 = self.Do_cmd('cat', '/proc/modules', None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Mtd(self):
        try:
            self['label2'].setText(_('Mtd'))
            info1 = self.Do_cmd('cat', '/proc/mtd', None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Partitions(self):
        try:
            self['label2'].setText(_('Partitions'))
            info1 = self.Do_cmd('cat', '/proc/partitions', None)
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Swap(self):
        try:
            self['label2'].setText(_('Swap'))
            info0 = self.Do_cmd('cat', '/proc/swaps', None, " | sed 's/\t/ /g; s/[ ]* / /g'")
            info0 = info0.split('\n')
            info1 = ''
            for l in info0[1:]:
                l1 = l.split(' ')
                info1 = info1 + 'Name: ' + l1[0] + '\n'
                info1 = info1 + 'Type: ' + l1[1] + '\n'
                info1 = info1 + 'Size: ' + l1[2] + '\n'
                info1 = info1 + 'Used: ' + l1[3] + '\n'
                info1 = info1 + 'Prio: ' + l1[4] + '\n\n'

            if info1[-1:] == '\n':
                info1 = info1[:-1]
            if info1[-1:] == '\n':
                info1 = info1[:-1]
            info1 = self.Do_cut(info1)
            self['label1'].setText(info1)
        except:
            self['label1'].setText(_('an internal error has occur'))

        return

    def Do_find(self, text, search):
        text = text + ' '
        ret = ''
        pos = text.find(search)
        pos1 = text.find(' ', pos)
        if pos > -1:
            ret = text[pos + len(search):pos1]
        return ret

    def Do_cut(self, text):
        text1 = text.split('\n')
        text = ''
        for line in text1:
            text = text + line[:95] + '\n'

        if text[-1:] == '\n':
            text = text[:-1]
        return text

    def Do_cmd(self, cmd, file, arg, pipe = ''):
        try:
            if file != None:
                if os.path.exists(file) is True:
                    o = command(cmd + ' ' + file + pipe, 0)
                else:
                    o = 'File not found: \n' + file
            elif arg == None:
                o = command(cmd, 0)
            else:
                o = command(cmd + ' ' + arg, 0)
            return o
        except:
            o = ''
            return o

        return