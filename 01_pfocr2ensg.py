import argparse
import os
import csv
from modules import pfocr
import pandas as pd

parser = argparse.ArgumentParser(description="This script extracts genes from Pathway Figure OCR based on a keyword, and writes it to a tsv file (./results).")

parser.add_argument("keyword", help="keyword to search for")
# parser.add_argument("column", type=int,help="column to search for the keyword. 0 for title, 2 for taxonomy")
# parser.add_argument("--taxonomy", help="NCBI taxonomy name if you are interested in genes except for Homo sapiens", default="Homo sapiens")

args = parser.parse_args()

def main():
    """
    
    """
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    pfocr.pfocr2genes(0,args.keyword)
    ensg_list = pfocr.genes2ensg(f"./results/pre_pfocr_genes.tsv","Homo sapiens")
    # os.remove("pfocr_genes.tsv")
    df = pd.DataFrame(ensg_list)
    df.to_csv(f"./results/pfocr_genes.tsv",sep="\t",index=False)

if __name__ == "__main__":
    main()