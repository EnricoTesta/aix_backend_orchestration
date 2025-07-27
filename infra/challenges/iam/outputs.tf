output "google_service_account--aix-worker" {
  value = google_service_account.aix-worker.account_id
}

output "google_service_account_iam_policy--aix-worker-policy" {
  value = google_service_account_iam_policy.aix-worker-policy.policy_data
}

output "google_project_iam_member--aix-worker-project-policy" {
  value = google_project_iam_member.aix-worker-project-policy.member
}