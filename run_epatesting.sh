#### epatesting Start.sh ###
#!/bin/bash

echo "Iniciando Epa Testing..."
export _JAVA_OPTIONS=-Xmx1024m
cd /home/jgodoy/workspace-epa/epatesting
newName=$(date +%Y-%m-%d_%H%M%S)
newName=epa_output.$newName.txt
rm -r /home/jgodoy/workspace-epa/epatesting/evosuite-report/ /home/jgodoy/workspace-epa/epatesting/all_resumes.csv
nohup python3.6 /home/jgodoy/workspace-epa/epatesting/script.py "/home/jgodoy/workspace-epa/epatesting/config_example_local.ini" "/home/jgodoy/workspace-epa/epatesting/runs_example_local.ini" > /home/jgodoy/workspace-epa/epatesting/$newName &
exit 0
