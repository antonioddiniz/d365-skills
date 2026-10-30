# Lifecycle requests (Web API)

GUIDs are placeholders. Actions are bound or unbound as shown. Check the action reference for your
version if a parameter is rejected.

## Qualify a lead, create account + contact + opportunity

```http
POST {org}/api/data/v9.2/leads(00000000-0000-0000-0000-000000000001)/Microsoft.Dynamics.CRM.QualifyLead
Content-Type: application/json

{
  "CreateAccount": true,
  "CreateContact": true,
  "CreateOpportunity": true,
  "Status": 3
}
```

The response lists the created records. When both account and contact are created, the contact's
parent customer is the account and the account's primary contact is the contact.

## Win an opportunity

```http
POST {org}/api/data/v9.2/WinOpportunity
Content-Type: application/json

{
  "OpportunityClose": {
    "subject": "Won",
    "actualrevenue": 120000,
    "opportunityid@odata.bind": "/opportunities(00000000-0000-0000-0000-000000000002)"
  },
  "Status": 3
}
```

Lose: `POST .../LoseOpportunity` with the same shape, `Status` 4 (Canceled) or 5 (Out-Sold), and
optionally `"competitorid@odata.bind": "/competitors(<id>)"`.

## Resolve a case

```http
POST {org}/api/data/v9.2/CloseIncident
Content-Type: application/json

{
  "IncidentResolution": {
    "subject": "Resolved by phone",
    "incidentid@odata.bind": "/incidents(00000000-0000-0000-0000-000000000003)"
  },
  "Status": 5
}
```

## Create an email with parties, then send it

```http
POST {org}/api/data/v9.2/emails
Content-Type: application/json

{
  "subject": "Your proposal",
  "description": "<p>Hello</p>",
  "regardingobjectid_opportunity_email@odata.bind": "/opportunities(00000000-0000-0000-0000-000000000002)",
  "email_activity_parties": [
    { "partyid_systemuser@odata.bind": "/systemusers(00000000-0000-0000-0000-000000000010)", "participationtypemask": 1 },
    { "partyid_contact@odata.bind": "/contacts(00000000-0000-0000-0000-000000000011)", "participationtypemask": 2 }
  ]
}
```

```http
POST {org}/api/data/v9.2/emails(<new email id>)/Microsoft.Dynamics.CRM.SendEmail
Content-Type: application/json

{ "IssueSend": true }
```

`IssueSend: false` only marks the email as sent (for emails sent outside Dynamics).
