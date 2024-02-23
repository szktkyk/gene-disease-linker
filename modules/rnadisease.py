import pandas as pd
import requests
import zipfile
import os
import csv
import re
import subprocess
import json
import xml.etree.ElementTree as ET


def download_file():
    print("RNADisease source data is downloading...")
    outputpath = "./results/rnadisease.zip"
    url = "http://www.rnadisease.org/static/download/RNADiseasev4.0_RNA-disease_experiment_all.zip"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(outputpath, 'wb') as file:
                file.write(response.content)           
            with zipfile.ZipFile("./results/rnadisease.zip") as existing_zip:
                existing_zip.extractall("./results/rnadisease")
                # delete the zip file  
                os.remove("./results/rnadisease.zip")
                print(f"Downloaded {url} to {outputpath}")
        else:
            print(f"Failed to download. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    

def convert_xlsx_to_csv():
    xlsx_file = "./results/rnadisease/RNADiseasev4.0_RNA-disease_experiment_all.xlsx"  
    csv_file = "./results/rnadisease/rnadisease.csv"  
    try:
        df = pd.read_excel(xlsx_file)
        df.to_csv(csv_file, index=False)
        print(f"Conversion successful: {xlsx_file} -> {csv_file}")
    except Exception as e:
        print(f"An error occurred: {e}")



def rnadisease2genes(DOID, score):
    """
    """
    # read rnadisease.csv and make a dataframe
    df = pd.read_csv("./results/rnadisease/rnadisease.csv")
    # extract the rows that have DOID
    df2 = df[df["DO ID"] == f"DOID:{DOID}"]
    df3 = df2[df2["specise"] == "Homo sapiens"]
    df4 = df3[df3["score"] > score]
    new_df = df4[["RNA Symbol","PMID"]]
    new_df["PMID"] = new_df["PMID"].astype(int)
    new_df["PMID"] = new_df["PMID"].astype(str)
    result = new_df.groupby('RNA Symbol')['PMID'].agg(','.join).reset_index()
    result = result.reset_index().rename(columns={"RNA Symbol":"RNA Symbol","PMID":"PMID"})
    result.to_csv("./results/rnadisease/pre_rnadisease.tsv", sep='\t',index=False, header=False)
    return print("pre file is done. Move to the next step")


def rna2ensg():
    """
    """
    ensg_list = []
    with open('./results/rnadisease/pre_rnadisease.tsv') as f:
        for line in f:
            gene = line.split("\t")[1]
            pmid = line.split("\t")[2]
            pmid = pmid.replace("\n","")
            print(f"\nrna:{gene}")
            # check if the end of the gene name is 5 digits
            if re.search(r'\d{6}$', gene):
                url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={gene}"
                try:
                    tree = use_eutils(url)
                except:
                    print(f"error at {url}")
                    continue

                geneid = get_text_by_tree("./IdList/Id", tree)
                print(f"ncbi geneid:{geneid}")
                if geneid == "":
                    print("No geneid. next loop")
                    continue
                else:
                    req = subprocess.run(
                        ["datasets", "summary", "gene", "gene-id", "{}".format(geneid)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                # req_geneid = json.loads(req.stdout.decode())
                # print(req_geneid)
                # exit()

            elif gene.startswith('hsa-'):
                gene_hsa = gene.split('-')
                gene = "".join(gene_hsa[1:3])
                print(gene)
                req = subprocess.run(
                    ["datasets", "summary", "gene", "symbol", "{}".format(gene), "--taxon","human"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            
            else:
                gene = gene
                req = subprocess.run(
                    ["datasets", "summary", "gene", "symbol", "{}".format(gene), "--taxon","human"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            req2 = json.loads(req.stdout.decode())
            # print(req2)
            # req2 = req.stdout.decode("json")
            if req2["total_count"] == 0:
                print("No results")
                continue
            elif req2["total_count"] == 1:
                try: 
                    ensg = req2["reports"][0]["gene"]["ensembl_gene_ids"][0]
                    ensg_list.append({"gene":ensg,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
                    print({"gene":ensg,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
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
                        if ensgid != "":
                            ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
                            print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
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
                    ensg_list.append({"gene":ensg,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
                    print({"gene":ensg,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
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
                        if ensgid != "":
                            ensg_list.append({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
                            print({"gene":ensgid,"PMID_PMCID":pmid,"evidence":"RNAdisease"})
                        else:
                            print("No ensgid. next loop")
                            continue

                    except:
                        # HGNCも取れなければ諦める
                        print("No results. next loop")
                        continue

    return ensg_list



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

