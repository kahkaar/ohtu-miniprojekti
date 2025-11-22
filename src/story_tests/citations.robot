*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***
At Start There Are No Citations
    Go To View Page
    Page Should Contain  No saved citations yet.

After Adding A Book Citation It Is Shown In The List
    Add Example Book
    Find Example Book

After Editing A Book It Is Shown In The List
    Add Example Book
    Edit Book
    Find Edited Book
    Confirm No Example Book Is In The List

After Deleting A Book It Is No Longer In The List
    Add Example Book
    Delete Book
    Confirm No Example Book Is In The List

*** Keywords ***
Add Example Book
    Go To Home Page
    Input Text  title  Example Book
    Input Text  author  John Doe
    Input Text  year  2020
    Input Text  publisher  Example Publisher
    Input Text  address  123 Example St    
    Click Button  Add Book
    Wait Until Page Contains  Book added successfully!

Find Example book
    Go To View Page
    Page Should Contain  John Doe
    Page Should Contain  Example Book
    Page Should Contain  2020
    Page Should Contain  Example Publisher
    Page Should Contain  123 Example St
    Page Should Not Contain  No saved citations yet.

Edit Book
    Go To View Page
    Click Link  Edit
    Input Text  title  Updated Book Title
    Input Text  author  Jane Smith
    Input Text  year  2021
    Input Text  publisher  Updated Publisher
    Input Text  address  456 Updated St
    Click Button  Save Changes
    Title Should Be  Saved Citations

Find Edited Book
    Go To View Page
    Page Should Contain  Jane Smith
    Page Should Contain  Updated Book Title
    Page Should Contain  2021
    Page Should Contain  Updated Publisher
    Page Should Contain  456 Updated St

Confirm No Example Book Is In The List
    Go To View Page
    Page Should Not Contain  John Doe
    Page Should Not Contain  Example Book
    Page Should Not Contain  2020
    Page Should Not Contain  Example Publisher
    Page Should Not Contain  123 Example St

Delete Book
    Go To View Page
    Click Button  Delete
    Handle Alert  action=ACCEPT
