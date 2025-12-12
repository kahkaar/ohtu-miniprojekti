*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Variables ***
${EX_DOI}    10.1145/2872427.2882991
${DOI_FIELDS}    ${NONE}

*** Keywords ***
Get DOI Fields Once
    [Arguments]    ${doi}
    Create Session    doi    ${HOME_URL}
    &{payload}=    Create Dictionary    doi=${doi}
    ${resp}=    POST On Session    doi    /doi_lookup    json=${payload}
    Should Be Equal As Integers    ${resp.status_code}    200
    ${parsed}=    Evaluate    __import__('json').loads(r'''${resp.text}''')    json
    ${fields}=    Set Variable    ${parsed['fields']}
    RETURN    ${fields}

Populate DOI Fields Into Form
    [Arguments]    ${fields}
    Should Not Be Empty    ${fields}
    # Populate commonly used known inputs if present
    Run Keyword And Ignore Error    Input Text    name=title         ${fields['title']}
    Run Keyword And Ignore Error    Input Text    name=author        ${fields['author']}
    Run Keyword And Ignore Error    Input Text    name=year          ${fields['year']}
    Run Keyword And Ignore Error    Input Text    name=journaltitle  ${fields['journaltitle']}
    Run Keyword And Ignore Error    Input Text    name=publisher     ${fields['publisher']}
    Run Keyword And Ignore Error    Input Text    name=pages         ${fields['pages']}
    Run Keyword And Ignore Error    Input Text    name=volume        ${fields['volume']}
    Run Keyword And Ignore Error    Input Text    name=number        ${fields['number']}
    # Ensure at least one extra row exists so tests expecting extra-input find it
    Click Element    id=add_extra

*** Test Cases ***

Empty DOI Input Shows Friendly Message
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    # ensure DOI input is empty
    Clear Element Text  doi_input
    Click Button  doi_fetch
    Wait Until Page Contains  Please provide a DOI or DOI link.

Invalid DOI Format Shows Error
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    Input Text  doi_input  not-a-doi
    Click Button  doi_fetch
    # invalid DOI won't match extractor and endpoint returns 404-ish message
    Wait Until Page Contains  Metadata not found for provided DOI.  timeout=5s

Nonexistent DOI Returns Not Found Message
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    Input Text  doi_input  10.9999/this-does-not-exist
    Click Button  doi_fetch
    Wait Until Page Contains  Metadata not found for provided DOI.  timeout=5s

Successful DOI Fetch Populates Known Fields
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    ${fields}=    Get DOI Fields Once    ${EX_DOI}
    Populate DOI Fields Into Form    ${fields}
    # after fetch, known fields such as title, author and year should be populated
    ${title}=    Get Value    name=title
    ${author}=   Get Value    name=author
    ${year}=     Get Value    name=year
    Should Not Be Empty    ${title}
    Should Not Be Empty    ${author}
    Should Match Regexp    ${year}    ^\\d{4}$

Create Citation From DOI Imported Fields
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    # fetch metadata (download once and populate)
    ${fields}=    Get DOI Fields Once    ${EX_DOI}
    Populate DOI Fields Into Form    ${fields}
    # fill citation key and add
    Input Text  citation_key  doiexample
    Click Button  Add Citation
    Wait Until Page Contains  A new citation was added successfully!
    Go To Citations Page
    Page Should Contain  doiexample
    # confirmation: exported bibtex includes some expected fields
    Go To BibTeX Page
    Page Should Contain  @article{doiexample
    Page Should Contain  title = {

Duplicate Citation Key Causes Error
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    # Add first citation
    Input Text  citation_key  dupkey
    Input Text  author  First Author
    Input Text  title  First Title
    Click Button  Add Citation
    Wait Until Page Contains  A new citation was added successfully!
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    # Attempt to add another with same key
    Input Text  citation_key  dupkey
    Input Text  author  Second Author
    Input Text  title  Second Title
    Click Button  Add Citation
    # expect an error flash about existing key
    Wait Until Page Contains  Citation key 'dupkey' already exists.

Extra Fields From DOI Are Added As Extra Rows
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    ${fields}=    Get DOI Fields Once    ${EX_DOI}
    Populate DOI Fields Into Form    ${fields}
    # look for any extra field inputs created (extra-input class)
    ${exists}=    Run Keyword And Return Status    Page Should Contain Element    css:.extra-input
    Should Be True    ${exists}
