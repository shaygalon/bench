#!/bin/bash
D=6
locname=( homepage info hello req writer counter )
for t in 1 10 20 40 ; do
 for ct in 1 10 100 ; do
  c=$[$t*$ct]
  li=0
  wrk -d $D -t $t -c $c -s csv.lua http://127.0.0.1:8080 | grep CSV | sed -e "s/CSV/${locname[$li]},$t,$c/"
  for loc in servlets/servlet/RequestInfoExample servlets/servlet/HelloWorldExample servlets/servlet/RequestHeaderExample servlets/nonblocking/numberwriter ; do
   li=$[$li+1]
   wrk -d $D -t $t -c $c -s csv.lua http://127.0.0.1:8080/examples/$loc | grep CSV | sed -e "s/CSV/${locname[$li]},$t,$c/"
  done
  li=$[$li+1]
  wrk -d $D -t $t -c $c -s bytecounter.lua http://127.0.0.1:8080 | grep CSV | sed -e "s/CSV/${locname[$li]},$t,$c/"
 done
done


