resource "google_service_account" "aix-worker" {
  account_id   = "aix-worker"
  display_name = "AIX Worker"
}

data "google_iam_policy" "aix-data" {
  binding {
    role = "roles/editor"

    members = [
      "serviceAccount:aix-worker@${var.project}.iam.gserviceaccount.com",
    ]
  }
}

resource "google_service_account_iam_policy" "aix-worker-policy" {
  service_account_id = google_service_account.aix-worker.name
  policy_data        = data.google_iam_policy.aix-data.policy_data
}

resource "google_project_iam_member" "aix-worker-project-policy" {
  project = var.project
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:aix-worker@${var.project}.iam.gserviceaccount.com"
}