import json
import requests
import pandas as pd


def get_evidence_otp(genes:list,efoID:str,size:int):
    opt_data = []
    for gene in genes:
        print(gene)

        pmids = []
        variables = {
        "ensemblId": gene,
        "efoId": efoID,
        "size": size
        }

        # Define your GraphQL query
        query_string = """
        query OpenTargetsGeneticsQuery(
        $ensemblId: String!
        $efoId: String!
        $size: Int!
        ) {
        disease(efoId: $efoId) {
            id
            evidences(
            ensemblIds: [$ensemblId]
            enableIndirect: true
            size: $size
            datasourceIds: ["crispr_screen","europepmc","ot_genetics_portal","clingen","gene_burden",]
            ) {
            rows {
                id
                disease {
                id
                name
                }
                literature
                score
            }
            }
        }
        }
        """


        base_url = "https://api.platform.opentargets.org/api/v4/graphql"

        # Perform POST request and check status code of response
        r = requests.post(base_url, json={"query": query_string, "variables": variables})
        # print(r.status_code)
        # Transform API response from JSON into Python dictionary and print in console
        api_response = json.loads(r.text)
        evidences = api_response["data"]["disease"]["evidences"]["rows"]
        for i in evidences:
            if i["literature"] != None:
                pmid = i["literature"][0]
                pmids.append(pmid)
            else:
                pass
        pmid_str = ','.join(pmids)
        opt_data.append({"gene": gene,"PMID_PMCID": pmid_str, "evidence": "OpenTargets"})

    df = pd.DataFrame(opt_data)
    return df