import winreg
import glob
import zipfile
from time import strftime, sleep
import os
from subprocess import Popen, PIPE, check_call, run, CalledProcessError
import datetime
import sys
from configobj import ConfigObj
from configobj import ConfigObjError

if datetime.date.today() >= datetime.date(2019, 12, 31):
    print('This is a test version and has a will not operate past 12/31/2019.')
    sys.exit()

def get_mysql_server_path():
    try:
        mysqlHKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                "SOFTWARE\\WOW6432Node\\MySQL AB\\MySQL Server 5.7")
        return mysqlHKey
    except:
        pass

    try:
        mysqlHKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                "SOFTWARE\\WOW6432Node\\MySQL AB\\MySQL Server 5.6")
        return mysqlHKey
    except:
        pass

    print('MySQL does not appear to be installed on this system.')
    
mysqlHKey = get_mysql_server_path()

mysql_data_location = winreg.QueryValueEx(mysqlHKey, "DataLocation")[0].replace('\\', '/')
mysql_location = winreg.QueryValueEx(mysqlHKey, "Location")[0]
winreg.CloseKey(mysqlHKey)

# Regenerate settings.ini
def regen_settings():
    if os.path.isfile(os.environ['PROGRAMDATA'] + '/RetailPro/Prism MySQL Backup/settings.ini') == False:
        default_settings = {"ScheduleBackup":'01:00', "AgeOfBackups":"14", "DBUser":"root" , "DBPass":"sysadmin", "BackupPath":"c:\\backups\\"}
        
        settings_parser = ConfigObj(encoding='utf8')
        settings_parser.filename = os.environ['PROGRAMDATA'] + '/RetailPro/Prism MySQL Backup/settings.ini'
        settings_parser['DEFAULT'] = {}
        settings_parser['DEFAULT']['ScheduleBackup'] = default_settings['ScheduleBackup']
        settings_parser['DEFAULT']['AgeOfBackups'] = default_settings['AgeOfBackups']
        settings_parser['DEFAULT']['DBUser'] = default_settings['DBUser']
        settings_parser['DEFAULT']['DBPass'] = default_settings['DBPass']
        settings_parser['DEFAULT']['BackupPath'] = default_settings['BackupPath']
        settings_parser.write()

regen_settings()

def get_settings(setting):
    try:
        settings_parser = ConfigObj(os.environ['PROGRAMDATA'] + '/RetailPro/Prism MySQL Backup/settings.ini', encoding='utf8')
    except ConfigObjError as e:
        settings_parser = e.config
    setting_value = settings_parser['DEFAULT'][setting]
    return setting_value

setting_names = ['BackupPath', 'ScheduleBackup', 'AgeOfBackups', 'DBUser', 'DBPass']
setting_values = {}

for name in setting_names:
    setting_value = get_settings(name)
    setting_values.update({name:setting_value})

def get_myini_path():
    if os.path.isfile(os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.7/my.ini'):
        myini_path = os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.7/my.ini'
        return myini_path
    if os.path.isfile(os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.7/my.cnf'):
        myini_path = os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.7/my.cnf'
        return myini_path
    if os.path.isfile(os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.6/my.ini'):
        myini_path = os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.6/my.ini'
        return myini_path
    if os.path.isfile(os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.6/my.cnf'):
        myini_path = os.environ['PROGRAMDATA'] + '/MySQL/MySQL Server 5.6/my.cnf'
        return myini_path
    
    if os.path.isfile('/my.ini'):
        myini_path = '/my.ini'
        return myini_path
    if os.path.isfile('/my.cnf'):
        myini_path = '/my.cnf'
        return myini_path

    if os.path.isfile('C:/my.ini'):
        myini_path = 'C:/my.ini'
        return myini_path
    if os.path.isfile('C:/my.cnf'):
        myini_path = 'C:/my.cnf'
        return myini_path

    if os.path.isfile(mysql_location[0] + '/my.ini'):
        myini_path = mysql_location[0] + '/my.ini'
        return myini_path
    if os.path.isfile(mysql_location[0] + '/my.cnf'):
        myini_path = mysql_location[0] + '/my.cnf'
        return myini_path

myini_path = get_myini_path()

# Comment out no-beep in my.ini file
'''
try:    
    with open(myini_path, 'r', encoding='utf8') as file:
            filedata = file.read()
except:
    with open(myini_path, 'r', encoding='cp1252') as file:
        filedata = file.read()

filedata = filedata.replace('no-beep', '#no-beep')

try: 
    with open(myini_path, 'w', encoding='utf8') as file:
        file.write(filedata)
except:
    with open(myini_path, 'w', encoding='cp1252') as file:
        file.write(filedata)
'''
def get_myini_value(value):
    try:
        myini_parser = ConfigObj(myini_path, encoding='utf8')
    except ConfigObjError as e:
        myini_parser = e.config
    myini_value = myini_parser['mysqld'][value]
    return myini_value

myini_names = ['log-bin', 'max_binlog_size', 'log_bin_trust_function_creators']
myini_values = {}

for name in myini_names:
    try:
        myini_value = get_myini_value(name)
        myini_values.update({name:myini_value})
    except:
        try:
            myini_parser = ConfigObj(myini_path, encoding='utf8')
        except ConfigObjError as e:
            myini_parser = e.config
        if name == 'log-bin':
            myini_parser['mysqld'][name] = mysql_data_location + 'binlog/mysql-bin'
            myini_parser.write()
        if name == 'max_binlog_size':
            myini_parser['mysqld'][name] = '100M'
            myini_parser.write()
        if name == 'log_bin_trust_function_creators':
            myini_parser['mysqld'][name] = '1'
            myini_parser.write()

# If bin-log directory doesn't exist create it.
if not os.path.exists(mysql_data_location + 'binlog\\mysql-bin'):
    os.makedirs(mysql_data_location + 'binlog\\mysql-bin')

# Variables
mysql_exe = '\"' + mysql_location + 'bin/mysql.exe' + '\"'
mysqldump_exe = '\"' + mysql_location + 'bin\\mysqldump.exe' + '\"'
mysqlbinlog_exe = '\"' + mysql_location + 'bin/mysqlbinlog.exe' + '\"'
temp_path = setting_values['BackupPath'] + 'Temp/'
binlog_path = mysql_data_location + 'binlog/'
weekly_path = setting_values['BackupPath'] + 'Weekly/'
database = 'rpsods'
hostname = os.environ['COMPUTERNAME']

# Setup timestamp for later use.
timestamp = strftime("%D %H:%M:%S")

def check_for_backup_path():
    if not os.path.isdir(setting_values['BackupPath']):
        os.makedirs(setting_values['BackupPath'])

def backup_db():
    db_backup_filename = setting_values['BackupPath'] + hostname + '.' + strftime('%Y-%m-%d_%H-%M-%S') + '.sql'
    Popen('echo SET SESSION SQL_LOG_BIN=0; > ' + db_backup_filename, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
    Popen(mysqldump_exe + ' --triggers --events --routines --single-transaction --flush-logs --delete-master-logs --add-drop-database -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' --databases ' + database + ' >> \"' + db_backup_filename + '\"', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
    #os.chdir('C:\\Program Files\\MySQL\\MySQL Server 5.7\\bin')
    #f = open(db_backup_filename, 'w')
    #run(['mysqldump.exe', '--triggers', '--events', '--routines', '--single-transaction', '--flush-logs', '--delete-master-logs', '--add-drop-database', '-u' + setting_values['DBUser'], '-p' + setting_values['DBPass'], '-h', 'localhost', '--databases', database], shell=True, stdout=f)
    #f.close()
    #check_call(mysqldump_exe + ' --triggers --events --routines --single-transaction --flush-logs --delete-master-logs --add-drop-database -u' + setting_values['DBUser'] + ' -p' + setting_values['DBPass'] + ' -h' + 'localhost' + ' --databases ' + database + ' >> \"' + db_backup_filename + '\"', shell=True, stdout=PIPE)
    #try:
    #    os.chdir(os.path.dirname(sys.executable))
    #except:
    #    os.chdir(os.path.dirname(__file__))

def make_zip():
    backup_path = setting_values['BackupPath']
    sql_file = glob.glob(backup_path + hostname + '*.sql')
    zip_file = os.path.splitext(sql_file[0])
    os.chdir(backup_path)
    zf = zipfile.ZipFile(zip_file[0] + '.zip', 'w', zipfile.ZIP_DEFLATED)
    zf.write(os.path.basename(sql_file[0]))
    zf.close()
    os.remove(sql_file[0])
    try:
        os.chdir(os.path.dirname(sys.executable))
    except:
        os.chdir(os.path.dirname(__file__))