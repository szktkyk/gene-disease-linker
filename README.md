# GeneRankerBibliome
Prioritize candidate genes by bibliome analysis
- This is a tool to categorize genes (including non-coding genes) into two types `reported in literature before` or `unreported` for a specific disease. 
    - if reported, evidence literature IDs will be shown. 
- This tool also ranks the genes based on the number of PubMed articles annotated to each gene in gene2pubmed.
- Input
    - A list of your interested genes in a text file (Ensembl gene ID). I have prepared the gene ID converter (00_geneconverter.py) if you have a list of gene names.
    - A keyword of disease name for 01_pfocr2ensg.py and 03_mirtex2ensg.py
    - A DOID (Disease Ontology ID) for 02_rnadisease2ensg.py
    - A NCIT disease term for 04_disgenet2ensg.py
    - A pubchem disease ID for 05_pubchem2ensg.py
- Output
    - A tsv file of showing all the genes that have been studied for the specific disease (including the evidence literature IDs) based on 5 bibliome databases.
    - A tsv file of categorized and ranked genes of your interest.

## Requirements


## Environment Setup
1. `conda create -n generb python=3.11`
2. `conda activate generb`
3. `conda install -c conda-forge ncbi-datasets-cli`
3. `cd GeneRankerBibliome`
4. `pip install -r requirements.txt`


## How to use
1. python 01_pfocr2ensg.py *the disease keyword* *0 or 2 (0 for search titles, 2 for search taxonomy name)*
2. python 02_rnadisease2ensg.py *DOID* *(int) score (Annotation score between 0 and 1.)*
3. python 03_mirtex2ensg.py *the disease keyword*
4. python 04_disgenet2ensg.py *ncit disease term* *score (to filter genes)*
5. python 05_pubchem2ensg.py *pubchem disease ID*
6. python 06_RankingGenes.py *path to your text file including a list of genes* *output_filename*



## Example
```
python -u 01_pfocr2ensg.py "parkinson" 0 2>&1 | tee ./log/pfocr_log.txt
python -u 02_rnadisease2ensg.py "14330" 0.65 2>&1 | tee ./log/rnadisease_log.txt` 
python -u 03_mirtex2ensg.py "parkinson" 2>&1 | tee ./log/mirtex_log.txt`
python -u 04_disgenet2ensg.py xxxxxxxx 2>&1 | tee ./log/disgenet_log.txt`
python -u 05_pubchem2ensg.py "DZID8805" 2>&1 | tee ./log/pubchem_log.txt`
python -u 06_RankingGenes.py "./" "parkinson_bibliome" 2>&1 | tee ./log/rankgenes_log.txt`
```
