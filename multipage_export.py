#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inkscape extension to export objects as single files
"""

import os
import inkex
import tempfile
import subprocess
import lxml.etree as et

__version__ = '1.0'

inkex.localize()

class MultipageExport(inkex.Effect):

  def __init__(self):
    inkex.Effect.__init__(self)

    self.OptionParser.add_option('-n', '--name',     action='store', type='string', dest='name',     help='Base name')
    self.OptionParser.add_option('-f', '--format',   action='store', type='string', dest='format',   help='File format')
    self.OptionParser.add_option('-a', '--autoname', action='store', type='string', dest='autoname', help='Use IDs for names')
    self.OptionParser.add_option('-r', '--replace',  action='store', type='string', dest='replace',  help='Replace existing files')

  def run_command(self, args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

  def write_tempfile(self):
    desc, tmpfile = tempfile.mkstemp(suffix='.svg', prefix='multipage-export-')
    self.document.write(os.fdopen(desc, 'wb'))

    return tmpfile

  def export_path(self, fformat):
    name = self.options.name
    home = os.path.expanduser('~')
    path = "%s/Documents/Exports/%s/%s" % (home, name, fformat.upper())

    if not os.path.exists(path):
      os.makedirs(path)

    return path

  def file_path(self, fname, fformat):
    path = self.export_path(fformat)
    path = "%s/%s.%s" % (path, fname, fformat)

    if self.options.replace == 'false' and os.path.exists(path):
      inkex.errormsg('File already exists!')
      exit()

    return path

  def remove_pt(self, path, fformat):
    if fformat == 'svg':
      xml = et.parse(path)
      svg = xml.getroot()

      svg.attrib['width']  = svg.attrib['width'].replace('pt', '')
      svg.attrib['height'] = svg.attrib['height'].replace('pt', '')
      xml.write(path)

  def inkscape_export_png(self, oid, output, tmpfile):
    self.run_command([
      'inkscape',
      '--export-id=%s' % oid,
      '--export-png=%s' % output,
      tmpfile
    ])

  def inkscape_export_format(self, oid, fformat, output):
    tmpfile = self.write_tempfile()
    fformat = 'plain-svg' if fformat == 'svg' else fformat

    self.run_command([
      'inkscape',
      '--select=%s' % oid,
      '--verb=EditCut',
      '--verb=EditSelectAll',
      '--verb=EditDelete',
      '--verb=EditPaste',
      '--verb=EditSelectAll',
      '--verb=FitCanvasToSelection',
      '--verb=FileSave',
      '--verb=FileClose',
      '--verb=FileQuit',
      tmpfile
    ])

    self.run_command([
      'inkscape',
      '--vacuum-defs',
      '--export-%s=%s' % (fformat, output),
      tmpfile
    ])

  def inkscape_export(self, oid, fformat, output, tmpfile):
    if fformat == 'png':
      self.inkscape_export_png(oid, output, tmpfile)
    else:
      self.inkscape_export_format(oid, fformat, output)

  def rsvg_export(self, oid, fformat, output, tmpfile):
    self.run_command([
      'rsvg-convert',
      '-u',
      '-i', oid,
      '-d', '96',
      '-p', '96',
      '-f', fformat,
      '-o', output,
      tmpfile
    ])

  def export(self, oid, fformat, output, tmpfile):
    self.rsvg_export(oid, fformat, output, tmpfile)

  def export_files(self):
    tmpfile = self.write_tempfile()
    fformat = self.options.format
    fname   = self.options.name
    findex  = 0

    for oid in self.options.ids:
      findex = findex + 1

      if self.options.autoname == 'true':
        output = self.file_path(oid, fformat)
      else:
        output = self.file_path("%s-%s" % (fname, findex), fformat)

      self.export(oid, fformat, output, tmpfile)
      self.remove_pt(output, fformat)

  def effect(self):
    if self.options.name is None:
      inkex.errormsg('Please enter the folder name.')
      exit()

    if len(self.options.ids) < 1:
      inkex.errormsg('Please select at least 1 object.')
      exit()

    self.export_files()

if __name__ == '__main__':
  exporter = MultipageExport()
  exporter.affect()
