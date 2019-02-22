
class LabelledBlob:
    download_url: str
    labels: [str]

    def __init__(self, download_url: str, labels: [str]):
        self.download_url = download_url
        self.labels = labels