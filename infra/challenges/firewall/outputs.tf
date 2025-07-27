output "google_compute_firewall_tfer--vault-deny-all-egress_self_link" {
  value = "${google_compute_firewall.vault-deny-all-egress.self_link}"
}

output "google_compute_firewall_tfer--vault-deny-all-ingress_self_link" {
  value = "${google_compute_firewall.vault-deny-all-ingress.self_link}"
}
