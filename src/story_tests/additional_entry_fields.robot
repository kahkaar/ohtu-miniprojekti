*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***

Add Additional Entry Field While Creating
	Go To Home Page
	Select From List By Label  entry_type  book
	Click Button  Select
	Wait Until Page Contains  Selected entry type 'book'
	Input Text  citation_key  doe_extra_create
	Input Text  author  Alice Example
	Input Text  publisher  Create Publisher
	Input Text  title  Create Extra Field Book
	Input Text  year  2025
	# Add an extra field of type 'note'
	Click Button  Add field
	Select From List By Value    xpath=(//select[contains(@class, 'extra-select')])[last()]    note
	Input Text    xpath=(//input[contains(@class, 'extra-input')])[last()]    This is an extra note added during creation
	Click Button  Add Citation
	Wait Until Page Contains  A new citation was added successfully!
	Go To Citations Page
	Click Button  View BibTeX
	Page Should Contain  note = {This is an extra note added during creation}

Add Additional Entry Field While Editing
	Add Example Book Citation
	Go To Citations Page
	Click Button  Edit
	Wait Until Page Contains  Edit Citation
	Title Should Be  Edit Citation
	Wait Until Element Is Visible    id=add_extra    timeout=5s
	Click Element    id=add_extra
	Wait Until Element Is Visible    xpath=(//select[contains(@class, 'extra-select')])[last()]    timeout=5s
	Select From List By Value    xpath=(//select[contains(@class, 'extra-select')])[last()]    note
	Input Text    xpath=(//input[contains(@class, 'extra-input')])[last()]    This is an extra note added in edit
	Click Button  Save Changes
	Wait Until Page Contains  Citation was updated successfully.
	Go To Citations Page
	Click Button  View BibTeX
	Page Should Contain  note = {This is an extra note added in edit}
