#! /usr/bin/env python

import sys
from aubio import source

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} <inputfile> [samplerate] [hop_size]')
        sys.exit(1)
    samplerate = 0
    if len(sys.argv) > 2: samplerate = int(sys.argv[2])
    hop_size = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    f = source(sys.argv[1], samplerate, hop_size)
    samplerate = f.samplerate

    total_frames, read = 0, f.hop_size
    while read:
        vec, read = f()
        total_frames += read
        if read < f.hop_size: break
    outstr = "read %.2fs" % (total_frames / float(samplerate))
    outstr += " (%d frames in" % total_frames
    outstr += " %d blocks" % (total_frames // f.hop_size)
    outstr += " at %dHz)" % f.samplerate
    outstr += f" from {f.uri}"
    print(outstr)
