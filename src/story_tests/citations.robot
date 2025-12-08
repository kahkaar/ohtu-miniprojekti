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

After Changing Entry Type While Editing It Is Reflected
    Add Example Book Citation
    Go To Citations Page
    # Open edit page for the added citation
    Click Button  Edit
    # Change citation key to ensure uniqueness and change entry type to 'article'
    Input Text  citation_key  doe2018
    Select From List By Label  entry_type  article
    Click Button  Save Changes
    Title Should Be  Saved Citations
    Wait Until Page Contains  Citation updated successfully.
    # Verify the entry type label is shown for the citation in the list
    Go To Citations Page
    Page Should Contain  @article

Edit Page Shows Entry Type Select
    Add Example Book Citation
    Go To Citations Page
    Click Button  Edit
    Page Should Contain  Entry type:

Keeping Entry Type Unchanged Preserves It
    Add Example Book Citation
    Go To Citations Page
    Click Button  Edit
    # change only citation key and explicitly choose the '(keep current: book)' option
    Input Text  citation_key  doe2017
    Select From List By Label  entry_type  (keep current: book)
    Click Button  Save Changes
    Wait Until Page Contains  Citation updated successfully.
    Go To Citations Page
    Page Should Contain  @book

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
    Wait Until Page Contains  An error occurred while adding the citation: Citation key 'doe2020' already exists.  timeout=5s
    Page Should Contain  An error occurred while adding the citation: Citation key 'doe2020' already exists.

*** Keywords ***
Find Example Book Citation
    Page Should Contain  John Doe (2020). Example Book. Example Publisher.
    Page Should Not Contain  No saved citations yet.

Edit Book Citation
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
    Page Should Contain  John Doe (2019). Changed Example Book. Example Publisher.

Confirm No Example Book Citation Is In The List
    Page Should Not Contain  John Doe (2020). Example Book. Example Publisher.

Delete Citation
    Go To Citations Page
    Click Button  Delete
    Handle Alert  action=ACCEPT
    Wait Until Page Contains  Citation deleted successfully.

Check That Duplicate Error Was Displayed
    Go To Home Page
    Page Should Not Contain  A new citation was added successfully!
