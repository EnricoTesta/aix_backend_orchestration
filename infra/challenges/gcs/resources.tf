resource "google_storage_bucket" "data-bucket" {
  default_event_based_hold    = "false"
  force_destroy               = "false"
  location                    = "EU"
  name                        = "${var.bucket}"
  project                     = "${var.project}"
  requester_pays              = "false"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = "true"
}

resource "google_storage_bucket_acl" "data-bucket" {
  bucket = "${var.bucket}"
}

resource "google_storage_bucket_iam_policy" "data-bucket" {
  bucket = "b/${var.bucket}"

  policy_data = <<POLICY
{
  "bindings": [
    {
      "members": [
        "projectEditor:${var.project}",
        "projectOwner:${var.project}"
      ],
      "role": "roles/storage.legacyBucketOwner"
    },
    {
      "members": [
        "projectViewer:${var.project}"
      ],
      "role": "roles/storage.legacyBucketReader"
    },
    {
      "members": [
        "projectEditor:${var.project}",
        "projectOwner:${var.project}"
      ],
      "role": "roles/storage.legacyObjectOwner"
    },
    {
      "members": [
        "projectViewer:${var.project}"
      ],
      "role": "roles/storage.legacyObjectReader"
    }
  ]
}
POLICY
}
