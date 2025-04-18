# Trace
a Compliance Operations Toolkit
by Konrad Zielinski, Peyton Hamilton, and Zach Elkins (Note that NONE of this tool has been built with code experience, just the help of GPT and learning as-we-go)

##### Problem #####
Compliance analysts spend significant time manually gathering data, understanding a customer’s business model, pulling transactions, and drafting narratives—before even beginning their analysis. 
Transaction analysis involves manually accessing and searching Pi for the appropriate query, copy/pasting the results into a Google Sheet, and organizing the transaction data for review. External research involves conducting manual Google searches of the customer and authorized representative’s name, accessing and reviewing various websites identified through those searches, and manually downloading PDF copies of those sites as appropriate. For internal research, analysts review various systems (including Diameter, Google Drive, Salesforce, and Slack) for references to the customer and document findings as appropriate.

##### Why It Matters #####
Each alert takes ~15–30 minutes of prep before true investigation begins.
Time is spent on repetitive, non-analytical work.
Streamlining this workflow will improve consistency across alerts and reduce the risk of errors–which often leads to rework across teams (Investigations, KYC, QA).


##### Needs as of 04/18/2025 #####

API access (Glean, OpenAI) + security handling (Okta, OAuth)
Data access/connection to Snowflake/AWS
Packaging for distribution to team (install package)
LLM experimentation support (e.g., OpenAI or Claude API access)
Stakeholder alignment with Investigations and Compliance Ops

##### The Solution #####

An AI-powered Toolkit and Automation Engine. It will:
Allow the investigator to choose an alert narrative template based on typology;
Pull transaction data within a custom date range based on user input via Snowflake, saving on cost per query due to Circle’s AWS license rather than charging per query. This transaction data should always include: 

  A complete transaction history for the customer
  TRM and Elliptic data (with a breakdown of direct and indirect exposure)
  Wallet label information - from our customers within Diameter:

    [select *
    from txcore.external_addresses
    where lower(address) like ‘XXXX’]

Fetch KYC and risk data;
Summarize the customer's business model;
Packages everything into a Word doc + Excel file
Providing all documentation as a .zip file for upload to Unit21/other systems.


##### Engineering Overview (items are listed in order of priority) #####

Structural Needs of v1

  Okta Integration
  OpenID Integration


Functional Needs

  GPT Queries Flow: 
    Currently, the app includes a search field that queries GPT-4o via ChatAI. This field should query ChatAI using the Glean workflow and each user of the application’s permissions.
    Per Bhushit Agarwal, enabling the app to perform OAuth and support Okta SAML would allow for use of Glean APIs with OAuth.

Transaction Analysis Flow:
  Query a customer’s transaction history based on customer ID and a custom date range set by the analyst. Note that we already have a script built into the app:
  Upon running, categorize transactions into BOTH an .xlsx sheet AND the aforementioned narrative document:
    Onchain Receives
    Onchain Spends
    Incoming Wires
    Outgoing Wires
    Other

Build (within the .xlsx sheet only and on different tabs):
  All transactions
  Top 50 destination blockchain addresses
  Top 50 from addresses
  Month-Year breakdown
  Chain-by-category statistics
  Include a field for analysts to write custom SQL queries (similar to Pi).


KYC/Narrative Flow:
  Use a customer ID to pull KYC documents and data directly from Diameter, COP, and Pi. This includes:
  Business Name and DBA
  Business Model Summary (Stated nature of business)
  Expected Monthly Volume (Crypto/Fiat) (From most recent PR)
  Account Opening Date
  Intended Account Use Description
  Date of last PR (and the result with rationale)
  Bank Statements
  Any RFI responses
  Stated occupation of authorized representative(s)
  Business certificates (e.g., DBAs, Articles of Incorporation)
  Identifying documents for authorized representative(s)
  Summarize and draft this data in a .docx narrative.
  Provide a drop-down menu of narratives tied to alert typologies in addition to fields for the start and end date of the alert’s review period, the customer’s name, their nature of business/purpose of the account, and a field for miscellaneous    notes (note these fields already exist)
  Auto-populating the alert narratives with the items highlighted above in the same .docx file as the narrative.
  Allow managers to add/edit the narrative library. 

Formatting/House-Keeping:
  Keeping the “Run Investigation” button to run ALL workflows in one process and adding workflow-specific “Run” buttons to limit the output only to one flow (e.g., “Run Transaction Analysis”).
  Ensure the “Run Investigation” button works even if fields are left blank.
  Populating A “X field(s) is/are blank, run anyway?” message in such cases to avoid errors.
  Compile each of the aforementioned documents in an “Investigation Folder” locally on the user’s system.
  All documentation compiled in the Investigation Folder must follow the format of {customer ID}_{name of document}.

##### Cross-Functional Opportunities #####

  KYC: Summarize customer profiles
  CRA tab - auto pull info to fill CRA template
  Sanctions: Apply same engine for hit justification memos
  QA: Pre-package files for review
      Unit21 doc pulls (~5 mins)
      Seek Discrepancies between narrative and documentation, cross-reference with scoring rubrik
      Auto-export errors into a document 
Training: Use AI narratives as starter examples
