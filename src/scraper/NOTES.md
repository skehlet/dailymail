# NOTES

## NLTK troubleshooting

paths: list[str] = []

for path in nltk.data.path:
    if not path.endswith("nltk_data"):
        path = os.path.join(path, "nltk_data")
    paths.append(path)

nltk.find(f"taggers/averaged_perceptron_tagger_eng", paths=paths)

nltk.find(f"tokenizers/punkt_tab", paths=paths)


## TODOS

* Why is unstructured so much slower now than the previous version?
* Look into why this site took  54.92250609397888 seconds for unstructured to partition: https://www.carsales.com.au/editorial/details/spy-pics-2025-volkswagen-id-2-spotted-147136/
