#!/usr/bin/env python

import sys, azutils

src = sys.argv[1]
dst = sys.argv[2]

f = open(src, 'r')
src_lines = f.readlines()
f.close()

f = open(dst, 'r')
dst_lines = f.readlines()
f.close()

src_lines = azutils.readToSplitList(src)
dst_lines = azutils.readToSplitList(dst)

src_dict = {}
for line in src_lines:
	line_list = line.strip().split('\t')
	src_dict[line_list[0]] = line_list[2]

dst_dict = {}
for line in dst_lines:
	line_list = line.strip().split('\t')
	dst_dict[line_list[0]] = line_list[2]

for key in dst_dict:
	if key in src_dict:
		src_time = azutils.invTimetuple(azutils.invDateTimeStr(src_dict[key]))
		dst_time = azutils.invTimetuple(azutils.invDateTimeStr(dst_dict[key]))
		if src_