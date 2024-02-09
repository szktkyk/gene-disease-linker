import os
import csv
from modules import pubchem
import pandas as pd
import argparse
import json
import requests


parser = argparse.ArgumentParser(description="This script collects genes associated with a given disease from Open Targets Platform based on the ID, and writes it to a tsv file (./results).")
parser.add_argument("efoID",type=str, help="efo ontology ID")
parser.add_argument("size", type=int, help="the number of genes to collect")
args = parser.parse_args()

def main():
    """
    
    """

    disease_genes = []

    variables = {
    "efoId": args.efoID,
    "size": args.size
    }

    # Define your GraphQL query
    query_string = """
    query associatedTargets (
        $efoId: String!
        $size: Int!
        ) {
        disease(efoId: $efoId){
            id
            name
            associatedTargets (page:{size:$size, index:0}) {
                count
                rows {
                    target {
                    id
                    approvedSymbol
            }
        }
        }
    }
    }

    """

    base_url = "https://api.platform.opentargets.org/api/v4/graphql"
    r = requests.post(base_url, json={"query": query_string, "variables": variables})
    api_response = json.loads(r.text)
    genes = api_response["data"]["disease"]["associatedTargets"]["rows"]
    for i in genes:
        if i["target"]["id"] != None:
            ensg = i["target"]["id"]
            disease_genes.append(ensg)
        else:
            pass

    with open("./results/otp_genes.txt", "w") as output:
        for row in disease_genes:
            output.write(str(row) + '\n')


if __name__ == "__main__":
    main()