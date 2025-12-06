*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***
At Start There Are No Citations
    Go To Citations Page
    Page Should Contain  No saved citations yet.

After Adding A Book Citation It Is Shown In The List
    Add Example Book Citation
    Go To Citations Page
    Find Example Book Citation

After Editing A Book Citation It Is Shown In The List
    Add Example Book Citation
    Go To Citations Page
    Edit Book Citation
    Go To Citations Page
    Find Edited Book Citation
    Confirm No Example Book Citation Is In The List

After Deleting A Book Citation It Is No Longer In The List
    Add Example Book Citation
    Go To Citations Page
    Delete Citation
    Go To Citations Page
    Confirm No Example Book Citation Is In The List

Adding Duplicate Citation Key Shows Error
    Add Example Book Citation
    Go To Home Page
    Select From List By Label  entry_type  book
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'book'
    Input Text  citation_key  doe2020
    Input Text  author  John Doe
    Input Text  publisher  Example Publisher
    Input Text  title  Example Book
    Input Text  year  2020
    Click Button  Add Citation
    Page Should Not Contain  A new citation was added successfully!

*** Keywords ***
Find Example Book Citation
    Go To Citations Page
    Page Should Contain  John Doe (2020). Example Book. Example Publisher.
    Page Should Not Contain  No saved citations yet.

Edit Book Citation
    Go To Citations Page
    Click Button  Edit
    Input Text  citation_key  doe2019
    Input Text  author  John Doe
    Input Text  publisher  Example Publisher
    Input Text  title  Changed Example Book
    Input Text  year  2019
    Click Button  Save Changes
    Title Should Be  Saved Citations
    Wait Until Page Contains  Citation updated successfully.

Find Edited Book Citation
    Go To Citations Page
    Page Should Contain  John Doe (2019). Changed Example Book. Example Publisher.

Confirm No Example Book Citation Is In The List
    Go To Citations Page
    Page Should Not Contain  John Doe (2020). Example Book. Example Publisher.

Delete Citation
    Go To Citations Page
    Click Button  Delete
    Handle Alert  action=ACCEPT
    Wait Until Page Contains  Citation deleted successfully.

Check That Duplicate Error Was Displayed
    Go To Home Page
    Page Should Not Contain  A new citation was added successfully!
