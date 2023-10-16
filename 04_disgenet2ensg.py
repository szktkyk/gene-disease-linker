import argparse
import os
import csv
from modules import disgenet
import pandas as pd

parser = argparse.ArgumentParser(description="This script extracts genes associated with disease from DisGeNET based on a ncit disease term, and writes it to a tsv file (./results).")

parser.add_argument("linked_data_Disease_ID", help="linked life data disease ID to search for")
parser.add_argument("score", type=float,help="minimum score between 0 and 1 to filter the genes")
parser.add_argument("--limit", help="limit of the number of evidence pmids for each gene", default="15")

args = parser.parse_args()

def main():
    """
    
    """
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    ensg_list = disgenet.disgenet2list(args.linked_data_Disease_ID,args.score,args.limit)
    print(ensg_list)
    df = pd.DataFrame(ensg_list)
    df.to_csv(f"./results/disgenet_genes.tsv",sep="\t",index=False)

if __name__ == "__main__":
    main()