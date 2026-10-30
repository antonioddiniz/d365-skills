# Trigger cases

Each line is a prompt a developer could type, and the skill that should load. "none" means no skill
in this pack should trigger (the request belongs to another tool or is generic).

Run them by hand in your agent, or give the list plus the seven skill descriptions to a model and
ask it to route each prompt. The README shows the result of the last run.

| # | Prompt | Expected |
|---|---|---|
| 1 | My Update plug-in on account fires twice and sometimes I get "infinite loop detected". Here is the Execute method. | d365-plugins |
| 2 | Create a Custom API that receives an order id and returns the computed discount, with the C# behind it. | d365-plugins |
| 3 | My TypeScript sync only brings 5,000 contacts from Dynamics. How do I get all 80k? | d365-webapi |
| 4 | POST to /contacts fails with "An undeclared property parentcustomerid was found in the payload". | d365-webapi |
| 5 | Nightly migration of 2 million rows into Dataverse keeps failing with 429 errors. Design the loader. | d365-limits-performance |
| 6 | Our FetchXML with like '%123' times out with PerformanceValidationIssuesCauseTimeout. | d365-limits-performance |
| 7 | Design roles for sales reps who should only see their region's accounts, managers see everything in the region. | d365-security-model |
| 8 | We need to hide the CPF column from call center agents but keep it for back office. | d365-security-model |
| 9 | We removed a column in dev but after deploying to production it is still there. Why? | d365-solution-alm |
| 10 | Set up a GitHub Actions pipeline that moves our Power Platform solution from dev to test to prod. | d365-solution-alm |
| 11 | My flow on "When a row is added, modified or deleted" runs on every save and sometimes creates duplicates. | d365-flow-reliability |
| 12 | Add proper error handling to this Power Automate flow so failures alert the team. | d365-flow-reliability |
| 13 | Write code that marks an opportunity as won with the actual revenue. | d365-crm-data-model |
| 14 | Log a phone call from the contact to the sales rep against the case, via the Web API. | d365-crm-data-model |
| 15 | Give john@contoso.com the Basic User role in the test environment. | none (admin task, see microsoft/Dataverse-skills dv-security) |
| 16 | Build a canvas app screen with a gallery of accounts. | none (see microsoft/power-platform-skills canvas-apps) |
| 17 | Write a SQL Server stored procedure that paginates a customers table. | none (not Dataverse) |
| 18 | Explain what Dynamics 365 Customer Insights does in two paragraphs. | none (product question, no code) |
| 19 | Write a PCF control that shows a star rating. | none (see microsoft/power-platform-skills pcf) |
