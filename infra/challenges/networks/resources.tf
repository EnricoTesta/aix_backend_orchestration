resource "google_compute_network" "vault" {
  auto_create_subnetworks         = "true"
  delete_default_routes_on_create = "false"
  enable_ula_internal_ipv6        = "false"
  mtu                             = "1460"
  name                            = "${var.network}"
  project                         = "${var.project}"
  routing_mode                    = "REGIONAL"
}
