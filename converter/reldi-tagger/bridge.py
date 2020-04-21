import os
import io
import pycrfsuite

## NE KORISTI SE OVO
python3_command = "python2 ..\\reldi-tagger-master\\tagger.py sr -l"  # launch your python2 script using bash

process = os.popen(python3_command) #RADI

instream, output = os.popen2(python3_command)



print(output.read())


print(process.read()) #RADI
