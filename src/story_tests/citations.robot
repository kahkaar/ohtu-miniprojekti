*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***
At start there are no citations
    Go To  ${VIEW_URL}
    Title Should Be  Saved Citations
    Page Should Contain  No saved citations yet.
