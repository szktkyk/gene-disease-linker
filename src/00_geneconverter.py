import pandas as pd
import argparse
import re
from modules import rnadisease
import subprocess
import json

parser = argparse.ArgumentParser(description="This script converts a list of gene names (text file with) to a list of ensembl gene ids (will write it to a text file in src directory).")

parser.add_argument("path_to_your_genes", help="path to your genes in a text file") 
parser.add_argument("output", help="Add this to the output file name")

args = parser.parse_args()

def gene2ensg():
    """
    """
    ensg_list = []
    with open(args.path_to_your_genes) as f:
        gene_list = f.read().splitlines()
        for gene in gene_list:
            print(f"\ngene:{gene}")
            if re.search(r'\d{5}$', gene):
                url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={gene}"
                try:
                    tree = rnadisease.use_eutils(url)
                except:
                    print(f"error at {url}")
                    continue

                geneid = rnadisease.get_text_by_tree("./IdList/Id", tree)
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
                    ensg_list.append(ensg)
                    print(f"ensg:{ensg}")
                except:
                    try:
                        # ENSGでないものは、HGNCのIDを取得する
                        hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]
                        id = hgnc.split(':')[1]
                        print(id)
                        url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                        try:
                            tree = rnadisease.reuse_eutils(url)
                        except:
                            print(f"error at {url}")
                            continue

                        ensgid = rnadisease.reget_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                        if ensgid != "":
                            ensg_list.append(ensgid)
                            print(f"ensg:{ensgid}")
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
                    ensg_list.append(ensg)
                    print(f"ensg:{ensg}")
                except:
                    try:
                        # ENSGでないものは、HGNCのIDを取得する
                        hgnc = req2["reports"][0]["gene"]["nomenclature_authority"]["identifier"]
                        id = hgnc.split(':')[1]
                        url = f"https://rest.genenames.org/fetch/hgnc_id/{id}"
                        try:
                            tree = rnadisease.use_eutils(url)
                        except:
                            print(f"error at {url}")
                            continue

                        ensgid = rnadisease.get_text_by_tree("./result/doc/str[@name='ensembl_gene_id']", tree)
                        if ensgid != "":
                            ensg_list.append(ensgid)
                            print(f"ensg:{ensgid}")
                        else:
                            print("No ensgid. next loop")
                            continue

                    except:
                        # HGNCも取れなければ諦める
                        print("No results. next loop")
                        continue
    df = pd.DataFrame(ensg_list)
    df.to_csv(f"./src/{args.output}.tsv",sep="\t",index=False)

if __name__ == "__main__":
    gene2ensg()