import subprocess, os

def toPainter(fbxPath, HomeDir):

    exe_path = r"C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"

    mesh_file_path = fbxPath

    cmd = f'"{exe_path}" --mesh "{mesh_file_path}" --export-path "{HomeDir}" {HomeDir}'
    subprocess.Popen(cmd, shell=True)

def openFolder(path):
    subprocess.Popen(['explorer', os.path.realpath(path)])

def exportToMA(path):
    pass


