*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***
At start there are no citations
    Go To View Page
    Page Should Contain  No saved citations yet.

After adding a book citation it is shown in the list
    Add Example Book
    Find Example book

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
