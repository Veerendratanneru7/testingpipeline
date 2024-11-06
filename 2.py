import os
import datetime
from google.cloud import certificatemanager_v1

def check_cert_expiry(request):
    client = certificatemanager_v1.CertificateManagerClient()
    
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION")  
    certificates = client.list_certificates(parent=f"projects/{project_id}/locations/{location}")
    
    all_certs_info = []
    for cert in certificates:
        expiry_date = cert.expire_time.date() 
        days_left = (expiry_date - datetime.datetime.now().date()).days
        all_certs_info.append(f"Certificate: {cert.name}, Expiry Date: {expiry_date}, Days Left: {days_left}")

    message = "\n".join(all_certs_info)
    print("Certificate Expiry Information:\n", message)

    return "Certificate expiry check completed and printed to console."
