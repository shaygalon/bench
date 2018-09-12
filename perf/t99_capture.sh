#!/bin/bash

if [[ -z "$DURATION" ]] ; then
DURATION=60
fi
if [[ -z "$RES" ]] ; then
	RES=$(date '+%y-%m-%d_%H%M%S')
fi

mkdir -p $RES
cnt=0
for counters in \
	"r23,r24,r1,r2" \
	"r3,r5,r17,r56" \
	"rd2,rd3,re8,r8" \
	"rd4,rd5,r216,r217" \
	"r1b,r21,r22,r2e" \
	"r40,r41,r42,r43" \
	"r50,r51,r52,r53" \
	"r6a,r6d,r6e,r7e" \
	"r2d,r2e,r121,r122" \
	"r150,r151,r15c,r15e" \
	"r153,r154,r158,r159" \
	"r155,r156,r157,r15b" \
	"r100,r180,r181,r182" \
	"r183,r184,r185,r186" 
do
	perf stat -e cycles,instructions,$counters -x, -a -I 1000 > $RES/total_perf_set_$cnt.csv 2>&1 -- sleep $DURATION
	perf stat -e cycles,instructions,$counters -x, -a -I 1000 --per-core > $RES/percore_perf_set_$cnt.csv 2>&1 -- sleep $DURATION
	cnt=$[$cnt+1]
done

tar czf perf_capture.tgz $RES

