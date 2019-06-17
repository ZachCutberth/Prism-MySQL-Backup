#! python
# MySQL Backup and Restore
# Version 0.1
# By Zach Cutberth
# zachcutberth@gmail.com

# Automates MySQL backups and provieds GUI for DB restores.

# MySQL backup automation

# Imports
from time import sleep
from time import time
from config import *
import schedule
import datetime
from shutil import copyfile

# Functions
def make_backup():
    check_for_backup_path()
    backup_db()
    make_zip()
    del_old_dailys()

def del_old_dailys():
    backup_path = setting_values['BackupPath']
    zip_files = glob.glob(backup_path + hostname + '*.zip')
    os.chdir(backup_path)
    current_time = time()
    for file in zip_files:
        creation_time = os.path.getctime(file)
        if (current_time - creation_time) / (24 * 3600) > int(setting_values['AgeOfBackups']):
            os.remove(file)
    try:
        os.chdir(os.path.dirname(sys.executable))
    except:
        os.chdir(os.path.dirname(__file__))  
    
def set_schedule():
    schedule.every().day.at(setting_values['ScheduleBackup']).do(make_backup)
    
if __name__ == '__main__':

    # Variables
    # backup_schedule_orig = setting_values['BackupSchedule']
    for name in setting_names:
                setting_value = get_settings(name)
                setting_values.update({name:setting_value})
    set_schedule()

    while True: 
        
        # Make a backup then sleep.
        for name in setting_names:
            setting_value = get_settings(name)
            setting_values.update({name:setting_value})
        schedule.run_pending()
        sleep(30)
            
