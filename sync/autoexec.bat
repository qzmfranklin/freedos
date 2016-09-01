@echo off
set lang=EN
set PATH=%dosdir%
set NLSPATH=%dosdir%
set HELPPATH=%dosdir%
set temp=%dosdir%
set tmp=%dosdir%
SET BLASTER=A220 I5 D1 H5 P330
set DIRCMD=/P /OGN
SET autofile=C:\autoexec.bat
SET CFGFILE=C:\config.sys
alias reboot=fdapm warmboot
alias halt=fdapm poweroff
echo Welcome to FreeDOS 1.1
echo Running in real mode for flashing the bios.
REM Uncomment and modify the following two lines to flash bios.
REM cd flash\X10SAE5.520
REM flash.bat X10SAE5.520
