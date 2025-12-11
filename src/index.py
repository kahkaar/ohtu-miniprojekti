from app import app
from util import set_session

if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0", debug=True)

    # Enable or disable tag and category search feature
    TC_SEARCH = True
    set_session("tc-search", TC_SEARCH)
