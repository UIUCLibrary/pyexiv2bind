@echo off
if not defined DevEnvDir (
    CALL C:\BuildTools\Common7\Tools\VsDevCmd.bat -no_logo -arch=amd64
    )
