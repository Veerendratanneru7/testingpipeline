gcloud functions deploy checkCertExpiry \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --region YOUR_REGION \
    --set-env-vars "SLACK_TOKEN=your_slack_token,SLACK_CHANNEL=your_channel,GCP_PROJECT_ID=your_project,GCP_LOCATION=your_location"


gcloud scheduler jobs create http certExpiryCheck \
    --schedule="0 10 * * 1" \
    --time-zone="Your/Time_Zone" \
    --uri="https://REGION-PROJECT_ID.cloudfunctions.net/checkCertExpiry" \
    --http-method=GET \
    --oidc-service-account-email="YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com"
