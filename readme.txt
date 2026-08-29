

FastAPI + Streamlit Telugu Text-to-Speech

The Streamlit container serves Cloud Run's public port (8501) and calls FastAPI on 127.0.0.1:8080. No separate backend URL or CORS configuration is needed. Use a Cloud Run service account with the roles/texttospeech.user role.

Local run:
  pip install -r requirements.txt
  bash start.sh

docker build -t us-central1-docker.pkg.dev/myownproject241124/my-repo/texttospeech:latest .
docker push us-central1-docker.pkg.dev/myownproject241124/my-repo/texttospeech:latest

gcloud run deploy texttospeech \
  --image us-central1-docker.pkg.dev/myownproject241124/my-repo/texttospeech:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501

gcloud run deploy texttospeech ^
  --image us-central1-docker.pkg.dev/myownproject241124/my-repo/texttospeech:latest ^
  --platform managed ^
  --region us-central1 ^
  --allow-unauthenticated ^
  --port 8501


gcloud run services logs read texttospeech --region us-central1




Git commands:
git init
git status
git add .
git status
git commit -m "Initial commit: Streamlit + Vertex AI chatbot"
git remote add origin https://github.com/<your-username>/texttospeechstreamlit.git  //template
git remote add origin https://github.com/mvsk2k/texttospeechstreamlit.git
git branch -M main
git push -u origin main

For any changes
git status
git add .
git commit -m "Change in readme.txt"
git push
