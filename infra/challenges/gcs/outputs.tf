output "google_storage_bucket_acl_data-bucket_id" {
  value = "${google_storage_bucket_acl.data-bucket.id}"
}

output "google_storage_bucket_iam_policy_data-bucket_id" {
  value = "${google_storage_bucket_iam_policy.data-bucket.id}"
}

output "google_storage_bucket_data-bucket_name" {
  value = "${google_storage_bucket.data-bucket.name}"
}

output "google_storage_bucket_data-bucket_self_link" {
  value = "${google_storage_bucket.data-bucket.self_link}"
}
