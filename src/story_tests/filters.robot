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
    Input Text     name=author     Jane
    Click Button   Apply filters

    Wait Until Page Contains      Jane Doe
    Page Should Not Contain       John Doe


Search By Entry Type Shows Only Matching Types
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Select From List By Label     entry_type     article
    Click Button   Apply filters

    Wait Until Page Contains      doe1998
    Page Should Not Contain       doe2020


Search By Year Range From
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Input Text     year_from    2000
    Click Button   Apply filters

    Wait Until Page Contains      doe2020
    Page Should Not Contain       doe1998


Search By Year Range To
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
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
    Select From List By Label     sort_by      Year
    Select From List By Label     direction    Ascending
    Click Button  Apply filters

    ${text}=   Get Text   css=body
    Should Match Regexp    ${text}    (?s)doe1998.*doe2020


Sorting By Citation Key Descending Shows Z→A
    Add Example Article Citation
    Add Example Book Citation

    Go To Citations Page
    Click Button  id=toggleFilters
    Select From List By Label     sort_by      Citation Key
    Select From List By Label     direction    Descending
    Click Button  Apply filters

    ${text}=   Get Text   css=body
    Should Match Regexp    ${text}    (?s)doe2020.*doe1998

