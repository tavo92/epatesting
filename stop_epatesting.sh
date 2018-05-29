#### epatesting Stop.sh ###
#!/bin/bash

echo "Deteniendo proceso Python..."
pkill python3.6
echo "Deteniendo procesos Java..."
pkill java
exit 0
