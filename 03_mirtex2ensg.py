import argparse
import csv
from modules import mirtex
import os

parser = argparse.ArgumentParser(description="This script extracts genes from miRTex based on a disease related keyword, and writes it to a tsv file (./results).")

parser.add_argument("keyword", help="keyword to search for")

args = parser.parse_args()

def main():
    """
    
    """
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    mirna_list,gene_list = mirtex.mirtex2list(args.keyword)
    mirtex.mirtexlist2ensg(mirna_list,gene_list,f"./results/mirtex_genes.tsv")
    mirtex.deleteduplicate()

if __name__ == "__main__":
    main()