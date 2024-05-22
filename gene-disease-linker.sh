#!/bin/bash

CHECK_FILE_PATHS=(
    "./results/rnadisease_genes.tsv"
    "./results/mirtex_genes.tsv"
    "./results/disgenet_genes.tsv"
    "./results/pubchem_genes.tsv"
    "./results/otp_genes.tsv"
)

download_needed=false
DATASETS="datasets"
DATAFORMAT="dataformat"

for CHECK_FILE_PATH in "${CHECK_FILE_PATHS[@]}"; do
    if [ ! -f "$CHECK_FILE_PATH" ]; then
        echo "File $CHECK_FILE_PATH not found. Downloading NCBI datasets cli"
        download_needed=true
        break
    fi
done

if $download_needed; then
    dataset_URL='https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'
    echo "Downloading file from $dataset_URL..."
    curl -o "$DATASETS" "$dataset_URL"

    dataformat_URL='https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/dataformat'
    echo "Downloading file from $dataformat_URL..."
    curl -o "$DATAFORMAT" "$dataformat_URL"
    chmod +x datasets dataformat

else
    echo "All files found. No need to download."
fi


# list of scripts to run
scripts=("01_rnadisease2ensg.py")

# log directory
log_dir="logs"
mkdir -p "$log_dir"

# run each script and log output
for script in "${scripts[@]}"; do
    log_file="$log_dir/${script%.py}.log"
    echo "Running $script and logging to $log_file"
    python -u "$script" 2>&1 | tee "$log_file"
    if [ $? -eq 0 ]; then
        echo "$script executed successfully."
    else
        echo "$script encountered an error. Check $log_file for details."
    fi

done


delete_files=true
for CHECK_FILE_PATH in "${CHECK_FILE_PATHS[@]}"; do
    if [ ! -f "$CHECK_FILE_PATH" ]; then
        echo "File $CHECK_FILE_PATH does not exist. Not all files were created."
        delete_files=false
        break
    fi
done

if $delete_files; then
    echo "All files exist. Deleting downloaded file."
    rm -f "datasets"
    rm -f "dataformat"
else
    echo "Some files do not exist. No files deleted."
fi

echo "Script completed."