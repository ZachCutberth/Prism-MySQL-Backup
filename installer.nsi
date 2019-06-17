# This installs two files, app.exe and logo.ico, creates a start menu shortcut, builds an uninstaller, and
# adds uninstall information to the registry for Add/Remove Programs
 
# To get started, put this script into a folder with the two files (app.exe, logo.ico, and license.rtf -
# You'll have to create these yourself) and run makensis on it
 
# If you change the names "app.exe", "logo.ico", or "license.rtf" you should do a search and replace - they
# show up in a few places.
# All the other settings can be tweaked by editing the !defines at the top of this script
!define APPNAME "Prism MySQL Backup"
!define COMPANYNAME "RetailPro"
!define DESCRIPTION "Automated Prism MySQL backups"
# These three must be integers
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
# These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
# It is possible to use "mailto:" links in here to open the email client
!define HELPURL "http://www.retailpro.com" # "Support Information" link
!define UPDATEURL "http://www.retailpro.com" # "Product Updates" link
!define ABOUTURL "http://www.retailpro.com" # "Publisher" link
# This is the size (in kB) of all the files copied into "Program Files"
!define INSTALLSIZE 14550
 
RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)
 
InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"
 
# rtf or txt file - remember if it is txt, it must be in the DOS text format (\r\n)
# LicenseData "license.rtf"
# This will be in the installer/uninstaller's title bar
Name "${COMPANYNAME} - ${APPNAME}"
Icon "logo.ico"
outFile "Prism-MySQL-Backup_1.0.exe"
 
!include LogicLib.nsh
 
# Just three pages - license agreement, install location, and installation
# page license
page directory
Page instfiles
 
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        quit
${EndIf}
!macroend
 
function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd
 
section "install"
	# Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
	setOutPath $INSTDIR
	# Files added here should be removed by the uninstaller (see section "uninstall")
	file "PrismMySQLBackupService.exe"
	file "PrismMySQLBackup.exe"
    file "nssm.exe"
    file "logo.ico"
	# Add any other files for the install directory (license files, app data, etc) here
	# Uninstaller - See function un.onInit and section "uninstall" for configuration
	writeUninstaller "$INSTDIR\uninstall.exe"
 
	# Copy settings.ini to programdata
	setOutPath "$APPDATA\${COMPANYNAME}\${APPNAME}"
	file "settings.ini"

	# Start Menu
	createDirectory "$SMPROGRAMS\${COMPANYNAME}"
	createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\PrismMySQLBackup.exe" "" "$INSTDIR\logo.ico"
 
	# Registry information for add/remove programs
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${COMPANYNAME} - ${APPNAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\logo.ico$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "$\"${COMPANYNAME}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "$\"${HELPURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "$\"${UPDATEURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	# There is no option for modifying or repairing the install
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
	# Set the INSTALLSIZE constant (!defined at the top of this script) so Add/Remove Programs can accurately report the size
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

	# Backup my.ini file
	SetShellVarContext all
	IfFileExists "$APPDATA\MySQL\MySQL Server 5.7\my.ini" file_found file_not_found
	file_found:
	CopyFiles "$APPDATA\MySQL\MySQL Server 5.7\my.ini" "$APPDATA\MySQL\MySQL Server 5.7\my.ini.PrismBackup"
	Goto end_of_file_check
	file_not_found:
	IfFileExists "$APPDATA\MySQL\MySQL Server 5.6\my.ini" file_found1 end_of_file_check
	file_found1:
	CopyFiles "$APPDATA\MySQL\MySQL Server 5.6\my.ini" "$APPDATA\MySQL\MySQL Server 5.6\my.ini.PrismBackup"

	end_of_file_check:
	

    # Install PrismMySQLBackupService as windows service
    nsExec::Exec '"$INSTDIR\nssm.exe" install PrismMySQLBackupService "$INstdir\PrismMySQLBackupService.exe"'
    # nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppParameters """$INSTDIR\pkgs\RabbitMQLogManager.pyc"""'
    nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppStdout "$INSTDIR\PrismMySQLBackupServiceLogging.txt"'
    nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppStderr "$INSTDIR\PrismMySQLBackupServiceLogging.txt"'
    nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppStderrCreationDisposition 2'
    nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppStdoutCreationDisposition 2'
    nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppNoConsole 1'
    # nsExec::Exec '"$INSTDIR\nssm.exe" set PrismMySQLBackupService AppTimestampLog 1'
    nsExec::Exec '"$INSTDIR\nssm.exe" start PrismMySQLBackupService'

    # Stop and Start MySQL Service
    nsExec::Exec 'net stop MySQL57'
    nsExec::Exec 'net stop MySQL56'
    nsExec::Exec 'net start MySQL57'
    nsExec::Exec 'net start MySQL56'
    
sectionEnd
 
# Uninstaller
 
function un.onInit
	SetShellVarContext all
 
	#Verify the uninstaller - last chance to back out
	MessageBox MB_OKCANCEL "Permanantly remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
functionEnd
 
section "uninstall"
    # Uninstall service
    nsExec::Exec '"$INSTDIR\nssm.exe" stop PrismMySQLBackupService'
    nsExec::Exec '"$INSTDIR\nssm.exe" remove PrismMySQLBackupService'

	# Restore my.ini file
	# Backup my.ini file
	SetShellVarContext all
	IfFileExists "$APPDATA\MySQL\MySQL Server 5.7\my.ini.PrismBackup" file_found2 file_not_found2
	file_found2:
	SetOverwrite on
	CopyFiles "$APPDATA\MySQL\MySQL Server 5.7\my.ini.PrismBackup" "$APPDATA\MySQL\MySQL Server 5.7\my.ini"
	delete "$APPDATA\MySQL\MySQL Server 5.7\my.ini.PrismBackup"
	Goto end_of_file_check1
	file_not_found2:
	IfFileExists "$APPDATA\MySQL\MySQL Server 5.6\my.ini.PrismBackup" file_found3 end_of_file_check1
	file_found3:
	SetOverwrite on
	CopyFiles "$APPDATA\MySQL\MySQL Server 5.6\my.ini.PrismBackup" "$APPDATA\MySQL\MySQL Server 5.6\my.ini"
	delete "$APPDATA\MySQL\MySQL Server 5.6\my.ini.PrismBackup"

	end_of_file_check1:

	# Remove Start Menu launcher
	delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
	# Try to remove the Start Menu folder - this will only happen if it is empty
	rmDir "$SMPROGRAMS\${COMPANYNAME}"
 
	# Remove files
	delete $INSTDIR\PrismMySQLBackupService.exe
	delete $INSTDIR\PrismMySQLBackup.exe
    delete "$APPDATA\${COMPANYNAME}\${APPNAME}\settings.ini"
    delete $INSTDIR\nssm.exe
    delete $INSTDIR\logo.ico
    delete $INSTDIR\PrismMySQLBackupServiceLogging.txt
	# Always delete uninstaller as the last action
	delete $INSTDIR\uninstall.exe
 
	# Try to remove the install directory - this will only happen if it is empty
	rmDir $INSTDIR
	rmDir "$APPDATA\${COMPANYNAME}\${APPNAME}"

	# Remove uninstaller information from the registry
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
sectionEnd