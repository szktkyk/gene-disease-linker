# import argparse
import os
import csv
from modules import pubchem
import pandas as pd
import argparse
import yaml


def main(config):
    """
    
    """
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    if not os.path.exists(f"./results"):
        os.mkdir(f"./results")
    pubchem_diseaseid = config["PUBCHEM_DISEASE_ID"]
    if not os.path.exists(f"./results/pubchem_genes.tsv"):
        pubchem_list = pubchem.pubchem2list(pubchem_diseaseid)
        print(pubchem_list)
        pubchem_list2 = []
        for i in pubchem_list:
            if i["PMID_PMCID"] != "":
                pubchem_list2.append(i)
            else:
                pass
        df = pd.DataFrame(pubchem_list2)
        df.to_csv(f"./results/pubchem_genes.tsv",sep="\t",index=False)
        return print("03_pubchem2ensg has been completed")
    else:
        return print("The file already exists.")

if __name__ == "__main__":
    main("./config.yml")