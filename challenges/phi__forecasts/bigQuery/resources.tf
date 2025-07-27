resource "google_bigquery_dataset" "phi-data-prod-evaluation_layer" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "OWNER"
    user_by_email = "admin@ai-exchange.io"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                      = "evaluation_layer"
  default_partition_expiration_ms = "0"
  delete_contents_on_destroy      = "false"
  location                        = "EU"
  project                         = "${var.project}"
}

resource "google_bigquery_dataset" "phi-data-prod-inference_layer" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "OWNER"
    user_by_email = "admin@ai-exchange.io"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                      = "inference_layer"
  default_partition_expiration_ms = "0"
  delete_contents_on_destroy      = "false"
  location                        = "EU"
  project                         = "${var.project}"
}

resource "google_bigquery_dataset" "phi-data-prod-information_layer" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "OWNER"
    user_by_email = "admin@ai-exchange.io"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                      = "information_layer"
  default_partition_expiration_ms = "0"
  delete_contents_on_destroy      = "false"
  location                        = "EU"
  project                         = "${var.project}"
}

resource "google_bigquery_dataset" "phi-data-prod-raw_data_layer" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "OWNER"
    user_by_email = "admin@ai-exchange.io"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                      = "raw_data_layer"
  default_partition_expiration_ms = "0"
  delete_contents_on_destroy      = "false"
  location                        = "EU"
  project                         = "${var.project}"
}

resource "google_bigquery_dataset" "phi-data-prod-training_layer" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "OWNER"
    user_by_email = "admin@ai-exchange.io"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  dataset_id                      = "training_layer"
  default_partition_expiration_ms = "0"
  delete_contents_on_destroy      = "false"
  location                        = "EU"
  project                         = "${var.project}"
}

resource "google_bigquery_table" "phi-data-prod-raw_data_layer-data" {
  dataset_id      = "${google_bigquery_dataset.phi-data-prod-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"Ref_DateTime\",\"type\":\"DATETIME\"},{\"name\":\"Feature_1\",\"type\":\"INT64\"},{\"name\":\"Feature_2\",\"type\":\"INT64\"},{\"name\":\"Feature_3\",\"type\":\"FLOAT\"},{\"name\":\"Feature_4\",\"type\":\"FLOAT\"},{\"name\":\"Target\",\"type\":\"INT64\"}]"
  table_id        = "data"
}
