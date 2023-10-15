import requests
from bs4 import BeautifulSoup
import subprocess
import json
import xml.etree.ElementTree as ET
import pandas as pd

def mirtex2list(keyword):
    response = requests.get(f"https://research.bioinformatics.udel.edu/miRTex/search/{keyword}")
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table")

    mirna_list = []
    gene_list = []
    for row in table.find_all("tr"):
        # print(row)
        # Find the cells in each row
        cells = row.find_all("td")
        # print(cells)
        if len(cells) >= 7:
            pmid = cells[0].text.strip()
            mirna = cells[1].text.strip()
            gene = cells[2].text.strip()
            mirna_list.append({"mirna":mirna,"PMID":pmid})
            gene_list.append({"gene":gene,"PMID":pmid})
        else:
            continue

    return mirna_list,gene_list


def mirtexlist2ensg(mirna_list,gene_list,output_filepath):
    ensg_list = []
    for i in mirna_list:
        mirna = i["mirna"]
        pmid = i["PMID"]
        print(f"\nmirna:{mirna}")

        if mirna.startswith('MicroRNA'):
            mirna = mirna.replace('MicroRNA-','miR')
            # print(mirna)
        elif mirna.startswith('microRNA'):
            mirna = mirna.replace('microRNA-','miR')
            # print(mirna)

        else:
            mirna = i["mirna"]

        mi_list = mirna.split('-')
        mirna = "".join(mi_list[0:2])
        # print(mirna)

        req = subprocess.run(
                ["datasets", "summary", "gene", "symbol", "{}".format(mirna), "--taxon","human"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        req2 = json.loads(req.stdout.decode())
        # print(req2)
        # req2 = req.stdout.decode("json")
        if req2["total_count"] == 0:
            print("Total count 0, No results. next loop")
        elif req2["total_count"] == 1:
            try: 
                ensg = req2["reports"][0]["gene"]["ensembl_gene_ids"][0]
                ensg_list.append({"gene":ensg,"PMID_PMCID":pmid,"evidence":"miRTex"})
                print({"gene":ensg,"PMID_PMCID":pmid,"evidence":"miRTex"})
            except:
                try:
                    # ENSGでないものは、HGNCのIDを取得する
                    hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]               
                    id = hgnc.split(':')[1]
                    # print(id)
                    url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                    try:
                        tree = use_eutils(url)
                    except:
                        print(f"error at {url}")
                        continue

                    ensgid = get_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                    if ensgid != "":
                        ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                        print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                    else:
                        print("No ensgid. next loop")
                        continue

                except:
                    # HGNCも取れなければ諦める
                    print("No results. next loop.")
                    continue

        elif req2["total_count"] > 1:
            print("More than one result")
            print(req2["total_count"])
            try:
                ensg = req2["reports"][0]["gene"]["ensembl_gene_ids"][0]
                ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
            except:
                try:
                    # ENSGでないものは、HGNCのIDを取得する
                    hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]             
                    id = hgnc.split(':')[1]
                    print(id)
                    url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                    try:
                        tree = use_eutils(url)
                    except:
                        print(f"error at {url}")
                        continue

                    ensgid = get_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                    print(ensgid)
                    if ensgid != "":
                        ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                        print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                    else:
                        print("No ensgid. next loop")
                        continue
                except:
                    # HGNCも取れなければ諦める
                    print("No results. next loop")
                    continue

    print(gene_list)
    for i in gene_list:
        gene = i["gene"]
        pmid = i["PMID"]
        print("\ngene:{}".format(gene))
        if gene.isascii() == False:
            print("gene is not ascii")
            continue
        else:
            req = subprocess.run(
                    ["datasets", "summary", "gene", "symbol", "{}".format(gene), "--taxon","human"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            req2 = json.loads(req.stdout.decode())
            # print(req2)
            # req2 = req.stdout.decode("json")
        if req2["total_count"] == 0:
            print("Total count 0, No results. next loop")
        elif req2["total_count"] == 1:
            try: 
                ensg = req2["reports"][0]["gene"]["ensembl_gene_ids"][0]
                ensg_list.append({"gene":ensg,"PMID_PMCID":pmid,"evidence":"miRTex"})
                print({"gene":ensg,"PMID_PMCID":pmid,"evidence":"miRTex"})
            except:
                try:
                    # ENSGでないものは、HGNCのIDを取得する
                    hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]
                    id = hgnc.split(':')[1]
                    url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                    try:
                        tree = use_eutils(url)
                    except:
                        print(f"error at {url}")
                        continue

                    ensgid = get_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                    if ensgid != "":
                        ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                        print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                    else:
                        print("No ensgid. next loop")
                        continue

                except:
                    # HGNCも取れなければ諦める
                    print("No results. next loop")
                    continue

        elif req2["total_count"] > 1:
            print("More than one result")
            print(req2["total_count"])
            try:
                ensg = req2["reports"][0]["gene"]["ensembl_gene_ids"][0]
                ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
            except:
                try:
                    # ENSGでないものは、HGNCのIDを取得する
                    hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]                
                    id = hgnc.split(':')[1]
                    url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                    try:
                        tree = use_eutils(url)
                    except:
                        print(f"error at {url}")
                        continue

                    ensgid = get_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                    if ensgid != "":
                        ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                        print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"miRTex"})
                    else:
                        print("No ensgid. next loop")
                        continue
                except:
                    # HGNCも取れなければ諦める
                    print("No results. next loop")
                    continue

    df = pd.Dataframe(ensg_list)
    # Delete duplicate
    df["PMID_PMCID"] = df["PMID_PMCID"].astype(str)
    result = df.groupby('gene')['PMID_PMCID'].agg(','.join).reset_index()
    result = result.reset_index().rename(columns={"gene":"gene","PMID_PMCID":"PMID_PMCID","evidence":"evidence"})
    result = result.drop("index",axis=1)
    result["evidence"] = "miRTex"
    result.to_csv(output_filepath, sep='\t',index=False)
    return print("mirtex_genes.tsv done")




    
def get_text_by_tree(treepath, element):
    """
    Parameters:
    ------
    treepath: str
        path to the required information

    element: str
        tree element

    Returns:
    ------
    information: str
        parsed information from XML

    None: Null
        if information could not be parsed.

    """
    if element.find(treepath) is not None:
        return element.find(treepath).text
    else:
        return ""


def use_eutils(api_url):
    """
    function to use API

    Parameters:
    -----
    api_url: str
        URL for API

    Return:
    --------
    tree: xml
        Output in XML

    """
    req = requests.get(api_url)
    req.raise_for_status()
    tree = ET.fromstring(req.content)
    return tree