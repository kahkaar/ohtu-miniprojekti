*** Settings ***
Resource    resource.robot

*** Test Cases ***
Create Citation With Category
    Open Clean Browser And Reset
    Create Article Citation    cat2025    Alice Example    Journal of Categories    Categorized Article    2025    Science
    Verify Citation On Citations Page    Science
    Close If Open

Create Citation With Tags
    Open Clean Browser And Reset
    Create Article Citation    tags2025    Bob Example    Journal of Tags    Tagged Article    2025    ${NONE}    testing,robot
    Verify Citation On Citations Page    testing
    Verify Citation On Citations Page    robot
    Close If Open

Create Citation With Category And Tags
    Open Clean Browser And Reset
    Create Article Citation    catstags2025    Carol Combo    Journal of Mixes    Combined Article    2025    Interdisciplinary    alpha,beta,gamma
    Verify Citation On Citations Page    Interdisciplinary
    Verify Citation On Citations Page    alpha
    Verify Citation On Citations Page    beta
    Verify Citation On Citations Page    gamma
    Close If Open

Edit Category Of Citation
    Open Clean Browser And Reset
    Create Article Citation    editcat2025    Dana Editor    Journal of Edits    To Be Edited    2025
    Go To Citations Page
    Click Button    Edit
        Wait Until Page Contains    Edit Citation
    Input Text    category_new    EditedCategory
    Save Changes
    Verify Citation On Citations Page    EditedCategory
    Close If Open

Edit Tags Of Citation
    Open Clean Browser And Reset
    Create Article Citation    edittags2025    Evan Editor    Journal of Edits    To Be Tagged    2025
    Go To Citations Page
    Click Button    Edit
        Wait Until Page Contains    Edit Citation
    Input Text    tags_new    t1,t2
    Save Changes
    Verify Citation On Citations Page    t1
    Verify Citation On Citations Page    t2
    Close If Open

Edit Category And Tags Of Citation
    Open Clean Browser And Reset
    Create Article Citation    editboth2025    Fiona Editor    Journal of Edits    To Be Changed    2025
    Go To Citations Page
    Click Button    Edit
        Wait Until Page Contains    Edit Citation
    Input Text    category_new    NewCat
    Input Text    tags_new    newa,newb
    Save Changes
    Verify Citation On Citations Page    NewCat
    Verify Citation On Citations Page    newa
    Verify Citation On Citations Page    newb
    Close If Open

Edit Category Replace Old Value
    Open Clean Browser And Reset
    Create Article Citation    cat-change-2025    Zoe Historian    Journal of Changes    Changing Category    2025    Science
    Go To Citations Page
    Click Button    Edit
        Wait Until Page Contains    Edit Citation
    Input Text    category_new    History
    Save Changes
    Go To Citations Page
    Wait Until Page Contains    History
    Wait Until Page Does Not Contain    Science
    Close If Open

Edit Tags Replace Old Values
    Open Clean Browser And Reset
    Create Article Citation    tags-change-2025    Yan Tagger    Journal of Tags    Changing Tags    2025    ${NONE}    alpha,beta
    Go To Citations Page
    Click Button    Edit
        Wait Until Page Contains    Edit Citation
    Unselect All From List    tags
    Input Text    tags_new    gamma,delta
    Save Changes
    Go To Citations Page
    Wait Until Page Contains    gamma
    Wait Until Page Contains    delta
    Wait Until Page Does Not Contain    alpha
    Wait Until Page Does Not Contain    beta
    Close If Open


*** Keywords ***
Open Clean Browser And Reset
    Open And Configure Browser
    Reset Database
    Go To Home Page

Create Article Citation
    [Arguments]    ${key}    ${author}    ${journaltitle}    ${title}    ${year}    ${category}=${NONE}    ${tags}=${NONE}
    Select From List By Label    entry_type    article
    Click Button    Select
    Wait Until Page Contains    Selected entry type 'article'
    Input Text    citation_key    ${key}
    Input Text    author    ${author}
    Input Text    journaltitle    ${journaltitle}
    Input Text    title    ${title}
    Input Text    year    ${year}
    Run Keyword If    '${category}' != 'None'    Input Text    category_new    ${category}
    Run Keyword If    '${tags}' != 'None'    Input Text    tags_new    ${tags}
    Click Button    Add Citation
    Wait Until Page Contains    A new citation was added successfully!

Verify Citation On Citations Page
    [Arguments]    ${text}
    Go To Citations Page
    Wait Until Page Contains    ${text}

Close If Open
    Close Browser

Save Changes
    Click Button    Save Changes
    Wait Until Page Contains    Citation updated successfully.
