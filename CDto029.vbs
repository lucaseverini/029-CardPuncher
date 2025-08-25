' CDto029.vbs
' This VBS script launches the program from main.py.
' Place next to main.py.

Dim fso, sh, appDir, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = appDir

' optional: ensure LOGS exists to capture output
If Not fso.FolderExists(appDir & "\LOGS") Then
  fso.CreateFolder appDir & "\LOGS"
End If

' Use python.exe (which works), but hide the window (windowstyle 0) via cmd /c
' cmd = "cmd /c python.exe ""main.py"" > ""LOGS\stdout.log"" 2> ""LOGS\stderr.log"""
cmd = "cmd /c python.exe ""main.py"""
sh.Run cmd, 0, False   ' 0 = hidden, False = don’t wait

