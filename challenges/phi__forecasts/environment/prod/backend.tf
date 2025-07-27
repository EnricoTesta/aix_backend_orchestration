terraform {
  backend "gcs" {
    bucket = "phi-data-prod-tfstate"
    prefix = "env/prod"
  }
}