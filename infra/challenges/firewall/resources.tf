resource "google_compute_firewall" "vault-deny-all-egress" {
  deny {
    protocol = "all"
  }

  destination_ranges = ["0.0.0.0/0"]
  direction          = "EGRESS"
  disabled           = "false"
  name               = "vault-deny-all-egress"
  network            = "https://www.googleapis.com/compute/v1/projects/${var.project}/global/networks/${var.network}"
  priority           = "1000"
  project            = "${var.project}"
}

resource "google_compute_firewall" "vault-deny-all-ingress" {
  deny {
    protocol = "all"
  }

  direction     = "INGRESS"
  disabled      = "false"
  name          = "vault-deny-all-ingress"
  network       = "https://www.googleapis.com/compute/v1/projects/${var.project}/global/networks/${var.network}"
  priority      = "1000"
  project       = "${var.project}"
  source_ranges = ["0.0.0.0/0"]
}
