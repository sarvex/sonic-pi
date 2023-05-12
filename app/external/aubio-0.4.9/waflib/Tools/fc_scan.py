#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import re
INC_REGEX="""(?:^|['">]\s*;)\s*(?:|#\s*)INCLUDE\s+(?:\w+_)?[<"'](.+?)(?=["'>])"""
USE_REGEX="""(?:^|;)\s*USE(?:\s+|(?:(?:\s*,\s*(?:NON_)?INTRINSIC)?\s*::))\s*(\w+)"""
MOD_REGEX="""(?:^|;)\s*MODULE(?!\s+(?:PROCEDURE|SUBROUTINE|FUNCTION))\s+(\w+)"""
SMD_REGEX="""(?:^|;)\s*SUBMODULE\s*\(([\w:]+)\)\s*(\w+)"""
re_inc=re.compile(INC_REGEX,re.I)
re_use=re.compile(USE_REGEX,re.I)
re_mod=re.compile(MOD_REGEX,re.I)
re_smd=re.compile(SMD_REGEX,re.I)
class fortran_parser(object):
	def __init__(self,incpaths):
		self.seen=[]
		self.nodes=[]
		self.names=[]
		self.incpaths=incpaths
	def find_deps(self,node):
		txt=node.read()
		incs=[]
		uses=[]
		mods=[]
		for line in txt.splitlines():
			if m := re_inc.search(line):
				incs.append(m.group(1))
			if m := re_use.search(line):
				uses.append(m.group(1))
			if m := re_mod.search(line):
				mods.append(m.group(1))
			if m := re_smd.search(line):
				uses.append(m.group(1))
				mods.append('{0}:{1}'.format(m.group(1),m.group(2)))
		return(incs,uses,mods)
	def start(self,node):
		self.waiting=[node]
		while self.waiting:
			nd=self.waiting.pop(0)
			self.iter(nd)
	def iter(self,node):
		incs,uses,mods=self.find_deps(node)
		for x in incs:
			if x in self.seen:
				continue
			self.seen.append(x)
			self.tryfind_header(x)
		for x in uses:
			name = f"USE@{x}"
			if name not in self.names:
				self.names.append(name)
		for x in mods:
			name = f"MOD@{x}"
			if name not in self.names:
				self.names.append(name)
	def tryfind_header(self,filename):
		found=None
		for n in self.incpaths:
			found=n.find_resource(filename)
			if found:
				self.nodes.append(found)
				self.waiting.append(found)
				break
		if not found and filename not in self.names:
			self.names.append(filename)
