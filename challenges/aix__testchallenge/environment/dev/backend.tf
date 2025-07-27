terraform {
  backend "gcs" {
    bucket = "aix-testchallenge-dev-tfstate"
    prefix = "env/dev"
  }
}