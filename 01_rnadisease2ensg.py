import argparse
import csv
from modules import rnadisease
import pandas as pd
import os
import yaml


def main(config):
    """
    
    """
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    doid = config["DISEASE_ONTOLOGY_ID"]
    score = config["RNA_DISEASE_SCORE"]
    score = float(score)
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    if not os.path.exists(f"./results/rnadisease/RNADiseasev4.0_RNA-disease_experiment_all.xlsx"):
        rnadisease.download_file()
    if not os.path.exists(f"./results/rnadisease/rnadisease.csv"):
        rnadisease.convert_xlsx_to_csv()
    if not os.path.exists(f"./results/rnadisease/pre_rnadisease.tsv"):
        rnadisease.rnadisease2genes(doid,score)
    if not os.path.exists(f"./results/rnadisease_genes.tsv"):
        ensg_list = rnadisease.rna2ensg()
        df = pd.DataFrame(ensg_list)
        df.to_csv(f"./results/rnadisease_genes.tsv",sep="\t",index=False)
        return print("01_rnadisease2ensg has been completed")
    else:
        return print("The file already exists.")

if __name__ == "__main__":
    main("./config.yml")