# NOTES

## Read-only file system errors

Note to self: if you get `[Errno 30] Read-only file system: '/home/sbx_user1051'` errors, it's probably because the NLTK library is trying to download its language packages at runtime.
I originally resolved this by pre-downloading them in the [Dockerfile](./Dockerfile), but recently upon upgrading to [0.15 of `unstructured`](./requirements.txt), 
I ran into this issue again because NLTK changed the libraries it uses, and this mysterious error came up again.

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
