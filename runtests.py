#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

if len(sys.argv) < 2:
  print "Too few arguments..."
  sys.exit(0)

ebin = sys.argv[1]
tests = ["cuter"]
for t in tests:
  print "Testing %s..." % t
  os.system("erl -noshell -pa %s -pa ../meck/ebin -eval \"eunit:test(%s, [verbose])\" -s init stop" % (ebin, t))