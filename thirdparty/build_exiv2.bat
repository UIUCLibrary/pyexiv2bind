@echo off
setlocal enabledelayedexpansion

IF NOT "%1"=="" (
    if not exist "%~1" (
        echo invalid path
        goto :eof
        
    ) else (
        set prefix=%~f1
    )
    
) else (
    set prefix=%CD%\dist\
)
echo using %prefix%
set cmake_generator="Visual Studio 14 2015 Win64"
REM set cmake_generator="Visual Studio 15 2017 Win64"
REM set cmake_generator="Ninja"
set libs_path=%CD%\libs

call "%VS140COMNTOOLS%..\..\VC\vcvarsall.bat" x86_amd64
if not exist "source\" mkdir source
if not exist "build\" mkdir build
if not exist %libs_path% mkdir %libs_path%

REM Build Zlib
if not exist "zlib1211.zip" wget https://zlib.net/zlib1211.zip  -P source
unzip -u source\zlib1211.zip -d source
if not exist "build\zlib" mkdir build\zlib
setlocal
cd build\zlib && cmake ..\..\source\zlib-1.2.11\ -G %cmake_generator% -DCMAKE_INSTALL_PREFIX="%libs_path%\zlib" -DCMAKE_BUILD_TYPE=Release && cmake --build . --config Release --target install
endlocal


REM Build Expat
if not exist "R_2_2_3.zip" wget https://github.com/libexpat/libexpat/archive/R_2_2_3.zip -P source
if not exist "build\libexpat" mkdir build\libexpat
unzip -u source\R_2_2_3.zip -d source

setlocal
cd build\libexpat && cmake ..\..\source\libexpat-R_2_2_3\expat -G %cmake_generator% -DCMAKE_INSTALL_PREFIX="%libs_path%\libexpat" -DCMAKE_BUILD_TYPE=Release -DBUILD_examples=off -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF -DBUILD_shared=OFF -DBUILD_tests=OFF -DBUILD_tools=OFF && cmake --build . --config Release --target install
endlocal

REM Build Googletest
if not exist "source\googletest" (
    cmd /c "cd source && git clone https://github.com/google/googletest.git"
    ) else (
        cmd /c "cd source\googletest && git pull"
        )

if not exist "build\gtest" mkdir build\gtest

setlocal
cd build\gtest && cmake ..\..\source\googletest -G %cmake_generator% -DCMAKE_INSTALL_PREFIX="%libs_path%\gtest" -DCMAKE_BUILD_TYPE=Release -DBUILD_GTEST=ON  -DBUILD_SHARED_LIBS=ON && cmake --build . --config Release --target install
endlocal


REM Build Exiv2
if not exist "source\exiv2" (
    cmd /c "cd source && git clone https://github.com/Exiv2/exiv2.git"
    ) else (
        cmd /c "cd source\exiv2 && git pull"
        )

if not exist "build\exiv2" mkdir build\exiv2


setlocal
cd build\exiv2 && cmake ..\..\source\exiv2 -G %cmake_generator% -DCMAKE_INSTALL_PREFIX="%prefix%\exiv2" -DCMAKE_BUILD_TYPE=Release -DZLIB_INCLUDE_DIR="%libs_path%\zlib\include" -DZLIB_LIBRARY_RELEASE="%libs_path%\zlib\lib\zlibstatic.lib" -DEXPAT_INCLUDE_DIR="%libs_path%\libexpat\include" -DEXPAT_LIBRARY="%libs_path%\libexpat\lib\expat.lib" -DBUILD_SHARED_LIBS=NO -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON -DEXIV2_BUILD_UNIT_TESTS=ON -DGTEST_ROOT="%libs_path%\gtest"
cmake --build . --config Release 

copy "%libs_path%\gtest\bin\*.dll" bin\
cd bin && unit_tests.exe
echo Exit Code is %errorlevel%
if %errorlevel% NEQ 0 (
    echo Tests fail
    exit /B
)
cd ..
cmake --build . --config Release --target install
endlocal


endlocal