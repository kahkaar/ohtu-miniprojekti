*** Settings ***
Library  SeleniumLibrary
Library  RequestsLibrary

*** Variables ***
${SERVER}     localhost:5001
${DELAY}      0.2 seconds
${HOME_URL}   http://${SERVER}
${VIEW_URL}   http://${SERVER}/citations
${SEARCH_URL}  http://${SERVER}/citations/search
${RESET_URL}  http://${SERVER}/test_env/reset_db
${BROWSER}    chrome
${HEADLESS}   true

*** Keywords ***
Open And Configure Browser
    IF  $BROWSER == 'chrome'
        ${options}  Evaluate  sys.modules['selenium.webdriver'].ChromeOptions()  sys
        Call Method  ${options}  add_argument  --incognito
    ELSE IF  $BROWSER == 'firefox'
        ${options}  Evaluate  sys.modules['selenium.webdriver'].FirefoxOptions()  sys
        Call Method  ${options}  add_argument  --private-window
    END
    IF  $HEADLESS == 'true'
        Set Selenium Speed  0.01 seconds
        Call Method  ${options}  add_argument  --headless
    ELSE
        Set Selenium Speed  ${DELAY}
    END
    Open Browser  browser=${BROWSER}  options=${options}

Reset Database
    Go To  ${RESET_URL}

Go To Home Page
    Go To  ${HOME_URL}
    Title Should Be  Add a new Citation

Go To Citations Page
    Go To  ${VIEW_URL}
    Title Should Be  Saved Citations

Go To BibTeX Page
    Go To Citations Page
    Click Button  View BibTeX
    Wait Until Page Contains  @
    Title Should Be  Citation in BibTeX format

Add Example Article Citation
    Go To Home Page
    Select From List By Label  entry_type  article
    Click Button  Select
    Wait Until Page Contains  Selected entry type 'article'
    Input Text  citation_key  doe1998
    Input Text  author  Jane Doe
    Input Text  journaltitle  Example Journal Title
    Input Text  title  An Example Article
    Input Text  year  1998
    Click Button  Add Citation
    Wait Until Page Contains  A new citation was added successfully!

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
    Wait Until Page Contains  A new citation was added successfully!
