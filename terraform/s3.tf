resource "aws_s3_bucket" "site_bucket" {
  bucket = var.domain
  policy = <<EOF
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"PublicReadForGetBucketObjects",
      "Effect":"Allow",
      "Principal": {"AWS":"*"},
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::${var.domain}/*"],
      "Condition": {
        "StringEquals": {
          "aws:UserAgent": "${var.cloudfront_password}"
        }
      }
    }
  ]
}
EOF

  force_destroy = true
}

resource "aws_s3_bucket_website_configuration" "site_bucket" {
  bucket = aws_s3_bucket.site_bucket.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}
