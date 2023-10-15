import pandas as pd
import argparse
import os
import datetime
from modules import gene2pubmed

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
now = datetime.datetime.now(JST)
date = now.strftime("%Y%m%d")

parser = argparse.ArgumentParser(description="This script takes a list of ensembl genes in a text file, and categorizes them into reported and unreported genes.")

parser.add_argument("path_to_your_genes", help="path to your genes in a text file")
parser.add_argument("output", help="Add this to the output file name")


args = parser.parse_args()

def main():
    pfocr_df = pd.read_csv("./results/pfocr_genes.tsv",sep="\t")
    mirtex_df = pd.read_csv("./results/mirtex_genes.tsv",sep="\t")
    rnadisease_df = pd.read_csv("./results/rnadisease_genes.tsv", sep="\t")
    disgenet_df = pd.read_csv("./results/disgenet_genes_01.tsv", sep="\t")
    pubchem_df = pd.read_csv("./results/pubchem_genes.tsv", sep="\t")

    bib_df = pd.concat([pfocr_df,mirtex_df,rnadisease_df,disgenet_df,pubchem_df],ignore_index=True)
    # print(len(bib_df))
    bib_df["PMID_PMCID"] = bib_df["PMID_PMCID"].astype(str)
    bib_df = bib_df.groupby('gene').agg({'PMID_PMCID':','.join,'evidence':','.join}).reset_index()
    bib_df = bib_df.reset_index().rename(columns={"gene":"gene","PMID_PMCID":"PMID_PMCID","evidence":"evidence"})
    bib_df = bib_df.drop("index",axis=1)
    # print(len(bib_df))
    bib_df.to_csv(f"./results/{args.output}_bib_genes.tsv", sep='\t',index=False)
    # bib_df = bib_df.drop_duplicates(subset=["gene","PMID_PMCID","evidence"])

    # read a txt file and make a list
    with open(args.path_to_your_genes) as f:
        gene_list = f.read().splitlines()
    # print(gene_list)

    # make a empty dataframe
    new_df = pd.DataFrame(columns=["ensembl_ID","gene_name","reported_or_unreported","evidence","count_of_PMIDs_from_evidence","count_of_PMIDs_from_gene2pubmed","PMIDs_from_evidence",])

    new_gene_list = gene2pubmed.search_pmids(gene_list)
    # print({"ensg":ensg,"count":count,"pmids":pmids_str})

    for gene in gene_list:
        # if gene is in the first column of bib_df, append it to reported_df
        if gene in bib_df["gene"].values:
            reported_row = bib_df[bib_df["gene"]==gene].to_dict(orient="records")[0]
            for new_gene in new_gene_list:
                if new_gene["ensg"] == gene:
                    counts = new_gene["count"]
                    gene_name = new_gene["gene_name"]
                    reportedgene_dict = {"ensembl_ID":gene,"gene_name":gene_name,"reported_or_unreported":"reported","evidence":reported_row["evidence"],"count_of_PMIDs_from_evidence":len(reported_row["PMID_PMCID"].split(",")),"count_of_PMIDs_from_gene2pubmed":counts,"PMIDs_from_evidence":reported_row["PMID_PMCID"]}
                    print(reportedgene_dict)
                    new_df = new_df._append(reportedgene_dict,ignore_index=True)
                    continue
                else:
                    pass
        else:
            for new_gene in new_gene_list:
                if new_gene["ensg"] == gene:
                    counts = new_gene["count"]
                    gene_name = new_gene["gene_name"]
                    a_row = {"ensembl_ID":gene,"gene_name":gene_name,"reported_or_unreported":"unreported","evidence":"-","count_of_PMIDs_from_evidence":0,"count_of_PMIDs_from_gene2pubmed":counts,"PMIDs_from_evidence":"-"}
                    new_df = new_df._append(a_row,ignore_index=True)
                    continue
                else:
                    pass
    
    # make a new directory in results directory if it doesn't exist
    if not os.path.exists(f"./results/{date}"):
        os.mkdir(f"./results/{date}")

    new_df = new_df.sort_values("count_of_PMIDs_from_gene2pubmed",ascending=True)
    new_df.to_csv(f"./results/{date}/{args.output}_rankedgenes.tsv",sep="\t",index=False)
    

if __name__ == "__main__":
    main()