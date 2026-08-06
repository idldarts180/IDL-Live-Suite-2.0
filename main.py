"""
IDL Live Suite
Version 1.0
"""

import time

from browser.scolia_client import ScoliaClient
from ui.dashboard import Dashboard


client = ScoliaClient()

client.wait_for_match()

app = Dashboard()


def refresh():

    data = client.get_match_data()

    if data:

        app.update_scores(data)

    app.after(1000, refresh)


refresh()

try:

    app.mainloop()

finally:

    client.close()