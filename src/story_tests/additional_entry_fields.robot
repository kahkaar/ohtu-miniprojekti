*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***

Add Additional Entry Fields While Editing
    Add Example Book Citation
    Go To Citations Page
    Click Button  Edit
    Wait Until Page Contains  Edit Citation
    Title Should Be  Edit Citation

    Click Button  Add field

    Select From List By Value    xpath=(//select[contains(@class, 'extra-select')])[last()]    note

    Input Text    xpath=(//input[contains(@class, 'extra-input')])[last()]    This is an extra note added in test

    Click Button  Save Changes
    Wait Until Page Contains  Citation updated successfully.

    Go To Citations Page
    Click Button  View BibTeX
    Page Should Contain  note = {This is an extra note added in test}
