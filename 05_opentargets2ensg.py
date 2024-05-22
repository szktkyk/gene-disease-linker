import os
import csv
from modules import pubchem
import pandas as pd
import argparse
import json
import requests
import yaml



def main(config):
    """
    
    """
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    
    if not os.path.exists(f"./results/otp_genes.txt"): 
        disease_genes = []
        efoid = config["EXPERIMENTAL_FACTOR_ONTOLOGY_ID"]
        variables = {
        "efoId": efoid,
        "size": 9999
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
        return print("05_opentargets2ensg has been completed")
    else:
        return print("The file already exists.")


if __name__ == "__main__":
    main("config.yml")