#### epatesting Start.sh ###
#!/bin/bash

echo "Iniciando Epa Testing..."
cd /home/jgodoy/workspace-epa/epatesting
newName=$(date +%Y-%m-%d_%H%M%S)
newName=epa_output.$newName
rm -r results/
nohup python3.6 /home/jgodoy/workspace-epa/epatesting/script.py "/home/jgodoy/workspace-epa/epatesting/config_example.ini"  > /home/jgodoy/workspace-epa/epatesting/$newName &
exit 0
