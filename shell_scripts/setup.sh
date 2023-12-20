# mkdir -p ./output_data

# Install requirements
pip3 install -r Pipeline/requirements.txt
echo -e "\nPIPELINE REQUIREMENTS INSTALLED."
sleep 1
pip3 install -r Dashboard/requirements.txt
echo -e "\nDASHBOARD REQUIREMENTS INSTALLED."
sleep 1

# Setup DB Schema
source shell_scripts/run_schema.sh
echo -e "\nDATABASE SCHEMA CONFIGURED."
sleep 1

echo -e "\n\nSETUP COMPLETE."
sleep 3