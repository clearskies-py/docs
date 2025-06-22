variable "route_53_hosted_zone_name" {
  type = string
  description = "The name of the route 53 hosted zone for our site"
}

variable "domain" {
  type = string
  description = "The domain for the site"
}

variable "cloudfront_password" {
  type = string
  description = "A 'password' shared by cloudfront and the bucket, which helps lock the bucket down to cloudfront"
  sensitive = true
}

variable "aws_region" {
  type = string
  description = "The AWS region for all of this."
  default = "us-east-1"
}

variable "trusted_signers" {
  type    = list(string)
  default = []
}

variable "forward-query-string" {
  type        = bool
  description = "Forward the query string to the origin"
  default     = false
}
