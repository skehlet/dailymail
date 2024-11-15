# DailyMail pipeline README

## Testing the Cloudwatch Alarms

```bash
aws cloudwatch set-alarm-state --alarm-name "DailyMail-ScraperQueue-dlq-alarm" --state-reason "Testing my Amazon Cloudwatch alarm" --state-value ALARM 
```
