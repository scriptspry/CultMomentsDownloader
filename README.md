Simple to setup and use. Have to enable the Gmail API over [here](https://developers.google.com/gmail/api/quickstart/python) and download `credentials.json` and place it in this repository. Login with the gmail you've used to register with cult, and allow access to read mail.

```
git clone https://github.com/scriptspry/CultMomentsDownloader.git
cd CultMomentsDownloader

virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

mkdir -p ~/Pictures/CULT
python FetchCultMoments.py ~/Pictures/CULT
```