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

class MultipageExport(inkex.Effect):

  def __init__(self):
    inkex.Effect.__init__(self)

    self.arg_parser.add_argument(
      '-n', '--name',
      type=str,
      dest='name',
      help='Base name'
    )

    self.arg_parser.add_argument(
      '-e', '--exporter',
      type=str,
      dest='exporter',
      help='Exporter'
    )

    self.arg_parser.add_argument(
      '-f', '--format',
      type=str,
      dest='format',
      help='File format'
    )

    self.arg_parser.add_argument(
      '-a', '--autoname',
      type=str,
      dest='autoname',
      help='Use IDs for names'
    )

    self.arg_parser.add_argument(
      '-r', '--replace',
      type=str,
      dest='replace',
      help='Replace existing files'
    )

    self.arg_parser.add_argument(
      '-c', '--combine',
      type=str,
      dest='combine',
      help='Combine into single PDF'
    )

  def run_command(self, args):
    try:
      with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        proc.wait(timeout=300)
    except OSError:
      inkex.errormsg('Program "%s" is not installed!' % args[0])
      exit()

  def write_tempfile(self):
    desc, tmpfile = tempfile.mkstemp(suffix='.svg', prefix='multipage-export-')
    file = os.fdopen(desc, 'wb')

    self.document.write(file)
    file.close()

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

    return path

  def remove_pt(self, path, fformat):
    if fformat == 'svg':
      xml = et.parse(path)
      svg = xml.getroot()

      svg.attrib['width']  = svg.attrib['width'].replace('pt', '')
      svg.attrib['height'] = svg.attrib['height'].replace('pt', '')
      xml.write(path)

  def inkscape_export(self, oid, fformat, output, tmpfile):
    self.run_command([
      'inkscape',
      '--vacuum-defs',
      '--export-id=%s' % oid,
      '--export-id-only',
      '--export-filename=%s' % output,
      tmpfile
    ])

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
    if self.options.exporter == 'inkscape':
      self.inkscape_export(oid, fformat, output, tmpfile)
    else:
      self.rsvg_export(oid, fformat, output, tmpfile)

  def pdftk_combine(self, output, file_paths):
    output  = self.file_path("%s-%s" % (output, 'All'), 'pdf')
    command = ['pdftk']

    command.extend(file_paths)
    command.extend(['cat', 'output', output])

    self.run_command(command)

  def export_files(self):
    tmpfile = self.write_tempfile()
    fformat = self.options.format
    fname   = self.options.name
    findex  = 0
    fpaths  = []

    for oid in self.options.ids:
      findex = findex + 1

      if self.options.autoname == 'true':
        output = self.file_path(oid, fformat)
      else:
        output = self.file_path("%s-%s" % (fname, findex), fformat)

      fpaths.append(output)

      if self.options.replace == 'false' and os.path.exists(output):
        continue

      self.export(oid, fformat, output, tmpfile)
      self.remove_pt(output, fformat)

    if self.options.combine == 'true' and fformat == 'pdf':
      self.pdftk_combine(fname, fpaths)

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
  exporter.run()
