#! python
# MySQL Backup and Restore
# Version 0.1
# By Zach Cutberth

# Automates MySQL backups and provieds GUI for DB restores.

# GUI

# Imports
import PySimpleGUI as sg
import win32serviceutil
import subprocess
from config import *
from threading import Thread

# Variables

# Functions
def get_service_status(serviceName):
    try:
        service = win32serviceutil.QueryServiceStatus(serviceName)[1]
    except:
        return 'Not Installed'
    if service == 4:
        return 'Running'
    if service == 1:
        return 'Stopped'
    if service == 3:
        return 'Stopping'
    if service == 2:
        return 'Starting'

def check_status(service, action):
    if action == 'stop':
        currentStatus = get_service_status(service)
        while currentStatus != 'Stopped':
            currentStatus = get_service_status(service)
        if currentStatus == 'Stopped':
            pass

    if action == 'start':
        currentStatus = get_service_status(service)
        while currentStatus != 'Running':
            currentStatus = get_service_status(service)
        if currentStatus == 'Running':
            pass

def restore_db():
    window.FindElement('Create Backup').Update(disabled = True)
    window.FindElement('Restore Database').Update(disabled = True)
    window.FindElement('Save Settings').Update(disabled = True) 
    recreate_db()
    selected_file = window.FindElement('select_file').Get()
    window.FindElement('status').Update(value = 'Starting Database Restore...')
    button, values = window.Read(timeout=0)
    unzip_backup(selected_file)
    unzipped_file = glob.glob(temp_path + hostname + '*.sql')
    window.FindElement('status').Update(value = 'Restoring Database, Please Wait...')
    button, values = window.Read(timeout=0)
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' ' + database + ' < ' + unzipped_file[0], shell=True).communicate()
    window.FindElement('status').Update(value = 'Cleaning Up Temp Files, Please Wait...')
    button, values = window.Read(timeout=0)
    os.remove(unzipped_file[0])
    os.rmdir(temp_path)
    window.FindElement('status').Update(value = 'Finished Restoring Database.')
    window.FindElement('Create Backup').Update(disabled = False)
    window.FindElement('Restore Database').Update(disabled = False)
    window.FindElement('Save Settings').Update(disabled = False)

def restore_db1():
    window.FindElement('Create Backup').Update(disabled = True)
    window.FindElement('Restore Database').Update(disabled = True)
    window.FindElement('Save Settings').Update(disabled = True) 
    selected_file = window.FindElement('select_file').Get()
    window.FindElement('status').Update(value = 'Starting Database Restore...')
    button, values = window.Read(timeout=0)
    unzip_backup(selected_file)
    unzipped_file = glob.glob(temp_path + hostname + '*.sql')
    window.FindElement('status').Update(value = 'Restoring Database, Please Wait...')
    button, values = window.Read(timeout=0)
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' ' + database + ' < ' + unzipped_file[0], shell=True).communicate()
    window.FindElement('status').Update(value = 'Cleaning Up Temp Files, Please Wait...')
    button, values = window.Read(timeout=0)
    os.remove(unzipped_file[0])
    os.rmdir(temp_path)
    window.FindElement('status').Update(value = 'Finished Restoring Database.')
    window.FindElement('Create Backup').Update(disabled = False)
    window.FindElement('Restore Database').Update(disabled = False)
    window.FindElement('Save Settings').Update(disabled = False)

def restore_most_recent_backup():
    window.FindElement('Create Backup').Update(disabled = True)
    window.FindElement('Restore Database').Update(disabled = True)
    window.FindElement('Save Settings').Update(disabled = True)
    recreate_db()
    backup_path = setting_values['BackupPath']
    #print(backup_path + hostname)
    zip_files = sorted(glob.glob(backup_path + hostname + '*.zip'), key=os.path.getctime, reverse=True)
    #print(zip_files)
    window.FindElement('status').Update(value = 'Starting Database Restore, Please Wait...')
    button, values = window.Read(timeout=0)
    unzip_backup(zip_files[0])
    unzipped_file = glob.glob(temp_path + hostname + '*.sql')
    window.FindElement('status').Update(value = 'Restoring Database, Please Wait...')
    button, values = window.Read(timeout=0)
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' ' + database + ' < ' + unzipped_file[0], shell=True).communicate()
    window.FindElement('status').Update(value = 'Cleaning Up Temp Files, Please Wait...')
    button, values = window.Read(timeout=0)
    os.remove(unzipped_file[0])
    os.rmdir(temp_path)
    window.FindElement('status').Update(value = 'Applying Binary Logs.')
    button, values = window.Read(timeout=0)
    apply_binlogs()
    window.FindElement('status').Update(value = 'Finished Restoring Database.')
    window.FindElement('Create Backup').Update(disabled = False)
    window.FindElement('Restore Database').Update(disabled = False)
    window.FindElement('Save Settings').Update(disabled = False)

def restore_most_recent_backup1():
    window.FindElement('Create Backup').Update(disabled = True)
    window.FindElement('Restore Database').Update(disabled = True)
    window.FindElement('Save Settings').Update(disabled = True)
    backup_path = setting_values['BackupPath']
    #print(backup_path + hostname)
    zip_files = sorted(glob.glob(backup_path + hostname + '*.zip'), key=os.path.getctime, reverse=True)
    #print(zip_files)
    window.FindElement('status').Update(value = 'Starting Database Restore, Please Wait...')
    button, values = window.Read(timeout=0)
    unzip_backup(zip_files[0])
    unzipped_file = glob.glob(temp_path + hostname + '*.sql')
    window.FindElement('status').Update(value = 'Restoring Database, Please Wait...')
    button, values = window.Read(timeout=0)
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' ' + database + ' < ' + unzipped_file[0], shell=True).communicate()
    window.FindElement('status').Update(value = 'Cleaning Up Temp Files, Please Wait...')
    button, values = window.Read(timeout=0)
    os.remove(unzipped_file[0])
    os.rmdir(temp_path)
    window.FindElement('status').Update(value = 'Applying Binary Logs.')
    button, values = window.Read(timeout=0)
    apply_binlogs()
    window.FindElement('status').Update(value = 'Finished Restoring Database.')
    window.FindElement('Create Backup').Update(disabled = False)
    window.FindElement('Restore Database').Update(disabled = False)
    window.FindElement('Save Settings').Update(disabled = False)

def make_manual_backup():
    window.FindElement('Create Backup').Update(disabled = True)
    window.FindElement('Restore Database').Update(disabled = True)
    window.FindElement('Save Settings').Update(disabled = True)
    window.FindElement('status').Update(value = 'Creating Backup, Please Wait...')
    button, values = window.Read(timeout=0) 
    check_for_backup_path()
    backup_db()
    make_zip()
    window.FindElement('status').Update(value = 'Finished Creating Backup.')
    window.FindElement('Create Backup').Update(disabled = False)
    window.FindElement('Restore Database').Update(disabled = False)
    window.FindElement('Save Settings').Update(disabled = False)

def apply_binlogs():
    binlogs = sorted(glob.glob(binlog_path + 'mysql-bin.[!i]*'))
    Popen(mysqlbinlog_exe + ' --disable-log-bin ' + '\"' + ' '.join(binlogs) + '\" | ' + mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'], shell=True).communicate()

def drop_db():
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' --init-command=\"SET SQL_LOG_BIN = 0;\" -e \"DROP DATABASE ' + database + '\"', shell=True).communicate()

def create_db():
    Popen(mysql_exe + ' -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' --init-command=\"SET SQL_LOG_BIN = 0;\" -e \"CREATE DATABASE ' + database + '\"', shell=True).communicate()

def recreate_db():
    window.FindElement('status').Update(value = 'Dropping And Recreating RPSODS Schema, Please Wait...')
    button, values = window.Read(timeout=0)
    drop_db()
    create_db()
    window.FindElement('status').Update(value = 'Finished Dropping and Recreating RPSODS Schema.')
    button, values = window.Read(timeout=0)

def unzip_backup(file):
    zf = zipfile.ZipFile(file, 'r')
    zf.extractall(temp_path)
    zf.close()
    
def settings_window():
    for name in setting_names:
        setting_value = get_settings(name)
        setting_values.update({name:setting_value})

def settings_save():
    try:
        settings_parser = ConfigObj(os.environ['PROGRAMDATA'] + '/RetailPro/Prism MySQL Backup/settings.ini', encoding='utf8')
    except ConfigObjError as e:
        settings_parser = e.config
    settings_parser['DEFAULT']['ScheduleBackup'] = backup_schedule
    settings_parser['DEFAULT']['AgeOfBackups'] = backup_age
    settings_parser['DEFAULT']['DBUser'] = db_user
    settings_parser['DEFAULT']['DBPass'] = db_pass
    settings_parser['DEFAULT']['BackupPath'] = backup_path
    settings_parser.write()

    for name in setting_names:
        setting_value = get_settings(name)
        setting_values.update({name:setting_value})

db_cred_layout = [
                [sg.Text('Database User'), sg.InputText(setting_values['DBUser'], key='db_user', do_not_clear=True)],
                #[sg.Text('Database Password'), sg.InputText(base64.b64decode(setting_values['DBPass']), key='db_pass', do_not_clear=True)]
                [sg.Text('Database Password'), sg.InputText(setting_values['DBPass'], password_char='*', key='db_pass', do_not_clear=True)]
]

db_backup_layout = [
                [sg.Text('Backup Path'), sg.InputText(setting_values['BackupPath'], key='backup_path', do_not_clear=True)],
                [sg.Text('Schedule Automated Backup'), sg.InputText(setting_values['ScheduleBackup'], key='backup_schedule', do_not_clear=True)],
                [sg.Text('Days to Retain Backups'), sg.InputText(setting_values['AgeOfBackups'], key='backup_age', do_not_clear=True)]
]

restore_layout = [[sg.Checkbox('Drop and recreate RPSODS schema before restoring database', key='drop_schema', default=False)],
            [sg.Radio('Restore most recent backup and apply binary logs', "RADIO1", key='restore_recent', change_submits=True, default=True), sg.Radio('Select database backup to restore', "RADIO1", key='select_db', change_submits=True)],
            [sg.InputText(key='select_file', disabled=True, do_not_clear=True), sg.FileBrowse(key='browse_file', disabled=True)],
            [sg.Button(button_text='Restore Database')] 
]

backup_layout = [[sg.Text('Manually Create Backup')], 
                [sg.Button(button_text='Create Backup')]]

tab2_layout = [[sg.Frame('Backup Database', backup_layout, font='Any 12', title_color='blue')]]

tab1_layout = [[sg.Frame('Restore Database', restore_layout, font='Any 12', title_color='blue')]]

tab3_layout = [[sg.Frame('Database Credentials', db_cred_layout, font='Any 12', title_color='blue')],
                [sg.Frame('Backup Settings', db_backup_layout, font='Any 12', title_color='blue')],
                [sg.Button(button_text='Save Settings')]]

layout = [
    [sg.TabGroup([[sg.Tab('Restore', tab1_layout), sg.Tab('Backup', tab2_layout), sg.Tab('Settings', tab3_layout)]])],
    [sg.Text('', size=(50, 1), key='status')]
    ]

if __name__ == '__main__':

    window = sg.Window('MySQL Backup and Restore').Layout(layout)

    while True:
        #print = sg.EasyPrint
        button, values = window.Read()

        if button is None:
            break

        if values['select_db'] == True:
            window.FindElement('select_file').Update(disabled = False)
            window.FindElement('browse_file').Update(disabled = False)
        else:
            window.FindElement('select_file').Update(disabled = True)
            window.FindElement('browse_file').Update(disabled = True)

        if button == 'Save Settings':
            db_user = window.FindElement('db_user').Get()
            db_pass = window.FindElement('db_pass').Get()
            backup_path = window.FindElement('backup_path').Get()
            backup_schedule = window.FindElement('backup_schedule').Get()
            backup_age = window.FindElement('backup_age').Get()
            settings_save()
            if get_service_status('PrismMySQLBackupService') == 'Running':
                win32serviceutil.StopService('PrismMySQLBackupService')
                check_status('PrismMySQLBackupService', 'stop')
            if get_service_status('PrismMySQLBackupService') == 'Stopped':
                win32serviceutil.StartService('PrismMySQLBackupService')
            window.FindElement('status').Update(value = 'Settings Saved.')

        if button == 'Create Backup':
            thread1 = Thread(target=make_manual_backup)
            thread1.start()
            
        if button == 'Restore Database':
            if values['restore_recent'] == True:
                if values['drop_schema'] == True:
                    thread3 = Thread(target = restore_most_recent_backup)
                    thread3.start()
                if values['drop_schema'] == False:
                    thread3 = Thread(target = restore_most_recent_backup1)
                    thread3.start()
            if values['select_db'] == True:
                if values['drop_schema'] == True:
                    thread4 = Thread(target = restore_db)
                    thread4.start()
                if values['drop_schema'] == False:
                    thread4 = Thread(target = restore_db1)
                    thread4.start()