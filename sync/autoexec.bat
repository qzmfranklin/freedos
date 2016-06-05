@echo off
set lang=EN
set PATH=%dosdir%
set NLSPATH=%dosdir%
set HELPPATH=%dosdir%
set temp=%dosdir%
set tmp=%dosdir%
SET BLASTER=A220 I5 D1 H5 P330
set DIRCMD=/P /OGN
if "%config%"=="4" goto end
lh doslfn
SHSUCDX /QQ /D3
IF EXIST FDBOOTCD.ISO LH SHSUCDHD /Q /F:FDBOOTCD.ISO
LH FDAPM APMDOS
if "%config%"=="2" LH SHARE
REM LH DISPLAY CON=(EGA,,1)
REM NLSFUNC C:\FDOS\COUNTRY.SYS
REM MODE CON CP PREP=((858) A:\cpi\EGA.CPX)
REM MODE CON CP SEL=858
REM CHCP 858
REM LH KEYB US,,C:\FDOS\KEY\US.KL
DEVLOAD /H /Q %dosdir%\uide.sys /D:FDCD0001 /S5
ShsuCDX /QQ /~ /D:?SHSU-CDH /D:?FDCD0001 /D:?FDCD0002 /D:?FDCD0003
mem /c /n
shsucdx /D
goto end
:end
SET autofile=C:\autoexec.bat
SET CFGFILE=C:\config.sys
alias reboot=fdapm warmboot
alias halt=fdapm poweroff
echo type HELP to get support on commands and navigation
echo.
echo Welcome to FreeDOS 1.1
echo
