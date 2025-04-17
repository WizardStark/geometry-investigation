import mouse
import time
import win32com.client
import os
import winshell
from pathlib import Path

#The coordinates used in this script for auto-creation of xy-files relies on specific screen mouse positions, in my case on a 1440p
#monitor. Tune values to suit needs, I suggest using MPos.

shell = win32com.client.Dispatch("WScript.Shell")
keyDelay = 0.05

def click():
    time.sleep(0.1)
    mouse.click()

def dclick():
    click()
    click()

def rclick():
    time.sleep(0.1)
    mouse.right_click()

def tab(reps):
    for i in range(reps):
        shell.SendKeys('{TAB}',0)
        time.sleep(keyDelay)

def backtab(reps):
    for i in range(reps):
        shell.SendKeys('+{TAB}',0)
        time.sleep(keyDelay)

def down(reps):
    for i in range(reps):
        shell.SendKeys('{DOWN}',0)
        time.sleep(keyDelay)

def enter():
    shell.SendKeys('{ENTER}',0)

def backspace(reps):
    for i in range(reps):
        shell.SendKeys('{BS}',0)
        time.sleep(keyDelay)

def vTypeSelector(dim:str):
    reps = {"x":1,"y":2,"z":3}[dim]
    down(reps)


def dirFinder(directory:str):
    for i in directory.split('\\'):
        if len(i)>4:
            i=i[0:4]
        for j in i:
            shell.SendKeys(j,0)
            time.sleep(0.1)
        time.sleep(0.1)
        shell.SendKeys('{ENTER}',0)
        time.sleep(0.2)

def make_shortcut(source, dest_dir, dest_name=None, verbose=False):

    # process user input
    if dest_name is None:
        dest_name = Path(source).name
    dest_path = str(Path(dest_dir, dest_name)) + '.lnk'
    
    # make shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(dest_path)
    shortcut.IconLocation = source
    shortcut.Targetpath = source
    shortcut.save()

gd = 0.5

lines = ["1","2","3","4","5"]
dims = ["x","y","z"]

# lines = ['1']
# dims = ["x"]


profile = winshell.folder('profile')
drive = os.getenv("SystemDrive")

workDir = os.getcwd()
parentFolder = "CFD Outlet Velocities"
folderName = "Lofted 630 Finest"
fileDir = os.path.join(workDir,parentFolder,folderName)

if not os.path.exists(fileDir):
    os.makedirs(fileDir)
                         
make_shortcut(fileDir, "C:\\PyShortcut", "temp shortcut name")
scDir = os.path.join("C:\\PyShortcut",folderName)

for j in dims:
    for i in lines:
        #move to XY plots
        mouse.move("120", "420")
        dclick()                        
        time.sleep(2*gd)

        #plot name and definition
        tab(5)
        time.sleep(gd)
        shell.SendKeys(f"v{j}-line{i}",0)

        tab(3)
        shell.SendKeys(' ',0)

        #select velocity
        tab(11)
        shell.SendKeys(' ',0)
        time.sleep(gd)
        down(2)
        # time.sleep(0.1)
        enter()
        time.sleep(gd)
        tab(1)
        vTypeSelector(j)

        #select "Curve Length"
        tab(1)
        shell.SendKeys(' ',0)
        time.sleep(gd)
        down(1)
        enter()
        time.sleep(gd)


        #line selector
        backtab(3)  
        shell.SendKeys("^a",0)
        shell.SendKeys(f"line{i}",0)
        time.sleep(gd)
        mouse.move("950", "870")
        click()
        time.sleep(gd)

        #save file
        tab(2)
        enter()
        time.sleep(gd*2)
        mouse.move("1260", "700")
        click()
        tab(1)
        shell.SendKeys(f"v{j}-line{i}",0)
        mouse.move("1260", "700")
        click()
        backspace(20)
        dirFinder(scDir)
        tab(3)
        enter()

        #close plot window
        mouse.move("850", "960")
        click()
        time.sleep(gd)
        backtab(2)
        enter()
        time.sleep(gd*2)
