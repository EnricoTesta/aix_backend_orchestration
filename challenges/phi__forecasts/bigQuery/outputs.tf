output "google_bigquery_dataset--evaluation_layer_self_link" {
  value = "${google_bigquery_dataset.phi-data-prod-evaluation_layer.self_link}"
}

output "google_bigquery_dataset_tfer--inference_layer_self_link" {
  value = "${google_bigquery_dataset.phi-data-prod-inference_layer.self_link}"
}

output "google_bigquery_dataset_tfer--information_layer_self_link" {
  value = "${google_bigquery_dataset.phi-data-prod-information_layer.self_link}"
}

output "google_bigquery_dataset_tfer--raw_data_layer_self_link" {
  value = "${google_bigquery_dataset.phi-data-prod-raw_data_layer.self_link}"
}

output "google_bigquery_dataset_tfer--training_layer_self_link" {
  value = "${google_bigquery_dataset.phi-data-prod-training_layer.self_link}"
}

output "google_bigquery_table_tfer--phi-data-prod-raw_data_layer-data_self_link" {
  value = "${google_bigquery_table.phi-data-prod-raw_data_layer-data.self_link}"
}