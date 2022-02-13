# mal-authtoken-generator will generate your own OAuth token to access MyAnimeList
# Copyright (C) 2022  Vidhu Kant Sharma <vidhukant@protonmail.ch>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import secrets
import webbrowser

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

client_id = ""
code_challenge = ""

def get_access_token(code):
    url = "https://myanimelist.net/v1/oauth2/token"
    my_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    my_data = {
        "client_id": client_id,
        "code_verifier": code_challenge,
        "grant_type": "authorization_code",
        "code": code,
    }
    return requests.post(url, data=my_data, headers=my_headers)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # the flakiest shit ever
        path = self.path
        params = urllib.parse.parse_qs(path[7:])
        
        try:
            code = params["code"][0]
            res = get_access_token(code)
            print(res.json())
        except KeyError:
            try:
                error = params["error"][0]
                error_message = params["message"][0]
                error_hint = params["hint"][0]

                print("Error:", error, "<" + error_message + ">", "(" + error_hint + ")")
                # write error message to browser window
                self.wfile.write(bytes("<html><head><title>Error</title></head>", "utf-8"))
                self.wfile.write(bytes("<body><p>Error: %s</p>" % error_hint, "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
            except:
                pass
        exit(0)

def get_new_code_challenge() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

def auth_link():
    return "https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id=" + client_id + "&code_challenge=" + code_challenge

def ask_for_client_id():
    has_client_id = input("Do you already have a MyAnimeList Client ID? [Y/n] ").lower()
    if has_client_id in ["y", ""]:
        global client_id 
        client_id = input("Please enter your Client ID: \u001b[32m")
        print("\u001b[0m") # reset color
    else:
        if has_client_id == "n":
            print("Please create a new Client ID here: \u001b[36mhttps://myanimelist.net/apiconfig/create\u001b[0m")
            print("\t\u001b[37;1m1. \u001b[0mSet the App Redirect URL to \u001b[36;1m\"http://localhost:8080\"\u001b[0m")
            print("\t\u001b[37;1m2. \u001b[0mRestart my script again and then enter your brand new Client ID!")
            print("Refer to this guide for more details: \u001b[36mhttps://myanimelist.net/blog.php?eid=835707\u001b[0m")
        else:
            print("Error: Invalid Input.")
        exit(2)

if __name__ == '__main__':
    # credits
    print("This script implements the wonderful guide by ZeroCrystal: \u001b[36mhttps://myanimelist.net/blog.php?eid=835707\u001b[0m")

    ask_for_client_id()
    code_challenge = get_new_code_challenge()

    auth_link = auth_link()
    print("Opening authentication prompt in web browser. If a browser doesn't get launched, please click on this link:")
    print("\u001b[36m" + auth_link + "\u001b[0m")
    webbrowser.open(auth_link, new = 2)

    myServer = HTTPServer(('', 8080), MyServer)
    myServer.serve_forever()
