import argparse
import csv
from modules import mirtex
import os
import yaml


def main(config):
    """
    
    """
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    if not os.path.exists(f"./results/mirtex_genes.tsv"):
        disease_keyword = config["DISEASE_KEYWORD"]
        mirna_list,gene_list = mirtex.mirtex2list(disease_keyword)
        mirtex.mirtexlist2ensg(mirna_list,gene_list,f"./results/mirtex_genes.tsv")
        return print("02_mirtex2ensg has been completed")
    else:
        return print("The file already exists.")

if __name__ == "__main__":
    main("./config.yml")