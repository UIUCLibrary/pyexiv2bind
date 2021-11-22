@echo off

if defined DevEnvDir (EXIT /B 0)
CALL C:\BuildTools\Common7\Tools\VsDevCmd.bat -arch=amd64
