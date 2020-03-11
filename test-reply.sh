#!/usr/bin/env bash

while true ; do 
  echo -en 'HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html; charset=utf-8\n\n{"rrset_values":["always_update"]}' | nc -w 1 -C -l 5000 ;
  echo
 done
