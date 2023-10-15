import argparse
import csv
from modules import rnadisease
import pandas as pd
import os

parser = argparse.ArgumentParser(description="This script extracts genes from RNAdisease based on a DOID (Disease Ontology ID) and annotation score, and writes it to a tsv file (./results).")

parser.add_argument("DOID", type=str,help="DOID to search for")
parser.add_argument("score",type=float, help="Annotation score to search for")

args = parser.parse_args()

def main():
    """
    
    """
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    rnadisease.download_file()
    rnadisease.convert_xlsx_to_csv()
    rnadisease.rnadisease2genes(args.DOID,args.score)
    ensg_list = rnadisease.rna2ensg()
    df = pd.DataFrame(ensg_list)
    df.to_csv(f"./results/rnadisease_genes.tsv",sep="\t",index=False)

if __name__ == "__main__":
    main()