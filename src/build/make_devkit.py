#!/usr/bin/env python

# Copyright (C) 2013 Bloomberg L.P. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function
import os, sys, bbutil, shutil
from blpwtk2 import content_version


scriptDir = os.path.dirname(os.path.realpath(__file__))
srcDir = os.path.abspath(os.path.join(scriptDir, os.pardir))
chromiumDir = os.path.abspath(os.path.join(srcDir, os.pardir))

def applyVariableToEnvironment(env, var, val):
  if env in os.environ:
    envItems = os.environ[env].split(" ")
  else:
    envItems = []
  found = False
  for i in range(0, len(envItems)):
    iSplit = envItems[i].split("=")
    if iSplit[0] == var:
      # Don't change it
      found = True
      break
  if not found:
    envItems.append(var + "=" + val)
  os.environ[env] = " ".join(envItems)


def copyVersionFile(destDir):
  gitHash = bbutil.getHEADSha()
  destFile = os.path.join(destDir, 'version.txt')
  with open(destFile, 'w') as fDest:
    if 'GN_GENERATORS' in os.environ:
      fDest.write('GN_GENERATORS="' + os.environ['GN_GENERATORS'] + '"\n')
    if 'GN_GENERATOR_FLAGS' in os.environ:
      fDest.write('GN_GENERATOR_FLAGS="' +
                  os.environ['GN_GENERATOR_FLAGS'] + '"\n')
    if 'GN_DEFINES' in os.environ:
      fDest.write('GN_DEFINES="' + os.environ['GN_DEFINES'] + '"\n')
    fDest.write('chromium.wtk2 commit ' + gitHash + '\n\n')


def findHeaderFiles(dirs):
  for d in dirs:
    for dirpath, dirnames, files in os.walk(d):
      relpath = os.path.relpath(dirpath, d)
      for f in files:
        if not f.endswith('.h'):
          continue
        yield d, relpath, f


def copyIncludeFilesFrom(destDir, sourceDirs):
  for basepath, relpath, f in findHeaderFiles(sourceDirs):
    destpath = os.path.join(destDir, relpath)
    if not os.path.exists(destpath):
      os.mkdir(destpath)

    src = os.path.join(basepath, relpath, f)
    dest = os.path.join(destpath, f)
    shutil.copyfile(src, dest)


def copyIncludeFiles(destDir):
  copyIncludeFilesFrom(
      os.path.join(destDir, 'include', 'blpwtk2'),
      [os.path.join(srcDir, 'blpwtk2', 'public'),
       os.path.join(srcDir, 'out', 'static', 'Debug', 'gen', 'blpwtk2', 'blpwtk2', 'public')])

  copyIncludeFilesFrom(
      os.path.join(destDir, 'include', 'v8'),
      [os.path.join(srcDir, 'v8', 'include'),
       os.path.join(srcDir, 'out', 'static', 'Debug', 'gen', 'blpwtk2', 'blpv8', 'public')])

def copyBin(destDir, version):
  productAppend = '.' + version

  products = [
    'blpwtk2_shell.exe',
    'blpwtk2_subprocess' + productAppend + '.exe',
    'content_shell.exe',
    'd8.exe',
    'blpv8' + productAppend + '.dll',
    'natives_blob' + productAppend + '.bin',
    'snapshot_blob' + productAppend + '.bin',
    'blpwtk2' + productAppend + '.dll',
    'blpcr_egl' + productAppend + '.dll',
    'blpcr_glesv2' + productAppend + '.dll',
    'd3dcompiler_47.dll',
    'icudtl' + productAppend + '.dat',
    'blpwtk2' + productAppend + '.pak',
    'content_shell.pak',
    'blpv8' + productAppend + '.dll.pdb',
    'blpv8' + productAppend + '.map',
    'blpwtk2' + productAppend + '.dll.pdb',
    'blpwtk2' + productAppend + '.map',
    'blpcr_egl' + productAppend + '.dll.pdb',
    'blpcr_egl' + productAppend + '.map',
    'blpcr_glesv2' + productAppend + '.dll.pdb',
    'blpcr_glesv2' + productAppend + '.map',
    'blpwtk2_subprocess' + productAppend + '.exe.pdb',
    'blpwtk2_subprocess' + productAppend + '.map',
  ]

  configs = ['Debug', 'Release']
  for config in configs:
    destBinDir = os.path.join(destDir, 'bin', config)
    srcBinDir = os.path.join(srcDir, 'out', 'static', config)
    for p in products:
      destFile = os.path.join(destBinDir, p)
      srcFile = os.path.join(srcBinDir, p)
      shutil.copy(srcFile, destFile)


def copyLib(destDir, version):
  productAppend = '.' + version

  products = [
    'blpv8' + productAppend + '.dll.lib',
    'blpwtk2' + productAppend + '.dll.lib',
  ]

  configs = ['Debug', 'Release']
  for config in configs:
    destBinDir = os.path.join(destDir, 'lib', config)
    srcBinDir = os.path.join(srcDir, 'out', 'static', config)
    for p in products:
      destFile = os.path.join(destBinDir, p)
      srcFile = os.path.join(srcBinDir, p)
      shutil.copy(srcFile, destFile)


def addGenFiles():
  configs = ['Debug', 'Release']

  def wantedFile(fname):
    fname = fname.lower()
    return fname.endswith('.h')     \
        or fname.endswith('.hpp')   \
        or fname.endswith('.c')     \
        or fname.endswith('.cc')    \
        or fname.endswith('.cpp')

  filesToAdd = []
  for config in configs:
    genDir = os.path.join(srcDir, 'out', 'static', config, 'gen')
    for dirpath, dirnames, filenames in os.walk(genDir):
      dirnames[:] = filter(lambda d: d != 'ffmpeg', dirnames)
      filenames = filter(lambda f: wantedFile(f), filenames)
      for f in filenames:
        f = os.path.relpath(os.path.join(dirpath, f))
        filesToAdd.append(f)
        if len(filesToAdd) > 20:
          cmd = 'git add -f -- ' + ' '.join(filesToAdd)
          bbutil.shellExec(cmd)
          filesToAdd = []
  if filesToAdd:
    cmd = 'git add -f -- ' + ' '.join(filesToAdd)
    bbutil.shellExec(cmd)

  cmd = 'git commit -m "Add generated files"'
  bbutil.shellExec(cmd)


def main(args):
  version = "bb717"   # SET BB VERSION NUMBER HERE

  outDir = None
  doClean = True
  doTag = False
  doPushTag = True
  for i in range(len(args)):
    if args[i] == '--outdir':
      outDir = args[i+1]
    elif args[i] == '--noclean':
      doClean = False
    elif args[i] == '--maketag':
      doTag = True
    elif args[i] == '--nopushtag':
      doPushTag = False
    elif args[i].startswith('-'):
      print("Usage: make_devkit.py --outdir <outdir> [--noclean] [--maketag [--nopushtag] ] [--gn]")
      return 1

  if not outDir:
    raise Exception("Specify outdir using --outdir")

  if not os.path.exists(outDir):
    raise Exception("Output directory does not exist: " + outDir)

  os.chdir(chromiumDir)
  version = content_version + '_' + version
  destDir = os.path.join(outDir, version)
  if os.path.exists(destDir):
    raise Exception("Path already exists: " + destDir)

  if doClean:
    print("Cleaning source tree...")
    sys.stdout.flush()
    buildOutDir = os.path.join(srcDir, 'out')
    if os.path.exists(buildOutDir):
      shutil.rmtree(buildOutDir)
    bbutil.shellExec('git clean -fdx')

  with open('devkit_version.txt', 'w') as f:
    f.write(version)

  os.environ['GN_GENERATORS'] = 'ninja'
  applyVariableToEnvironment('GN_DEFINES', 'bb_generate_map_files', 'true')

  print ("srcDir is : " + srcDir)
  os.chdir(srcDir)

  rc = bbutil.shellExecNoPipe('python build/runhooks.py')
  if rc != 0:
    return rc

  print("Building Debug...")
  sys.stdout.flush()
  rc = bbutil.shellExecNoPipe('python build/blpwtk2.py static Debug --bb_version')
  if rc != 0:
    return rc

  rc = bbutil.shellExecNoPipe('ninja.exe -C out/static/Debug blpwtk2_all')
  if rc != 0:
    return rc

  print("Building Release...")
  sys.stdout.flush()
  applyVariableToEnvironment('GN_DEFINES', 'is_official_build', 'true')
  rc = bbutil.shellExecNoPipe('python build/blpwtk2.py static Release --bb_version')
  if rc != 0:
    return rc

  rc = bbutil.shellExecNoPipe('ninja.exe -C out/static/Release blpwtk2_all')
  if rc != 0:
    return rc

  os.chdir("..")

  print("Creating devkit at " + destDir)
  sys.stdout.flush()
  os.mkdir(destDir)
  os.mkdir(os.path.join(destDir, 'bin'))
  os.mkdir(os.path.join(destDir, 'bin', 'Debug'))
  os.mkdir(os.path.join(destDir, 'bin', 'Release'))
  os.mkdir(os.path.join(destDir, 'include'))
  os.mkdir(os.path.join(destDir, 'lib'))
  os.mkdir(os.path.join(destDir, 'lib', 'Debug'))
  os.mkdir(os.path.join(destDir, 'lib', 'Release'))

  copyIncludeFiles(destDir)
  copyBin(destDir, version)
  copyLib(destDir, version)

  if doTag:
    print("Adding generated code to source control...")
    sys.stdout.flush()
    addGenFiles()

  # Copy version.txt *after* committing the generated files so that the sha in
  # the version.txt file includes the generated code.
  copyVersionFile(destDir)

  if doTag:
    print("Creating tag...")
    sys.stdout.flush()
    versions = version.split('_')
    crVersion = versions[0]
    bbVersion = versions[1]
    tag = 'devkit/stable/' + crVersion + '/' + bbVersion
    rc = bbutil.shellExecNoPipe('git tag -fm "devkit ' + tag + '" ' + tag)
    if rc != 0:
      return rc
    print("Tag '" + tag + "' created.")

    if doPushTag:
      print("Pushing tag...")
      rc = bbutil.shellExecNoPipe('git push origin tag ' + tag)
      if rc != 0:
        return rc

  print("Compressing...")
  sys.stdout.flush()
  os.chdir(outDir)
  rc = bbutil.shellExecNoPipe('7zr.exe a {}.7z {}'.format(version, version))
  if rc != 0:
    return rc

  print("All done!")
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
