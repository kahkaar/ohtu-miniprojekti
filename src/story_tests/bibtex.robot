*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***

Article Citations In BibTeX Format Are Shown Correctly
    Add Example Article Citation
    Go To Citations Page
    Go To BibTeX Page
    Page Should Contain  @article{doe1998
    Page Should Contain  author = {Jane Doe},
    Page Should Contain  journaltitle = {Example Journal Title},
    Page Should Contain  title = {An Example Article},
    Page Should Contain  year = {1998}
    Page Should Contain  }

Book Citations In BibTeX Format Are Shown Correctly
    Add Example Book Citation
    Go To Citations Page
    Go To BibTeX Page
    Page Should Contain  @book{doe2020
    Page Should Contain  author = {John Doe},
    Page Should Contain  publisher = {Example Publisher}
    Page Should Contain  title = {Example Book},
    Page Should Contain  year = {2020}
    Page Should Contain  }

Export Selected Citations Downloads BibTeX
    Add Example Book Citation
    Go To Citations Page
    Click Element    css=input[name="doe2020"]
    ${cid}=    Get Element Attribute    css=input[name="doe2020"]    id
    Create Session    export    ${HOME_URL}
    ${resp}=    Get On Session    export    /export_bibtex    params=citation_ids=${cid}
    Should Be Equal As Integers    ${resp.status_code}    200
    ${body}=    Convert To String    ${resp.content}
    Should Contain    ${body}    @book{doe2020
    Should Contain    ${body}    author = {John Doe},
