locals {
  data_lake_bucket = "agents_data_lake"
}

variable "project" {
  description = "Your GCP Project ID"
  default = "agents-and-precipitation"
  type = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "US-EAST1"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "agents"
}