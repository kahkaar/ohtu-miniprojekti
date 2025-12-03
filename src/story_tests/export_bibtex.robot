*** Settings ***
Resource  resource.robot
Suite Setup      Open And Configure Browser
Suite Teardown   Close Browser
Test Setup       Reset Database

*** Test Cases ***

Alert When No Citations Selected For BibTeX Export
    Add Example Book Citation
    Go To Citations Page
    Click Button  Export
    Alert Should Be Present  Please select at least one citation to export.

Exporting selected citations returns correct BibTeX file
    Add Example Article Citation
    Add Example Book Citation
    Go To Citations Page
    Select Checkbox  doe1998
    Select Checkbox  doe2020
    Click Button  Export
    # Simulate the GET request that would be made by the form submission
    ${resp}=  GET  url=http://localhost:5001/export_bibtex?citation_keys=doe1998,doe2020
    Status Should Be  200  ${resp}
    Should Contain   ${resp.headers['Content-Disposition']}  attachment; filename=selected_citations.bib
    Should Contain  ${resp.text}  @book{doe2020
    Should Contain  ${resp.text}  @article{doe1998
