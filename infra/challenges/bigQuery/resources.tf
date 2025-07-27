resource "google_bigquery_dataset" "tfer--aix-data-stocks-003A-evaluation_layer" {
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

resource "google_bigquery_dataset" "tfer--aix-data-stocks-003A-inference_layer" {
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

resource "google_bigquery_dataset" "tfer--aix-data-stocks-003A-information_layer" {
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

resource "google_bigquery_dataset" "tfer--aix-data-stocks-003A-raw_data_layer" {
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

resource "google_bigquery_dataset" "tfer--aix-data-stocks-003A-training_layer" {
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

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-evaluation_layer-002E-d_holdout" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-evaluation_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Ret_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_48W\",\"type\":\"FLOAT\"}]"
  table_id        = "d_holdout"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-evaluation_layer-002E-p_perimeter" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-evaluation_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"TICKER\",\"type\":\"STRING\"}]"
  table_id        = "p_perimeter"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-evaluation_layer-002E-prices" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-evaluation_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"Date\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Open\",\"type\":\"FLOAT\"},{\"name\":\"High\",\"type\":\"FLOAT\"},{\"name\":\"Low\",\"type\":\"FLOAT\"},{\"name\":\"Close\",\"type\":\"FLOAT\"},{\"name\":\"Volume\",\"type\":\"FLOAT\"},{\"name\":\"Dividends\",\"type\":\"FLOAT\"},{\"name\":\"Stock_Splits\",\"type\":\"FLOAT\"}]"
  table_id        = "prices"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-evaluation_layer-002E-t_target" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-evaluation_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"TARGET_VARIABLE\",\"type\":\"INTEGER\"}]"
  table_id        = "t_target"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-inference_layer-002E-d_backfill_inference" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-inference_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Ret_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_48W\",\"type\":\"FLOAT\"}]"
  table_id        = "d_backfill_inference"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-inference_layer-002E-d_inference" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-inference_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Ret_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_48W\",\"type\":\"FLOAT\"}]"
  table_id        = "d_inference"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-inference_layer-002E-p_perimeter" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-inference_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"TICKER\",\"type\":\"STRING\"}]"
  table_id        = "p_perimeter"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-information_layer-002E-f_prices" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-information_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"mode\":\"NULLABLE\",\"name\":\"Ticker\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_2w\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Open_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_2w\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_High_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_2w\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Low_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_2w\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Ret_Close_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_2W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Open_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_2W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_High_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_2W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Low_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_2W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Close_48W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_1W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_2W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_3W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_4W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_6W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_8W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_12W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_16W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_20W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_24W\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Range_Volume_48W\",\"type\":\"FLOAT\"}]"
  table_id        = "f_prices"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-bloomberg_ticker_suffix" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"bloomberg_ticker_suffix\",\"type\":\"STRING\"}]"
  table_id        = "bloomberg_ticker_suffix"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-map_ticker_yahoo_bloomberg" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"yahoo_ticker\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"bloomberg_ticker\",\"type\":\"STRING\"}]"
  table_id        = "map_ticker_yahoo_bloomberg"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-p_signals" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"Obs_Date\",\"type\":\"DATE\"},{\"mode\":\"NULLABLE\",\"name\":\"Ticker\",\"type\":\"STRING\"}]"
  table_id        = "p_signals"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-prices" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"Date\",\"type\":\"DATE\"},{\"mode\":\"NULLABLE\",\"name\":\"Ticker\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"Open\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"High\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Low\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Close\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Volume\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Dividends\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"Stock_Splits\",\"type\":\"FLOAT\"}]"
  table_id        = "prices"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-t_signals" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"bloomberg_ticker\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"friday_date\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"data_type\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"target_4d\",\"type\":\"FLOAT\"},{\"mode\":\"NULLABLE\",\"name\":\"target_20d\",\"type\":\"FLOAT\"}]"
  table_id        = "t_signals"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-t_target" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"TARGET_VARIABLE\",\"type\":\"INTEGER\"}]"
  table_id        = "t_target"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-yahoo_ticker_list" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"Ticker\",\"type\":\"STRING\"}]"
  table_id        = "yahoo_ticker_list"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-raw_data_layer-002E-yahoo_ticker_suffix" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-raw_data_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"mode\":\"NULLABLE\",\"name\":\"yahoo_ticker_suffix\",\"type\":\"STRING\"}]"
  table_id        = "yahoo_ticker_suffix"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-training_layer-002E-d_train" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-training_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Ret_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_2w\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Ret_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Open_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_High_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Low_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Close_48W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_1W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_2W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_3W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_4W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_6W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_8W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_12W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_16W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_20W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_24W\",\"type\":\"FLOAT\"},{\"name\":\"Range_Volume_48W\",\"type\":\"FLOAT\"},{\"name\":\"TARGET_VARIABLE\",\"type\":\"INTEGER\"}]"
  table_id        = "d_train"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-training_layer-002E-p_perimeter" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-training_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"TICKER\",\"type\":\"STRING\"}]"
  table_id        = "p_perimeter"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-training_layer-002E-prices" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-training_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"Date\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"Open\",\"type\":\"FLOAT\"},{\"name\":\"High\",\"type\":\"FLOAT\"},{\"name\":\"Low\",\"type\":\"FLOAT\"},{\"name\":\"Close\",\"type\":\"FLOAT\"},{\"name\":\"Volume\",\"type\":\"FLOAT\"},{\"name\":\"Dividends\",\"type\":\"FLOAT\"},{\"name\":\"Stock_Splits\",\"type\":\"FLOAT\"}]"
  table_id        = "prices"
}

resource "google_bigquery_table" "tfer--aix-data-stocks-003A-training_layer-002E-t_target" {
  dataset_id      = "${google_bigquery_dataset.tfer--aix-data-stocks-003A-training_layer.dataset_id}"
  expiration_time = "0"
  project         = "${var.project}"
  schema          = "[{\"name\":\"OBS_DATE\",\"type\":\"DATE\"},{\"name\":\"Ticker\",\"type\":\"STRING\"},{\"name\":\"TARGET_VARIABLE\",\"type\":\"INTEGER\"}]"
  table_id        = "t_target"
}
