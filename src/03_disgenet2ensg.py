import argparse
import os
import csv
from modules import disgenet
import pandas as pd
import yaml


def main(config):
    """
    
    """
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    if not os.path.exists(f"./results/disgenet_genes.tsv"):
        ncit = config["NCIT_DISEASE_TERM"]
        score = config["DISGENET_SCORE"]
        score = float(score)
        limit = config["DISGENET_PUBLICATION_LIMIT"]
        limit = int(limit)
        ensg_list = disgenet.disgenet2list(ncit,score,limit)
        print(ensg_list)
        df = pd.DataFrame(ensg_list)
        df.to_csv(f"./results/disgenet_genes.tsv",sep="\t",index=False)
        return print("03_disgenet2ensg has been completed")
    else:
        return print("The file already exists.")

if __name__ == "__main__":
    main("./config.yml")