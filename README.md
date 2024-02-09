# gene-disease-linker
- This tool collects genes associated with a given disease.
    - The association is collected only if the evidence paper exists.
    - The following 6 databases are referred to collect gene-disease associations.
        - Open Targets Platform: [Ref](https://doi.org/10.1093/nar/gkac1046)
        - RNADisease: [Ref](https://doi.org/10.1093/nar/gkac814)
        - miRTex: [Ref](10.1371/journal.pcbi.1004391)
        - DisGeNET: [Ref](https://doi.org/10.1093/nar/gkw943)
        - PubChem: [Ref](https://ceur-ws.org/Vol-3415/paper-4.pdf)
        - gene2pubmed

- Also, this tool links your gene set with the collected information (gene-disease associations and evidences).
    - It would indicate how well your gene is studied for a given disease by checking the number of evidence papers annotated.

- INPUT
    - DISEASE KEYWORD (ex: "parkinson")
    - DISEASE ONTOLOGY ID (ex: "14330")
    - NCIT DISEASE TERM (ex: "C0030567")
    - PUBCHEM DISEASE ID (ex: "DZID8805")
    - EXPERIMENTAL FACTOR ONTOLOGY ID (ex: "MONDO_0021095")
    - TEXT FILE WITH ENSEMBL GENE IDs (ex: "gene_set.txt")

- OUTPUT
    - Genes associated with a given disease (ex: "test_bib_genes.tsv")
    - Your gene set annotated with evidence sources and papers (ex: "test_output.tsv")


## Environment Setup
1. `conda create -n generb python=3.11`
2. `conda activate gdl`
3. `conda install -c conda-forge ncbi-datasets-cli`
3. `cd gene-disease-bibliome`
4. `pip install -r requirements.txt`


## How to use
1. `python 01_rnadisease2ensg.py *DOID* *score(Int, Annotation score between 0 and 1.)*`
    - Look for the DOID (Disease Ontology ID) from this website (https://disease-ontology.org/)
2. `python 02_mirtex2ensg.py *the disease keyword*`
3. `python 03_disgenet2ensg.py *ncit disease ID* *score(to filter genes)*`
    - Look for ncit disease ID from this website (https://ncit.nci.nih.gov/ncitbrowser/pages/multiple_search.jsf?nav_type=terminologies)
4. `python 04_pubchem2ensg.py *pubchem disease ID*`
    - Download pc_disease.ttl.gz from this website (https://pubchem.ncbi.nlm.nih.gov/docs/rdf-disease) and look for the disease ID
5. `python 05_opentargets2ensg.py *efoID* *size(to filter the number of literatures)*`
    - Look for efoID from this website (https://platform.opentargets.org/)
6. `python 06_LinkGenesDisease.py *path to your text file including a list of genes* *efoID* *output_filename*`


## Example 
```
python -u 01_rnadisease2ensg.py "14330" 0.65 2>&1 | tee ./log/rnadisease_log.txt 
python -u 02_mirtex2ensg.py "parkinson" 2>&1 | tee ./log/mirtex_log.txt
python -u 03_disgenet2ensg.py "C0030567" 0.3 2>&1 | tee ./log/disgenet_log.txt
python -u 04_pubchem2ensg.py "DZID8805" 2>&1 | tee ./log/pubchem_log.txt
python -u 05_opentargets2ensg.py "MONDO_0021095" 5000 2>&1 | tee ./log/otp_log.txt
python -u 06_LinkGenesDisease.py "168genes.txt" "MONDO_0021095" "test" 2>&1 | tee ./log/linkgenesdisease_log.txt
```
