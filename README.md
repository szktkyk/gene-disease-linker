# gene-disease-linker
- This tool collects genes associated with a given disease.
    - The association is collected only if the evidence paper exists.
    - The following 6 databases are referred to collect gene-disease associations.
        - Open Targets Platform: [Ref](https://doi.org/10.1093/nar/gkac1046)
        - RNADisease: [Ref](https://doi.org/10.1093/nar/gkac814)
        - miRTex: [Ref](https://doi.org/10.1371/journal.pcbi.1004391)
        - DisGeNET: [Ref](https://doi.org/10.1093/nar/gkw943)
        - PubChem: [Ref](https://ceur-ws.org/Vol-3415/paper-4.pdf)
        - gene2pubmed [Ref](https://ftp.ncbi.nlm.nih.gov/gene/DATA/)

- Also, this tool links your gene set with the collected information (gene-disease associations and evidences).
    - It would indicate how well your gene is studied for a given disease by checking the number of evidence papers annotated.

- INPUT
    - `DISEASE_ONTOLOGY_ID` (ex: "14330") for RNAdisease
        - Look for the DOID (Disease Ontology ID) from this website (https://disease-ontology.org/)
    - `RNA_DISEASE_SCORE` (ex: "0.65") for RNAdisease
    - `DISEASE_KEYWORD` (ex: "parkinson") for miRTex
    - `NCIT_DISEASE_TERM` (ex: "C0030567") for DisGeNET
        - Look for ncit disease ID from this website (https://ncit.nci.nih.gov/ncitbrowser/pages/multiple_search.jsf?nav_type=terminologies)
    - `DISGENET_SCORE` (ex: "0.3") for DisGeNET
    - `DISGENET_PUBLICATION_LIMIT` (ex: "15") for DisGeNET
    - `PUBCHEM_DISEASE_ID` (ex: "DZID8805") for PubChem
        - Download pc_disease.ttl.gz from this website (https://pubchem.ncbi.nlm.nih.gov/docs/rdf-disease) and look for the disease ID
    - `EXPERIMENTAL_FACTOR_ONTOLOGY_ID` (ex: "MONDO_0021095") for Open Targets Platform
        - Look for efoID from this website (https://platform.opentargets.org/)
    - `TEXT_FILE_WITH_ENSEMBL_GENE_IDs` (ex: "168genes.txt")
    - `OUTPUT_PREFIX` (ex: "20240208")

- OUTPUT
    - Genes associated with a given disease (ex: "20240214_bib_genes.tsv")
    - Your gene set annotated with evidence sources and papers (ex: "20240214_output.tsv")
        - See `Result Example` below.


## Environment Setup
1. Prepare your txt file with ensembl gene IDs separated by line.
2. Fill in `config.yml`. Please refer to my config.yml in this GitHub repository.
3.  `docker build -t gene-disease-linker .`



## How to run
1. `docker run --rm -it -v $(pwd):/app gene-disease-linker ./script/gene-disease-linker.sh`
2. output_files will be located in results directory.


## Result Example
| ensembl_ID       | ncbi_geneid | gene_name | availability_association | evidence    | count_of_PMIDs_from_evidence | count_of_PMIDs_from_gene2pubmed | PMIDs_from_evidence                           | PMIDs_from_gene2pubmed                                                                                     |
|------------------|-------------|-----------|--------------------------|-------------|-----------------------------|---------------------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| ENSG00000273015  | None        | None      | yes                      | RNAdisease  | 1                           | 0                               | 35173238                                     | -                                                                                                           |
| ENSG00000205837  | 400941      | LINC00487 | no                       | -           | 0                           | 0                               | -                                            | -                                                                                                           |
| ENSG00000176681  | 9884        | LRRC37A   | yes                      | OpenTargets | 4                           | 11                              | 19915575, 22451204, 31701892, 34064523       | 9628581, 12477932, 14702039, 15489334, 15533724, 16344560, 22419166, 22952603, 23064749, 29507755, 34373451 |
| ENSG00000136059  | 50853       | VILL      | no                       | -           | 0                           | 12                              | -                                            | 9179494, 12477932, 15489334, 16921170, 18006815, 18022635, 21873635, 26871637, 28514442, 30021884, 33961781, 36543142 |
| ENSG00000276168  | 6029        | RN7SL1    | yes                      | RNAdisease  | 1                           | 12                              | 27021022                                     | 6084597, 12086622, 12244299, 15667936, 17881443, 18067920, 23221635, 26718402, 28709002, 30165668, 33080218, 35143945 |
