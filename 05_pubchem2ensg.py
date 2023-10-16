# import argparse
import os
import csv
from modules import pubchem
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="This script extracts genes associated with disease from pubchem based on a pubchem disease ID, and writes it to a tsv file (./results).")
parser.add_argument("pubchem_diseaseID", help="pubchem disease ID (ncit disease term) to search for")
args = parser.parse_args()

def main():
    """
    
    """
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    pubchem_list = pubchem.pubchem2list(args.pubchem_diseaseID)
    print(pubchem_list)
    pubchem_list2 = []
    for i in pubchem_list:
        if i["PMID_PMCID"] != "":
            pubchem_list2.append(i)
        else:
            pass
    df = pd.DataFrame(pubchem_list2)
    df.to_csv(f"./results/pubchem_genes.tsv",sep="\t",index=False)

if __name__ == "__main__":
    main()