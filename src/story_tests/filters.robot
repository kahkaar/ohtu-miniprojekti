*** Settings ***
Resource        resource.robot
Suite Setup     Open And Configure Browser
Suite Teardown  Close Browser
Test Setup      Reset Database

*** Test Cases ***

At Start There Are No Citations
    Go To Citations Page
    Click Button    Search
    Wait Until Page Contains    No saved citations yet


After Adding Two Citations Search By Author Works
    Add Example Article Citation
    Add Example Book Citation
    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=author  timeout=2s
    Input Text     name=author     Jane
    Click Button   Apply filters

    Wait Until Page Contains      Jane Doe
    Page Should Not Contain       John Doe


Search By Entry Type Shows Only Matching Types
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=entry_type  timeout=2s
    Select From List By Label     entry_type     article
    Click Button   Apply filters

    Wait Until Page Contains      doe1998
    Page Should Not Contain       doe2020


Search By Year Range From
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=year_from  timeout=2s
    Input Text     year_from    2000
    Click Button   Apply filters

    Wait Until Page Contains      doe2020
    Page Should Not Contain       doe1998


Search By Year Range To
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=year_to  timeout=2s
    Input Text     year_to    2000
    Click Button   Apply filters

    Wait Until Page Contains      doe1998
    Page Should Not Contain       doe2020


Full Text Q Search Matches In Any Field
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Input Text     q     Journal
    Click Button   Search

    Wait Until Page Contains      Example Journal Title
    Page Should Not Contain       Example Publisher


Sorting By Year Ascending Shows Older First
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=sort_by  timeout=2s
    Select From List By Label     sort_by      Year
    Select From List By Label     direction    Ascending
    Click Button  Apply filters

    Wait Until Page Contains  doe1998  timeout=3s
    ${text}=   Get Text   css=body
    Should Match Regexp    ${text}    (?s)doe1998.*doe2020


Sorting By Citation Key Descending Shows Z→A
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Wait Until Element Is Visible  name=sort_by  timeout=2s
    Select From List By Label     sort_by      Citation Key
    Select From List By Label     direction    Descending
    Click Button  Apply filters

    Wait Until Page Contains  doe2020  timeout=3s
    ${text}=   Get Text   css=body
    Should Match Regexp    ${text}    (?s)doe2020.*doe1998

Searching By Tags Only Shows Citations In the Selected Tags
    Add Example Article Citation
    Go To Home Page
    Select From List By Label  entry_type  book
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'book'
    Input Text  citation_key  doe2020
    Input Text  author  John Doe
    Input Text  publisher  Example Publisher
    Input Text  title  Example Book
    Input Text  year  2020
    Input Text    name=category_new    Work
    Input Text    name=tags_new        School

    Click Button  Add Citation
    Wait Until Page Contains  A new citation was added successfully!
    Go To Citations Page
    Click Button  id=toggleFilters
    Select From List By Label    id=tag-select    School
    Click Button   Apply filters
    Wait Until Page Contains      John Doe
    Page Should Not Contain       Jane Doe

Searching By Categories Only Shows Citations In the Selected Categories
    Add Example Article Citation
    Go To Home Page
    Select From List By Label  entry_type  book
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'book'
    Input Text  citation_key  doe2020
    Input Text  author  John Doe
    Input Text  publisher  Example Publisher
    Input Text  title  Example Book
    Input Text  year  2020
    Input Text    name=category_new    Work
    Input Text    name=tags_new        School

    Click Button  Add Citation
    Wait Until Page Contains  A new citation was added successfully!
    Go To Citations Page
    Click Button  id=toggleFilters
    Select From List By Label    id=category-select    Work
    Click Button   Apply filters
    Wait Until Page Contains      John Doe
    Page Should Not Contain       Jane Doe
