#!/bin/bash

CHECK_FILE_PATHS=(
    "./results/rnadisease_genes.tsv"
    "./results/mirtex_genes.tsv"
    "./results/disgenet_genes.tsv"
    "./results/pubchem_genes.tsv"
    "./results/otp_genes.tsv"
)

download_needed=false
DATASETS="./datasets"
DATAFORMAT="./dataformat"


if [ ! -f "$DATASETS" ]; then
    dataset_URL='https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets'
    echo "Downloading file from $dataset_URL..."
    curl -o "$DATASETS" "$dataset_URL"
else
    echo "File $DATASETS found. No need to download."
fi

if [ ! -f "$DATAFORMAT" ]; then
    dataformat_URL='https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/dataformat'
    echo "Downloading file from $dataformat_URL..."
    curl -o "$DATAFORMAT" "$dataformat_URL"
    chmod +x datasets dataformat
else
    echo "File $DATAFORMAT found. No need to download."
fi


# list of scripts to run
scripts=(
    "src/01_rnadisease2ensg.py"
    "src/02_mirtex2ensg.py"
    "src/03_disgenet2ensg.py"
    "src/04_pubchem2ensg.py"
    "src/05_opentargets2ensg.py"
    "src/06_LinkGenesDisease.py" 
    )
logname=${script#src/}

# log directory
log_dir="logs"
mkdir -p "$log_dir"


# # run each script and log output
for script in "${scripts[@]}"; do

    script_base=$(basename "$script" .py)  # 拡張子を除いたファイル名を取得
    log_file="$log_dir/$script_base.txt"  # 固定のログファイル名を使用

    echo "Running $script and logging to $log_file"
    # PIPEFAILオプションを設定
    set -o pipefail

    python -u "$script" 2>&1 | tee "$log_file"
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "$script executed successfully."
    else
        echo "$script encountered an error(Exit code: $EXIT_CODE).. Check $log_file for details."
    fi

done


# delete_files=true
# for CHECK_FILE_PATH in "${CHECK_FILE_PATHS[@]}"; do
#     if [ ! -f "$CHECK_FILE_PATH" ]; then
#         echo "File $CHECK_FILE_PATH does not exist. Not all files were created."
#         delete_files=false
#         break
#     fi
# done

# if $delete_files; then
#     echo "All files exist. Deleting downloaded file."
#     rm -f "$DATASETS"
#     rm -f "$DATAFORMAT"
# else
#     echo "Some files do not exist. No files deleted."
# fi

date=$(date +%Y%m%d)

RESULTS_DIR="./results/$date"

FILE_PATTERN="*_output.tsv"

FILES_FOUND=$(find "$RESULTS_DIR" -name "$FILE_PATTERN")

if [ -n "$FILES_FOUND" ]; then
    echo "Files found:"
    echo "$FILES_FOUND"
    echo "Script completed successfully."
    exit 0
else
    echo "Warning: No files matching the pattern '$RESULTS_DIR/$FILE_PATTERN' were found."
    exit 1
fi
