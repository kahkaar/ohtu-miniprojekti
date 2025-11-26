*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***
Citations In Bibtex Format Are Shown Correctly
    Add Example Book
    Go To Bibtex Page
    Page Should Contain  @book{
    Page Should Contain  title = {Example Book},
    Page Should Contain  author = {John Doe},
    Page Should Contain  year = {2020},
    Page Should Contain  publisher = {Example Publisher},
    Page Should Contain  address = {123 Example St}
    Page Should Contain  }
