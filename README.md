Service for posting tagged images from Slack to Aaptiv's internal social feed

To start:

```
pip install -r requirements.txt
python init_db.py # if running for the first time
gunicorn app:api  # start server
```
