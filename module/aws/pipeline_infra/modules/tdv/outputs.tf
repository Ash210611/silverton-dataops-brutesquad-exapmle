output "output_bucket" {
  value = var.dest_bucket
}

output "output_prefix" {
  value = local.destination_folder
}

output "type" {
  value = var.type
}

output "type_map_output" {
  value = var.type_map
}
