# SES Domain Identity for stevekehlet.com
# This allows sending emails from any address @stevekehlet.com

resource "aws_ses_domain_identity" "stevekehlet" {
  domain = "stevekehlet.com"
}

# DKIM signing for email authentication
resource "aws_ses_domain_dkim" "stevekehlet" {
  domain = aws_ses_domain_identity.stevekehlet.domain
}

# # Output the DNS records that need to be added to GoDaddy manually
# output "ses_verification_instructions" {
#   value       = <<-EOT

#     ==================================================================================
#     DNS RECORDS TO ADD TO GODADDY FOR stevekehlet.com
#     ==================================================================================

#     1. Domain Verification TXT Record:
#        Type: TXT
#        Name: _amazonses.stevekehlet.com
#        Value: ${aws_ses_domain_identity.stevekehlet.verification_token}

#     2. DKIM CNAME Records (add all 3):
#        Type: CNAME
#        Name: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[0]}._domainkey.stevekehlet.com
#        Value: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[0]}.dkim.amazonses.com

#        Type: CNAME
#        Name: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[1]}._domainkey.stevekehlet.com
#        Value: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[1]}.dkim.amazonses.com

#        Type: CNAME
#        Name: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[2]}._domainkey.stevekehlet.com
#        Value: ${aws_ses_domain_dkim.stevekehlet.dkim_tokens[2]}.dkim.amazonses.com

#     ==================================================================================
#     After adding these records to GoDaddy, verification typically completes within
#     5-10 minutes but can take up to 72 hours. You can check the status in the AWS
#     SES console or by running: aws ses get-identity-verification-attributes 
#                                  --identities stevekehlet.com --region us-west-2
#     ==================================================================================
#   EOT
#   description = "DNS records to manually add to GoDaddy"
# }

# Separate outputs for programmatic access if needed
output "ses_dkim_tokens" {
  value       = aws_ses_domain_dkim.stevekehlet.dkim_tokens
  description = "DKIM tokens for stevekehlet.com"
}

output "ses_verification_token" {
  value       = aws_ses_domain_identity.stevekehlet.verification_token
  description = "Domain verification token for stevekehlet.com"
}
